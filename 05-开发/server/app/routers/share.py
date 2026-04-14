"""微信分享码生成路由。"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ShareLinkResponse(BaseModel):
    spot_id: int
    title: str
    description: str
    url_scheme: str
    webpage_url: str


@router.get("/share/spots/{spot_id}", response_model=dict)
async def get_share_link(
    spot_id: int,
    title: str = "钓了吗",
    description: str = "一起来钓鱼吧！",
):
    """生成分享链接。
    URL Scheme: diaolema://spot/{spot_id}
    """
    url_scheme = f"diaolema://spot/{spot_id}"
    webpage_url = f"https://diaolema.com/share/spot?id={spot_id}"
    return {
        "code": 0,
        "data": {
            "spot_id": spot_id,
            "title": title,
            "description": description,
            "url_scheme": url_scheme,
            "webpage_url": webpage_url,
        },
        "msg": "",
    }


@router.post("/share/generate-qr", response_model=dict)
async def generate_qr(
    spot_id: int,
    title: str = "钓了吗",
):
    """生成分享二维码（返回 data URL）。
    实际项目建议调用微信 OCR 接口或第三方二维码服务。
    """
    import qrcode
    import io
    import base64

    url_scheme = f"diaolema://spot/{spot_id}"
    img = qrcode.make(url_scheme)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    data_url = f"data:image/png;base64,{b64}"

    return {
        "code": 0,
        "data": {
            "spot_id": spot_id,
            "title": title,
            "qr_data_url": data_url,
        },
        "msg": "",
    }
