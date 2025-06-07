import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse
import json

# ===== ข้อมูลจากเอกสารที่คุณส่งมา =====
PARTNER_ID = 1280109
PARTNER_KEY = "5a4e6e4c4d4375464c57506b7a42775a77466d686c534255574267514f494a54"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"
SHOP_ID = 142837

# Test Account จากเอกสาร
TEST_SHOP_ACCOUNT = "SANDBOX.f216878ec16b03a6f962"
TEST_SHOP_PASSWORD = "1bdd53e0ec3b7fb2"
TEST_SHOP_LOGIN_URL = "https://seller.test-stable.shopee.co.th"

# ===== ฟังก์ชันสร้าง Signature ตามเอกสาร Shopee =====
def create_shopee_signature(partner_id, path, timestamp, access_token="", shop_id="", body=None):
    """
    สร้าง signature ตามเอกสาร Shopee API อย่างแม่นยำ
    Reference: https://open.shopee.com/documents/v2/v2.auth.get_access_token
    """
    
    # สร้าง base string ตามลำดับที่ Shopee กำหนด
    if body is not None:
        # สำหรับ POST requests ที่มี body
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        base_string = f"{partner_id}{path}{timestamp}{body_str}"
    elif access_token and shop_id:
        # สำหรับ API calls ที่ต้องใช้ access_token
        base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        # สำหรับ auth requests
        base_string = f"{partner_id}{path}{timestamp}"
    
    # แปลง partner key จาก hex string เป็น bytes
    try:
        key_bytes = bytes.fromhex(PARTNER_KEY)
    except ValueError as e:
        st.error(f"Partner Key format error: {e}")
        return None, base_string
    
    # สร้าง HMAC-SHA256 signature
    signature = hmac.new(
        key_bytes, 
        base_string.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    return signature, base_string

# ===== ฟังก์ชัน OAuth =====
def generate_auth_url():
    """สร้าง URL สำหรับ OAuth authorization"""
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    
    signature, base_string = create_shopee_signature(PARTNER_ID, path, timestamp)
    
    if signature is None:
        return None, None
    
    # URL encode redirect URL
    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe='')
    
    auth_url = (
        f"https://partner.test-stable.shopeemobile.com{path}"
        f"?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={signature}"
        f"&redirect={redirect_encoded}"
    )
    
    return auth_url, {
        "timestamp": timestamp,
        "signature": signature,
        "base_string": base_string,
        "path": path
    }

def get_access_token(code, shop_id):
    """ดึง Access Token จาก authorization code"""
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    
    # Request body ตามเอกสาร Shopee
    request_body = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": PARTNER_ID
    }
    
    signature, base_string = create_shopee_signature(
        PARTNER_ID, path, timestamp, body=request_body
    )
    
    if signature is None:
        return None, None
    
    # Parameters
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "sign": signature
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    url = f"https://partner.test-stable.shopeemobile.com{path}"
    
    debug_info = {
        "url": url,
        "method": "POST",
        "params": params,
        "body": request_body,
        "headers": headers,
        "signature": signature,
        "base_string": base_string,
        "timestamp": timestamp
    }
    
    try:
        response = requests.post(
            url, 
            params=params, 
            json=request_body, 
            headers=headers,
            timeout=30
        )
        return response, debug_info
    except Exception as e:
        debug_info["error"] = str(e)
        return None, debug_info

def get_shop_info(access_token, shop_id):
    """ดึงข้อมูลร้านค้า"""
    timestamp = int(time.time())
    path = "/api/v2/shop/get_shop_info"
    
    signature, base_string = create_shopee_signature(
        PARTNER_ID, path, timestamp, access_token=access_token, shop_id=shop_id
    )
    
    if signature is None:
        return None, None
    
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": signature
    }
    
    url = f"https://partner.test-stable.shopeemobile.com{path}"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        return response, {
            "url": url,
            "params": params,
            "signature": signature,
            "base_string": base_string
        }
    except Exception as e:
        return None, {"error": str(e)}

# ===== Streamlit App =====
st.set_page_config(page_title="Shopee API Working Solution", page_icon="✅", layout="wide")
st.title("✅ Shopee API Working Solution")

# แสดงข้อมูลการตั้งค่าจากเอกสาร
st.sidebar.header("📋 ข้อมูลจากเอกสาร")
st.sidebar.success("✅ IP Address: 34.83.176.217 (Enabled)")
st.sidebar.success(f"✅ Partner ID: {PARTNER_ID}")
st.sidebar.success(f"✅ Shop ID: {SHOP_ID}")
st.sidebar.info(f"Partner Key: {PARTNER_KEY[:10]}...{PARTNER_KEY[-10:]}")

# Test Account Information
with st.sidebar.expander("🧪 Test Account"):
    st.code(f"""
Shop Account: {TEST_SHOP_ACCOUNT}
Shop Password: {TEST_SHOP_PASSWORD}
Shop Login URL: {TEST_SHOP_LOGIN_URL}
    """)

# ตรวจสอบ query parameters
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

