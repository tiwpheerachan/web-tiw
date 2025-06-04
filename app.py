import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse
import json
import base64
import re

# ===== ตั้งค่าแอป Shopee =====
PARTNER_ID = 1280109
PARTNER_KEY = "5a4e6e4c4d4375464c57506b7a42775a77466d686c534255574267514f494a54"
# ⚠️ ตรวจสอบ Redirect URL ให้ตรงกับที่ตั้งค่าใน Shopee Console (รวมถึง / ท้ายสุด)
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"

# ===== Function สร้างลิงก์ login Shopee (ปรับปรุงใหม่) =====
def generate_login_url():
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    base_url = f"https://partner.test-stable.shopeemobile.com{path}"

    # สร้าง sign ด้วย partner_id + path + timestamp
    sign_base = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(bytes.fromhex(PARTNER_KEY), sign_base.encode(), hashlib.sha256).hexdigest()

    # ตรวจสอบว่า REDIRECT_URL ลงท้ายด้วย / หรือไม่
    if not REDIRECT_URL.endswith('/'):
        redirect_url = f"{REDIRECT_URL}/"
    else:
        redirect_url = REDIRECT_URL
        
    redirect_encoded = urllib.parse.quote(redirect_url, safe="")
    login_url = (
        f"{base_url}?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={redirect_encoded}"
    )
    
    # Debug information
    st.session_state.last_login_url = login_url
    st.session_state.last_sign_base = sign_base
    st.session_state.last_sign = sign
    st.session_state.last_timestamp = timestamp
    
    return login_url

# ===== Function ดึง Access Token (ปรับปรุงใหม่) =====
def get_access_token(code, shop_id):
    url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get"
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    
    # ✅ ทดลองวิธีที่ 1: partner_id + path + timestamp
    sign_base = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(bytes.fromhex(PARTNER_KEY), sign_base.encode(), hashlib.sha256).hexdigest()

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
    debug_info = {
        "url": url,
        "method": "POST",
        "headers": headers,
        "params": params,
        "json_data": json_data,
        "sign_base": sign_base,
        "sign": sign,
        "timestamp": timestamp
    }
    st.session_state.last_token_request = debug_info
    
    return requests.post(url, headers=headers, params=params, json=json_data)

# ===== Function ดึง Access Token แบบที่ 2 =====
def get_access_token_alt(code, shop_id):
    url = "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get"
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    
    # Request body
    json_data = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": PARTNER_ID
    }
    
    # ✅ ทดลองวิธีที่ 2: partner_id + path + timestamp + body
    body_str = json.dumps(json_data, separators=(',', ':'), sort_keys=True)
    sign_base = f"{PARTNER_ID}{path}{timestamp}{body_str}"
    sign = hmac.new(bytes.fromhex(PARTNER_KEY), sign_base.encode(), hashlib.sha256).hexdigest()

    headers = {"Content-Type": "application/json"}
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }

    # Debug information
    debug_info = {
        "url": url,
        "method": "POST",
        "headers": headers,
        "params": params,
        "json_data": json_data,
        "sign_base": sign_base,
        "sign": sign,
        "timestamp": timestamp,
        "body_str": body_str
    }
    st.session_state.last_token_request_alt = debug_info
    
    return requests.post(url, headers=headers, params=params, json=json_data)

# ===== Function ดึงข้อมูลร้านค้า =====
def get_shop_info(access_token, shop_id):
    url = "https://partner.test-stable.shopeemobile.com/api/v2/shop/get_shop_info"
    timestamp = int(time.time())
    path = "/api/v2/shop/get_shop_info"
    
    # สร้าง signature: partner_id + path + timestamp + access_token + shop_id
    sign_base = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(bytes.fromhex(PARTNER_KEY), sign_base.encode(), hashlib.sha256).hexdigest()

    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": sign
    }

    return requests.get(url, params=params)

# ===== Function ตรวจสอบ Partner Key =====
def validate_partner_key(key):
    # ตรวจสอบว่าเป็น hex string หรือไม่
    try:
        # ลองแปลงเป็น bytes
        bytes.fromhex(key)
        return True
    except ValueError:
        return False

# ===== Function สร้าง direct URL ที่มี code และ shop_id =====
def create_direct_url(code, shop_id):
    base_url = REDIRECT_URL
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    return f"{base_url}?code={code}&shop_id={shop_id}"

# ====== หน้าเว็บ ======
st.set_page_config(page_title="Shopee OAuth & Shop Data", page_icon="🛒")
st.title("🛒 Shopee OAuth & Shop Management")

