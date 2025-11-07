import requests
from fastapi import HTTPException
from .config import settings


def wechat_code2session(code: str) -> dict:
    """调用微信官方 jscode2session 接口，返回 openid、session_key 等。
    开发环境可通过 WECHAT_MOCK=1 使用模拟数据。
    """

    if settings.WECHAT_MOCK == "1" or not (settings.WECHAT_APPID and settings.WECHAT_APP_SECRET):
        # 模拟：仅用于联调与H5环境
        return {
            "openid": f"mock_{code}",
            "session_key": "mock_session",
            "is_mock": True,
        }

    url = (
        "https://api.weixin.qq.com/sns/jscode2session"
        f"?appid={settings.WECHAT_APPID}&secret={settings.WECHAT_APP_SECRET}&js_code={code}&grant_type=authorization_code"
    )
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError:
            raise HTTPException(status_code=502, detail="invalid json from wechat")
    except requests.exceptions.RequestException as e:
        # 网络异常或微信服务不可用
        raise HTTPException(status_code=502, detail=f"wechat network error: {str(e)}")

    if "errcode" in data and data.get("errcode") not in (None, 0):
        raise HTTPException(status_code=400, detail=f"wechat error: {data.get('errmsg','unknown')}")
    if "openid" not in data:
        raise HTTPException(status_code=400, detail="openid not found from wechat")
    return data