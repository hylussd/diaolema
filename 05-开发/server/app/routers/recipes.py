"""配方 CRUD 路由。"""
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeResponse
from app.services.anti_spam_service import anti_spam_service

router = APIRouter()


def _recipe_to_dict(r: Recipe, include_user: bool = True) -> dict:
    return {
        "id": r.id,
        "user_id": r.user_id if include_user else None,
        "name": r.name,
        "pressure_min": r.pressure_min,
        "pressure_max": r.pressure_max,
        "water_temp_min": r.water_temp_min,
        "water_temp_max": r.water_temp_max,
        "fish_species": r.fish_species,
        "spot_type": r.spot_type,
        "is_public": bool(r.is_public),
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }


@router.post("/recipes", response_model=dict)
async def create_recipe(
    data: RecipeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
):
    """创建配方。"""
    if data.spot_type:
        anti_spam_service.validate_spot_type(data.spot_type)

    recipe = Recipe(
        user_id=user_id,
        name=data.name,
        pressure_min=data.pressure_min,
        pressure_max=data.pressure_max,
        water_temp_min=data.water_temp_min,
        water_temp_max=data.water_temp_max,
        fish_species=data.fish_species,
        spot_type=data.spot_type,
        is_public=1 if data.is_public else 0,
    )
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    return {
        "code": 0,
        "data": {"id": recipe.id, "name": recipe.name},
        "msg": "配方创建成功",
    }


@router.get("/recipes/me", response_model=dict)
async def list_my_recipes(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """查询我的所有配方（含公开和私有）。"""
    stmt = (
        select(Recipe)
        .where(Recipe.user_id == user_id)
        .offset(offset)
        .limit(limit)
        .order_by(Recipe.created_at.desc())
    )
    count_stmt = select(func.count(Recipe.id)).where(Recipe.user_id == user_id)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    result = await db.execute(stmt)
    items = [_recipe_to_dict(r) for r in result.scalars().all()]

    return {"code": 0, "data": {"total": total, "items": items}, "msg": ""}


@router.get("/recipes/public", response_model=dict)
async def list_public_recipes(
    db: Annotated[AsyncSession, Depends(get_db)],
    fish_species: str | None = Query(None),
    spot_type: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """查询社区公开配方列表（匿名，不暴露创建者）。"""
    stmt = select(Recipe).where(Recipe.is_public == 1)
    count_stmt = select(func.count(Recipe.id)).where(Recipe.is_public == 1)

    if fish_species:
        stmt = stmt.where(Recipe.fish_species == fish_species)
        count_stmt = count_stmt.where(Recipe.fish_species == fish_species)
    if spot_type:
        stmt = stmt.where(Recipe.spot_type == spot_type)
        count_stmt = count_stmt.where(Recipe.spot_type == spot_type)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.offset(offset).limit(limit).order_by(Recipe.created_at.desc())
    result = await db.execute(stmt)
    items = [_recipe_to_dict(r, include_user=False) for r in result.scalars().all()]

    return {"code": 0, "data": {"total": total, "items": items}, "msg": ""}


@router.get("/recipes/{recipe_id}", response_model=dict)
async def get_recipe(
    recipe_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(None, description="用户ID，TODO: 替换为真实认证"),
):
    """查询单条配方。公开配方任意访问，私有配方仅创建者。"""
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    if not bool(recipe.is_public) and (user_id is None or recipe.user_id != user_id):
        raise HTTPException(status_code=403, detail="无权查看此配方")
    return {
        "code": 0,
        "data": _recipe_to_dict(recipe, include_user=bool(recipe.is_public)),
        "msg": "",
    }


@router.put("/recipes/{recipe_id}", response_model=dict)
async def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
):
    """更新配方（仅创建者可操作）。"""
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    if recipe.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权修改此配方")

    update_dict = data.model_dump(exclude_unset=True)
    if "spot_type" in update_dict and update_dict["spot_type"]:
        anti_spam_service.validate_spot_type(update_dict["spot_type"])
    if "is_public" in update_dict:
        update_dict["is_public"] = 1 if update_dict["is_public"] else 0
    if "updated_at" not in update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc)

    for k, v in update_dict.items():
        setattr(recipe, k, v)

    await db.commit()
    return {"code": 0, "data": {"id": recipe.id}, "msg": "更新成功"}


@router.delete("/recipes/{recipe_id}", response_model=dict)
async def delete_recipe(
    recipe_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
):
    """删除配方（仅创建者可操作）。"""
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    if recipe.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此配方")

    await db.delete(recipe)
    await db.commit()
    return {"code": 0, "data": {"id": recipe_id}, "msg": "删除成功"}
