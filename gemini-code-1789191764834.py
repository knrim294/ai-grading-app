import re
import streamlit as st

# ==========================================
# 1. 커스텀 CSS (파란 상자 & 회색 상자 스타일)
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
    /* 입력창 간격 조절 */
    .stTextInput, .stTextArea {
        margin-top: -10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 채점 로직 정의
# ==========================================

def grade_set1_q1(ans1, ans2, ans3):
    score = 0
    feedback = []
    kw1 = ["쉬운", "노력", "친숙", "좋아하는"]
    if any(k in ans1 for k in kw1):
        score += 2
        feedback.append("(1) 정답 (+2점)")
    else:
        feedback.append("(1) 오답: '쉬운 과제' 또는 '친숙한 과목' 특성 미포함")

    kw2_pos = ["혼자", "차분", "집중", "익숙", "연습"]
    kw2_neg = ["함께", "모임", "친구", "도서관", "커피숍"]
    if any(k in ans2 for k in kw2_pos) and not any(k in ans2 for k in kw2_neg):
        score += 2
        feedback.append("(2) 정답 (+2점)")
    elif any(k in ans2 for k in kw2_neg):
        feedback.append("(2) 오답 (오개념): 어려운 과제에 '타인과 함께함' 특성 적용")
    else:
        feedback.append("(2) 오답: '혼자 차분히 집중함'의 의미 부족")

    if "사회적 억제" in ans3.replace(" ", ""):
        score += 2
        feedback.append("(3) 정답 (+2점)")
    else:
        feedback.append("(3) 오답: 정확한 학술 용어인 '사회적 억제' 미입력")

    return score, feedback

def grade_set1_q2(ans1, ans2):
    score = 0
    feedback = []
    methods = {
        "예시": ["예를 들어", "예컨대", "커피숍", "도서관", "모임"],
        "대조": ["반면", "반대에", "달리", "차분히 혼자"],
        "인과": ["때문에", "하므로", "효과적이다", "높일 수 있다"],
        "정의": ["란", "이란", "의미한다", "말한다"]
    }
    def detect_method(text):
        found = []
        for m, kws in methods.items():
            if f"({m})" in text or f"[{m}]" in text or any(k in text for k in kws):
                found.append(m)
        return found

    m1 = detect_method(ans1)
    m2 = detect_method(ans2)

    c1_pos = ["효과", "높이", "좋다", "함께", "도서관", "커피숍"]
    if any(k in ans1 for k in c1_pos) and len(m1) > 0:
        score += 2
        feedback.append("(1) 문장 정답 (+2점)")
    else:
        feedback.append("(1) 문장 감점/오답: 설명 방법 특성 미흡 또는 결론 미달성")

    c2_pos = ["혼자", "집중", "시간", "익숙"]
    if any(k in ans2 for k in c2_pos) and len(m2) > 0:
        if set(m1) == set(m2) and len(m1) == 1:
            score += 1
            feedback.append("(2) 문장 부분 점수 (+1점): (1)과 동일한 설명 방법 중복 사용")
        else:
            score += 2
            feedback.append("(2) 문장 정답 (+2점)")
    else:
        feedback.append("(2) 문장 오답: 어려운 과제 학습 전략 결론 미달성")

    return score, feedback

def grade_set1_q3(vis_plan, vis_eff, aud_plan, aud_eff):
    score = 0
    feedback = []
    if any(k in vis_plan for k in ["혼자", "단독", "개인", "몰입"]) and not any(k in vis_plan for k in ["함께", "여럿", "친구"]):
        if any(k in vis_eff for k in ["어려운", "도전", "혼자", "집중"]):
            score += 3
            feedback.append("시각 요소 연출 및 효과 정답 (+3점)")
        else:
            score += 1.5
            feedback.append("시각 요소 부분 점수 (+1.5점): 연출은 적절하나 효과 서술 근거 부족")
    else:
        feedback.append("시각 요소 오답: '혼자 집중하는 환경' 연출 미흡 또는 오개념 포함")

    if any(k in aud_plan for k in ["정적", "최소", "배제", "소음", "연필", "잔잔", "조용한"]):
        if any(k in aud_eff for k in ["차단", "안정", "집중", "차분"]):
            score += 3
            feedback.append("청각 요소 연출 및 효과 정답 (+3점)")
        else:
            score += 1.5
            feedback.append("청각 요소 부분 점수 (+1.5점): 연출은 적절하나 효과 서술 근거 부족")
    else:
        feedback.append("청각 요소 오답: 정적 연출 미흡")

    return score, feedback

# ==========================================
# 3. UI 구성
# ==========================================

st.title("📝 서논술형 답안 작성 및 자동 채점 시스템")

tab1, tab2, tab3 = st.tabs(["[세트 1] 사회적 촉진/억제", "[세트 2] 정전기 특징", "[세트 3] AI와 예술"])

with tab1:
    # 자료 영역 (파란 상자)
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

    # --------------------------------------
    # 문항 1
    # --------------------------------------
    st.subheader("[서·논술형 1]")
    st.write("윗글을 요약하여 표로 정리하였다. (1)~(3)에 들어갈 내용을 찾아 쓰시오.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("** (1) 과제의 특성 **")
        ans1_1 = st.text_input("s1_1_input", label_visibility="collapsed", key="s1_1")
    with col2:
        st.markdown("** (2) 효율적인 환경 및 방법 **")
        ans1_2 = st.text_input("s1_2_input", label_visibility="collapsed", key="s1_2")
    with col3:
        st.markdown("** (3) 관련된 심리 현상 **")
        ans1_3 = st.text_input("s1_3_input", label_visibility="collapsed", key="s1_3")

    st.divider()

    # --------------------------------------
    # 문항 2
    # --------------------------------------
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
    ans2_1 = st.text_area("s1_2_1_input", label_visibility="collapsed", key="s1_2_1")

    st.markdown("** (2) 문장 작성 **")
    ans2_2 = st.text_area("s1_2_2_input", label_visibility="collapsed", key="s1_2_2")

    st.divider()

    # --------------------------------------
    # 문항 3
    # --------------------------------------
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

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("** (1) 시각 요소 연출 (Ⓐ) **")
        ans3_vp = st.text_input("s1_3_vp_input", label_visibility="collapsed", key="s1_3_vp")
        
        st.markdown("** 시각 요소의 효과 **")
        ans3_ve = st.text_area("s1_3_ve_input", label_visibility="collapsed", key="s1_3_ve")

    with col_b:
        st.markdown("** (2) 청각 요소 연출 (Ⓑ) **")
        ans3_ap = st.text_input("s1_3_ap_input", label_visibility="collapsed", key="s1_3_ap")
        
        st.markdown("** 청각 요소의 효과 **")
        ans3_ae = st.text_area("s1_3_ae_input", label_visibility="collapsed", key="s1_3_ae")

    # 제출 버튼
    st.write("")
    if st.button("제출 및 채점하기", type="primary", key="btn_s1"):
        s1, f1 = grade_set1_q1(ans1_1, ans1_2, ans1_3)
        s2, f2 = grade_set1_q2(ans2_1, ans2_2)
        s3, f3 = grade_set1_q3(ans3_vp, ans3_ve, ans3_ap, ans3_ae)
        total = s1 + s2 + s3

        st.success(f"🎉 채점 완료! 총점: {total} / 16점")
        
        with st.expander("🔍 상세 피드백 확인하기", expanded=True):
            st.write("**[서·논술형 1]**")
            for f in f1: st.write(f"- {f}")
            st.write("**[서·논술형 2]**")
            for f in f2: st.write(f"- {f}")
            st.write("**[서·논술형 3]**")
            for f in f3: st.write(f"- {f}")

with tab2:
    st.info("2번 세트도 동일하게 라벨이 숨겨진 밀착 입력창 레이아웃이 적용됩니다.")

with tab3:
    st.info("3번 세트도 동일하게 라벨이 숨겨진 밀착 입력창 레이아웃이 적용됩니다.")
