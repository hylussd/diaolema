"""商城服务层。"""
import json
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select, update, delete, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Product, Cart, CartItem, Order, OrderItem, ProductCategory, User
)
from app.models.order import generate_order_no
from app.schemas.shop import (
    CartItemSchema, CartSchema, OrderSchema, OrderItemSchema,
    OrderCreateResponse,
)


class ShopService:
    """商城业务逻辑服务。"""

    # -------------------
    # 购物车
    # -------------------

    @staticmethod
    async def get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
        """获取或创建用户购物车。"""
        result = await db.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.flush()
        return cart

    @staticmethod
    async def get_cart_with_items(db: AsyncSession, user_id: int) -> CartSchema:
        """获取用户购物车（含 items 和 total_amount）。"""
        cart = await ShopService.get_or_create_cart(db, user_id)

        result = await db.execute(
            select(CartItem, Product)
            .join(Product, CartItem.product_id == Product.id)
            .where(CartItem.cart_id == cart.id)
        )
        rows = result.all()

        items = []
        total_amount = 0
        total_count = 0
        for cart_item, product in rows:
            subtotal = product.price * cart_item.quantity
            total_amount += subtotal
            total_count += cart_item.quantity

            item_schema = CartItemSchema(
                id=cart_item.id,
                product_id=product.id,
                name=product.name,
                price=product.price,
                images=json.loads(product.images) if product.images else None,
                specs=json.loads(cart_item.specs) if cart_item.specs else None,
                quantity=cart_item.quantity,
                subtotal=subtotal,
            )
            items.append(item_schema)

        return CartSchema(
            id=cart.id,
            items=items,
            total_amount=total_amount,
            total_count=total_count,
        )

    @staticmethod
    async def create_or_update_cart_item(
        db: AsyncSession,
        user_id: int,
        product_id: int,
        quantity: int,
        specs: dict | None = None,
    ) -> dict:
        """
        添加/更新购物车商品。
        同 product_id + specs 则累加 quantity；否则新建。
        库存不足时 raise 422。
        返回 {"cart_id": int, "item_id": int}
        """
        # 校验商品
        prod_result = await db.execute(select(Product).where(Product.id == product_id))
        product = prod_result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

        if not product.is_active:
            raise HTTPException(status_code=400, detail="商品已下架")

        specs_json = json.dumps(specs, ensure_ascii=False) if specs else None

        cart = await ShopService.get_or_create_cart(db, user_id)

        # 查找同 product_id + specs 的已有项
        existing_result = await db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id,
                CartItem.specs == specs_json,
            )
        )
        existing_item = existing_result.scalar_one_or_none()

        new_quantity = quantity
        if existing_item:
            new_quantity = existing_item.quantity + quantity

        # 库存校验
        if new_quantity > product.stock:
            raise HTTPException(
                status_code=422,
                detail=f"库存不足，当前库存 {product.stock} 件",
            )

        if existing_item:
            existing_item.quantity = new_quantity
            await db.flush()
            item_id = existing_item.id
        else:
            new_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                specs=specs_json,
            )
            db.add(new_item)
            await db.flush()
            item_id = new_item.id

        await db.commit()
        return {"cart_id": cart.id, "item_id": item_id}

    @staticmethod
    async def update_cart_item(
        db: AsyncSession,
        user_id: int,
        item_id: int,
        quantity: int,
    ) -> None:
        """更新购物车商品数量；quantity=0 等同删除。"""
        cart = await ShopService.get_or_create_cart(db, user_id)

        if quantity == 0:
            await db.execute(
                delete(CartItem).where(
                    CartItem.id == item_id, CartItem.cart_id == cart.id
                )
            )
            await db.commit()
            return

        # 校验库存
        item_result = await db.execute(
            select(CartItem, Product)
            .join(Product, CartItem.product_id == Product.id)
            .where(CartItem.id == item_id, CartItem.cart_id == cart.id)
        )
        row = item_result.one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="购物车项不存在")

        cart_item, product = row
        if quantity > product.stock:
            raise HTTPException(
                status_code=422,
                detail=f"库存不足，当前库存 {product.stock} 件",
            )

        cart_item.quantity = quantity
        await db.commit()

    @staticmethod
    async def delete_cart_item(
        db: AsyncSession, user_id: int, item_id: int
    ) -> None:
        """删除购物车商品。"""
        cart = await ShopService.get_or_create_cart(db, user_id)
        result = await db.execute(
            delete(CartItem).where(
                CartItem.id == item_id, CartItem.cart_id == cart.id
            )
        )
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="购物车项不存在")

    @staticmethod
    async def clear_cart(db: AsyncSession, user_id: int) -> None:
        """清空用户购物车。"""
        cart = await ShopService.get_or_create_cart(db, user_id)
        await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        await db.commit()

    # -------------------
    # 订单
    # -------------------

    @staticmethod
    async def create_order_from_cart(
        db: AsyncSession,
        user_id: int,
        address_name: str,
        address_phone: str,
        address_detail: str,
        remark: str | None,
        pay_status: str = "unpaid",
    ) -> OrderCreateResponse:
        """
        购物车全量结算：扣库存 → 创建订单 → 清空购物车。
        库存不足 raise 422。
        """
        cart = await ShopService.get_or_create_cart(db, user_id)

        # 取出所有购物车项
        items_result = await db.execute(
            select(CartItem, Product)
            .join(Product, CartItem.product_id == Product.id)
            .where(CartItem.cart_id == cart.id)
        )
        rows = list(items_result.all())
        if not rows:
            raise HTTPException(status_code=400, detail="购物车为空")

        # 校验库存并扣减（原子操作）
        total_amount = 0
        order_items_data = []
        for cart_item, product in rows:
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=422,
                    detail=f"商品「{product.name}」库存不足，当前库存 {product.stock} 件",
                )
            # 原子扣库存
            result = await db.execute(
                update(Product)
                .where(
                    Product.id == product.id,
                    Product.stock >= cart_item.quantity,
                )
                .values(stock=Product.stock - cart_item.quantity)
            )
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=422,
                    detail=f"商品「{product.name}」库存不足（并发冲突）",
                )

            subtotal = product.price * cart_item.quantity
            total_amount += subtotal
            order_items_data.append(
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "product_price": product.price,
                    "quantity": cart_item.quantity,
                    "specs": cart_item.specs,
                }
            )

        # 生成订单号
        order_no = generate_order_no()

        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user_id,
            total_amount=total_amount,
            status="pending",
            address_name=address_name,
            address_phone=address_phone,
            address_detail=address_detail,
            remark=remark,
            pay_status=pay_status,
            pay_time=datetime.utcnow() if pay_status == "paid" else None,
        )
        db.add(order)
        await db.flush()

        # 创建订单项
        for item_data in order_items_data:
            order_item = OrderItem(order_id=order.id, **item_data)
            db.add(order_item)

        # 清空购物车
        await db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))

        await db.commit()

        return OrderCreateResponse(
            order_id=order.id,
            order_no=order.order_no,
            total_amount=order.total_amount,
            status=order.status,
            pay_status=order.pay_status,
        )

    @staticmethod
    async def get_order_list(
        db: AsyncSession,
        user_id: int,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> dict:
        """订单列表。"""
        stmt = select(Order).where(Order.user_id == user_id)
        count_stmt = select(func.count(Order.id)).where(Order.user_id == user_id)

        if status:
            stmt = stmt.where(Order.status == status)
            count_stmt = count_stmt.where(Order.status == status)

        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = stmt.offset(offset).limit(limit).order_by(Order.created_at.desc())
        orders = (await db.execute(stmt)).scalars().all()

        items = []
        for order in orders:
            items_result = await db.execute(
                select(OrderItem).where(OrderItem.order_id == order.id)
            )
            order_items = items_result.scalars().all()
            items.append(
                OrderSchema(
                    order_id=order.id,
                    order_no=order.order_no,
                    total_amount=order.total_amount,
                    status=order.status,
                    pay_status=order.pay_status,
                    address_name=order.address_name,
                    address_phone=order.address_phone,
                    address_detail=order.address_detail,
                    remark=order.remark,
                    items=[OrderItemSchema.from_orm(oi) for oi in order_items],
                    created_at=order.created_at,
                    pay_time=order.pay_time,
                )
            )

        return {"total": total, "items": items}

    @staticmethod
    async def get_order_detail(
        db: AsyncSession, user_id: int, order_id: int
    ) -> OrderSchema:
        """订单详情。"""
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        items_result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order_items = items_result.scalars().all()

        # 手机号脱敏
        phone = order.address_phone
        if phone and len(phone) >= 7:
            phone = phone[:3] + "****" + phone[-4:]

        return OrderSchema(
            order_id=order.id,
            order_no=order.order_no,
            total_amount=order.total_amount,
            status=order.status,
            pay_status=order.pay_status,
            address_name=order.address_name,
            address_phone=phone,
            address_detail=order.address_detail,
            remark=order.remark,
            items=[OrderItemSchema.from_orm(oi) for oi in order_items],
            created_at=order.created_at,
            pay_time=order.pay_time,
        )

    @staticmethod
    async def cancel_order(db: AsyncSession, user_id: int, order_id: int) -> None:
        """取消订单（仅 pending 状态），退回库存。"""
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        if order.status != "pending":
            raise HTTPException(status_code=400, detail="仅待支付订单可取消")

        # 退回库存
        items_result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order_items = items_result.scalars().all()

        for item in order_items:
            await db.execute(
                update(Product)
                .where(Product.id == item.product_id)
                .values(stock=Product.stock + item.quantity)
            )

        order.status = "cancelled"
        await db.commit()

    @staticmethod
    async def mock_pay(
        db: AsyncSession, user_id: int, order_id: int, pay_status: str
    ) -> dict:
        """模拟支付：更新 pay_status 和 pay_time。"""
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        if order.pay_status == "paid":
            raise HTTPException(status_code=400, detail="订单已支付")

        order.pay_status = pay_status
        order.status = "paid" if pay_status == "paid" else order.status
        if pay_status == "paid":
            order.pay_time = datetime.utcnow()
        await db.commit()

        return {"order_no": order.order_no, "pay_status": order.pay_status}


shop_service = ShopService()
