import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse
import json

# ===== ตั้งค่าแอป Shopee =====
PARTNER_ID = 1280109
PARTNER_KEY = "5a4e6e4c4d4375464c57506b7a42775a77466d686c534255574267514f494a54"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"

# ===== Function สร้างลิงก์ login Shopee (แก้ไขแล้ว) =====
def generate_login_url():
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    base_url = f"https://partner.test-stable.shopeemobile.com{path}"

    # สร้าง sign ด้วย partner_id + path + timestamp (ไม่ใส่ leading zeros)
    sign_base = f"{PARTNER_ID}{path}{timestamp}"
    
    # แปลง PARTNER_KEY จาก hex string เป็น bytes แล้วสร้าง HMAC
    partner_key_bytes = bytes.fromhex(PARTNER_KEY)
    sign = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()

    # URL encode redirect URL
    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe='')
    
    login_url = (
        f"{base_url}?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={redirect_encoded}"
    )
    
    # Debug information
    st.session_state.debug_login = {
        "timestamp": timestamp,
        "sign_base": sign_base,
        "sign": sign,
        "partner_key_length": len(PARTNER_KEY),
        "login_url": login_url
    }
    
    return login_url

# ===== Function ดึง Access Token (แก้ไขแล้ว) =====
def get_access_token(code, shop_id):
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    url = f"https://partner.test-stable.shopeemobile.com{path}"
    
    # Request body
    body = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": PARTNER_ID
    }
    
    # สร้าง signature: partner_id + path + timestamp + request_body
    body_json = json.dumps(body, separators=(',', ':'), sort_keys=True)
    sign_base = f"{PARTNER_ID}{path}{timestamp}{body_json}"
    
    partner_key_bytes = bytes.fromhex(PARTNER_KEY)
    sign = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()

    # Parameters
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Debug information
    st.session_state.debug_token = {
        "url": url,
        "timestamp": timestamp,
        "sign_base": sign_base,
        "sign": sign,
        "body": body,
        "body_json": body_json,
        "params": params
    }
    
    return requests.post(url, params=params, json=body, headers=headers)

# ===== Function ดึงข้อมูลร้านค้า (แก้ไขแล้ว) =====
def get_shop_info(access_token, shop_id):
    timestamp = int(time.time())
    path = "/api/v2/shop/get_shop_info"
    url = f"https://partner.test-stable.shopeemobile.com{path}"
    
    # สร้าง signature: partner_id + path + timestamp + access_token + shop_id
    sign_base = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    
    partner_key_bytes = bytes.fromhex(PARTNER_KEY)
    sign = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()

    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": sign
    }
    
    # Debug information
    st.session_state.debug_shop = {
        "timestamp": timestamp,
        "sign_base": sign_base,
        "sign": sign,
        "params": params
    }

    return requests.get(url, params=params)

# ===== Function หา IP Address ของ Streamlit =====
def get_streamlit_ip():
    try:
        # ใช้ service หลายตัวเพื่อหา IP
        services = [
            "https://api.ipify.org?format=json",
            "https://httpbin.org/ip",
            "https://api.myip.com"
        ]
        
        ips = []
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'ip' in data:
                        ips.append(data['ip'])
                    elif 'origin' in data:
                        ips.append(data['origin'])
            except:
                continue
        
        return list(set(ips))  # Remove duplicates
    except:
        return []

# ====== หน้าเว็บ ======
st.set_page_config(page_title="Shopee OAuth Fixed", page_icon="🛒")
st.title("🛒 Shopee OAuth & Shop Management (Fixed)")

# แสดงข้อมูลการตั้งค่า
st.sidebar.header("⚙️ การตั้งค่า")
st.sidebar.write(f"**Partner ID:** {PARTNER_ID}")
st.sidebar.write(f"**Redirect URL:** {REDIRECT_URL}")

