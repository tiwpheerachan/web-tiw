import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse
import json

# ===== ตั้งค่าแอป Shopee =====
PARTNER_ID = 1280109
# ⚠️ คุณต้องใส่ Partner Key จริงที่นี่
PARTNER_KEY = "5a4e6e4c4d4375464c57506b7a42775a77466d686c534255574267514f494a54"  # แทนที่ด้วย key จริง
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
    
    # สร้าง signature: partner_id + path + timestamp
    sign_base = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), sign_base.encode(), hashlib.sha256).hexdigest()

    headers = {"Content-Type": "application/json"}
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }
    
    # Request body
    json_data = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": PARTNER_ID
    }

    # Debug information
    st.write("🔍 **Debug Token Request:**")
    st.write(f"- URL: {url}")
    st.write(f"- Sign Base: `{sign_base}`")
    st.write(f"- Sign: `{sign}`")
    st.write(f"- Body: `{json.dumps(json_data)}`")
    st.write(f"- Timestamp: {timestamp}")

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

# ====== หน้าเว็บ ======
st.set_page_config(page_title="Shopee OAuth & Shop Data", page_icon="🛒")
st.title("🛒 Shopee OAuth & Shop Management")

# แสดงข้อมูลการตั้งค่า
st.sidebar.header("⚙️ การตั้งค่า")
st.sidebar.write(f"**Partner ID:** {PARTNER_ID}")
st.sidebar.write(f"**Shop ID:** 142837")
st.sidebar.write(f"**Redirect URL:** {REDIRECT_URL}")

# ตรวจสอบว่าใส่ Partner Key หรือยัง
if PARTNER_KEY == "YOUR_ACTUAL_PARTNER_KEY_HERE":
    st.error("⚠️ **กรุณาใส่ Partner Key จริงในโค้ด!**")
    st.write("ไปที่บรรทัดที่ 10 ในโค้ด และแทนที่ `YOUR_ACTUAL_PARTNER_KEY_HERE` ด้วย Partner Key จริงจาก Shopee Console")
    st.stop()

# ✅ ปรับปรุงการจัดการ query parameters
query_params = st.query_params

# ตรวจสอบ parameters ทั้งหมดที่ได้รับ
st.write("🔍 **All Query Parameters:**")
for key, value in query_params.items():
    st.write(f"- {key}: {value}")

# จัดการ parameters ที่เป็นไปได้
code = query_params.get("code")
shop_id = query_params.get("shop_id") 
query_token = query_params.get("query_token")
cookie_token = query_params.get("cookie_token")

# แสดงสถานะ parameters
if query_token is not None or cookie_token is not None:
    st.warning("⚠️ พบ query_token หรือ cookie_token - อาจเป็น error จากการ redirect")
    
    if query_token == "" and cookie_token == "":
        st.info("💡 **คำแนะนำ:** ลองคลิก 'Confirm Authorization' ในหน้า Shopee อีกครั้ง")

if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    if st.button("🔄 ดึง Access Token"):
        with st.spinner("🔄 กำลังดึง Access Token..."):
            try:
                res = get_access_token(code, shop_id)
                
                st.write("📋 **Response Status:**", res.status_code)
                
                if res.status_code == 200:
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
                else:
                    st.error(f"❌ HTTP Error {res.status_code}")
                    try:
                        error_data = res.json()
                        st.json(error_data)
                        
                        # แสดงคำแนะนำเพิ่มเติม
                        if "error_sign" in str(error_data):
                            st.info("💡 **คำแนะนำ:** ตรวจสอบ Partner Key อีกครั้ง")
                    except:
                        st.text(res.text)
                        
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")

elif code and not shop_id:
    st.warning("⚠️ ได้รับ code แต่ไม่มี shop_id")
    st.write(f"Code: {code}")
    
elif not code and shop_id:
    st.warning("⚠️ ได้รับ shop_id แต่ไม่มี code")
    st.write(f"Shop ID: {shop_id}")

# แสดงข้อมูลร้านค้าถ้ามี access token
if hasattr(st.session_state, 'access_token') and st.session_state.access_token:
    st.divider()
    st.subheader("🏪 ข้อมูลร้านค้า")
    
    if st.button("📊 ดึงข้อมูลร้านค้า", use_container_width=True):
        with st.spinner("🔄 กำลังดึงข้อมูลร้านค้า..."):
            try:
                shop_res = get_shop_info(st.session_state.access_token, st.session_state.shop_id)
                
                if shop_res.status_code == 200:
                    shop_data = shop_res.json()
                    
                    if "error" not in shop_data:
                        st.success("✅ ดึงข้อมูลร้านค้าสำเร็จ!")
                        st.json(shop_data)
                    else:
                        st.error(f"❌ API Error: {shop_data}")
                else:
                    st.error(f"❌ HTTP Error {shop_res.status_code}")
                    st.text(shop_res.text)
                    
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")

else:
    st.info("👇 กรุณาคลิกปุ่มเพื่อเริ่มต้นการ Login กับ Shopee")
    
    # แสดงข้อมูล Test Account
    with st.expander("🧪 ข้อมูล Test Account"):
        st.write("**Shop ID:** 142837")
        st.write("**Shop Account:** SANDBOX.f216878ec16b03a6f962")
        st.write("**Shop Password:** 1bdd53e0ec3b7fb2")
        st.write("**Shop Login URL:** https://seller.test-stable.shopee.co.th")
    
    # แสดงขั้นตอนการใช้งาน
    with st.expander("📋 ขั้นตอนการใช้งาน"):
        st.write("""
        1. คลิกปุ่ม "คลิกเพื่อ Login Shopee" ด้านล่าง
        2. ใช้ข้อมูล Test Account ด้านบนเพื่อ Login
        3. คลิก "Confirm Authorization" ในหน้า Shopee
        4. รอให้ระบบ redirect กลับมาที่หน้านี้
        5. คลิก "ดึง Access Token" เพื่อขอ token
        """)
    
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

# แสดงข้อมูล Debug
with st.expander("🔧 Debug Information"):
    st.write("**Current Query Parameters:**")
    st.json(dict(query_params))
    
    st.write("**Configuration:**")
    st.write(f"- Partner ID: {PARTNER_ID}")
    st.write(f"- Partner Key: {'*' * 20}...{PARTNER_KEY[-4:] if len(PARTNER_KEY) > 4 else 'NOT_SET'}")
    st.write(f"- Redirect URL: {REDIRECT_URL}")
    
    if hasattr(st.session_state, 'access_token'):
        st.write("**Session State:**")
        st.write(f"- Access Token: {st.session_state.access_token[:20]}...")
        st.write(f"- Shop ID: {st.session_state.shop_id}")

# แสดงคำแนะนำเพิ่มเติม
st.info("""
💡 **สถานะปัจจุบัน:** คุณได้ไปถึงหน้า Authorization ของ Shopee แล้ว! 

**ขั้นตอนต่อไป:**
1. ใส่ Partner Key จริงในโค้ด (บรรทัดที่ 10)
2. คลิก "Confirm Authorization" ในหน้า Shopee
3. รอให้ระบบ redirect กลับมา
4. คลิก "ดึง Access Token"

**หากยังมี error:** ลองตรวจสอบ Partner Key และ Redirect URL อีกครั้ง
""")
