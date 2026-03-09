import streamlit as st
import requests
import time

# رابط قاعدة البيانات الخاصة بكِ
DB_URL = "https://tabaqiya-929e4-default-rtdb.firebaseio.com/.json"

st.set_page_config(page_title="لعبة الطبقية - النسخة الاحترافية", page_icon="⚔️", layout="wide")

# تصميم الواجهة
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏰 صراع الطبقات: الملك والمواطن والعبد</h1>", unsafe_allow_html=True)
st.divider()

# 1. إعدادات اللاعب والنقاط
if 'my_id' not in st.session_state:
    st.session_state.my_id = ""
if 'points' not in st.session_state:
    st.session_state.points = 100
if 'current_round' not in st.session_state:
    st.session_state.current_round = 1

# القائمة الجانبية للمعلومات
with st.sidebar:
    st.header("📊 لوحة التحكم")
    if not st.session_state.my_id:
        st.session_state.my_id = st.text_input("أدخلي اسمكِ (ID):", placeholder="مثلاً: الملكة")
    st.metric("💰 رصيدكِ", f"{st.session_state.points} نقطة")
    st.info(f"📅 الجولة الحالية: {st.session_state.current_round} / 3")
    if st.button("إعادة ضبط اللعبة 🔄"):
        st.session_state.points = 100
        st.session_state.current_round = 1
        st.rerun()

# 2. منطقة اللعب
friend_id = st.text_input("🔍 أدخلي ID الصديقة (عائشة):", placeholder="اكتبي الرمز هنا...")

if friend_id:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🃏 اختاري ورقتكِ")
        choice = st.radio("القوة المتاحة:", ["الملك 👑", "المواطن ⚒️", "العبد ⛓️"], help="الملك يهزم المواطن، المواطن يهزم العبد، والعبد يغدر بالملك!")
    
    with col2:
        st.subheader("💸 الرهان")
        bet = st.slider("كم نقطة ستخاطرين بها؟", 5, st.session_state.points, 10)
