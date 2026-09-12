import streamlit as st

# ==========================================
# 1. 커스텀 CSS (파란 상자 & 회색 상자 & 밀착 레이아웃)
# ==========================================
st.set_page_config(page_title="서논술형 자동 채점 시스템", layout="wide")

st.markdown("""
<style>
    /* 파란 상자: 지문 및 자료 */
    .blue-box {
        background-color: #eef6ff;
        border-left: 5px solid #2b7fff;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #1a2530;
    }
    /* 회색 상자: 조건 */
    .gray-box {
        background-color: #f2f4f7;
        border: 1px solid #d0d5dd;
        padding: 12px 18px;
        border-radius: 8px;
        margin-top: 8px;
        margin-bottom: 15px;
        color: #344054;
    }
    /* 입력창 간격 밀착 조절 */
    .stTextInput, .stTextArea {
        margin-top: -10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 문항별 자동 채점 로직
# ==========================================

# --- [세트 1] 채점 함수 ---
def grade_set1_q1(ans1, ans2, ans3):
    score, feedback = 0, []
    if any(k in ans1 for k in ["쉬운", "노력", "친숙", "좋아하는"]):
        score += 2; feedback.append("(1) 정답 (+2점)")
    else: feedback.append("(1) 오답: '쉬운 과제' 또는 '친숙한 과목' 특성 미포함")

    kw2_pos = ["혼자", "차분", "집중", "익숙", "연습"]
    kw2_neg = ["함께", "모임", "친구", "도서관", "커피숍"]
    if any(k in ans2 for k in kw2_pos) and not any(k in ans2 for k in kw2_neg):
        score += 2; feedback.append("(2) 정답 (+2점)")
    elif any(k in ans2 for k in kw2_neg):
        feedback.append("(2) 오답 (오개념): 어려운 과제에 '타인과 함께함' 특성을 적용함")
    else: feedback.append("(2) 오답: '혼자 차분히 집중함' 의미 부족")

    if "사회적 억제" in ans3.replace(" ", ""):
        score += 2; feedback.append("(3) 정답 (+2점)")
    else: feedback.append("(3) 오답: '사회적 억제' 명칭 오기 또는 미입력")
    return score, feedback

def grade_set1_q2(ans1, ans2):
    score, feedback = 0, []
    methods = {"예시": ["예를 들어", "예컨대", "커피숍", "도서관"], "대조": ["반면", "달리", "혼자"], "인과": ["때문에", "하므로"], "정의": ["란", "의미"]}
    detect = lambda t: [m for m, kws in methods.items() if f"({m})" in t or any(k in t for k in kws)]
    m1, m2 = detect(ans1), detect(ans2)

    if any(k in ans1 for k in ["효과", "높이", "좋다", "함께", "도서관"]) and len(m1) > 0:
        score += 2; feedback.append("(1) 문장 정답 (+2점)")
    else: feedback.append("(1) 문장 감점/오답: 설명 방법 미흡 또는 결론 미달성")

    if any(k in ans2 for k in ["혼자", "집중", "시간", "익숙"]) and len(m2) > 0:
        if set(m1) == set(m2) and len(m1) == 1:
            score += 1; feedback.append("(2) 문장 부분 점수 (+1점): (1)과 동일한 설명 방법 중복 사용")
        else: score += 2; feedback.append("(2) 문장 정답 (+2점)")
    else: feedback.append("(2) 문장 오답: 결론 방향성 미달성")
    return score, feedback

def grade_set1_q3(vp, ve, ap, ae):
    score, feedback = 0, []
    if any(k in vp for k in ["혼자", "단독", "몰입"]) and not any(k in vp for k in ["함께", "친구"]):
        if any(k in ve for k in ["어려운", "도전", "혼자", "집중"]):
            score += 3; feedback.append("시각 요소 정답 (+3점)")
        else: score += 1.5; feedback.append("시각 요소 부분 점수 (+1.5점): 연출은 좋으나 지문 근거 연결 부족")
    else: feedback.append("시각 요소 오답: 혼자 집중하는 환경 연출 미흡")

    if any(k in ap for k in ["정적", "최소", "배제", "연필", "잔잔"]):
        if any(k in ae for k in ["차단", "안정", "집중", "차분"]):
            score += 3; feedback.append("청각 요소 정답 (+3점)")
        else: score += 1.5; feedback.append("청각 요소 부분 점수 (+1.5점): 연출은 좋으나 지문 근거 연결 부족")
    else: feedback.append("청각 요소 오답: 정적 연출 미흡")
    return score, feedback


# --- [세트 2] 채점 함수 ---
def grade_set2_q1(ans1, ans2, ans3):
    score, feedback = 0, []
    if "고여 있는 물" in ans1 or "고여있는 물" in ans1:
        score += 2; feedback.append("(1) 정답 (+2점)")
    else: feedback.append("(1) 오답: '고여 있는 물' 특성이 나타나지 않음")

    if any(k in ans2 for k in ["이동하지", "머물러", "정지"]):
        score += 2; feedback.append("(2) 정답 (+2점)")
    else: feedback.append("(2) 오답: '전하가 이동하지 않고 머물러 있음' 표현 미포함")

    if any(k in ans3 for k in ["전압", "높"]) and any(k in ans3 for k in ["위험하지", "피해"]):
        score += 2; feedback.append("(3) 정답 (+2점)")
    else: feedback.append("(3) 오답: 전압의 높음과 비위험성 이유/결과 조건 미달성")
    return score, feedback

def grade_set2_q2(ans1, ans2):
    score, feedback = 0, []
    methods = {"정의": ["란", "의미"], "비교": ["같다", "처럼"], "대조": ["달리", "반면"], "인과": ["때문에"]}
    detect = lambda t: [m for m, kws in methods.items() if f"({m})" in t or any(k in t for k in kws)]
    m1, m2 = detect(ans1), detect(ans2)

    if any(k in ans1 for k in ["정지", "머물러", "전기"]) and len(m1) > 0:
        score += 2; feedback.append("(1) 문장 정답 (+2점)")
    else: feedback.append("(1) 문장 오답: 정전기의 정의/특성 부족")

    if any(k in ans2 for k in ["흐르는 물", "고여 있는 물", "전하"]) and len(m2) > 0:
        score += 2; feedback.append("(2) 문장 정답 (+2점)")
    else: feedback.append("(2) 문장 오답: 비유 및 대조 설명 방식 부족")
    return score, feedback

def grade_set2_q3(vp, ve, ap, ae):
    score, feedback = 0, []
    if any(k in vp for k in ["높은", "고여", "수조", "떨어지지"]):
        if any(k in ve for k in ["이동하지", "위험하지"]):
            score += 3; feedback.append("시각 요소 정답 (+3점)")
        else: score += 1.5; feedback.append("시각 요소 부분 점수 (+1.5점): 효과 근거 작성 부족")
    else: feedback.append("시각 요소 오답: 고여 있는 물 연출 미흡")

    if any(k in ap for k in ["고요", "정적", "소리 없", "잔잔"]):
        if any(k in ae for k in ["대조", "머물러", "이동하지"]):
            score += 3; feedback.append("청각 요소 정답 (+3점)")
        else: score += 1.5; feedback.append("청각 요소 부분 점수 (+1.5점): 효과 근거 작성 부족")
    else: feedback.append("청각 요소 오답: 실생활 전기와 대조되는 정적 미흡")
    return score, feedback


# --- [세트 3] 채점 함수 ---
def grade_set3_q1(ans1, ans2, ans3):
    score, feedback = 0, []
    if any(k in ans1 for k in ["로봇", "피겨"]):
        score += 2; feedback.append("(1) 정답 (+2점)")
    else: feedback.append("(1) 오답: '로봇의 피겨 스케이팅' 비유 대상 누락")

    if any(k in ans2 for k in ["감정", "철학", "이야기", "경험"]) and any(k in ans2 for k in ["어렵", "아니다"]):
        score += 2; feedback.append("(2) 정답 (+2점)")
    else: feedback.append("(2) 오답: 감정/철학의 부재 근거 작성 미흡")

    if any(k in ans3 for k in ["변화", "확장", "범주", "상징"]):
        score += 2; feedback.append("(3) 정답 (+2점)")
    else: feedback.append("(3) 오답: AI 미술의 상징적 가치/범주 확장 서술 미흡")
    return score, feedback

def grade_set3_q2(ans1, ans2):
    score, feedback = 0, []
    methods = {"예시": ["올림픽", "선수"], "비교": ["처럼", "듯"], "대조": ["달리", "반면"]}
    detect = lambda t: [m for m, kws in methods.items() if f"({m})" in t or any(k in t for k in kws)]
    m1, m2 = detect(ans1), detect(ans2)

    if any(k in ans1 for k in ["노력", "감정", "경험", "작가"]) and len(m1) > 0:
        score += 2; feedback.append("(1) 문장 정답 (+2점)")
    else: feedback.append("(1) 문장 오답: 인간 예술의 특성 서술 부족")

    if any(k in ans2 for k in ["범주", "가치", "한계", "철학"]) and len(m2) > 0:
        score += 2; feedback.append("(2) 문장 정답 (+2점)")
    else: feedback.append("(2) 문장 오답: AI 예술의 가치 및 대조 설명 부족")
    return score, feedback

def grade_set3_q3(vp, ve, ap, ae):
    score, feedback = 0, []
    if any(k in vp for k in ["고뇌", "노력", "눈물", "감격", "고민"]):
        if any(k in ve for k in ["감정", "철학", "경험", "울림"]):
            score += 3; feedback.append("시각 요소 정답 (+3점)")
        else: score += 1.5; feedback.append("시각 요소 부분 점수 (+1.5점): 효과 서술 근거 부족")
    else: feedback.append("시각 요소 오답: 인간의 감정/고뇌 표현 연출 미흡")

    if any(k in ap for k in ["숨소리", "오케스트라", "클래식", "서정"]):
        if any(k in ae for k in ["울림", "공감", "대조"]):
            score += 3; feedback.append("청각 요소 정답 (+3점)")
        else: score += 1.5; feedback.append("청각 요소 부분 점수 (+1.5점): 효과 서술 근거 부족")
    else: feedback.append("청각 요소 오답: 장면 1과 대비되는 감정 음향 미흡")
    return score, feedback


# ==========================================
# 3. UI 탭 화면 구성
# ==========================================

st.title("📝 서논술형 답안 작성 및 자동 채점 시스템")

tab1, tab2, tab3 = st.tabs(["[세트 1] 사회적 촉진/억제", "[세트 2] 정전기 특징", "[세트 3] AI와 예술"])

# ------------------------------------------
# TAB 1: 1번 세트
# ------------------------------------------
with tab1:
    st.markdown("""
    <div class="blue-box">
        <h4>📖 [지문 자료]</h4>
        <p><b>기자:</b> 심리학 용어인 '사회적 촉진'과 '사회적 억제'를 일상생활, 특히 우리의 학습에 어떻게 적용할 수 있을까요?</p>
        <p><b>전문가:</b> 이 두 가지 개념을 알면 상황에 맞춰 유용하게 활용할 수 있습니다. 예를 들어, 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제를 할 때는 어떨까요?</p>
        <p><b>기자:</b> 음, 그냥 집에서 편하게 혼자 하는 게 집중이 잘되지 않을까요?</p>
        <p><b>전문가:</b> 그렇지 않습니다. 오히려 집에서 혼자 하는 것보다는 커피숍이나 도서관에서 하는 것이 더 효율적일 수 있습니다. 평소 친숙하고 좋아하는 과목이라면 공부 모임을 만들어 다른 사람들과 함께 공부하는 것도 좋은 방법이죠.</p>
        <p><b>기자:</b> 그렇다면 어렵고 복잡한 과제를 할 때는 어떻게 해야 하나요?</p>
        <p><b>전문가:</b> 그럴 때는 반대입니다. 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가지는 것이 좋습니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # [서·논술형 1]
    st.subheader("[서·논술형 1]")
    st.write("윗글을 요약하여 표로 정리하였다. (1)~(3)에 들어갈 내용을 찾아 쓰시오.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("** (1) 과제의 특성 **")
        s1_q1_1 = st.text_input("lbl_s1_q1_1", label_visibility="collapsed", key="s1_q1_1")
    with c2:
        st.markdown("** (2) 효율적인 환경 및 방법 **")
        s1_q1_2 = st.text_input("lbl_s1_q1_2", label_visibility="collapsed", key="s1_q1_2")
    with c3:
        st.markdown("** (3) 관련된 심리 현상 **")
        s1_q1_3 = st.text_input("lbl_s1_q1_3", label_visibility="collapsed", key="s1_q1_3")

    st.divider()

    # [서·논술형 2]
    st.subheader("[서·논술형 2]")
    st.write("윗글을 활용하여 '과제 난이도에 따른 효율적인 학습 전략'에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 <조건>에 맞추어 작성하시오.")
    st.info("<b>주어진 첫 문장:</b> 과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.", icon="✍️")
    st.markdown("""
    <div class="gray-box">
        <b><i style="color: #d92d20;">📌 [작성 조건]</i></b><br>
        ⚠️ 서로 다른 2가지의 설명 방법을 사용하여, 주어진 문장에 이어지는 문장을 (1), (2)에 각각 하나씩 작성할 것.<br>
        ⚠️ 윗글에 제시된 내용만을 활용하여 문장을 구성할 것. (지문에 없는 외부 배경지식을 활용할 경우 인정하지 않음)<br>
        ⚠️ 각 문장의 끝에 자신이 사용한 설명 방법의 명칭을 괄호에 넣어 표기할 것.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("** (1) 문장 작성 **")
    s1_q2_1 = st.text_area("lbl_s1_q2_1", label_visibility="collapsed", key="s1_q2_1")
    st.markdown("** (2) 문장 작성 **")
    s1_q2_2 = st.text_area("lbl_s1_q2_2", label_visibility="collapsed", key="s1_q2_2")

    st.divider()

    # [서·논술형 3]
    st.subheader("[서·논술형 3]")
    st.write("윗글을 바탕으로 '상황에 맞는 학습 공간 선택법'을 설명하는 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
    st.markdown("""
    <div class="blue-box">
        <h4>🎬 [영상 기획안]</h4>
        <p><b>주제:</b> 사회적 촉진과 억제를 활용한 스마트한 공부법</p>
        <p><b>[장면 1] 쉬운 과제를 할 때</b><br>
        - 시각 요소: 백색소음이 있는 밝은 도서관에서 친구들과 가볍게 미소 지으며 공부하는 학생들의 모습을 넓은 화면(풀샷)으로 보여줌.<br>
        - 청각 요소: 경쾌하고 리듬감 있는 배경음악과 함께 사람들의 가벼운 발소리와 책장 넘기는 소리를 깔아줌</p>
        <p><b>[장면 2] 어려운 과제를 할 때</b><br>
        - 시각 요소 (Ⓐ): <i>[작성 내용]</i><br>
        - 청각 요소 (Ⓑ): <i>[작성 내용]</i></p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="gray-box">
        <b><i style="color: #d92d20;">📌 [작성 조건]</i></b><br>
        ⚠️ 윗글을 참고하여 어려운 과제를 할 때 필요한 환경의 특성이 잘 드러나도록 Ⓐ와 Ⓑ에 들어갈 연출 계획을 세울 것.<br>
        ⚠️ 자신이 설정한 시각/청각 요소가 글의 내용을 전달하는 데 어떤 효과가 있는지 각각 서술할 것.
    </div>
    """, unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown("** (1) 시각 요소 연출 (Ⓐ) **")
        s1_q3_vp = st.text_input("lbl_s1_q3_vp", label_visibility="collapsed", key="s1_q3_vp")
        st.markdown("** 시각 요소의 효과 **")
        s1_q3_ve = st.text_area("lbl_s1_q3_ve", label_visibility="collapsed", key="s1_q3_ve")
    with cb:
        st.markdown("** (2) 청각 요소 연출 (Ⓑ) **")
        s1_q3_ap = st.text_input("lbl_s1_q3_ap", label_visibility="collapsed", key="s1_q3_ap")
        st.markdown("** 청각 요소의 효과 **")
        s1_q3_ae = st.text_area("lbl_s1_q3_ae", label_visibility="collapsed", key="s1_q3_ae")

    st.write("")
    if st.button("세트 1 제출 및 채점하기", type="primary", key="btn_s1"):
        s1, f1 = grade_set1_q1(s1_q1_1, s1_q1_2, s1_q1_3)
        s2, f2 = grade_set1_q2(s1_q2_1, s1_q2_2)
        s3, f3 = grade_set1_q3(s1_q3_vp, s1_q3_ve, s1_q3_ap, s1_q3_ae)
        st.success(f"🎉 [세트 1] 총점: {s1 + s2 + s3} / 16점")
        with st.expander("🔍 세트 1 피드백 확인", expanded=True):
            for f in f1 + f2 + f3: st.write(f"- {f}")


# ------------------------------------------
# TAB 2: 2번 세트
# ------------------------------------------
with tab2:
    st.markdown("""
    <div class="blue-box">
        <h4>📖 [지문 자료]</h4>
        <p><b>기자:</b> 겨울철 불청객인 '정전기'란 정확히 무엇인지 설명 부탁드립니다.</p>
        <p><b>전문가:</b> 정전기란 전하가 정지 상태로 있어 그 분포가 시간적으로 변화하지 않는 전기, 그리고 그로 인한 전기 현상을 말합니다. 쉽게 설명하면 흐르지 않고 머물러 있는 전기라고 해서 "움직이지 아니하여 조용하다."는 뜻을 가진 한자 '정(靜)'을 써서 정전기라고 부르는 것이죠.</p>
        <p><b>기자:</b> 우리가 실생활에서 쓰는 전기와는 어떻게 다른가요? 물에 비유해서 설명해 주시면 이해가 쉬울 것 같습니다.</p>
        <p><b>전문가:</b> 아주 좋은 비유가 될 수 있습니다. 우리가 실생활에서 쓰는 전기가 '흐르는 물'이라면, 정전기는 '높은 곳에 고여 있는 물'이라고 할 수 있습니다.</p>
        <p><b>기자:</b> 정전기가 일어날 때 찌릿한 느낌이 드는데, 혹시 위험하지는 않은가요?</p>
        <p><b>전문가:</b> 정전기의 전압은 매우 높지만, 우리가 실생활에서 쓰는 전기와는 다르게 전하가 이동하지 않고 머물러 있어 위험하지는 않습니다. 어마어마하게 높은 곳에 고여 있는 물이지만 떨어지지 않고 있어서 별 피해가 없는 것과 같다고 이해하시면 됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # [서·논술형 1]
    st.subheader("[서·논술형 1]")
    st.write("윗글을 요약하여 표로 정리하였다. (1)~(3)에 들어갈 내용을 찾아 쓰시오.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("** (1) 정전기의 물의 상태 비유 **")
        s2_q1_1 = st.text_input("lbl_s2_q1_1", label_visibility="collapsed", key="s2_q1_1")
    with c2:
        st.markdown("** (2) 정전기의 전하 상태 **")
        s2_q1_2 = st.text_input("lbl_s2_q1_2", label_visibility="collapsed", key="s2_q1_2")
    with c3:
        st.markdown("** (3) 정전기의 위험성 **")
        s2_q1_3 = st.text_input("lbl_s2_q1_3", label_visibility="collapsed", key="s2_q1_3")

    st.divider()

    # [서·논술형 2]
    st.subheader("[서·논술형 2]")
    st.write("윗글을 활용하여 '정전기의 특징'에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 <조건>에 맞추어 작성하시오.")
    st.info("<b>주어진 첫 문장:</b> 겨울철에 흔히 겪는 정전기는 우리가 평소 집에서 사용하는 전기와는 다른 뚜렷한 특징이 있다.", icon="✍️")
    st.markdown("""
    <div class="gray-box">
        <b><i style="color: #d92d20;">📌 [작성 조건]</i></b><br>
        ⚠️ 주어진 문장에 이어지는 문장을 (1), (2)에 각각 하나씩 작성할 것. (1)과 (2)에는 서로 다른 설명 방법이 1가지 이상 활용되어야 하며, 각 문장에 사용된 설명 방법의 명칭을 괄호에 넣어 문장 끝에 기재할 것.<br>
        ⚠️ 윗글에 제시된 내용만을 활용하여 문장을 구성할 것.<br>
        ⚠️ (1)과 (2)가 논리적 흐름을 갖고 이어지도록 할 것.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("** (1) 문장 작성 **")
    s2_q2_1 = st.text_area("lbl_s2_q2_1", label_visibility="collapsed", key="s2_q2_1")
    st.markdown("** (2) 문장 작성 **")
    s2_q2_2 = st.text_area("lbl_s2_q2_2", label_visibility="collapsed", key="s2_q2_2")

    st.divider()

    # [서·논술형 3]
    st.subheader("[서·논술형 3]")
    st.write("윗글을 바탕으로 '정전기의 특징'을 설명하는 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
    st.markdown("""
    <div class="blue-box">
        <h4>🎬 [영상 기획안]</h4>
        <p><b>주제:</b> 전압은 높지만 위험하지 않은 정전기의 비밀</p>
        <p><b>[장면 1] 실생활 전기 (흐르는 물)</b><br>
        - 시각 요소: 거대한 폭포수가 콸콸 쏟아져 내려오며 물레방아를 힘차게 돌리는 역동적인 그래픽을 보여줌.<br>
        - 청각 요소: 물이 거세게 부딪히는 웅장하고 큰 소리를 배경음으로 사용함.</p>
        <p><b>[장면 2] 정전기 (고여 있는 물)</b><br>
        - 시각 요소 (Ⓐ): <i>[작성 내용]</i><br>
        - 청각 요소 (Ⓑ): <i>[작성 내용]</i></p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="gray-box">
        <b><i style="color: #d92d20;">📌 [작성 조건]</i></b><br>
        ⚠️ 윗글을 바탕으로 정전기의 특성이 잘 드러나도록 Ⓐ와 Ⓑ에 들어갈 연출 계획을 세울 것.<br>
        ⚠️ 설정한 시각 및 청각 요소의 연출 효과를 각각 서술하되, 반드시 윗글의 내용을 근거로 포함할 것.
    </div>
    """, unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown("** (1) 시각 요소 연출 (Ⓐ) **")
        s2_q3_vp = st.text_input("lbl_s2_q3_vp", label_visibility="collapsed", key="s2_q3_vp")
        st.markdown("** 시각 요소의 효과 **")
        s2_q3_ve = st.text_area("lbl_s2_q3_ve", label_visibility="collapsed", key="s2_q3_ve")
    with cb:
        st.markdown("** (2) 청각 요소 연출 (Ⓑ) **")
        s2_q3_ap = st.text_input("lbl_s2_q3_ap", label_visibility="collapsed", key="s2_q3_ap")
        st.markdown("** 청각 요소의 효과 **")
        s2_q3_ae = st.text_area("lbl_s2_q3_ae", label_visibility="collapsed", key="s2_q3_ae")

    st.write("")
    if st.button("세트 2 제출 및 채점하기", type="primary", key="btn_s2"):
        s1, f1 = grade_set2_q1(s2_q1_1, s2_q1_2, s2_q1_3)
        s2, f2 = grade_set2_q2(s2_q2_1, s2_q2_2)
        s3, f3 = grade_set2_q3(s2_q3_vp, s2_q3_ve, s2_q3_ap, s2_q3_ae)
        st.success(f"🎉 [세트 2] 총점: {s1 + s2 + s3} / 16점")
        with st.expander("🔍 세트 2 피드백 확인", expanded=True):
            for f in f1 + f2 + f3: st.write(f"- {f}")


# ------------------------------------------
# TAB 3: 3번 세트
# ------------------------------------------
with tab3:
    st.markdown("""
    <div class="blue-box">
        <h4>📖 [지문 자료]</h4>
        <p><b>기자:</b> 최근 생성형 인공 지능이 그린 그림이 미술계에서 큰 화제를 모으고 있습니다. 어떤 작품인지 소개해 주실 수 있을까요?</p>
        <p><b>전문가:</b> 네, 대표적으로 「에드몽 드 벨라미」라는 작품이 있습니다. 이 작품은 14~20세기에 그려진 초상화 1만 5,000점을 토대로 알고리즘과 데이터를 사용해 그려졌습니다. 뉴욕 크리스티 경매에서 최종 낙찰가 43만 2,000달러에 판매되어 큰 놀라움을 주었죠.</p>
        <p><b>기자:</b> 그렇다면 이 그림을 인간이 만든 예술 작품과 같다고 볼 수 있을까요?</p>
        <p><b>전문가:</b> 올림픽 경기를 예로 들어 볼게요. 우리가 올림픽에 열광하는 이유는 선수들이 경기를 위해 기울인 노력이나 열정을 알기 때문입니다. 반면 로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 해내더라도 우리의 마음을 울리지는 못하지요. 이처럼 인간의 작품에는 작가의 고유한 감정이나 철학, 그리고 작가가 살아온 삶의 경험, 세상을 바라보는 관점, 그를 둘러싼 환경 같은 내외부적인 요소가 종합적으로 담겨 있으므로 예술로 볼 수 있습니다. 하지만 인공 지능은 감정도 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 이를 예술로 보기는 어렵습니다.</p>
        <p><b>기자:</b> 그렇다면 인공 지능이 그린 그림은 가치가 전혀 없는 것인가요?</p>
        <p><b>전문가:</b> 그렇지는 않습니다. 비록 인간과 같은 감정은 없더라도, 기존 미술계에 큰 변화를 가져왔다는 점에서 분명한 의미가 있습니다. 또한 앞으로 우리가 알고 있던 예술의 범주를 확장할 수 있다는 점에서 상징적인 가치를 지닙니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # [서·논술형 1]
    st.subheader("[서·논술형 1]")
    st.write("윗글을 요약하여 표로 정리하였다. (1)~(3)에 들어갈 내용을 찾아 쓰시오.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("** (1) AI 예술의 올림픽 비유 **")
        s3_q1_1 = st.text_input("lbl_s3_q1_1", label_visibility="collapsed", key="s3_q1_1")
    with c2:
        st.markdown("** (2) AI 예술로 볼 수 있는가 (근거) **")
        s3_q1_2 = st.text_input("lbl_s3_q1_2", label_visibility="collapsed", key="s3_q1_2")
    with c3:
        st.markdown("** (3) AI 예술로서의 가치 **")
        s3_q1_3 = st.text_input("lbl_s3_q1_3", label_visibility="collapsed", key="s3_q1_3")

    st.divider()

    # [서·논술형 2]
    st.subheader("[서·논술형 2]")
    st.write("윗글을 활용하여 '인공 지능이 그린 그림을 바라보는 시각'에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 <조건>에 맞추어 작성하시오.")
    st.info("<b>주어진 첫 문장:</b> 인공 지능이 그린 그림이 늘어나는 요즘, 우리는 이 작품들을 어떤 눈으로 바라봐야 할지 올바르게 생각해야 한다.", icon="✍️")
    st.markdown("""
    <div class="gray-box">
        <b><i style="color: #d92d20;">📌 [작성 조건]</i></b><br>
        ⚠️ 주어진 문장에 이어지는 문장을 (1), (2)에 각각 하나씩 작성할 것. (1)과 (2)에는 서로 다른 설명 방법이 1가지 이상 활용되어야 하며, 각 문장에 사용된 설명 방법의 명칭을 괄호에 넣어 문장 끝에 기재할 것.<br>
        ⚠️ 윗글에 제시된 내용만을 활용하여 문장을 구성할 것.<br>
        ⚠️ (1)과 (2)가 논리적 흐름을 갖고 이어지도록 할 것.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("** (1) 문장 작성 **")
    s3_q2_1 = st.text_area("lbl_s3_q2_1", label_visibility="collapsed", key="s3_q2_1")
    st.markdown("** (2) 문장 작성 **")
    s3_q2_2 = st.text_area("lbl_s3_q2_2", label_visibility="collapsed", key="s3_q2_2")

    st.divider()

    # [서·논술형 3]
    st.subheader("[서·논술형 3]")
    st.write("윗글을 바탕으로 '인공 지능이 그린 그림을 바라보는 시각'을 설명하는 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
    st.markdown("""
    <div class="blue-box">
        <h4>🎬 [영상 기획안]</h4>
        <p><b>주제:</b> 인간의 감정이 담긴 진정한 예술의 가치</p>
        <p><b>[장면 1] 감정이 없는 완벽한 기술</b><br>
        - 시각 요소: 로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 해내지만 우리의 마음을 울리지는 못하는 동영상을 보여줌.<br>
        - 청각 요소: 기계음이나 일정한 박자의 메트로놈 소리를 깔아 차갑고 정형화된 분위기를 조성함.</p>
        <p><b>[장면 2] 마음에 울림을 주는 진정한 예술</b><br>
        - 시각 요소 (Ⓐ): <i>[작성 내용]</i><br>
        - 청각 요소 (Ⓑ): <i>[작성 내용]</i></p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="gray-box">
        <b><i style="color: #d92d20;">📌 [작성 조건]</i></b><br>
        ⚠️ 윗글을 바탕으로 인간이 만들어내는 예술의 특성이 잘 드러나도록 Ⓐ와 Ⓑ에 들어갈 연출 계획을 세울 것.<br>
        ⚠️ 설정한 시각 및 청각 요소의 연출 효과를 각각 서술하되, 반드시 윗글의 내용을 근거로 포함할 것.
    </div>
    """, unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown("** (1) 시각 요소 연출 (Ⓐ) **")
        s3_q3_vp = st.text_input("lbl_s3_q3_vp", label_visibility="collapsed", key="s3_q3_vp")
        st.markdown("** 시각 요소의 효과 **")
        s3_q3_ve = st.text_area("lbl_s3_q3_ve", label_visibility="collapsed", key="s3_q3_ve")
    with cb:
        st.markdown("** (2) 청각 요소 연출 (Ⓑ) **")
        s3_q3_ap = st.text_input("lbl_s3_q3_ap", label_visibility="collapsed", key="s3_q3_ap")
        st.markdown("** 청각 요소의 효과 **")
        s3_q3_ae = st.text_area("lbl_s3_q3_ae", label_visibility="collapsed", key="s3_q3_ae")

    st.write("")
    if st.button("세트 3 제출 및 채점하기", type="primary", key="btn_s3"):
        s1, f1 = grade_set3_q1(s3_q1_1, s3_q1_2, s3_q1_3)
        s2, f2 = grade_set3_q2(s3_q2_1, s3_q2_2)
        s3, f3 = grade_set3_q3(s3_q3_vp, s3_q3_ve, s3_q3_ap, s3_q3_ae)
        st.success(f"🎉 [세트 3] 총점: {s1 + s2 + s3} / 16점")
        with st.expander("🔍 세트 3 피드백 확인", expanded=True):
            for f in f1 + f2 + f3: st.write(f"- {f}")
