import streamlit as st
import requests
import time
import random

# إعدادات قاعدة البيانات
DB_URL = "https://tabaqiya-929e4-default-rtdb.firebaseio.com/"

st.set_page_config(page_title="صراع العروش | علي", layout="wide", page_icon="⚔️")

# --- دالات النظام ---
def fb_get(path): return requests.get(f"{DB_URL}{path}.json").json() or {}
def fb_update(path, data): requests.patch(f"{DB_URL}{path}.json", json=data)
def fb_put(path, data): requests.put(f"{DB_URL}{path}.json", json=data)

# --- نظام الدخول واختيار الشخصية ---
if 'user' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: gold;'>🛡️ اختيار المحاربين 🛡️</h1>", unsafe_allow_html=True)
    u_id = st.text_input("ادخل الـ ID الخاص بك:")
    char = st.radio("اختر شخصيتك القتالية:", ["علاوي 🔥", "عائشة ✨", "زوين ⚡"])
    
    if st.button("دخول الساحة ⚔️"):
        if u_id:
            st.session_state.user = u_id
            st.session_state.char = char
            fb_update(f"users/{u_id}", {"char": char, "status": "online"})
            st.rerun()
    st.stop()

user = st.session_state.user
my_char = st.session_state.char

# --- القائمة الجانبية (الأصدقاء والدردشة) ---
with st.sidebar:
    st.header(f"👤 {my_char} ({user})")
    st.divider()
    
    # إضافة صديق ودعوة
    f_id = st.text_input("إضافة صديق بالـ ID:")
    if st.button("إضافة ✅"):
        fb_update(f"friends/{user}", {f_id: "friend"})
        fb_update(f"friends/{f_id}", {user: "friend"})
    
    friends = fb_get(f"friends/{user}")
    if friends:
        friend_choice = st.selectbox("دردشة ودعوة:", list(friends.keys()))
        chat_id = "".join(sorted([user, friend_choice]))
        c_msg = st.text_input("رسالة خاصة:")
        if st.button("إرسال 🚀"):
            fb_update(f"chats/{chat_id}", {str(int(time.time())): f"{my_char}: {c_msg}"})
        
        chat_data = fb_get(f"chats/{chat_id}")
        if chat_data:
            for m in list(chat_data.values())[-3:]: st.caption(m)
        
        if st.button(f"⚔️ تحدي {friend_choice}"):
            fb_update(f"invites/{friend_choice}", {user: "pending"})

# --- محرك اللعبة ---
st.title("🏟️ الميدان الملكي")

# استقبال الدعوات
invs = fb_get(f"invites/{user}")
if invs:
    for sender, status in invs.items():
        if status == "pending" and st.button(f"🔔 قبول تحدي من {sender}"):
            starter = random.choice([user, sender])
            g_id = f"game_{user}_{sender}"
            fb_update(f"invites/{user}", {sender: "accepted"})
            fb_put(f"games/{g_id}/config", {"p1": user, "p2": sender, "king_start": starter, "round": 1})
            st.session_state.game_id = g_id
            # إعداد الحقيبة الأولية (تخزن في جلسة اللاعب)
            st.session_state.my_deck = [] 
            st.rerun()

# استرجاع اللعبة
if 'game_id' not in st.session_state:
    all_invs = fb_get(f"invites/{user}")
    for s, status in all_invs.items():
        if status == "accepted":
            id1, id2 = f"game_{user}_{s}", f"game_{s}_{user}"
            st.session_state.game_id = id1 if fb_get(f"games/{id1}") else id2

if 'game_id' in st.session_state:
    g_id = st.session_state.game_id
    game = fb_get(f"games/{g_id}")
    conf = game.get("config", {})
    curr_round = conf.get("round", 1)
    
    # تبادل الأدوار كل 3 جولات
    phase = (curr_round - 1) // 3
    is_king_start = (user == conf.get('king_start'))
    role = "الملك 👑" if (phase % 2 == 0) == is_king_start else "العبد ⛓️"

    # إدارة الحقيبة (Deck Management)
    if 'my_deck' not in st.session_state or not st.session_state.my_deck or (curr_round-1)%3 == 0:
        if "الملك" in role:
            st.session_state.my_deck = ["ملك 👑"] + ["مواطن ⚒️"]*4
        else:
            st.session_state.my_deck = ["عبد ⛓️"] + ["مواطن ⚒️"]*4

    st.subheader(f"📅 الجولة: {curr_round} / 12 | دورك: {role}")
    st.write(f"بطاقاتك المتبقية: {st.session_state.my_deck}")

    choice = st.selectbox("اختر بطاقتك للهجوم:", st.session_state.my_deck)
    bet = st.number_input("الرهان:", 10, 1000, 50)
    
    if st.button("إرسال الهجوم ⚔️"):
        fb_update(f"games/{g_id}/moves/{user}", {"card": choice, "bet": bet, "ready": True})
        st.success("تم التثبيت!")

    if st.button("كشف النتيجة 🔄"):
        moves = fb_get(f"games/{g_id}/moves")
        opp_id = conf['p2'] if user == conf['p1'] else conf['p1']
        
        if opp_id in moves and moves[opp_id].get("ready"):
            m_c, o_c, o_b = choice, moves[opp_id]['card'], moves[opp_id]['bet']
            st.markdown(f"#### أنت ({m_c}) VS الخصم ({o_c})")
            
            # حتى في التعادل.. البطاقة تُحذف من الحقيبة
            if choice in st.session_state.my_deck:
                st.session_state.my_deck.remove(choice)
            
            mult = 5 if "عبد" in m_c else 2
            
            if (m_c == "ملك 👑" and "مواطن" in o_c) or ("مواطن" in m_c and "عبد" in o_c) or ("عبد" in m_c and "ملك" in o_c):
                st.balloons(); st.success(f"فوز! ربحت {o_b * mult} نقطة")
            elif m_c == o_c:
                st.info("تعادل! (تم استهلاك البطاقات)")
            else:
                st.error("خسارة!")
            
            # تحديث الجولة وتصفير الجاهزية
            fb_update(f"games/{g_id}/config", {"round": curr_round + 1})
            fb_update(f"games/{g_id}/moves/{user}", {"ready": False})
            time.sleep(1); st.rerun()
        else:
            st.warning("بانتظار الخصم...")

st.divider()
st.caption("إصدار علي 2026 - نظام الشخصيات المحدودة")
