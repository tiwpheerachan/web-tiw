import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse
import json
import base64
from datetime import datetime

# ===== ตั้งค่าแอป Shopee =====
PARTNER_ID = 1280109
PARTNER_KEY = "5a4e6e4c4d4375464c57506b7a42775a77466d686c534255574267514f494a54"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"

# ===== Multiple Signature Methods =====
def create_signature_method1(partner_id, path, timestamp, access_token="", shop_id="", body=""):
    """วิธีที่ 1: Standard method"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        sign_base = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        sign_base = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        sign_base = f"{partner_id}{path}{timestamp}"
    
    partner_key_bytes = bytes.fromhex(PARTNER_KEY)
    signature = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, sign_base

def create_signature_method2(partner_id, path, timestamp, access_token="", shop_id="", body=""):
    """วิธีที่ 2: Without body sorting"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'))  # ไม่ sort_keys
        sign_base = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        sign_base = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        sign_base = f"{partner_id}{path}{timestamp}"
    
    partner_key_bytes = bytes.fromhex(PARTNER_KEY)
    signature = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, sign_base

def create_signature_method3(partner_id, path, timestamp, access_token="", shop_id="", body=""):
    """วิธีที่ 3: Base64 encoded key"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        sign_base = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        sign_base = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        sign_base = f"{partner_id}{path}{timestamp}"
    
    # ลองใช้ key เป็น base64
    try:
        partner_key_bytes = base64.b64decode(PARTNER_KEY)
    except:
        partner_key_bytes = PARTNER_KEY.encode('utf-8')
    
    signature = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, sign_base

def create_signature_method4(partner_id, path, timestamp, access_token="", shop_id="", body=""):
    """วิธีที่ 4: UTF-8 encoded key"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        sign_base = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        sign_base = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        sign_base = f"{partner_id}{path}{timestamp}"
    
    partner_key_bytes = PARTNER_KEY.encode('utf-8')
    signature = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, sign_base

# ===== Test All Signature Methods =====
def test_all_signature_methods(code, shop_id):
    """ทดสอบทุกวิธีการสร้าง signature"""
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    url = f"https://partner.test-stable.shopeemobile.com{path}"
    
    body = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": PARTNER_ID
    }
    
    methods = [
        ("Method 1: Hex + Sorted JSON", create_signature_method1),
        ("Method 2: Hex + Unsorted JSON", create_signature_method2),
        ("Method 3: Base64 Key", create_signature_method3),
        ("Method 4: UTF-8 Key", create_signature_method4)
    ]
    
    results = []
    
    for method_name, method_func in methods:
        try:
            signature, sign_base = method_func(PARTNER_ID, path, timestamp, body=body)
            
            params = {
                "partner_id": PARTNER_ID,
                "timestamp": timestamp,
                "sign": signature
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, params=params, json=body, headers=headers, timeout=10)
            
            result = {
                "method": method_name,
                "signature": signature,
                "sign_base": sign_base,
                "status_code": response.status_code,
                "response": response.text[:500],  # First 500 chars
                "success": response.status_code == 200
            }
            
            results.append(result)
            
        except Exception as e:
            results.append({
                "method": method_name,
                "error": str(e),
                "success": False
            })
    
    return results

# ===== Alternative API Testing =====
def test_shop_info_direct():
    """ทดสอบ API โดยตรงด้วย hardcoded token (ถ้ามี)"""
    # นี่เป็นการทดสอบเพื่อดูว่า API ทำงานหรือไม่
    pass

def validate_partner_credentials():
    """ตรวจสอบความถูกต้องของ Partner credentials"""
    issues = []
    
    # ตรวจสอบ Partner ID
    if not str(PARTNER_ID).isdigit():
        issues.append("Partner ID ต้องเป็นตัวเลข")
    
    # ตรวจสอบ Partner Key
    if len(PARTNER_KEY) != 64:
        issues.append(f"Partner Key ควรมีความยาว 64 ตัวอักษร (ปัจจุบัน: {len(PARTNER_KEY)})")
    
    # ตรวจสอบว่าเป็น hex หรือไม่
    try:
        bytes.fromhex(PARTNER_KEY)
    except ValueError:
        issues.append("Partner Key ไม่ใช่ hex string ที่ถูกต้อง")
    
    # ตรวจสอบ Redirect URL
    if not REDIRECT_URL.startswith(('http://', 'https://')):
        issues.append("Redirect URL ต้องขึ้นต้นด้วย http:// หรือ https://")
    
    return issues

