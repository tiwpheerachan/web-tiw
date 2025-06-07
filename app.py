import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse
import json
import base64
from datetime import datetime
import re

# ===== ข้อมูลจากเอกสาร =====
PARTNER_ID = 1280109
PARTNER_KEY = "5a4e6e4c4d4375464c57506b7a42775a77466d686c534255574267514f494a54"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"
SHOP_ID = 142837

# ===== Smart Signature Generation Methods =====
class ShopeeSignatureGenerator:
    def __init__(self, partner_key):
        self.partner_key = partner_key
        
    def method_1_standard(self, partner_id, path, timestamp, body=None, access_token="", shop_id=""):
        """Standard method from documentation"""
        if body:
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            base_string = f"{partner_id}{path}{timestamp}{body_str}"
        elif access_token and shop_id:
            base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
        else:
            base_string = f"{partner_id}{path}{timestamp}"
        
        key_bytes = bytes.fromhex(self.partner_key)
        signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature, base_string
    
    def method_2_no_sort(self, partner_id, path, timestamp, body=None, access_token="", shop_id=""):
        """Method without JSON sorting"""
        if body:
            body_str = json.dumps(body, separators=(',', ':'))  # No sort_keys
            base_string = f"{partner_id}{path}{timestamp}{body_str}"
        elif access_token and shop_id:
            base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
        else:
            base_string = f"{partner_id}{path}{timestamp}"
        
        key_bytes = bytes.fromhex(self.partner_key)
        signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature, base_string
    
    def method_3_utf8_key(self, partner_id, path, timestamp, body=None, access_token="", shop_id=""):
        """Method with UTF-8 encoded key"""
        if body:
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            base_string = f"{partner_id}{path}{timestamp}{body_str}"
        elif access_token and shop_id:
            base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
        else:
            base_string = f"{partner_id}{path}{timestamp}"
        
        key_bytes = self.partner_key.encode('utf-8')
        signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature, base_string
    
    def method_4_base64_key(self, partner_id, path, timestamp, body=None, access_token="", shop_id=""):
        """Method with base64 decoded key"""
        if body:
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            base_string = f"{partner_id}{path}{timestamp}{body_str}"
        elif access_token and shop_id:
            base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
        else:
            base_string = f"{partner_id}{path}{timestamp}"
        
        try:
            key_bytes = base64.b64decode(self.partner_key)
        except:
            key_bytes = self.partner_key.encode('utf-8')
        
        signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature, base_string
    
    def method_5_different_order(self, partner_id, path, timestamp, body=None, access_token="", shop_id=""):
        """Method with different parameter order"""
        if body:
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            base_string = f"{path}{partner_id}{timestamp}{body_str}"  # Different order
        elif access_token and shop_id:
            base_string = f"{path}{partner_id}{timestamp}{access_token}{shop_id}"
        else:
            base_string = f"{path}{partner_id}{timestamp}"
        
        key_bytes = bytes.fromhex(self.partner_key)
        signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature, base_string
    
    def method_6_uppercase_hex(self, partner_id, path, timestamp, body=None, access_token="", shop_id=""):
        """Method with uppercase hex signature"""
        if body:
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            base_string = f"{partner_id}{path}{timestamp}{body_str}"
        elif access_token and shop_id:
            base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
        else:
            base_string = f"{partner_id}{path}{timestamp}"
        
        key_bytes = bytes.fromhex(self.partner_key)
        signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest().upper()
        return signature, base_string
    
    def method_7_compact_json(self, partner_id, path, timestamp, body=None, access_token="", shop_id=""):
        """Method with most compact JSON"""
        if body:
            body_str = json.dumps(body, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
            base_string = f"{partner_id}{path}{timestamp}{body_str}"
        elif access_token and shop_id:
            base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
        else:
            base_string = f"{partner_id}{path}{timestamp}"
        
        key_bytes = bytes.fromhex(self.partner_key)
        signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature, base_string
    
    def method_8_sha1(self, partner_id, path, timestamp, body=None, access_token="", shop_id=""):
        """Method with SHA1 instead of SHA256"""
        if body:
            body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
            base_string = f"{partner_id}{path}{timestamp}{body_str}"
        elif access_token and shop_id:
            base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
        else:
            base_string = f"{partner_id}{path}{timestamp}"
        
        key_bytes = bytes.fromhex(self.partner_key)
        signature = hmac.new(key_bytes, base_string.encode('utf-8'), hashlib.sha1).hexdigest()
        return signature, base_string
    
    def get_all_methods(self):
        """Get all signature methods"""
        return [
            ("Method 1: Standard Hex + SHA256", self.method_1_standard),
            ("Method 2: No JSON Sort", self.method_2_no_sort),
            ("Method 3: UTF-8 Key", self.method_3_utf8_key),
            ("Method 4: Base64 Key", self.method_4_base64_key),
            ("Method 5: Different Order", self.method_5_different_order),
            ("Method 6: Uppercase Hex", self.method_6_uppercase_hex),
            ("Method 7: Compact JSON", self.method_7_compact_json),
            ("Method 8: SHA1 Hash", self.method_8_sha1),
        ]

# ===== Smart Testing Function =====
def smart_test_all_methods(code, shop_id):
    """ทดสอบทุกวิธีการอย่างชาญฉลาด"""
    generator = ShopeeSignatureGenerator(PARTNER_KEY)
    methods = generator.get_all_methods()
    
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    url = f"https://partner.test-stable.shopeemobile.com{path}"
    
    body = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": PARTNER_ID
    }
    
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
            
            # ทดสอบทั้ง POST และ GET
            for http_method in ["POST", "GET"]:
                try:
                    if http_method == "POST":
                        response = requests.post(url, params=params, json=body, headers=headers, timeout=15)
                    else:
                        # ลอง GET ด้วย body ใน query string
                        get_params = params.copy()
                        get_params.update(body)
                        response = requests.get(url, params=get_params, timeout=15)
                    
                    result = {
                        "method": f"{method_name} ({http_method})",
                        "signature": signature,
                        "base_string": base_string,
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_text": response.text[:1000],
                        "timestamp": timestamp,
                        "http_method": http_method
                    }
                    
                    if response.status_code == 200:
                        try:
                            result["response_json"] = response.json()
                        except:
                            pass
                    
                    results.append(result)
                    
                    # หากสำเร็จ ให้หยุดทดสอบวิธีอื่น
                    if response.status_code == 200:
                        return results
                        
                except Exception as e:
                    results.append({
                        "method": f"{method_name} ({http_method})",
                        "error": str(e),
                        "success": False
                    })
                    
        except Exception as e:
            results.append({
                "method": method_name,
                "error": str(e),
                "success": False
            })
    
    return results

