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

