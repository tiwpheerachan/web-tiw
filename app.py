import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse

# ===== ตั้งค่าแอป Shopee =====
PARTNER_ID = 1280109
PARTNER_KEY = "426d64704149597959665661444854666f417a69786e626a656d70454b76534e"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"  # ต้องตรงกับใน Shopee Developer Console

# ===== Function สร้างลิงก์ login =====
def generate_login_url():
    timestamp = int(time.time())
    base_url = "https://partner.test-stable.shopeemobile.com/api/v2/shop/auth_partner"
    sign_base = f"{PARTNER_ID}{REDIRECT_URL}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()
    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe="")
    login_url = f"{base_url}?partner_id={PARTNER_ID}&redirect={redirect_encoded}&timestamp={timestamp}&sign={sign}"
    return login_url

# ====== หน้าเว็บ ======
st.title("\U0001f511 Shopee OAuth Login")

query_params = st.query_params
code = query_params.get("code", [None])[0]

if code:
    st.success(f"ได้รับ code: {code}")
    st.write("\U0001f447 ดึง access token ได้ตรงนี้:")

    url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get"
    timestamp = int(time.time())

    shop_id = query_params.get("shop_id", [None])[0]
    sign_base = f"{PARTNER_ID}/api/v2/auth/token/get{timestamp}{code}"
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()

    headers = {"Content-Type": "application/json"}
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }
    json_data = {
        "code": code,
        "shop_id": int(shop_id) if shop_id else None,
        "partner_id": PARTNER_ID
    }

    res = requests.post(url, headers=headers, params=params, json=json_data)
    st.json(res.json())

else:
    login_url = generate_login_url()
    st.markdown(f"[\U0001f7e2 คลิกเพื่อ Login Shopee]({login_url})")
