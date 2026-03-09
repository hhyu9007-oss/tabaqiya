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

# --- محرك اللعبة الرئيسي ---
st.title("🏟️ ميدان التحدي الملكي")

invites = fb_get(f"invites/{user}")
if invites:
    for sender, status in invites.items():
        if status == "pending":
            if st.button(f"🔔 قبول تحدي من {sender}"):
                starter_king = random.choice([user, sender])
                game_id = f"game_{user}_{sender}"
                fb_update(f"invites/{user}", {sender: "accepted"})
                fb_put(f"games/{game_id}/config", {"p1": user, "p2": sender, "king_start": starter_king, "round": 1})
                st.session_state.game_id = game_id
                st.rerun()

if 'game_id' not in st.session_state:
    all_invites = fb_get(f"invites/{user}")
    for sender, status in all_invites.items():
        if status == "accepted":
            id1, id2 = f"game_{user}_{sender}", f"game_{sender}_{user}"
            st.session_state.game_id = id1 if fb_get(f"games/{id1}") else id2

if 'game_id' in st.session_state:
    g_id = st.session_state.game_id
    game_data = fb_get(f"games/{g_id}")
    conf = game_data.get("config", {})
    curr_round = conf.get("round", 1)
    
    # نظام الـ 3 جولات
    phase = (curr_round - 1) // 3
    if phase % 2 == 0:
        role = "الملك 👑" if user == conf.get("king_start") else "العبد ⛓️"
    else:
        role = "العبد ⛓️" if user == conf.get("king_start") else "الملك 👑"

    st.subheader(f"📅 الجولة: {curr_round} / 12 | دورك: {role}")

    if "الملك" in role:
        deck = ["ملك 👑"] + ["مواطن ⚒️"] * 4
    else:
        deck = ["عبد ⛓️"] + ["مواطن ⚒️"] * 4
        
    choice = st.selectbox("اختر ورقتك:", deck)
    bet = st.number_input("الرهان:", 10, 1000, 50)
    
    if st.button("إرسال الهجوم ⚔️"):
        fb_update(f"games/{g_id}/moves/{user}", {"card": choice, "bet": bet, "ready": True})
        st.success("تم الإرسال!")

    if st.button("كشف النتيجة 🔄"):
        moves = fb_get(f"games/{g_id}/moves")
        opp = conf['p2'] if user == conf['p1'] else conf['p1']
        
        if opp in moves and moves[opp].get("ready"):
            m_c, o_c, o_b = choice, moves[opp]['card'], moves[opp]['bet']
            st.markdown(f"### أنت ({m_c}) VS الخصم ({o_c})")
            
            mult = 5 if "عبد" in m_c else 2
            if (m_c == "ملك 👑" and "مواطن" in o_c) or ("مواطن" in m_c and "عبد" in o_c) or ("عبد" in m_c and "ملك" in o_c):
                st.balloons(); st.success(f"🎊 فزت بربح {o_b * mult} نقطة")
                fb_update(f"games/{g_id}/config", {"round": curr_round + 1})
            elif m_c == o_c:
                st.info("تعادل!")
            else:
                st.error("💀 خسرت الجولة")
                fb_update(f"games/{g_id}/config", {"round": curr_round + 1})
            
            fb_update(f"games/{g_id}/moves/{user}", {"ready": False})
            time.sleep(1); st.rerun()
        else:
            st.warning("بانتظار الخصم...")

st.divider()
st.caption("برمجة علي 2026 | نظام الـ 12 جولة الكامل")
