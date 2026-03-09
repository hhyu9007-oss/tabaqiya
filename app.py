import streamlit as st
import requests
import time
from datetime import datetime

# إعدادات Firebase - تأكد من صحة الرابط الخاص بك
DB_URL = "https://tabaqiya-929e4-default-rtdb.firebaseio.com/"

st.set_page_config(page_title="إمبراطورية الطبقية | علي", layout="wide", page_icon="👑")

# --- دالات النظام الأساسية ---
def fb_get(path):
    res = requests.get(f"{DB_URL}{path}.json")
    return res.json() or {}

def fb_update(path, data):
    requests.patch(f"{DB_URL}{path}.json", json=data)

def get_rank(p):
    if p < 50: return "العبد المنبوذ ⛓️"
    if p < 150: return "المواطن الكادح ⚒️"
    if p < 300: return "المحارب النبيل ⚔️"
    return "الإمبراطور العظيم 👑"

# --- نظام الحسابات ---
if 'user' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: gold;'>🛡️ مرحباً بك في ساحة الإمبراطور 🛡️</h1>", unsafe_allow_html=True)
    with st.container():
        name = st.text_input("سجل اسمك القتالي للدخول:", placeholder="مثلاً: علي القاهر")
        if st.button("اقتحام الساحة"):
            if name:
                st.session_state.user = name
                current = fb_get(f"players/{name}")
                if not current:
                    fb_update(f"players/{name}", {"points": 100, "wins": 0, "rank": "مبتدئ"})
                st.rerun()
    st.stop()

user = st.session_state.user
p_data = fb_get(f"players/{user}")
points = p_data.get("points", 100)

# --- الواجهة الجانبية (البروفايل) ---
with st.sidebar:
    st.title(f"🎖️ {user}")
    st.subheader(get_rank(points))
    st.metric("💰 الرصيد الملكي", f"{points} نقطة")
    st.write(f"📈 الانتصارات: {p_data.get('wins', 0)}")
    
    st.divider()
    st.subheader("💬 ديوان الدردشة")
    msg = st.text_input("أرسل رسالة للجميع...", key="chat_in")
    if st.button("إرسال"):
        t_str = datetime.now().strftime("%H:%M")
        fb_update("global_chat", {str(int(time.time())): f"[{t_str}] **{user}:** {msg}"})
    
    chat = fb_get("global_chat")
    if chat:
        for m in list(chat.values())[-10:]:
            st.caption(m)

# --- ساحة العمليات ---
tab1, tab2, tab3 = st.tabs(["⚔️ ميدان القتال", "🛒 المتجر الملكي", "🏆 لوحة الشرف"])

with tab1:
    st.subheader("🔥 تحدي الأنداد")
    opp_id = st.text_input("ادخل اسم الخصم (الضحية القادمة):")
    
    if opp_id:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🛡️ خطتك الاستراتيجية")
            move = st.selectbox("اختر ورقتك:", ["الملك 👑", "المواطن ⚒️", "العبد ⛓️"])
            bet = st.select_slider("حدد مبلغ الرهان:", options=[5, 10, 20, 50, 100], value=10)
            
            if st.button("تأفيذ الهجوم ⚔️"):
                fb_update(f"arena/{user}", {"move": move, "bet": bet, "target": opp_id, "status": "ready"})
                st.success("تم تثبيت حركتك في قاعدة البيانات!")

        with c2:
            st.markdown("### 📡 رادار الخصم")
            opp_move_data = fb_get(f"arena/{opp_id}")
            if opp_move_data and opp_move_data.get("target") == user and opp_move_data.get("status") == "ready":
                st.warning(f"⚠️ الخصم {opp_id} استعد للهجوم!")
                if st.button("كشف المصير 🛡️"):
                    my_m = fb_get(f"arena/{user}")['move']
                    o_m = opp_move_data['move']
                    o_b = opp_move_data['bet']
                    
                    st.header(f"{my_m} VS {o_m}")
                    
                    if my_m == o_m:
                        st.info("تعادل الأبطال!")
                    elif (my_m == "الملك 👑" and o_m == "المواطن ⚒️") or \
                         (my_m == "المواطن ⚒️" and o_m == "العبد ⛓️") or \
                         (my_m == "العبد ⛓️" and o_m == "الملك 👑"):
                        st.balloons()
                        st.success(f"🎊 نصر ساحق! غنمت {o_b} نقطة")
                        fb_update(f"players/{user}", {"points": points + o_b, "wins": p_data.get('wins', 0) + 1})
                    else:
                        st.error(f"💀 سقطت في المعركة.. فقدت {bet} نقطة")
                        fb_update(f"players/{user}", {"points": points - bet})
                    
                    fb_update(f"arena/{user}", {"status": "waiting"})
            else:
                st.write("بانتظار أن يجهز الخصم أوراقه...")

with tab2:
    st.subheader("🛍️ متجر الإمبراطورية")
    st.write("قريباً: اشترِ 'رؤية حركة الخصم' أو 'حماية النقاط'!")
    st.button("شراء درع حماية (50 نقطة) - قريباً")

with tab3:
    st.subheader("🥇 سادة الساحة")
    all_p = fb_get("players")
    top_list = sorted(all_p.items(), key=lambda x: x[1]['points'], reverse=True)
    for i, (n, d) in enumerate(top_list[:10]):
        color = "gold" if i == 0 else "silver" if i == 1 else "white"
        st.markdown(f"<p style='color:{color};'>{i+1}. {n} — {d['points']} نقطة ({get_rank(d['points'])})</p>", unsafe_allow_html=True)

st.divider()
st.caption("تم التطوير بواسطة: المبرمج علي | 2026")



