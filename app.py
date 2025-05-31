import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse

# ===== ตั้งค่าแอป Shopee (Sandbox/Test) =====
PARTNER_ID = 1280109
PARTNER_KEY = "426d64704149597959665661444854666f417a69786e626a656d70454b76534e"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"  # ต้องตรงกับ Shopee Console แบบเป๊ะ (รวม / ท้ายสุด)

# ===== Function สร้างลิงก์ login Shopee =====
def generate_login_url():
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    base_url = f"https://partner.test-stable.shopeemobile.com{path}"

    # sign base ตาม Shopee: partner_id + path + timestamp
    sign_base = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()

    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe="")
    login_url = (
        f"{base_url}?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={redirect_encoded}"
    )
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