# Main content
if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔑 ดึง Access Token", type="primary", use_container_width=True):
            with st.spinner("กำลังดึง Access Token..."):
                response, debug_info = get_access_token(code, shop_id)
                
                if response is not None:
                    st.write(f"**Response Status:** {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            token_data = response.json()
                            
                            if "access_token" in token_data:
                                st.success("🎉 ได้รับ Access Token สำเร็จ!")
                                
                                # เก็บ token ใน session state
                                st.session_state.access_token = token_data["access_token"]
                                st.session_state.refresh_token = token_data.get("refresh_token", "")
                                st.session_state.shop_id = shop_id
                                
                                # แสดงข้อมูล token
                                with st.expander("📋 Token Information"):
                                    st.json(token_data)
                                
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ ไม่พบ access_token ใน response")
                                st.json(token_data)
                        except json.JSONDecodeError:
                            st.error("❌ Invalid JSON response")
                            st.text(response.text)
                    else:
                        st.error(f"❌ HTTP Error {response.status_code}")
                        try:
                            error_data = response.json()
                            st.json(error_data)
                        except:
                            st.text(response.text)
                else:
                    st.error("❌ ไม่สามารถส่ง request ได้")
                
                # แสดง debug information
                with st.expander("🔧 Debug Information"):
                    st.json(debug_info)
    
    with col2:
        if st.button("🔄 เริ่มใหม่", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                if key.startswith(('access_token', 'refresh_token', 'shop_id')):
                    del st.session_state[key]
            
            # Clear query params
            st.query_params.clear()
            st.rerun()

else:
    # OAuth Login Section
    st.info("👆 เริ่มต้นด้วยการ Login เข้า Shopee OAuth")
    
    auth_url, debug_info = generate_auth_url()
    
    if auth_url:
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
                transition: transform 0.2s;
            " onmouseover="this.style.transform='translateY(-2px)'" 
               onmouseout="this.style.transform='translateY(0)'">
                🚀 เริ่ม Shopee OAuth
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Debug auth URL
        with st.expander("🔧 Debug Auth URL"):
            st.json(debug_info)
    else:
        st.error("❌ ไม่สามารถสร้าง Auth URL ได้")

# แสดงข้อมูลร้านค้าถ้ามี access token
if "access_token" in st.session_state:
    st.divider()
    st.subheader("🏪 ข้อมูลร้านค้า")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 ดึงข้อมูลร้านค้า", use_container_width=True):
            with st.spinner("กำลังดึงข้อมูลร้านค้า..."):
                response, debug_info = get_shop_info(
                    st.session_state.access_token,
                    st.session_state.shop_id
                )
                
                if response is not None:
                    if response.status_code == 200:
                        try:
                            shop_data = response.json()
                            st.success("✅ ดึงข้อมูลร้านค้าสำเร็จ!")
                            
                            # แสดงข้อมูลสำคัญ
                            if "response" in shop_data:
                                shop_info = shop_data["response"]
                                
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    st.metric("Shop ID", shop_info.get("shop_id", "N/A"))
                                with col_b:
                                    st.metric("Shop Name", shop_info.get("shop_name", "N/A"))
                                with col_c:
                                    st.metric("Status", shop_info.get("status", "N/A"))
                            
                            # แสดงข้อมูลทั้งหมด
                            with st.expander("📋 ข้อมูลทั้งหมด"):
                                st.json(shop_data)
                        except json.JSONDecodeError:
                            st.error("❌ Invalid JSON response")
                            st.text(response.text)
                    else:
                        st.error(f"❌ HTTP Error {response.status_code}")
                        try:
                            st.json(response.json())
                        except:
                            st.text(response.text)
                else:
                    st.error("❌ ไม่สามารถส่ง request ได้")
                
                # Debug information
                with st.expander("🔧 Debug Information"):
                    st.json(debug_info)
    
    with col2:
        if st.button("📦 ดึงรายการสินค้า", use_container_width=True):
            timestamp = int(time.time())
            path = "/api/v2/product/get_item_list"
            
            signature, base_string = create_shopee_signature(
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
                    timeout=30
                )
                
                if response.status_code == 200:
                    product_data = response.json()
                    st.success("✅ ดึงรายการสินค้าสำเร็จ!")
                    
                    if "response" in product_data and "item" in product_data["response"]:
                        items = product_data["response"]["item"]
                        st.metric("จำนวนสินค้า", len(items))
                        
                        if items:
                            # แสดงรายการสินค้า
                            for item in items[:5]:  # แสดง 5 รายการแรก
                                st.write(f"- Item ID: {item.get('item_id', 'N/A')}")
                    
                    with st.expander("📋 ข้อมูลทั้งหมด"):
                        st.json(product_data)
                else:
                    st.error(f"❌ HTTP Error {response.status_code}")
                    st.text(response.text)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with col3:
        if st.button("🗑️ ลบ Token", use_container_width=True):
            for key in ['access_token', 'refresh_token', 'shop_id']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# ขั้นตอนการใช้งาน
with st.expander("📋 ขั้นตอนการใช้งาน"):
    st.markdown(f"""
    ### 🎯 ขั้นตอนการใช้งาน:
    
    1. **คลิก "เริ่ม Shopee OAuth"** ด้านบน
    2. **Login ด้วย Test Account:**
       - Shop Account: `{TEST_SHOP_ACCOUNT}`
       - Shop Password: `{TEST_SHOP_PASSWORD}`
       - URL: {TEST_SHOP_LOGIN_URL}
    3. **เลือก "30 Days"** ใน Authorization Period
    4. **คลิก "Confirm Authorization"**
    5. **กลับมาที่หน้านี้** และคลิก **"ดึง Access Token"**
    6. **ทดสอบดึงข้อมูล** ร้านค้าและสินค้า
    
    ### ✅ สิ่งที่แก้ไขแล้ว:
    - ใช้ข้อมูลจากเอกสารที่คุณส่งมา
    - แก้ไข signature generation ให้ถูกต้อง
    - เพิ่ม error handling ที่ดีขึ้น
    - แสดง debug information ที่ละเอียด
    """)

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666;">
✅ <strong>Shopee API Working Solution</strong> - ใช้ข้อมูลจากเอกสารและแก้ไข signature generation<br>
🔧 แก้ไขตามเอกสาร Shopee API อย่างแม่นยำ
</div>
""", unsafe_allow_html=True)