# แสดงข้อมูลการตั้งค่า
st.sidebar.header("⚙️ การตั้งค่า")
st.sidebar.write(f"**Partner ID:** {PARTNER_ID}")
st.sidebar.write(f"**Shop ID:** 142837")
st.sidebar.write(f"**Redirect URL:** {REDIRECT_URL}")

# ตรวจสอบ Partner Key
if not validate_partner_key(PARTNER_KEY):
    st.error("⚠️ **Partner Key ไม่ถูกต้อง!**")
    st.write("Partner Key ต้องเป็น hex string (0-9, a-f)")
    st.stop()

# ✅ ปรับปรุงการจัดการ query parameters
query_params = st.query_params

# ✅ ตรวจสอบ manual input
manual_input = st.sidebar.checkbox("ใส่ code และ shop_id เอง")

if manual_input:
    with st.sidebar:
        manual_code = st.text_input("Authorization Code")
        manual_shop_id = st.text_input("Shop ID", "142837")
        
        if st.button("ใช้ค่าที่ใส่เอง"):
            # สร้าง URL ที่มี code และ shop_id
            direct_url = create_direct_url(manual_code, manual_shop_id)
            st.success(f"สร้าง URL สำเร็จ: {direct_url}")
            st.markdown(f"[คลิกเพื่อใช้ค่าที่ใส่เอง]({direct_url})")

# ลบ parameters ที่ไม่ต้องการ (empty values)
filtered_params = {}
for key, value in query_params.items():
    if value and value.strip():  # เฉพาะ values ที่ไม่ว่าง
        filtered_params[key] = value

# ตรวจสอบ parameters ที่สำคัญ
code = filtered_params.get("code")
shop_id = filtered_params.get("shop_id")

