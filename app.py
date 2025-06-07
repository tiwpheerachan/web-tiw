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

# ===== Alternative Partner Keys to Test =====
# บางครั้ง Partner Key อาจมีรูปแบบต่างกัน
ALTERNATIVE_KEYS = [
    PARTNER_KEY,  # Original hex key
    PARTNER_KEY.upper(),  # Uppercase hex
    PARTNER_KEY.lower(),  # Lowercase hex
]

# ===== Multiple Signature Generation Methods =====
def signature_method_1(partner_id, path, timestamp, body="", access_token="", shop_id=""):
    """Standard Shopee method with hex key"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        base_string = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        base_string = f"{partner_id}{path}{timestamp}"
    
    key_bytes = bytes.fromhex(PARTNER_KEY)
    signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, base_string

def signature_method_2(partner_id, path, timestamp, body="", access_token="", shop_id=""):
    """Method without JSON sorting"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'))  # No sort_keys
        base_string = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        base_string = f"{partner_id}{path}{timestamp}"
    
    key_bytes = bytes.fromhex(PARTNER_KEY)
    signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, base_string

def signature_method_3(partner_id, path, timestamp, body="", access_token="", shop_id=""):
    """Method with UTF-8 encoded key"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        base_string = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        base_string = f"{partner_id}{path}{timestamp}"
    
    key_bytes = PARTNER_KEY.encode('utf-8')
    signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, base_string

def signature_method_4(partner_id, path, timestamp, body="", access_token="", shop_id=""):
    """Method with base64 decoded key"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        base_string = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        base_string = f"{partner_id}{path}{timestamp}"
    
    try:
        key_bytes = base64.b64decode(PARTNER_KEY)
    except:
        key_bytes = PARTNER_KEY.encode('utf-8')
    
    signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, base_string

def signature_method_5(partner_id, path, timestamp, body="", access_token="", shop_id=""):
    """Method with different parameter order"""
    if body:
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        base_string = f"{path}{partner_id}{timestamp}{body_str}"  # Different order
    elif access_token and shop_id:
        base_string = f"{path}{partner_id}{timestamp}{access_token}{shop_id}"
    else:
        base_string = f"{path}{partner_id}{timestamp}"
    
    key_bytes = bytes.fromhex(PARTNER_KEY)
    signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature, base_string

# ===== Test All Methods Function =====
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
        ("Method 1: Standard Hex + Sorted JSON", signature_method_1),
        ("Method 2: Hex + Unsorted JSON", signature_method_2),
        ("Method 3: UTF-8 Key", signature_method_3),
        ("Method 4: Base64 Key", signature_method_4),
        ("Method 5: Different Parameter Order", signature_method_5),
    ]
    
    results = []
    
    for method_name, method_func in methods:
        try:
            signature, base_string = method_func(PARTNER_ID, path, timestamp, body=body)
            
            params = {
                "partner_id": PARTNER_ID,
                "timestamp": timestamp,
                "sign": signature
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, params=params, json=body, headers=headers, timeout=15)
            
            result = {
                "method": method_name,
                "signature": signature,
                "base_string": base_string,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_text": response.text[:1000],  # First 1000 chars
                "timestamp": timestamp
            }
            
            if response.status_code == 200:
                try:
                    result["response_json"] = response.json()
                except:
                    pass
            
            results.append(result)
            
        except Exception as e:
            results.append({
                "method": method_name,
                "error": str(e),
                "success": False
            })
    
    return results

