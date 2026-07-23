import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(page_title="[2차시-1] 소비전력만 보고 판단할 수 있을까?", layout="wide")

st.title("⚡ 2차시-1: 소비전력만 보고 판단할 수 있을까?")

# 세션 상태 관리
if "activity2_submitted" not in st.session_state:
    st.session_state.activity2_submitted = False

if "activity2_expectation" not in st.session_state:
    st.session_state.activity2_expectation = ""

if "activity2_reflection" not in st.session_state:
    st.session_state.activity2_reflection = ""

# -----------------------------------------------------------------------------
# 2. 반전 상황 제시 (도입 동기유발)
# -----------------------------------------------------------------------------
st.markdown("""
### 📢 [생각 열기] **전기다리미의 반전?!**
전기다리미는 소비전력이 매우 큰 편이었어요.  
 그런데 스마트 홈 앱의 [가전별 전기에너지 소비 리포트]를 보니 **실제로 전기 다리미로 쓴 전기에너지량의 비중이 생각보다 크지 않은데요?**  
""")
st.image("data/report.png")
st.markdown("""
- 왜 그럴까요? 이유를 예상하여 적어봅시다.
""")

expectation_input = st.text_area(
    "나의 생각:",
    value=st.session_state.activity2_expectation,
    height=50,
    placeholder="왜 그럴까? 나의 생각을 적어봅시다.",
    key="act2_expectation_input",
    label_visibility="collapsed"
)
st.session_state.activity2_expectation = expectation_input

if st.button("✅ 작성 완료", use_container_width=True):
    if expectation_input.strip():
        st.session_state.activity2_submitted = True
    else:
        st.error("⚠️ 내용을 작성한 후 완료 버튼을 눌러주세요.")

if not st.session_state.activity2_submitted:
    st.stop()

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. Step 1: 사용 시간 조작 및 데이터 연산
# -----------------------------------------------------------------------------
st.markdown("#### ⏱️ Step 1: 고심이네 집 가전제품 사용 시간 조작하기")
st.caption("슬라이더를 조작하여 각 가전제품의 하루 평균 사용 시간을 설정해보고, 어떤 결과가 나타나는지 확인해봅시다.")

col_in1, col_in2, col_in3, col_in4 = st.columns(4)

with col_in1:
    st.markdown("#### ♨️ 전기다리미")
    st.caption("소비전력: **2,000 W**")
    dryer_min = st.slider("일주일 사용 시간 (분)", min_value=0, max_value=120, value=10, step=5, key="act2_dryer_min")
    dryer_hr = dryer_min / 60.0

with col_in2:
    st.markdown("#### 📺 TV")
    st.caption("소비전력: **80 W**")
    tv_hr = st.slider("하루 사용 시간 (시간)", min_value=0.0, max_value=12.0, value=4.0, step=0.5, key="act2_tv_hr")

with col_in3:
    st.markdown("#### 🌀 선풍기")
    st.caption("소비전력: **50 W**")
    fan_hr = st.slider("하루 사용 시간 (시간)", min_value=0.0, max_value=24.0, value=10.0, step=1.0, key="act2_fan_hr")
with col_in4:
    st.markdown("#### 🔌 폰 충전기")
    st.caption("소비전력: **25 W**")
    charger_hr = st.slider("하루 사용 시간 (시간)", min_value=0.0, max_value=24.0, value=10.0, step=1.0, key="act2_charger_hr")
# 🔬 전기에너지 연산 (kWh) = (W * h * 30일) / 1000
dryer_kwh = (2000 * dryer_hr * 4) / 1000.0
tv_kwh = (80 * tv_hr * 30) / 1000.0
fan_kwh = (50 * fan_hr * 30) / 1000.0
charger_kwh = (25 * charger_hr * 30) / 1000.0

act2_df = pd.DataFrame({
    "가전제품": ["전기다리미", "TV", "선풍기", "폰 충전기"],
    "소비전력(W)": [2000, 80, 50, 25],
    "하루 사용시간(시간)": [round(dryer_hr, 2), tv_hr, fan_hr, charger_hr],
    "월간 전기에너지(kWh)": [round(dryer_kwh, 2), round(tv_kwh, 2), round(fan_kwh, 2), round(charger_kwh, 2)]
})

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. Step 2: 반전 그래프 시각화 비교
# -----------------------------------------------------------------------------
st.markdown("#### 📊 Step 2: 소비전력 vs 전기에너지 사용량")

col_chart1, col_chart2 = st.columns(2)

color_map = {
    "전기다리미": "#FF4B4B", # 빨강 (단시간 고소비)
    "TV": "#1C83E1",       # 파랑 (장시간 중소비)
    "선풍기": "#6BCB77",        # 초록 (장시간 저소비)
    "폰 충전기": "#FFD700"       # 노랑 (장시간 극저소비)
}

with col_chart1:
    fig_w = px.bar(
        act2_df,
        x="가전제품",
        y="소비전력(W)",
        color="가전제품",
        color_discrete_map=color_map,
        text="소비전력(W)",
        title="<b>[차트 A] 단순 소비전력(W) 크기 순위</b>"
    )
    fig_w.update_traces(texttemplate='%{text} W', textposition='outside')
    fig_w.update_layout(height=400, showlegend=False, yaxis_range=[0, 1900])
    st.plotly_chart(fig_w, use_container_width=True)

with col_chart2:
    fig_kwh = px.bar(
        act2_df,
        x="가전제품",
        y="월간 전기에너지(kWh)",
        color="가전제품",
        color_discrete_map=color_map,
        text="월간 전기에너지(kWh)",
        title="<b>[차트 B] 실제 사용 시간(h)을 반영한 월간 전기에너지 사용량(kWh)</b>"
    )
    fig_kwh.update_traces(texttemplate='%{text:.2f} kWh', textposition='outside')
    fig_kwh.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_kwh, use_container_width=True)

# 💡 개념 정립 안내 상자

st.markdown("""
- 실제 전기에너지의 사용량은 소비전력($W$) 외에도 어떤 요소를 고려하는 것이 중요할까요?
""")

reflection_input = st.text_area(
    "어떤 점을 고려해야 할까?:",
    value=st.session_state.activity2_reflection,
    height=50,
    placeholder="나의 생각을 적어봅시다.",
    key="act2_reflection_input",
    label_visibility="collapsed",    
)
st.session_state.activity2_reflection = reflection_input

if st.button("✅ 작성 완료!", use_container_width=True):
    if reflection_input.strip():
        st.session_state.activity2_submitted = True
        st.success("🎉 학습지를 pdf로 저장하여 제출하세요.")
        st.balloons()
    else:
        st.error("⚠️ 내용을 작성한 후 완료 버튼을 눌러주세요.")

st.markdown("---")