import streamlit as st
import requests
import uuid

# رابط محرككِ في Firebase
DB_URL = "https://tabaqiya-929e4-default-rtdb.firebaseio.com/.json"

if 'my_id' not in st.session_state:
    st.session_state.my_id = str(uuid.uuid4())[:6].upper()
    st.session_state.points = 100

st.set_page_config(page_title="لعبة الطبقية", page_icon="👑")
st.markdown("<h1 style='text-align: center; color: gold;'>🏯 لعبة الطبقية</h1>", unsafe_allow_html=True)

st.sidebar.markdown(f"### 👤 هويتي (ID): `{st.session_state.my_id}`")
st.sidebar.write(f"💰 رصيدك: {st.session_state.points}")

friend_id = st.text_input("أدخلي ID الصديقة للبدء:")

if friend_id:
    st.success(f"تحدي مع: {friend_id}")
    choice = st.radio("اختاري بطاقتكِ:", ["الملك 🟡👑", "المواطن 🔵⚒️", "العبد 🔴⛓️"])
    bet = st.number_input("الرهان:", 5, st.session_state.points, step=5)

    if st.button("إرسال الحركة ⚔️"):
        move_data = {st.session_state.my_id: {"choice": choice, "bet": bet, "target": friend_id}}
        requests.patch(DB_URL, json=move_data)
        st.info("تم الإرسال! بانتظار الخصم...")

if st.button("كشف الأوراق 🔄"):
    try:
        data = requests.get(DB_URL).json()
        if data and friend_id in data:
            st.warning(f"صديقتكِ لعبت: {data[friend_id]['choice']}")
        else:
            st.error("لم يتم إرسال حركة من الطرف الآخر.")
    except:
        st.error("تأكدي من الاتصال.")