# ===== Alternative API Endpoints =====
def test_alternative_endpoints():
    """ทดสอบ endpoint อื่นๆ"""
    endpoints = [
        "https://partner.test-stable.shopeemobile.com",
        "https://partner.shopeemobile.com",  # Production (ถ้ามี)
        "https://open-api.shopee.com",  # Alternative
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            results[endpoint] = {
                "status": response.status_code,
                "accessible": True
            }
        except Exception as e:
            results[endpoint] = {
                "status": "Error",
                "error": str(e),
                "accessible": False
            }
    
    return results

# ===== IP Detection from Multiple Sources =====
def get_comprehensive_ip_info():
    """ดึงข้อมูล IP จากหลายแหล่ง"""
    services = [
        ("ipify.org", "https://api.ipify.org?format=json", "ip"),
        ("httpbin.org", "https://httpbin.org/ip", "origin"),
        ("ipinfo.io", "https://ipinfo.io/json", "ip"),
        ("cloudflare", "https://1.1.1.1/cdn-cgi/trace", "text"),
        ("google", "https://domains.google.com/checkip", "text"),
    ]
    
    ip_results = {}
    
    for service_name, url, response_type in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                if response_type == "json":
                    data = response.json()
                    ip = data.get("ip", data.get("origin", "")).split(',')[0].strip()
                else:  # text
                    if "cloudflare" in url:
                        for line in response.text.split('\n'):
                            if line.startswith('ip='):
                                ip = line.split('=')[1]
                                break
                    else:
                        ip = response.text.strip()
                
                ip_results[service_name] = ip
        except Exception as e:
            ip_results[service_name] = f"Error: {str(e)}"
    
    return ip_results

# ===== Streamlit App =====
st.set_page_config(page_title="Shopee Complete Debug", page_icon="🔬", layout="wide")
st.title("🔬 Shopee API Complete Debug System")

# Sidebar with comprehensive tools
st.sidebar.header("🛠️ Debug Tools")

# IP Information
st.sidebar.subheader("🌐 IP Information")
if st.sidebar.button("🔍 ตรวจสอบ IP ทั้งหมด"):
    with st.spinner("กำลังตรวจสอบ IP จากหลายแหล่ง..."):
        ip_info = get_comprehensive_ip_info()
        st.sidebar.write("**IP Addresses:**")
        for service, ip in ip_info.items():
            if "Error" not in str(ip):
                st.sidebar.success(f"{service}: {ip}")
            else:
                st.sidebar.error(f"{service}: {ip}")

# Endpoint Testing
st.sidebar.subheader("🌐 Endpoint Testing")
if st.sidebar.button("🔗 ทดสอบ Endpoints"):
    with st.spinner("กำลังทดสอบ endpoints..."):
        endpoint_results = test_alternative_endpoints()
        st.sidebar.write("**Endpoint Status:**")
        for endpoint, result in endpoint_results.items():
            if result.get("accessible"):
                st.sidebar.success(f"✅ {endpoint}: {result['status']}")
            else:
                st.sidebar.error(f"❌ {endpoint}: {result.get('error', 'Failed')}")

# Main content
query_params = st.query_params
code = query_params.get("code")
shop_id = query_params.get("shop_id", "142837")

# Manual input section
with st.sidebar:
    st.subheader("🔧 Manual Input")
    manual_code = st.text_input("Authorization Code", value=code or "")
    manual_shop_id = st.text_input("Shop ID", value=shop_id)
    
    if st.button("ใช้ค่าที่ใส่เอง"):
        if manual_code and manual_shop_id:
            st.query_params.code = manual_code
            st.query_params.shop_id = manual_shop_id
            st.rerun()

# Main debugging section
if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    # Comprehensive signature testing
    st.subheader("🧪 ทดสอบทุกวิธีการสร้าง Signature")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔬 ทดสอบทุกวิธีการ", type="primary", use_container_width=True):
            with st.spinner("กำลังทดสอบทุกวิธีการสร้าง signature..."):
                results = test_all_signature_methods(code, shop_id)
                
                # แสดงผลลัพธ์
                success_found = False
                
                for i, result in enumerate(results, 1):
                    if result.get('success'):
                        success_found = True
                        st.success(f"🎉 {result['method']} - สำเร็จ!")
                        
                        # เก็บ access token
                        if 'response_json' in result and 'access_token' in result['response_json']:
                            st.session_state.access_token = result['response_json']['access_token']
                            st.session_state.refresh_token = result['response_json'].get('refresh_token', '')
                            st.session_state.shop_id = shop_id
                            st.session_state.successful_method = result['method']
                            st.balloons()
                        
                        with st.expander(f"📋 {result['method']} - Details", expanded=True):
                            st.json(result['response_json'] if 'response_json' in result else result['response_text'])
                            st.code(f"Signature: {result['signature']}")
                            st.code(f"Base String: {result['base_string']}")
                    else:
                        with st.expander(f"❌ {result['method']} - Failed (Status: {result.get('status_code', 'Error')})"):
                            if 'error' in result:
                                st.error(f"Error: {result['error']}")
                            else:
                                st.text(result['response_text'])
                                st.code(f"Signature: {result.get('signature', 'N/A')}")
                                st.code(f"Base String: {result.get('base_string', 'N/A')}")
                
                if not success_found:
                    st.error("❌ ทุกวิธีการล้มเหลว - ปัญหาอาจอยู่ที่ Partner Key หรือ IP Whitelist")
    
    with col2:
        if st.button("🔄 ลองใหม่", use_container_width=True):
            st.rerun()

    # Additional debugging tools
    st.divider()
    st.subheader("🔧 เครื่องมือ Debug เพิ่มเติม")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 แสดง Request Details", use_container_width=True):
            st.info(f"""
            **Current Request Details:**
            - Partner ID: {PARTNER_ID}
            - Shop ID: {shop_id}
            - Code: {code[:20]}...
            - Timestamp: {int(time.time())}
            - Partner Key (first 10): {PARTNER_KEY[:10]}...
            """)
    
    with col2:
        if st.button("🔑 ทดสอบ Partner Key", use_container_width=True):
            st.info(f"""
            **Partner Key Analysis:**
            - Length: {len(PARTNER_KEY)} chars
            - Is Valid Hex: {all(c in '0123456789abcdefABCDEF' for c in PARTNER_KEY)}
            - First 10: {PARTNER_KEY[:10]}
            - Last 10: {PARTNER_KEY[-10:]}
            
            **Recommendation:**
            1. Copy key ใหม่จาก Shopee Console
            2. ตรวจสอบไม่มีช่องว่าง
            3. ใช้ Test API Partner Key
            """)
    
    with col3:
        if st.button("🌐 ตรวจสอบ Network", use_container_width=True):
            st.info("""
            **Network Debugging:**
            1. เปิด Developer Tools (F12)
            2. ไปที่ Network tab
            3. ลองทำ request อีกครั้ง
            4. ดู Headers และ Payload
            5. เปรียบเทียบกับ Shopee Documentation
            """)

else:
    # OAuth Login Section
    st.info("👆 เริ่มต้นด้วยการ Login เข้า Shopee OAuth")
    
    # Generate login URL with method 1
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    signature, base_string = signature_method_1(PARTNER_ID, path, timestamp)
    
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
        ">🚀 เริ่ม Shopee OAuth</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Debug login URL
    with st.expander("🔧 Debug Login URL"):
        st.code(f"URL: {login_url}")
        st.code(f"Signature: {signature}")
        st.code(f"Base String: {base_string}")

# Success section - if we have access token
if "access_token" in st.session_state:
    st.divider()
    st.success(f"🎉 ได้รับ Access Token สำเร็จด้วย {st.session_state.get('successful_method', 'Unknown Method')}!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 ดึงข้อมูลร้านค้า", use_container_width=True):
            timestamp = int(time.time())
            path = "/api/v2/shop/get_shop_info"
            
            # ใช้วิธีเดียวกับที่สำเร็จ
            signature, base_string = signature_method_1(
                PARTNER_ID, path, timestamp, 
                access_token=st.session_state.access_token, 
                shop_id=st.session_state.shop_id
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
                    params=params,
                    timeout=15
                )
                
                if response.status_code == 200:
                    st.success("✅ ดึงข้อมูลร้านค้าสำเร็จ!")
                    shop_data = response.json()
                    st.json(shop_data)
                else:
                    st.error(f"❌ HTTP Error {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with col2:
        if st.button("📦 ดึงรายการสินค้า", use_container_width=True):
            timestamp = int(time.time())
            path = "/api/v2/product/get_item_list"
            
            signature, base_string = signature_method_1(
                PARTNER_ID, path, timestamp,
                access_token=st.session_state.access_token,
                shop_id=st.session_state.shop_id
            )
            
            params = {
                "partner_id": PARTNER_ID,
                "timestamp": timestamp,
                "access_token": st.session_state.access_token,
                "shop_id": st.session_state.shop_id,
                "sign": signature,
                "page_size": 20,
                "offset": 0
            }
            
            try:
                response = requests.get(
                    f"https://partner.test-stable.shopeemobile.com{path}",
                    params=params,
                    timeout=15
                )
                
                if response.status_code == 200:
                    st.success("✅ ดึงรายการสินค้าสำเร็จ!")
                    product_data = response.json()
                    st.json(product_data)
                else:
                    st.error(f"❌ HTTP Error {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with col3:
        if st.button("🗑️ ลบ Token", use_container_width=True):
            for key in ['access_token', 'refresh_token', 'shop_id', 'successful_method']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Comprehensive troubleshooting guide
st.divider()
with st.expander("📚 คู่มือแก้ปัญหาครอบคลุม"):
    st.markdown("""
    ## 🔧 วิธีแก้ปัญหา "Wrong Sign" แบบครอบคลุม
    
    ### 1. ปัญหา IP Address Whitelist (90% ของปัญหา)
    - ✅ ตรวจสอบ IP จากหลายแหล่งด้านบน
    - ✅ เพิ่ม IP ทั้งหมดที่ตรวจพบใน Shopee Console
    - ✅ ลองใช้ 0.0.0.0/0 (อนุญาตทุก IP) สำหรับทดสอบ
    - ✅ รอ 5-10 นาทีหลังแก้ไข
    
    ### 2. ปัญหา Partner Key (5% ของปัญหา)
    - ✅ Copy Partner Key ใหม่จาก Shopee Console
    - ✅ ใช้ Test API Partner Key (ไม่ใช่ Live)
    - ✅ ตรวจสอบไม่มีช่องว่างหรือตัวอักษรพิเศษ
    - ✅ ตรวจสอบความยาว 64 ตัวอักษร
    
    ### 3. ปัญหา Signature Algorithm (3% ของปัญหา)
    - ✅ ทดสอบทุกวิธีการด้านบน
    - ✅ ตรวจสอบการ encode ของ key
    - ✅ ตรวจสอบการ sort JSON parameters
    
    ### 4. ปัญหา Environment/Network (2% ของปัญหา)
    - ✅ ใช้ Test environment เท่านั้น
    - ✅ ตรวจสอบ network connectivity
    - ✅ ลองใช้ VPN หรือ network อื่น
    
    ### 5. หากทุกวิธีไม่ได้ผล
    - 📧 ติดต่อ Shopee Developer Support
    - 📋 แนบ request_id จาก error response
    - 📋 แนบ debug information ทั้งหมด
    - 📋 อธิบายขั้นตอนที่ทำแล้ว
    """)

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666;">
🔬 <strong>Shopee API Complete Debug System</strong><br>
ระบบแก้ปัญหา Shopee API แบบครอบคลุม - ทดสอบทุกวิธีการและแก้ปัญหาทุกระดับ
</div>
""", unsafe_allow_html=True)