# ===== Alternative API Testing =====
def test_alternative_approaches(code, shop_id):
    """ทดสอบวิธีการอื่นๆ"""
    alternatives = []
    
    # 1. ทดสอบ endpoint อื่น
    endpoints = [
        "https://partner.test-stable.shopeemobile.com/api/v2/auth/token/get",
        "https://partner.shopeemobile.com/api/v2/auth/token/get",  # Production
        "https://open-api.shopee.com/api/v2/auth/token/get",  # Alternative
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            alternatives.append({
                "type": "Endpoint Test",
                "endpoint": endpoint,
                "status": response.status_code,
                "accessible": True
            })
        except Exception as e:
            alternatives.append({
                "type": "Endpoint Test",
                "endpoint": endpoint,
                "error": str(e),
                "accessible": False
            })
    
    # 2. ทดสอบ Partner Key variations
    key_variations = [
        PARTNER_KEY,
        PARTNER_KEY.upper(),
        PARTNER_KEY.lower(),
        PARTNER_KEY.replace('a', 'A').replace('b', 'B').replace('c', 'C').replace('d', 'D').replace('e', 'E').replace('f', 'F')
    ]
    
    for i, key_var in enumerate(key_variations):
        try:
            generator = ShopeeSignatureGenerator(key_var)
            signature, base_string = generator.method_1_standard(PARTNER_ID, "/api/v2/auth/token/get", int(time.time()), body={
                "code": code,
                "shop_id": int(shop_id),
                "partner_id": PARTNER_ID
            })
            
            alternatives.append({
                "type": "Key Variation",
                "variation": f"Variation {i+1}",
                "key_preview": f"{key_var[:10]}...{key_var[-10:]}",
                "signature": signature[:20] + "...",
                "success": True
            })
        except Exception as e:
            alternatives.append({
                "type": "Key Variation",
                "variation": f"Variation {i+1}",
                "error": str(e),
                "success": False
            })
    
    return alternatives

# ===== Streamlit App =====
st.set_page_config(page_title="Shopee Smart Debug", page_icon="🧠", layout="wide")
st.title("🧠 Shopee Smart Debug System")

# Header with current status
st.error("""
🚨 **ปัญหาที่พบ:** ยังคงได้ "wrong sign" error แม้จะแก้ไขหลายครั้งแล้ว

**วิธีการแก้ไข:** ใช้ Smart Testing ทดสอบทุกความเป็นไปได้อย่างเป็นระบบ
""")

# Sidebar
st.sidebar.header("🧠 Smart Debug Tools")
st.sidebar.info(f"""
**ข้อมูลปัจจุบัน:**
- Partner ID: {PARTNER_ID}
- Shop ID: {SHOP_ID}
- Partner Key: {PARTNER_KEY[:10]}...{PARTNER_KEY[-10:]}
""")

# Main content
query_params = st.query_params
code = query_params.get("code")
shop_id = query_params.get("shop_id", str(SHOP_ID))

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

if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    # Smart Testing Section
    st.subheader("🧠 Smart Testing - ทดสอบทุกความเป็นไปได้")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🚀 เริ่ม Smart Testing", type="primary", use_container_width=True):
            with st.spinner("กำลังทดสอบทุกวิธีการอย่างชาญฉลาด..."):
                # Test all signature methods
                results = smart_test_all_methods(code, shop_id)
                
                success_found = False
                
                for result in results:
                    if result.get('success'):
                        success_found = True
                        st.success(f"🎉 {result['method']} - สำเร็จ!")
                        
                        # Save successful result
                        if 'response_json' in result and 'access_token' in result['response_json']:
                            st.session_state.access_token = result['response_json']['access_token']
                            st.session_state.refresh_token = result['response_json'].get('refresh_token', '')
                            st.session_state.shop_id = shop_id
                            st.session_state.successful_method = result['method']
                            st.balloons()
                        
                        with st.expander(f"📋 {result['method']} - Success Details", expanded=True):
                            if 'response_json' in result:
                                st.json(result['response_json'])
                            else:
                                st.text(result['response_text'])
                            st.code(f"Signature: {result['signature']}")
                            st.code(f"Base String: {result['base_string']}")
                        
                        break  # หยุดแสดงผลเมื่อเจอวิธีที่สำเร็จ
                
                if not success_found:
                    st.error("❌ ทุกวิธีการล้มเหลว")
                    
                    # แสดงผลลัพธ์ที่ล้มเหลว
                    for result in results[:5]:  # แสดง 5 วิธีแรก
                        with st.expander(f"❌ {result['method']} - Failed"):
                            if 'error' in result:
                                st.error(f"Error: {result['error']}")
                            else:
                                st.write(f"Status Code: {result.get('status_code', 'N/A')}")
                                st.text(result.get('response_text', 'No response'))
                                if 'signature' in result:
                                    st.code(f"Signature: {result['signature']}")
                                    st.code(f"Base String: {result['base_string']}")
    
    with col2:
        if st.button("🔍 Alternative Tests", use_container_width=True):
            with st.spinner("กำลังทดสอบวิธีการอื่น..."):
                alternatives = test_alternative_approaches(code, shop_id)
                
                st.subheader("🔍 Alternative Test Results")
                
                for alt in alternatives:
                    if alt['type'] == 'Endpoint Test':
                        if alt.get('accessible'):
                            st.success(f"✅ {alt['endpoint']}: {alt['status']}")
                        else:
                            st.error(f"❌ {alt['endpoint']}: {alt.get('error', 'Failed')}")
                    
                    elif alt['type'] == 'Key Variation':
                        if alt.get('success'):
                            st.info(f"🔑 {alt['variation']}: {alt['key_preview']}")
                        else:
                            st.warning(f"⚠️ {alt['variation']}: {alt.get('error', 'Failed')}")

else:
    # OAuth Login Section
    st.info("👆 เริ่มต้นด้วยการ Login เข้า Shopee OAuth")
    
    # Generate auth URL
    generator = ShopeeSignatureGenerator(PARTNER_KEY)
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    
    signature, base_string = generator.method_1_standard(PARTNER_ID, path, timestamp)
    
    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe='')
    auth_url = (
        f"https://partner.test-stable.shopeemobile.com{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={signature}"
        f"&redirect={redirect_encoded}"
    )
    
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{auth_url}" target="_self" style="
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

