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

# ===== ฟังก์ชันตรวจสอบ IP =====
def get_current_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except:
        return None

# ===== ฟังก์ชันสร้าง Signature (แบบง่าย) =====
def create_simple_signature(partner_id, path, timestamp, body=""):
    if body:
        body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
        sign_base = f"{partner_id}{path}{timestamp}{body_str}"
    else:
        sign_base = f"{partner_id}{path}{timestamp}"
    
    partner_key_bytes = bytes.fromhex(PARTNER_KEY)
    signature = hmac.new(partner_key_bytes, sign_base.encode('utf-8'), hashlib.sha256).hexdigest()
    return signature

# ===== ฟังก์ชันทดสอบ API =====
def test_api_connection():
    """ทดสอบการเชื่อมต่อ API โดยไม่ต้องใช้ token"""
    try:
        # ทดสอบด้วย public endpoint
        response = requests.get("https://partner.test-stable.shopeemobile.com", timeout=10)
        return response.status_code == 200
    except:
        return False

# ===== Streamlit App =====
st.set_page_config(page_title="Shopee Fix Final", page_icon="🔧")
st.title("🔧 Shopee OAuth - Final Solution")

# แสดงสถานะปัจจุบัน
st.error("""
🚨 **ปัญหาที่พบ:** IP Address ยังไม่ได้เพิ่มใน Shopee Console

**IP ที่ตรวจพบ:** `34.83.176.217`

**ต้องทำ:** เพิ่ม IP นี้ใน Shopee Console ก่อนจึงจะใช้งานได้
""")

# ขั้นตอนแก้ไขแบบละเอียด
st.subheader("📋 ขั้นตอนแก้ไขแบบละเอียด")

with st.expander("🔧 ขั้นตอนที่ 1: เข้า Shopee Console", expanded=True):
    st.markdown("""
    1. **เปิดแท็บใหม่** ในเบราว์เซอร์
    2. **ไปที่:** https://open.shopee.com
    3. **Login** ด้วยบัญชีที่สร้างแอป
    4. **คลิก "App Management"** หรือ **"การจัดการแอป"**
    """)
    
    if st.button("🌐 เปิด Shopee Console", use_container_width=True):
        st.markdown('[🔗 คลิกที่นี่เพื่อเปิด Shopee Console](https://open.shopee.com)')

with st.expander("🔧 ขั้นตอนที่ 2: หาแอปของคุณ"):
    st.markdown("""
    1. ในหน้า App Management ให้หา **"test tiw"**
    2. **คลิกเข้าไป**ที่แอปนั้น
    3. คุณจะเห็นหน้าข้อมูลแอป
    """)

with st.expander("🔧 ขั้นตอนที่ 3: แก้ไข IP Whitelist", expanded=True):
    current_ip = get_current_ip()
    
    st.markdown(f"""
    **ในหน้าแอป ให้ทำตามนี้:**
    
    1. **เลื่อนลงหา** "IP Address Whitelist" หรือ "Whitelist"
    2. **ลบ IP เก่าทั้งหมด:**
       - `104.16.0.1`
       - `104.16.3.2`
       - `104.16.8.8`
    3. **เพิ่ม IP ใหม่:** `{current_ip or '34.83.176.217'}`
    4. **คลิก Save** หรือ **บันทึก**
    5. **รอ 2-3 นาที** ให้ระบบอัปเดต
    """)
    
    st.code(f"IP ที่ต้องเพิ่ม: {current_ip or '34.83.176.217'}")

with st.expander("🔧 ขั้นตอนที่ 4: ทดสอบ"):
    st.markdown("""
    1. **กลับมาที่หน้านี้**
    2. **Refresh หน้า** (กด F5)
    3. **คลิก "ทดสอบการเชื่อมต่อ"** ด้านล่าง
    4. **หากสำเร็จ** จะแสดงสีเขียว
    """)

# ส่วนทดสอบ
st.divider()
st.subheader("🧪 ทดสอบการเชื่อมต่อ")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🌐 ทดสอบ Network", use_container_width=True):
        if test_api_connection():
            st.success("✅ เชื่อมต่อ Shopee API ได้")
        else:
            st.error("❌ ไม่สามารถเชื่อมต่อ Shopee API")

