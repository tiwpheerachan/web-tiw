import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse
import json

# ===== ตั้งค่าแอป Shopee (Sandbox/Test) =====
PARTNER_ID = 1280109
PARTNER_KEY = "426d64704149597959665661444854666f417a69786e626a656d70454b76534e"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"

# ===== Function สร้างลิงก์ login Shopee =====
def generate_login_url():
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    base_url = f"https://partner.test-stable.shopeemobile.com{path}"

    # สร้าง sign ด้วย partner_id + path + timestamp
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

# ===== Function ดึง Access Token =====
def get_access_token(code, shop_id):
    url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get"
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    
    # สร้าง request body
    json_data = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": PARTNER_ID
    }
    
    # แปลง body เป็น JSON string (ไม่มีช่องว่าง)
    body_str = json.dumps(json_data, separators=(',', ':'))
    
    # ✅ สร้าง signature ที่ถูกต้อง: partner_id + path + timestamp + body
    sign_base = f"{PARTNER_ID}{path}{timestamp}{body_str}"
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()

    headers = {"Content-Type": "application/json"}
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }

    return requests.post(url, headers=headers, params=params, json=json_data)

# ===== Function ดึงข้อมูลร้านค้า =====
def get_shop_info(access_token, shop_id):
    url = "https://partner.test-stable.shopeemobile.com/api/v2/shop/get_shop_info"
    timestamp = int(time.time())
    path = "/api/v2/shop/get_shop_info"
    
    # สร้าง signature: partner_id + path + timestamp + access_token + shop_id
    sign_base = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()

    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": sign
    }

    return requests.get(url, params=params)

# ===== Function ดึงรายการสินค้า =====
def get_products(access_token, shop_id, page_size=20, offset=0):
    url = "https://partner.test-stable.shopeemobile.com/api/v2/product/get_item_list"
    timestamp = int(time.time())
    path = "/api/v2/product/get_item_list"
    
    # สร้าง signature
    sign_base = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()

    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": sign,
        "page_size": page_size,
        "offset": offset
    }

    return requests.get(url, params=params)

# ====== หน้าเว็บ ======
st.set_page_config(page_title="Shopee OAuth & Shop Data", page_icon="🛒")
st.title("🛒 Shopee OAuth & Shop Management")

# ตรวจสอบ query parameters
query_params = st.query_params
code = query_params.get("code")
shop_id = query_params.get("shop_id")

if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    # ดึง Access Token
    with st.spinner("🔄 กำลังดึง Access Token..."):
        try:
            res = get_access_token(code, shop_id)
            res.raise_for_status()
            token_data = res.json()
            
            if "access_token" in token_data:
                access_token = token_data["access_token"]
                refresh_token = token_data.get("refresh_token", "")
                
                st.success("🎉 ได้รับ Access Token สำเร็จ!")
                
                # แสดงข้อมูล Token
                with st.expander("📋 Token Information"):
                    st.json(token_data)
                
                # เก็บ token ใน session state
                st.session_state.access_token = access_token
                st.session_state.shop_id = shop_id
                st.session_state.refresh_token = refresh_token
                
            else:
                st.error("❌ ไม่พบ access_token ใน response")
                st.json(token_data)
                
        except requests.exceptions.HTTPError as http_err:
            st.error(f"❌ HTTP Error: {http_err}")
            if hasattr(http_err.response, 'text'):
                st.code(http_err.response.text)
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")

# แสดงข้อมูลร้านค้าถ้ามี access token
if hasattr(st.session_state, 'access_token') and st.session_state.access_token:
    st.divider()
    st.subheader("🏪 ข้อมูลร้านค้า")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 ดึงข้อมูลร้านค้า", use_container_width=True):
            with st.spinner("🔄 กำลังดึงข้อมูลร้านค้า..."):
                try:
                    shop_res = get_shop_info(st.session_state.access_token, st.session_state.shop_id)
                    shop_res.raise_for_status()
                    shop_data = shop_res.json()
                    
                    if "error" not in shop_data:
                        st.success("✅ ดึงข้อมูลร้านค้าสำเร็จ!")
                        st.json(shop_data)
                    else:
                        st.error(f"❌ API Error: {shop_data}")
                        
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
    
    with col2:
        if st.button("📦 ดึงรายการสินค้า", use_container_width=True):
            with st.spinner("🔄 กำลังดึงรายการสินค้า..."):
                try:
                    products_res = get_products(st.session_state.access_token, st.session_state.shop_id)
                    products_res.raise_for_status()
                    products_data = products_res.json()
                    
                    if "error" not in products_data:
                        st.success("✅ ดึงรายการสินค้าสำเร็จ!")
                        
                        if "response" in products_data and "item" in products_data["response"]:
                            items = products_data["response"]["item"]
                            st.write(f"📊 จำนวนสินค้าทั้งหมด: {len(items)} รายการ")
                            
                            # แสดงรายการสินค้าในตาราง
                            if items:
                                import pandas as pd
                                df = pd.DataFrame(items)
                                st.dataframe(df, use_container_width=True)
                            else:
                                st.info("ไม่มีสินค้าในร้าน")
                        else:
                            st.json(products_data)
                    else:
                        st.error(f"❌ API Error: {products_data}")
                        
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")

else:
    st.info("👇 กรุณาคลิกปุ่มเพื่อเริ่มต้นการ Login กับ Shopee")
    login_url = generate_login_url()
    
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <a href="{login_url}" target="_self" style="
            background-color: #ee4d2d;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            display: inline-block;
        ">🟢 คลิกเพื่อ Login Shopee</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **หมายเหตุ:** หลังจาก Login สำเร็จ คุณจะสามารถดึงข้อมูลร้านค้าและรายการสินค้าได้")

# แสดงข้อมูล Debug
with st.expander("🔧 Debug Information"):
    st.write("**Current Query Parameters:**")
    st.json(dict(query_params))
    
    if hasattr(st.session_state, 'access_token'):
        st.write("**Session State:**")
        st.write(f"- Access Token: {st.session_state.access_token[:20]}...")
        st.write(f"- Shop ID: {st.session_state.shop_id}")