# ===== IP Address Checker =====
def get_current_ip_comprehensive():
    """ตรวจสอบ IP Address จากหลายแหล่ง"""
    ip_services = [
        ("ipify.org", "https://api.ipify.org?format=json", "ip"),
        ("httpbin.org", "https://httpbin.org/ip", "origin"),
        ("ipinfo.io", "https://ipinfo.io/json", "ip"),
        ("myip.com", "https://api.myip.com", "ip"),
        ("whatismyipaddress.com", "https://ipv4.icanhazip.com", "text")
    ]
    
    detected_ips = {}
    
    for service_name, url, key in ip_services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                if key == "text":
                    ip = response.text.strip()
                else:
                    data = response.json()
                    ip = data.get(key, "").split(',')[0].strip()  # Handle multiple IPs
                
                if ip:
                    detected_ips[service_name] = ip
        except:
            detected_ips[service_name] = "Failed"
    
    return detected_ips

# ===== Streamlit App =====
st.set_page_config(page_title="Shopee Debug Center", page_icon="🔧", layout="wide")
st.title("🔧 Shopee API Debug Center")

# Sidebar
st.sidebar.header("🛠️ Debug Tools")

# Credential Validation
st.sidebar.subheader("📋 Credential Check")
if st.sidebar.button("🔍 ตรวจสอบ Credentials"):
    issues = validate_partner_credentials()
    if issues:
        for issue in issues:
            st.sidebar.error(f"❌ {issue}")
    else:
        st.sidebar.success("✅ Credentials ดูถูกต้อง")

# IP Address Check
st.sidebar.subheader("🌐 IP Address Check")
if st.sidebar.button("🔍 ตรวจสอบ IP ทั้งหมด"):
    with st.spinner("กำลังตรวจสอบ IP..."):
        ips = get_current_ip_comprehensive()
        st.sidebar.write("**IP Addresses ที่ตรวจพบ:**")
        for service, ip in ips.items():
            if ip != "Failed":
                st.sidebar.code(f"{service}: {ip}")
            else:
                st.sidebar.error(f"{service}: Failed")

# Main content
query_params = st.query_params
code = query_params.get("code")
shop_id = query_params.get("shop_id", "142837")

# Manual input
with st.sidebar:
    st.subheader("🔧 Manual Input")
    manual_code = st.text_input("Authorization Code", value=code or "")
    manual_shop_id = st.text_input("Shop ID", value=shop_id)
    
    if st.button("ใช้ค่าที่ใส่เอง"):
        if manual_code and manual_shop_id:
            st.query_params.code = manual_code
            st.query_params.shop_id = manual_shop_id
            st.rerun()

# Debug Section
if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    # Test all signature methods
    st.subheader("🧪 ทดสอบทุกวิธีการสร้าง Signature")
    
    if st.button("🔬 ทดสอบทุกวิธี", type="primary", use_container_width=True):
        with st.spinner("กำลังทดสอบทุกวิธีการสร้าง signature..."):
            results = test_all_signature_methods(code, shop_id)
            
            for i, result in enumerate(results, 1):
                with st.expander(f"🔬 {result['method']}", expanded=result.get('success', False)):
                    if result.get('success'):
                        st.success(f"✅ สำเร็จ! Status Code: {result['status_code']}")
                        st.json(result['response'])
                        
                        # ถ้าสำเร็จ ให้เก็บข้อมูล
                        try:
                            response_data = json.loads(result['response'])
                            if "access_token" in response_data:
                                st.session_state.access_token = response_data["access_token"]
                                st.session_state.refresh_token = response_data.get("refresh_token", "")
                                st.session_state.shop_id = shop_id
                                st.balloons()
                                st.success("🎉 บันทึก Access Token แล้ว!")
                        except:
                            pass
                    else:
                        st.error(f"❌ ล้มเหลว! Status Code: {result.get('status_code', 'N/A')}")
                        if 'error' in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.text(result.get('response', 'No response'))
                    
                    # แสดง debug info
                    st.write("**Debug Information:**")
                    st.code(f"Signature: {result.get('signature', 'N/A')}")
                    st.code(f"Sign Base: {result.get('sign_base', 'N/A')}")

    # Alternative debugging approaches
    st.divider()
    st.subheader("🔧 วิธีการแก้ปัญหาเพิ่มเติม")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🌐 ตรวจสอบ Network", use_container_width=True):
            st.info("""
            **ขั้นตอนตรวจสอบ Network:**
            1. เปิด Developer Tools (F12)
            2. ไปที่แท็บ Network
            3. ลองทำ request อีกครั้ง
            4. ดู request/response headers
            5. ตรวจสอบ payload ที่ส่งไป
            """)
    
    with col2:
        if st.button("🔑 ตรวจสอบ Partner Key", use_container_width=True):
            st.info(f"""
            **Partner Key Analysis:**
            - Length: {len(PARTNER_KEY)} characters
            - First 10: {PARTNER_KEY[:10]}
            - Last 10: {PARTNER_KEY[-10:]}
            - Is Hex: {all(c in '0123456789abcdefABCDEF' for c in PARTNER_KEY)}
            
            **ลองตรวจสอบใน Shopee Console:**
            1. ไปที่ App Management
            2. เลือกแอป test tiw
            3. ดู Test API Partner Key
            4. Copy key ใหม่มาใส่
            """)
    
    with col3:
        if st.button("⏰ ตรวจสอบ Timestamp", use_container_width=True):
            current_time = int(time.time())
            st.info(f"""
            **Timestamp Analysis:**
            - Current: {current_time}
            - DateTime: {datetime.fromtimestamp(current_time)}
            - Timezone: UTC
            
            **หมายเหตุ:** Shopee อาจมีข้อกำหนดเรื่องเวลา
            """)

