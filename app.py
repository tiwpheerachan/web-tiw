import streamlit as st
import requests
import time
import hashlib
import hmac
import urllib.parse
import json
import pandas as pd
from datetime import datetime, timedelta

# ===== ตั้งค่าแอป Shopee =====
PARTNER_ID = 1280109
PARTNER_KEY = "5a4e6e4c4d4375464c57506b7a42775a77466d686c534255574267514f494a54"
REDIRECT_URL = "https://web-tiw-f6am2usgmpzwel2adoj5qg.streamlit.app/"
BASE_URL = "https://partner.test-stable.shopeemobile.com"

# ===== Helper Functions =====
def create_signature(partner_id, path, timestamp, access_token="", shop_id="", body=""):
    """สร้าง HMAC signature สำหรับ Shopee API"""
    if body:
        # สำหรับ POST requests ที่มี body
        sign_base = f"{partner_id}{path}{timestamp}{body}"
    elif access_token and shop_id:
        # สำหรับ API calls ที่ต้องใช้ access_token
        sign_base = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    else:
        # สำหรับ auth requests
        sign_base = f"{partner_id}{path}{timestamp}"
    
    partner_key_bytes = bytes.fromhex(PARTNER_KEY)
    signature = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()
    
    return signature, sign_base

def make_shopee_request(endpoint, method="GET", body=None, access_token="", shop_id=""):
    """ทำ request ไปยัง Shopee API"""
    timestamp = int(time.time())
    path = endpoint
    url = f"{BASE_URL}{path}"
    
    # สร้าง signature
    body_json = ""
    if body:
        body_json = json.dumps(body, separators=(',', ':'), sort_keys=True)
    
    signature, sign_base = create_signature(
        PARTNER_ID, path, timestamp, access_token, shop_id, body_json
    )
    
    # สร้าง parameters
    params = {
        "partner_id": PARTNER_ID,
        "timestamp": timestamp,
        "sign": signature
    }
    
    if access_token:
        params["access_token"] = access_token
    if shop_id:
        params["shop_id"] = shop_id
    
    # Headers
    headers = {"Content-Type": "application/json"} if body else {}
    
    # Debug info
    debug_info = {
        "url": url,
        "method": method,
        "timestamp": timestamp,
        "sign_base": sign_base,
        "signature": signature,
        "params": params,
        "body": body
    }
    
    # ทำ request
    try:
        if method == "POST":
            response = requests.post(url, params=params, json=body, headers=headers)
        else:
            response = requests.get(url, params=params)
        
        return response, debug_info
    except Exception as e:
        return None, {"error": str(e), "debug": debug_info}

# ===== OAuth Functions =====
def generate_login_url():
    """สร้าง URL สำหรับ OAuth login"""
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    
    signature, sign_base = create_signature(PARTNER_ID, path, timestamp)
    
    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe='')
    login_url = (
        f"{BASE_URL}{path}?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={signature}"
        f"&redirect={redirect_encoded}"
    )
    
    return login_url

def get_access_token(code, shop_id):
    """ดึง Access Token จาก authorization code"""
    body = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": PARTNER_ID
    }
    
    response, debug_info = make_shopee_request(
        "/api/v2/auth/token/get", 
        method="POST", 
        body=body
    )
    
    return response, debug_info

# ===== Data Retrieval Functions =====
def get_shop_info(access_token, shop_id):
    """ดึงข้อมูลร้านค้า"""
    response, debug_info = make_shopee_request(
        "/api/v2/shop/get_shop_info",
        access_token=access_token,
        shop_id=shop_id
    )
    return response, debug_info

def get_shop_profile(access_token, shop_id):
    """ดึงข้อมูลโปรไฟล์ร้านค้า"""
    response, debug_info = make_shopee_request(
        "/api/v2/shop/get_profile",
        access_token=access_token,
        shop_id=shop_id
    )
    return response, debug_info

def get_product_list(access_token, shop_id, page_size=20, offset=0):
    """ดึงรายการสินค้า"""
    endpoint = f"/api/v2/product/get_item_list?page_size={page_size}&offset={offset}"
    response, debug_info = make_shopee_request(
        endpoint,
        access_token=access_token,
        shop_id=shop_id
    )
    return response, debug_info

def get_order_list(access_token, shop_id, time_from=None, time_to=None, page_size=20):
    """ดึงรายการออเดอร์"""
    if not time_from:
        time_from = int((datetime.now() - timedelta(days=7)).timestamp())
    if not time_to:
        time_to = int(datetime.now().timestamp())
    
    endpoint = f"/api/v2/order/get_order_list?time_range_field=create_time&time_from={time_from}&time_to={time_to}&page_size={page_size}"
    response, debug_info = make_shopee_request(
        endpoint,
        access_token=access_token,
        shop_id=shop_id
    )
    return response, debug_info

