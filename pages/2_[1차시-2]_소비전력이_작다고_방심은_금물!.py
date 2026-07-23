import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(page_title="활동 2: 소비전력이 작다고 방심은 금물!", layout="wide")

st.title("⚡ 활동 3. 소비전력이 작다고 방심은 금물!")
st.subheader("믿었던 TV의 배신...")

# 세션 상태 관리
if "activity2_submitted" not in st.session_state:
    st.session_state.activity2_submitted = False

if "activity2_reflection" not in st.session_state:
    st.session_state.activity2_reflection = ""

# -----------------------------------------------------------------------------
# 2. 반전 상황 제시 (도입 동기유발)
# -----------------------------------------------------------------------------
st.error("""
📢 **[고심이네 집 사건 발생!]**

 "TV는 소비전력이 엄청 작은 제품이었는데...

한 달 뒤 스마트 홈 앱의 **[가전별 전기에너지 소비 리포트]**를 보니 **TV로 쓴 전기에너지량이 엄청나네요.** 

대체 왜 이런 일이 일어났을까요?"
""")

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. Step 1: 사용 시간 조작 및 데이터 연산
# -----------------------------------------------------------------------------
st.markdown("### ⏱️ Step 1: 고심이네 집 가전제품 사용 시간 조작하기")
st.caption("슬라이더를 조작하여 각 가전제품의 하루 평균 사용 시간을 설정해보고, 어떤 결과가 나타나는지 확인해봅시다.")

col_in1, col_in2, col_in3, col_in4 = st.columns(4)

with col_in1:
    st.markdown("#### 💨 헤어드라이어")
    st.caption("소비전력: **1,300 W**")
    dryer_min = st.slider("하루 사용 시간 (분)", min_value=0, max_value=60, value=10, step=5, key="act2_dryer_min")
    dryer_hr = dryer_min / 60.0

with col_in2:
    st.markdown("#### 📺 TV")
    st.caption("소비전력: **150 W**")
    tv_hr = st.slider("하루 사용 시간 (시간)", min_value=0.0, max_value=12.0, value=4.0, step=0.5, key="act2_tv_hr")

with col_in3:
    st.markdown("#### 🌀 선풍기")
    st.caption("소비전력: **50 W**")
    fan_hr = st.slider("하루 사용 시간 (시간)", min_value=0.0, max_value=24.0, value=10.0, step=1.0, key="act2_fan_hr")
with col_in4:
    st.markdown("#### 🌀 폰 충전기")
    st.caption("소비전력: **25 W**")
    charger_hr = st.slider("하루 사용 시간 (시간)", min_value=0.0, max_value=24.0, value=10.0, step=1.0, key="act2_charger_hr")
# 🔬 전기에너지 연산 (kWh) = (W * h * 30일) / 1000
dryer_kwh = (1300 * dryer_hr * 30) / 1000.0
tv_kwh = (150 * tv_hr * 30) / 1000.0
fan_kwh = (50 * fan_hr * 30) / 1000.0
charger_kwh = (25 * charger_hr * 30) / 1000.0

act2_df = pd.DataFrame({
    "가전제품": ["헤어드라이어", "TV", "선풍기", "폰 충전기"],
    "소비전력(W)": [1300, 150, 50, 25],
    "하루 사용시간(시간)": [round(dryer_hr, 2), tv_hr, fan_hr, charger_hr],
    "월간 전기에너지(kWh)": [round(dryer_kwh, 2), round(tv_kwh, 2), round(fan_kwh, 2), round(charger_kwh, 2)]
})

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. Step 2: 반전 그래프 시각화 비교
# -----------------------------------------------------------------------------
st.markdown("### 📊 Step 2: 소비전력(W) vs 월간 전기에너지(kWh) 순위 대반전")

col_chart1, col_chart2 = st.columns(2)

color_map = {
    "헤어드라이어": "#FF4B4B", # 빨강 (단시간 고소비)
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
        title="<b>[차트 B] 실제 사용 시간(h)을 반영한 월간 전기에너지(kWh)</b>"
    )
    fig_kwh.update_traces(texttemplate='%{text:.2f} kWh', textposition='outside')
    fig_kwh.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_kwh, use_container_width=True)

# 💡 개념 정립 안내 상자


st.markdown("---")

# -----------------------------------------------------------------------------
# 5. Step 3: 데이터 탐구 소감 및 개념 정리
# -----------------------------------------------------------------------------
st.markdown("### 🔍 Step 3: 데이터 분석")

st.markdown("""
아래 질문에 대해 데이터에 기반하여 답을 작성해 봅시다.
1. 소비전력($W$)이 작아도 실제 전기에너지($kWh$)를 더 많이 쓰게 되는 이유는 무엇인가요?
2. 우리가 일상생활에서 전기에너지를 절약하기 위해서는 **가전 교체** 외에 **어떤 행동**을 실천해야 할까요?
""")

reflection_input = st.text_area(
    "나의 데이터 분석 및 소감 작성:",
    value=st.session_state.activity2_reflection,
    height=50,
    placeholder="나의 생각을 적어봅시다.",
    key="act2_reflection_input"
)
st.session_state.activity2_reflection = reflection_input

if st.button("✅ 활동 2 작성 완료", type="primary", use_container_width=True):
    if reflection_input.strip():
        st.session_state.activity2_submitted = True
        st.success("🎉 활동 2 완료!")
        st.balloons()
    else:
        st.error("⚠️ 분석 소감을 작성한 후 완료 버튼을 눌러주세요.")

st.markdown("---")