else:
    # OAuth Login Section
    st.info("👆 เริ่มต้นด้วยการ Login เข้า Shopee OAuth")
    
    # Generate login URL
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    
    signature, sign_base = create_signature_method1(PARTNER_ID, path, timestamp)
    
    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe='')
    login_url = (
        f"https://partner.test-stable.shopeemobile.com{path}?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={signature}"
        f"&redirect={redirect_encoded}"
    )
    
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
        ">
            🚀 เริ่ม Shopee OAuth
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Debug login URL
    with st.expander("🔧 Debug Login URL"):
        st.code(f"Login URL: {login_url}")
        st.code(f"Signature: {signature}")
        st.code(f"Sign Base: {sign_base}")

# Success section
if "access_token" in st.session_state:
    st.divider()
    st.success("🎉 ได้รับ Access Token สำเร็จ!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 ทดสอบดึงข้อมูลร้านค้า", use_container_width=True):
            # ทดสอบดึงข้อมูลร้านค้า
            timestamp = int(time.time())
            path = "/api/v2/shop/get_shop_info"
            
            signature, sign_base = create_signature_method1(
                PARTNER_ID, path, timestamp, 
                st.session_state.access_token, 
                st.session_state.shop_id
            )
            
            params = {
                "partner_id": PARTNER_ID,
                "timestamp": timestamp,
                "access_token": st.session_state.access_token,
                "shop_id": st.session_state.shop_id,
                "sign": signature
            }
            
            try:
                response = requests.get(
                    f"https://partner.test-stable.shopeemobile.com{path}",
                    params=params
                )
                
                if response.status_code == 200:
                    st.success("✅ ดึงข้อมูลร้านค้าสำเร็จ!")
                    st.json(response.json())
                else:
                    st.error(f"❌ HTTP Error {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with col2:
        if st.button("🗑️ ลบ Token", use_container_width=True):
            for key in ['access_token', 'refresh_token', 'shop_id']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Comprehensive troubleshooting guide
st.divider()
with st.expander("📚 คู่มือแก้ปัญหาแบบละเอียด"):
    st.markdown("""
    ## 🔧 วิธีแก้ปัญหา "Wrong Sign" แบบละเอียด
    
    ### 1. ตรวจสอบ IP Address Whitelist
    - ✅ เพิ่ม IP Address จริงใน Shopee Console
    - ✅ ลบ IP ปลอมทั้งหมด
    - ✅ ลองใช้ 0.0.0.0/0 สำหรับทดสอบ
    
    ### 2. ตรวจสอบ Partner Key
    - ✅ Copy Partner Key ใหม่จาก Shopee Console
    - ✅ ตรวจสอบว่าไม่มีช่องว่างหรือตัวอักษรพิเศษ
    - ✅ ใช้ Test API Partner Key (ไม่ใช่ Live)
    
    ### 3. ตรวจสอบ Signature Algorithm
    - ✅ ลองทุกวิธีการสร้าง signature ด้านบน
    - ✅ ตรวจสอบการ encode ของ Partner Key
    - ✅ ตรวจสอบการ sort JSON body
    
    ### 4. ตรวจสอบ Request Format
    - ✅ ตรวจสอบ Content-Type header
    - ✅ ตรวจสอบ URL encoding
    - ✅ ตรวจสอบ timestamp format
    
    ### 5. ตรวจสอบ Environment
    - ✅ ใช้ Test environment (partner.test-stable.shopeemobile.com)
    - ✅ ตรวจสอบ network connectivity
    - ✅ ลองใช้ Postman หรือ curl
    
    ### 6. ติดต่อ Shopee Support
    - หากทุกวิธีไม่ได้ผล ให้ติดต่อ Shopee Developer Support
    - แนบ request_id จาก error response
    - แนบ debug information
    """)

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666;">
🔧 <strong>Shopee API Debug Center</strong> - ระบบแก้ปัญหา Shopee API<br>
ทดสอบทุกวิธีการสร้าง signature และแก้ปัญหา "wrong sign" error
</div>
""", unsafe_allow_html=True)
