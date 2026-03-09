import streamlit as st
import requests
import time
import random

# إعدادات Firebase
DB_URL = "https://tabaqiya-929e4-default-rtdb.firebaseio.com/"

st.set_page_config(page_title="إمبراطورية علي | صراع الطبقات", layout="wide", page_icon="🛡️")

# --- دالات النظام ---
def fb_get(path): return requests.get(f"{DB_URL}{path}.json").json() or {}
def fb_update(path, data): requests.patch(f"{DB_URL}{path}.json", json=data)
def fb_put(path, data): requests.put(f"{DB_URL}{path}.json", json=data)

# --- نظام تسجيل الدخول ---
if 'user' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏰 ساحة صراع الطبقات</h1>", unsafe_allow_html=True)
    u_id = st.text_input("أدخل الـ ID الخاص بك (اسمك):", placeholder="مثلاً: علي القوي")
    if st.button("تسجيل الدخول"):
        if u_id:
            st.session_state.user = u_id
            fb_update(f"users/{u_id}", {"status": "متصل", "points": 1000})
            st.rerun()
    st.stop()

user = st.session_state.user

# --- القائمة الجانبية (الأصدقاء والدردشة) ---
with st.sidebar:
    st.title(f"👤 {user}")
    st.divider()
    
    # 1. إضافة الأصدقاء
    st.subheader("➕ إضافة صديق")
    new_f = st.text_input("ادخل ID الصديق:")
    if st.button("إرسال طلب"):
        fb_update(f"friends/{user}", {new_f: "friend"})
        fb_update(f"friends/{new_f}", {user: "friend"})
        st.success(f"تمت إضافة {new_f}!")

    # 2. الأصدقاء والدردشة الخاصة
    friends_list = fb_get(f"friends/{user}")
    if friends_list:
        friend = st.selectbox("دردشة ودعوة:", list(friends_list.keys()))
        
        # الدردشة
        chat_id = "".join(sorted([user, friend]))
        c_msg = st.text_input(f"رسالة إلى {friend}:")
        if st.button("إرسال"):
            fb_update(f"chats/{chat_id}", {str(int(time.time())): f"{user}: {c_msg}"})
        
        chat_data = fb_get(f"chats/{chat_id}")
        for m in list(chat_data.values())[-5:]: st.caption(m)
        
        st.divider()
        # 3. نظام الدعوات
        if st.button(f"⚔️ إرسال دعوة قتال لـ {friend}"):
            fb_update(f"invites/{friend}", {user: "pending"})
            st.info("تم إرسال الدعوة...")

# --- ساحة اللعب الرئيسية ---
st.markdown("### 🏟️ ميدان التحدي")

# فحص الدعوات الواردة
invites = fb_get(f"invites/{user}")
if invites:
    for sender, status in invites.items():
        if status == "pending":
            if st.button(f"🔔 قبول تحدي من {sender}"):
                # قرعة عشوائية للملك الأول
                starter = random.choice([user, sender])
                game_id = f"game_{user}_{sender}"
                fb_update(f"invites/{user}", {sender: "accepted"})
                fb_put(f"games/{game_id}/config", {"p1": user, "p2": sender, "king": starter, "round": 1})
                st.session_state.game_id = game_id
                st.rerun()

# استرجاع اللعبة النشطة
if 'game_id' not in st.session_state:
    # محاولة العثور على لعبة مقبولة
    all_invites = fb_get(f"invites/{user}")
    for sender, status in all_invites.items():
        if status == "accepted":
            st.session_state.game_id = f"game_{sender}_{user}" if fb_get(f"games/game_{sender}_{user}") else f"game_{user}_{sender}"

if 'game_id' in st.session_state:
    g_id = st.session_state.game_id
    game = fb_get(f"games/{g_id}")
    if not game: 
        st.write("بانتظار بناء الساحة...")
        st.stop()
        
    conf = game.get("config")
    curr_round = conf['round']
    
    # منطق تبديل الأدوار كل 3 جولات
    # الجولات (1،2،3) و (7،8،9) الفريق الأول ملك | الجولات (4،5،6) و (10،11،12) الفريق الثاني ملك
    cycle = (curr_round - 1) // 3
    if cycle % 2 == 0:
        role = "الملك 👑" if user == conf['king'] else "العبد ⛓️"
    else:
        role = "العبد ⛓️" if user == conf['king'] else "الملك 👑"

    st.subheader(f"📅 الجولة: {curr_round} / 12")
    st.info(f"دورك الحالي: {role}")

    # الحقيبة
    deck = ["ملك 👑"] + ["مواطن ⚒️"]*4 if "الملك" in role else ["عبد ⛓️"] + ["مواطن ⚒️"]*4
    choice = st.selectbox("اختر بطاقتك للهجوم:", deck)
    bet = st.number_input("الرهان (النقاط):", 10, 1000, 50)
    
    if st.button("إرسال الهجوم ⚔️"):
        fb_update(f"games/{g_id}/moves/{user}", {"card": choice, "bet": bet, "ready": True})
        st.success("تم إرسال البطاقة! بانتظار الخصم...")

    if st.button("كشف النتيجة 🔄"):
        moves = game.get("moves", {})
        opp = conf['p2'] if user == conf['p1'] else conf['p1']
        
        if opp in moves and moves[opp].get("ready"):
            m_c = choice
            o_c = moves[opp]['card']
            o_b = moves[opp]['bet']
            
            st.markdown(f"#### أنت: {m_c} VS الخصم: {o_c}")
            
            # حساب النقاط (مواطن/ملك x2 | عبد x5)
            won = False
            mult = 2
            if "عبد" in m_c: mult = 5
            
            if (m_c == "ملك 👑" and "مواطن" in o_c) or \
               ("مواطن" in m_c and "عبد" in o_c) or \
               ("عبد" in m_c and "ملك" in o_c):
                won = True
                points_won = o_b * mult
                st.balloons()
                st.success(f"🏆 فزت! ربحت {points_won} نقطة!")
                fb_update(f"games/{g_id}/config", {"round": curr_round + 1}) # جولة جديدة
            elif m_c == o_c:
                st.warning("تعادل! اعد اللعب بنفس الجولة.")
            else:
                st.error(f"💀 خسرت الجولة ورهانك {bet}")
                fb_update(f"games/{g_id}/config", {"round": curr_round + 1})
            
            # تصفير الجاهزية للجولة القادمة
            fb_update(f"games/{g_id}/moves/{user}", {"ready": False})
        else:
            st.warning("الخصم لم يرسل حركته بعد.")

st.divider()
st.caption("نظام صراع الطبقات 2026 | إشراف المبرمج علي")