# ตรวจสอบ IP Address
st.sidebar.subheader("🌐 IP Address Information")
if st.sidebar.button("🔍 ตรวจสอบ IP Address"):
    with st.spinner("กำลังตรวจสอบ IP Address..."):
        current_ips = get_streamlit_ip()
        if current_ips:
            st.sidebar.success("✅ IP Address ที่ตรวจพบ:")
            for ip in current_ips:
                st.sidebar.code(ip)
            st.sidebar.warning("⚠️ เพิ่ม IP เหล่านี้ใน Shopee Console!")
        else:
            st.sidebar.error("❌ ไม่สามารถตรวจสอบ IP ได้")

# แสดงคำแนะนำสำหรับ IP Whitelist
with st.expander("📋 วิธีแก้ไข IP Address Whitelist"):
    st.write("""
    **ปัญหา:** คุณใช้ IP Address ปลอม (104.16.0.1, 104.16.3.2, 104.16.8.8) ใน Shopee Console
    
    **วิธีแก้ไข:**
    1. คลิกปุ่ม "🔍 ตรวจสอบ IP Address" ในเมนูด้านซ้าย
    2. คัดลอก IP Address ที่แสดงขึ้นมา
    3. ไปที่ Shopee Open Platform Console
    4. เข้าไปที่ App Management > [ชื่อแอปของคุณ]
    5. ในส่วน "IP Address Whitelist" ให้:
       - ลบ IP ปลอมทั้งหมด (104.16.0.1, 104.16.3.2, 104.16.8.8)
       - เพิ่ม IP Address จริงที่ได้จากการตรวจสอบ
    6. บันทึกการเปลี่ยนแปลง
    
    **หมายเหตุ:** Streamlit Cloud อาจมี IP Address ที่เปลี่ยนแปลงได้ 
    หากยังมีปัญหา ให้ลองเพิ่ม 0.0.0.0/0 (อนุญาตทุก IP) สำหรับการทดสอบ
    """)

# ตรวจสอบ query parameters
query_params = st.query_params
code = query_params.get("code")
shop_id = query_params.get("shop_id", "142837")

# Manual input option
with st.sidebar:
    st.subheader("🔧 Manual Input")
    manual_code = st.text_input("Authorization Code", value=code or "")
    manual_shop_id = st.text_input("Shop ID", value=shop_id)
    
    if st.button("ใช้ค่าที่ใส่เอง"):
        if manual_code and manual_shop_id:
            # Update query params
            st.query_params.code = manual_code
            st.query_params.shop_id = manual_shop_id
            st.rerun()