# Success section
if "access_token" in st.session_state:
    st.divider()
    st.success(f"🎉 ได้รับ Access Token สำเร็จด้วย {st.session_state.get('successful_method', 'Unknown Method')}!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 ดึงข้อมูลร้านค้า", use_container_width=True):
            generator = ShopeeSignatureGenerator(PARTNER_KEY)
            timestamp = int(time.time())
            path = "/api/v2/shop/get_shop_info"
            
            signature, base_string = generator.method_1_standard(
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
                    shop_data = response.json()
                    st.success("✅ ดึงข้อมูลร้านค้าสำเร็จ!")
                    st.json(shop_data)
                else:
                    st.error(f"❌ HTTP Error {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with col2:
        if st.button("📦 ดึงรายการสินค้า", use_container_width=True):
            st.info("🚧 Feature coming soon...")
    
    with col3:
        if st.button("🗑️ ลบ Token", use_container_width=True):
            for key in ['access_token', 'refresh_token', 'shop_id', 'successful_method']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Advanced troubleshooting
st.divider()
with st.expander("🧠 Advanced Troubleshooting Guide"):
    st.markdown("""
    ## 🧠 Smart Debugging Strategy
    
    ### 1. Systematic Testing Approach
    - ✅ ทดสอบ 8 วิธีการสร้าง signature ที่แตกต่างกัน
    - ✅ ทดสอบทั้ง POST และ GET methods
    - ✅ ทดสอบ Partner Key variations
    - ✅ ทดสอบ alternative endpoints
    
    ### 2. Common Issues & Solutions
    - **Wrong Sign Error:** มักเกิดจาก signature algorithm ที่ไม่ถูกต้อง
    - **IP Whitelist:** ตรวจสอบว่าได้เพิ่ม IP แล้วและ enabled
    - **Partner Key:** ลอง copy key ใหม่จาก Console
    - **Timestamp:** ตรวจสอบว่าเวลาระบบถูกต้อง
    
    ### 3. Next Steps if Still Failing
    1. ติดต่อ Shopee Developer Support
    2. แนบ request_id จาก error response
    3. แนบ debug information ทั้งหมด
    4. ขอตัวอย่าง working code จาก Shopee
    """)

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666;">
🧠 <strong>Shopee Smart Debug System</strong> - ระบบแก้ปัญหาอย่างชาญฉลาด<br>
ทดสอบทุกความเป็นไปได้และหาวิธีที่ถูกต้องอย่างเป็นระบบ
</div>
""", unsafe_allow_html=True)