with col2:
    if st.button("🔍 ตรวจสอบ IP", use_container_width=True):
        ip = get_current_ip()
        if ip:
            st.success(f"✅ IP ปัจจุบัน: {ip}")
        else:
            st.error("❌ ไม่สามารถตรวจสอบ IP")

with col3:
    if st.button("🔄 Refresh หน้า", use_container_width=True):
        st.rerun()

# ส่วนทดสอบ OAuth (หลังแก้ไข IP)
query_params = st.query_params
code = query_params.get("code")
shop_id = query_params.get("shop_id", "142837")

if code and shop_id:
    st.divider()
    st.success(f"✅ ได้รับ authorization code และ shop_id: `{shop_id}`")
    
    if st.button("🔑 ทดสอบดึง Access Token", type="primary", use_container_width=True):
        with st.spinner("กำลังทดสอบ..."):
            timestamp = int(time.time())
            path = "/api/v2/auth/token/get"
            
            body = {
                "code": code,
                "shop_id": int(shop_id),
                "partner_id": PARTNER_ID
            }
            
            signature = create_simple_signature(PARTNER_ID, path, timestamp, body)
            
            params = {
                "partner_id": PARTNER_ID,
                "timestamp": timestamp,
                "sign": signature
            }
            
            try:
                response = requests.post(
                    f"https://partner.test-stable.shopeemobile.com{path}",
                    params=params,
                    json=body,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                st.write(f"**Response Status:** {response.status_code}")
                
                if response.status_code == 200:
                    token_data = response.json()
                    if "access_token" in token_data:
                        st.success("🎉 สำเร็จ! ได้รับ Access Token แล้ว!")
                        st.json(token_data)
                        
                        # เก็บ token
                        st.session_state.access_token = token_data["access_token"]
                        st.session_state.shop_id = shop_id
                        
                        st.balloons()
                    else:
                        st.error("❌ ไม่พบ access_token")
                        st.json(token_data)
                elif response.status_code == 403:
                    st.error("❌ ยังคงได้ HTTP 403 - IP Address ยังไม่ได้เพิ่มใน Console")
                    st.json(response.json())
                else:
                    st.error(f"❌ HTTP Error {response.status_code}")
                    st.text(response.text)
                    
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")

else:
    # ส่วน OAuth Login
    st.divider()
    st.info("👆 หลังจากแก้ไข IP Whitelist แล้ว ให้คลิกปุ่มด้านล่าง")
    
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    signature = create_simple_signature(PARTNER_ID, path, timestamp)
    
    redirect_encoded = urllib.parse.quote(REDIRECT_URL, safe='')
    login_url = (
        f"https://partner.test-stable.shopeemobile.com{path}?partner_id={PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={signature}"
        f"&redirect={redirect_encoded}"
    )
    
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <a href="{login_url}" target="_self" style="
            background: #ee4d2d;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            display: inline-block;
        ">🚀 ทดสอบ Shopee OAuth</a>
    </div>
    """, unsafe_allow_html=True)

# หากมี Access Token แล้ว
if "access_token" in st.session_state:
    st.divider()
    st.success("🎉 มี Access Token แล้ว!")
    
    if st.button("📊 ทดสอบดึงข้อมูลร้านค้า", use_container_width=True):
        timestamp = int(time.time())
        path = "/api/v2/shop/get_shop_info"
        
        sign_base = f"{PARTNER_ID}{path}{timestamp}{st.session_state.access_token}{st.session_state.shop_id}"
        signature = hmac.new(
            bytes.fromhex(PARTNER_KEY), 
            sign_base.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
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

# คำแนะนำเพิ่มเติม
st.divider()
st.info("""
## 💡 หากยังไม่ได้ผล:

1. **ตรวจสอบอีกครั้ง** ว่าได้เพิ่ม IP `34.83.176.217` ใน Shopee Console แล้ว
2. **รอ 5-10 นาที** ให้ระบบ Shopee อัปเดต
3. **ลองใช้ `0.0.0.0/0`** ใน IP Whitelist (อนุญาตทุก IP) สำหรับทดสอบ
4. **ตรวจสอบ Partner Key** ใน Shopee Console ว่าตรงกับในโค้ด
5. **ติดต่อ Shopee Support** หากทุกวิธีไม่ได้ผล

**Test Account:**
- Shop Account: SANDBOX.f216878ec16b03a6f962
- Shop Password: 1bdd53e0ec3b7fb2
""")
