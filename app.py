import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse

PARTNER_ID = 1280109
PARTNER_KEY = "426d64704149597959665661444854666f417a69786e626a656d70454b76534e"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"
BASE_URL = "https://partner.test-stable.shopeemobile.com"

def generate_login_url():
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    sign_base = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()
    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe="")

    return (
        f"{BASE_URL}{path}?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}&sign={sign}&redirect={redirect_encoded}"
    )

# ===== Streamlit Web App =====
st.set_page_config(page_title="Shopee OAuth Login", page_icon="🔑")
st.title("🔑 Shopee OAuth Login")

query_params = st.query_params
code = query_params.get("code", [None])[0]
shop_id = query_params.get("shop_id", [None])[0]

if code and shop_id:
    st.success(f"✅ ได้รับ code: `{code}` และ shop_id: `{shop_id}`")
    st.write("📦 เรียก API เพื่อขอ access token...")

    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    sign_base = f"{PARTNER_ID}{path}{timestamp}{code}"  # 🔑 ใช้ code ไม่ใช่ shop_id
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()

    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }
    json_data = {
        "code": code,
        "partner_id": PARTNER_ID,
        "shop_id": int(shop_id)
    }

    try:
        res = requests.post(url, headers=headers, params=params, json=json_data)
        res.raise_for_status()
        data = res.json()
        if "access_token" in data:
            st.success("🎉 ได้รับ Access Token แล้ว!")
            st.code(data["access_token"])
        else:
            st.error(data)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("👇 กรุณาคลิกเพื่อเริ่มต้นการ Login กับ Shopee")
    login_url = generate_login_url()
    st.markdown(f"[🟢 Login Shopee ที่นี่]({login_url})")