# ✅ ตรวจสอบว่ามี code และ shop_id หรือไม่
if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    # แสดงปุ่มดึง Access Token
    method = st.radio(
        "เลือกวิธีการสร้าง Signature:",
        ["วิธีที่ 1: partner_id + path + timestamp", 
         "วิธีที่ 2: partner_id + path + timestamp + body"],
        index=0
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 ดึง Access Token", use_container_width=True, type="primary"):
            with st.spinner("🔄 กำลังดึง Access Token..."):
                try:
                    if method == "วิธีที่ 1: partner_id + path + timestamp":
                        res = get_access_token(code, shop_id)
                        debug_key = "last_token_request"
                    else:
                        res = get_access_token_alt(code, shop_id)
                        debug_key = "last_token_request_alt"
                    
                    st.write("📋 **Response Status:**", res.status_code)
                    
                    # แสดง request details
                    with st.expander("📋 Request Details"):
                        st.json(st.session_state.get(debug_key, {}))
                    
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
                            
                            # Auto-refresh หน้าเพื่อแสดงส่วนข้อมูลร้านค้า
                            st.rerun()
                            
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
                                st.info("""
                                💡 **คำแนะนำสำหรับ Wrong sign:**
                                1. ตรวจสอบว่า Partner Key ถูกต้อง
                                2. ลองใช้วิธีการสร้าง signature แบบอื่น
                                3. ตรวจสอบว่า timestamp ที่ใช้เป็นเวลาปัจจุบัน
                                """)
                        except:
                            st.text(res.text)
                            
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
    
    with col2:
        if st.button("🔄 ล้างข้อมูลและเริ่มใหม่", use_container_width=True):
            # ล้าง session state และ query params
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Redirect ไปยังหน้าเดิมโดยไม่มี query params
            st.rerun()

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
    
    with col2:
        if st.button("🔄 ล้าง Token", use_container_width=True):
            # ล้าง token จาก session state
            if hasattr(st.session_state, 'access_token'):
                del st.session_state.access_token
            if hasattr(st.session_state, 'shop_id'):
                del st.session_state.shop_id
            if hasattr(st.session_state, 'refresh_token'):
                del st.session_state.refresh_token
            st.rerun()

else:
    # ✅ เพิ่มวิธีการแก้ปัญหา query_token, cookie_token
    st.warning("""
    ⚠️ **ปัญหาที่พบ:** Shopee มักส่ง `query_token=, cookie_token=` กลับมาแทนที่จะส่ง code และ shop_id
    
    **วิธีแก้ไข:**
    1. ลองใช้ "ใส่ code และ shop_id เอง" ในเมนูด้านซ้าย
    2. หรือลองวิธีการ workaround ด้านล่าง
    """)
    
    # แสดงวิธีการ workaround
    with st.expander("🔧 วิธีการ Workaround"):
        st.write("""
        1. คลิกปุ่ม "คลิกเพื่อ Login Shopee" ด้านล่าง
        2. เมื่อถึงหน้า Authorization ของ Shopee ให้เลือก "30 Days" และคลิก "Confirm Authorization"
        3. หากเกิด error `query_token=, cookie_token=` ให้ดูที่ URL ในเบราว์เซอร์
        4. URL จะมีลักษณะคล้าย: `https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/?query_token=&cookie_token=`
        5. แก้ไข URL เป็น: `https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/?code=YOUR_CODE&shop_id=142837`
        6. แทนที่ YOUR_CODE ด้วย code ที่ได้จาก Shopee (ดูได้จาก Network tab ใน Developer Tools)
        7. กด Enter เพื่อไปยัง URL ที่แก้ไขแล้ว
        """)
    
    # แสดงข้อมูล Test Account
    with st.expander("🧪 ข้อมูล Test Account"):
        st.write("**Shop ID:** 142837")
        st.write("**Shop Account:** SANDBOX.f216878ec16b03a6f962")
        st.write("**Shop Password:** 1bdd53e0ec3b7fb2")
        st.write("**Shop Login URL:** https://seller.test-stable.shopee.co.th")
    
    # แสดงขั้นตอนการใช้งาน
    with st.expander("📋 ขั้นตอนการใช้งาน"):
        st.write("""
        1. ✅ คลิกปุ่ม "คลิกเพื่อ Login Shopee" ด้านล่าง
        2. ✅ ใช้ข้อมูล Test Account ด้านบนเพื่อ Login
        3. ✅ เลือก "30 Days" ใน Authorization Period
        4. ✅ คลิก "Confirm Authorization" ในหน้า Shopee
        5. 🔄 หากเกิด error ให้ใช้วิธีการ Workaround ด้านบน
        6. 🎯 คลิก "ดึง Access Token" เพื่อขอ token
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
    st.write("**All Query Parameters (Raw):**")
    st.json(dict(query_params))
    
    st.write("**Filtered Parameters:**")
    st.json(filtered_params)
    
    st.write("**Configuration:**")
    st.write(f"- Partner ID: {PARTNER_ID}")
    st.write(f"- Partner Key: {PARTNER_KEY[:5]}...{PARTNER_KEY[-5:]}")
    st.write(f"- Redirect URL: {REDIRECT_URL}")
    
    if hasattr(st.session_state, 'last_login_url'):
        st.write("**Last Login URL:**")
        st.write(st.session_state.last_login_url)
        st.write(f"- Sign Base: {st.session_state.last_sign_base}")
        st.write(f"- Sign: {st.session_state.last_sign}")
        st.write(f"- Timestamp: {st.session_state.last_timestamp}")
    
    if hasattr(st.session_state, 'access_token'):
        st.write("**Session State:**")
        st.write(f"- Access Token: {st.session_state.access_token[:20]}...")
        st.write(f"- Shop ID: {st.session_state.shop_id}")

# ✅ เพิ่มวิธีการแก้ปัญหาแบบละเอียด
st.info("""
## 🔍 วิธีการแก้ปัญหา query_token, cookie_token

### วิธีที่ 1: ใช้ Developer Tools ในเบราว์เซอร์
1. กด F12 หรือคลิกขวา > Inspect เพื่อเปิด Developer Tools
2. ไปที่แท็บ Network
3. คลิกปุ่ม "คลิกเพื่อ Login Shopee" และทำตามขั้นตอนจนถึงหน้า Confirm Authorization
4. คลิก "Confirm Authorization"
5. ในแท็บ Network จะมี request ที่มี code และ shop_id
6. คัดลอก code และใส่ในช่อง "Authorization Code" ในเมนูด้านซ้าย

### วิธีที่ 2: ใช้ Postman หรือ API Client อื่นๆ
1. สร้าง request ไปยัง Shopee API โดยตรง
2. ใช้ Partner ID และ Partner Key ที่ถูกต้อง
3. สร้าง signature ตามที่ Shopee กำหนด
4. ทดสอบ API เพื่อดูว่าทำงานได้หรือไม่

### วิธีที่ 3: ตรวจสอบ Redirect URL
1. ตรวจสอบว่า Redirect URL ใน Shopee Console ตรงกับที่ใช้ในโค้ด
2. ตรวจสอบว่ามี / ท้ายสุดหรือไม่ (ต้องตรงกัน)
3. ลองใช้ URL ที่ไม่มี query parameters
""")