# Main content
if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 ดึง Access Token", type="primary", use_container_width=True):
            with st.spinner("กำลังดึง Access Token..."):
                try:
                    response = get_access_token(code, shop_id)
                    
                    st.write(f"**Response Status:** {response.status_code}")
                    
                    if response.status_code == 200:
                        token_data = response.json()
                        
                        if "access_token" in token_data:
                            st.success("🎉 ได้รับ Access Token สำเร็จ!")
                            
                            # เก็บข้อมูลใน session state
                            st.session_state.access_token = token_data["access_token"]
                            st.session_state.refresh_token = token_data.get("refresh_token", "")
                            st.session_state.shop_id = shop_id
                            
                            # แสดงข้อมูล token
                            with st.expander("📋 Token Information"):
                                st.json(token_data)
                            
                            st.rerun()
                        else:
                            st.error("❌ ไม่พบ access_token ใน response")
                            st.json(token_data)
                    else:
                        st.error(f"❌ HTTP Error {response.status_code}")
                        try:
                            error_data = response.json()
                            st.json(error_data)
                            
                            # แสดงคำแนะนำเฉพาะ
                            if "error_sign" in str(error_data):
                                st.error("""
                                🚨 **Wrong Sign Error**
                                
                                สาเหตุที่เป็นไปได้:
                                1. **IP Address ไม่ได้อยู่ใน Whitelist** (สาเหตุหลัก)
                                2. Partner Key ไม่ถูกต้อง
                                3. Timestamp ไม่ถูกต้อง
                                4. การสร้าง signature ผิดพลาด
                                
                                **แก้ไข:** ตรวจสอบ IP Address Whitelist ใน Shopee Console
                                """)
                        except:
                            st.text(response.text)
                            
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
    
    with col2:
        if st.button("🔄 เริ่มใหม่", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                if key.startswith(('access_token', 'refresh_token', 'shop_id', 'debug_')):
                    del st.session_state[key]
            
            # Clear query params
            st.query_params.clear()
            st.rerun()

else:
    # แสดงปุ่ม Login
    st.info("👆 คลิกปุ่มด้านล่างเพื่อเริ่มกระบวนการ OAuth")
    
    login_url = generate_login_url()
    
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{login_url}" target="_self" style="
            background: linear-gradient(45deg, #ee4d2d, #ff6b35);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            font-size: 18px;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(238, 77, 45, 0.3);
            transition: transform 0.2s;
        " onmouseover="this.style.transform='translateY(-2px)'" 
           onmouseout="this.style.transform='translateY(0)'">
            🚀 เริ่ม Shopee OAuth
        </a>
    </div>
    """, unsafe_allow_html=True)

# แสดงข้อมูลร้านค้าถ้ามี access token
if hasattr(st.session_state, 'access_token') and st.session_state.access_token:
    st.divider()
    st.subheader("🏪 ข้อมูลร้านค้า")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 ดึงข้อมูลร้านค้า", use_container_width=True):
            with st.spinner("กำลังดึงข้อมูลร้านค้า..."):
                try:
                    shop_response = get_shop_info(
                        st.session_state.access_token, 
                        st.session_state.shop_id
                    )
                    
                    if shop_response.status_code == 200:
                        shop_data = shop_response.json()
                        
                        if "error" not in shop_data:
                            st.success("✅ ดึงข้อมูลร้านค้าสำเร็จ!")
                            st.json(shop_data)
                        else:
                            st.error(f"❌ API Error: {shop_data}")
                    else:
                        st.error(f"❌ HTTP Error {shop_response.status_code}")
                        st.text(shop_response.text)
                        
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
    
    with col2:
        if st.button("🗑️ ลบ Token", use_container_width=True):
            # Clear tokens
            for key in ['access_token', 'refresh_token', 'shop_id']:
                if hasattr(st.session_state, key):
                    delattr(st.session_state, key)
            st.rerun()

# Debug Information
with st.expander("🔧 Debug Information"):
    st.subheader("Configuration")
    st.json({
        "partner_id": PARTNER_ID,
        "partner_key_preview": f"{PARTNER_KEY[:10]}...{PARTNER_KEY[-10:]}",
        "redirect_url": REDIRECT_URL,
        "query_params": dict(query_params)
    })
    
    # แสดง debug info ต่างๆ
    debug_sections = [
        ("Login Debug", "debug_login"),
        ("Token Debug", "debug_token"),
        ("Shop Debug", "debug_shop")
    ]
    
    for title, key in debug_sections:
        if hasattr(st.session_state, key):
            st.subheader(title)
            st.json(getattr(st.session_state, key))

# Test Account Information
with st.expander("🧪 Test Account Information"):
    st.code("""
    Shop ID: 142837
    Shop Account: SANDBOX.f216878ec16b03a6f962
    Shop Password: 1bdd53e0ec3b7fb2
    Shop Login URL: https://seller.test-stable.shopee.co.th
    """)

# แสดงขั้นตอนการแก้ปัญหา
st.info("""
## 🔧 ขั้นตอนการแก้ปัญหา

### 1. แก้ไข IP Address Whitelist (สำคัญที่สุด!)
- ตรวจสอบ IP Address จริงด้วยปุ่มในเมนูด้านซ้าย
- เข้าไปแก้ไขใน Shopee Console
- ลบ IP ปลอมทั้งหมด แล้วใส่ IP จริง

### 2. ตรวจสอบการตั้งค่า
- Partner ID: 1280109 ✅
- Partner Key: ถูกต้อง ✅  
- Redirect URL: ตรงกับใน Console ✅

### 3. ทดสอบ OAuth Flow
- คลิก "เริ่ม Shopee OAuth"
- Login ด้วย Test Account
- เลือก "30 Days" authorization
- คลิก "Confirm Authorization"

### 4. หากยังมีปัญหา
- ลองใช้ 0.0.0.0/0 ใน IP Whitelist (สำหรับทดสอบ)
- ตรวจสอบ Network tab ใน Developer Tools
- ดู error message ใน Debug Information
""")