# ===== Streamlit App =====
st.set_page_config(page_title="Shopee Data Retrieval", page_icon="🛒", layout="wide")
st.title("🛒 Shopee Data Retrieval System")

# Sidebar
st.sidebar.header("⚙️ การตั้งค่า")
st.sidebar.write(f"**Partner ID:** {PARTNER_ID}")
st.sidebar.write(f"**Shop ID:** 142837")

# Check for authorization code
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

# Main content
if code and shop_id:
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    # Get Access Token
    if "access_token" not in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔑 ดึง Access Token", type="primary", use_container_width=True):
                with st.spinner("กำลังดึง Access Token..."):
                    response, debug_info = get_access_token(code, shop_id)
                    
                    if response and response.status_code == 200:
                        token_data = response.json()
                        
                        if "access_token" in token_data:
                            st.session_state.access_token = token_data["access_token"]
                            st.session_state.refresh_token = token_data.get("refresh_token", "")
                            st.session_state.shop_id = shop_id
                            
                            st.success("🎉 ได้รับ Access Token สำเร็จ!")
                            st.rerun()
                        else:
                            st.error("❌ ไม่พบ access_token ใน response")
                            st.json(token_data)
                    else:
                        st.error(f"❌ HTTP Error {response.status_code if response else 'No response'}")
                        if response:
                            try:
                                st.json(response.json())
                            except:
                                st.text(response.text)
        
        with col2:
            if st.button("🔄 เริ่มใหม่", use_container_width=True):
                st.query_params.clear()
                st.rerun()
    
    # Data Retrieval Section
    if "access_token" in st.session_state:
        st.divider()
        st.header("📊 ดึงข้อมูลจาก Shopee")
        
        # Create tabs for different data types
        tab1, tab2, tab3, tab4 = st.tabs(["🏪 ข้อมูลร้านค้า", "📦 สินค้า", "🛒 ออเดอร์", "👤 โปรไฟล์"])
        
        with tab1:
            st.subheader("ข้อมูลร้านค้า")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 ดึงข้อมูลร้านค้า", use_container_width=True):
                    with st.spinner("กำลังดึงข้อมูลร้านค้า..."):
                        response, debug_info = get_shop_info(
                            st.session_state.access_token,
                            st.session_state.shop_id
                        )
                        
                        if response and response.status_code == 200:
                            shop_data = response.json()
                            
                            if "error" not in shop_data:
                                st.success("✅ ดึงข้อมูลร้านค้าสำเร็จ!")
                                
                                # แสดงข้อมูลในรูปแบบที่อ่านง่าย
                                if "response" in shop_data:
                                    shop_info = shop_data["response"]
                                    
                                    # สร้าง metrics
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
                                else:
                                    st.json(shop_data)
                            else:
                                st.error(f"❌ API Error: {shop_data}")
                        else:
                            st.error(f"❌ HTTP Error {response.status_code if response else 'No response'}")
                            if response:
                                try:
                                    st.json(response.json())
                                except:
                                    st.text(response.text)
            
            with col2:
                if st.button("👤 ดึงโปรไฟล์ร้านค้า", use_container_width=True):
                    with st.spinner("กำลังดึงโปรไฟล์ร้านค้า..."):
                        response, debug_info = get_shop_profile(
                            st.session_state.access_token,
                            st.session_state.shop_id
                        )
                        
                        if response and response.status_code == 200:
                            profile_data = response.json()
                            st.success("✅ ดึงโปรไฟล์ร้านค้าสำเร็จ!")
                            st.json(profile_data)
                        else:
                            st.error(f"❌ HTTP Error {response.status_code if response else 'No response'}")
                            if response:
                                try:
                                    st.json(response.json())
                                except:
                                    st.text(response.text)
        
        with tab2:
            st.subheader("รายการสินค้า")
            
            col1, col2 = st.columns([2, 1])
            
            with col2:
                page_size = st.selectbox("จำนวนสินค้าต่อหน้า", [10, 20, 50, 100], index=1)
                offset = st.number_input("Offset", min_value=0, value=0, step=10)
            
            with col1:
                if st.button("📦 ดึงรายการสินค้า", use_container_width=True):
                    with st.spinner("กำลังดึงรายการสินค้า..."):
                        response, debug_info = get_product_list(
                            st.session_state.access_token,
                            st.session_state.shop_id,
                            page_size=page_size,
                            offset=offset
                        )
                        
                        if response and response.status_code == 200:
                            product_data = response.json()
                            
                            if "error" not in product_data and "response" in product_data:
                                st.success("✅ ดึงรายการสินค้าสำเร็จ!")
                                
                                products = product_data["response"].get("item", [])
                                
                                if products:
                                    # แสดงเป็นตาราง
                                    df = pd.DataFrame(products)
                                    st.dataframe(df, use_container_width=True)
                                    
                                    # แสดงสถิติ
                                    st.metric("จำนวนสินค้าที่พบ", len(products))
                                else:
                                    st.info("ไม่พบสินค้าในร้านค้า")
                                
                                # แสดงข้อมูลทั้งหมด
                                with st.expander("📋 ข้อมูลทั้งหมด"):
                                    st.json(product_data)
                            else:
                                st.error(f"❌ API Error: {product_data}")
                        else:
                            st.error(f"❌ HTTP Error {response.status_code if response else 'No response'}")
                            if response:
                                try:
                                    st.json(response.json())
                                except:
                                    st.text(response.text)
        
        with tab3:
            st.subheader("รายการออเดอร์")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                days_back = st.selectbox("ย้อนหลัง", [1, 7, 14, 30], index=1)
            
            with col2:
                page_size = st.selectbox("จำนวนออเดอร์ต่อหน้า", [10, 20, 50], index=1, key="order_page_size")
            
            with col3:
                if st.button("🛒 ดึงรายการออเดอร์", use_container_width=True):
                    with st.spinner("กำลังดึงรายการออเดอร์..."):
                        time_from = int((datetime.now() - timedelta(days=days_back)).timestamp())
                        time_to = int(datetime.now().timestamp())
                        
                        response, debug_info = get_order_list(
                            st.session_state.access_token,
                            st.session_state.shop_id,
                            time_from=time_from,
                            time_to=time_to,
                            page_size=page_size
                        )
                        
                        if response and response.status_code == 200:
                            order_data = response.json()
                            
                            if "error" not in order_data and "response" in order_data:
                                st.success("✅ ดึงรายการออเดอร์สำเร็จ!")
                                
                                orders = order_data["response"].get("order_list", [])
                                
                                if orders:
                                    # แสดงเป็นตาราง
                                    df = pd.DataFrame(orders)
                                    st.dataframe(df, use_container_width=True)
                                    
                                    # แสดงสถิติ
                                    st.metric("จำนวนออเดอร์ที่พบ", len(orders))
                                else:
                                    st.info("ไม่พบออเดอร์ในช่วงเวลาที่เลือก")
                                
                                # แสดงข้อมูลทั้งหมด
                                with st.expander("📋 ข้อมูลทั้งหมด"):
                                    st.json(order_data)
                            else:
                                st.error(f"❌ API Error: {order_data}")
                        else:
                            st.error(f"❌ HTTP Error {response.status_code if response else 'No response'}")
                            if response:
                                try:
                                    st.json(response.json())
                                except:
                                    st.text(response.text)
        
        with tab4:
            st.subheader("การจัดการ Token")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Access Token:** {st.session_state.access_token[:20]}...")
                st.info(f"**Shop ID:** {st.session_state.shop_id}")
                
                if st.button("🗑️ ลบ Token", use_container_width=True):
                    for key in ['access_token', 'refresh_token', 'shop_id']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            
            with col2:
                if st.button("📋 แสดง Debug Info", use_container_width=True):
                    st.json({
                        "access_token": st.session_state.access_token,
                        "shop_id": st.session_state.shop_id,
                        "refresh_token": st.session_state.get("refresh_token", "")
                    })

else:
    # OAuth Login Section
    st.info("👆 เริ่มต้นด้วยการ Login เข้า Shopee OAuth")
    
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
    
    # แสดงขั้นตอนการใช้งาน
    with st.expander("📋 ขั้นตอนการใช้งาน"):
        st.write("""
        1. ✅ คลิกปุ่ม "เริ่ม Shopee OAuth" ด้านบน
        2. ✅ Login ด้วย Test Account:
           - Shop Account: SANDBOX.f216878ec16b03a6f962
           - Shop Password: 1bdd53e0ec3b7fb2
        3. ✅ เลือก "30 Days" ใน Authorization Period
        4. ✅ คลิก "Confirm Authorization"
        5. 🎯 กลับมาที่หน้านี้และคลิก "ดึง Access Token"
        6. 📊 เลือกข้อมูลที่ต้องการดึงจากแท็บต่างๆ
        """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    🛒 <strong>Shopee Data Retrieval System</strong> - ระบบดึงข้อมูลจาก Shopee API<br>
    ✅ รองรับการดึงข้อมูลร้านค้า, สินค้า, ออเดอร์, และโปรไฟล์
</div>
""", unsafe_allow_html=True)
