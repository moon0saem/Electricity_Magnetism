import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 페이지 및 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="2차시-2: 나의 에너지 다이어트 계획 세우기", layout="wide")

st.title("🍃 [활동 2] 나의 에너지 다이어트 계획 세우기")

st.markdown("""
### 📖 활동 소개
소비전력($W$)과 사용 시간($h$)이 만나 전기에너지 사용량($kWh$)이 결정되는 것을 알았어요 !  
에너지는 무한하지 않으므로, 아끼는 것이 중요하다고 했는데... 구체적으로 어떻게 절약할 수 있을까요?  
나의 생활 데이터를 입력하고, 목표를 설정하여 **돈을 들이지 않고도 실천할 수 있는 나만의 에너지 다이어트 계획**을 세워봅시다.
""")

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. 고심이네/나의 현재 사용 현황 입력 (Step 1: Before 진단)
# -----------------------------------------------------------------------------
st.markdown("#### ⚙️ Step 1: 나의 현재 전기에너지 소비 현황 (Before)")
st.caption("나의 평소 생활 습관 수치를 설정해 보세요.")

col_b1, col_b2, col_b3, col_b4 = st.columns(4)

with col_b1:
    st.markdown("##### ❄️ 에어컨 설정")
    outdoor_temp = st.number_input("여름철 야외 기온 (°C)", value=33, step=1)
    ac_temp_before = st.slider("현재 에어컨 설정 온도 (°C)", 18, 26, 22)
    ac_hours_before = st.slider("하루 에어컨 가동 시간 (시간)", 0.0, 15.0, 5.0, step=0.5)

with col_b2:
    st.markdown("##### 🧊 냉장고 설정")
    room_temp = st.number_input("실내 온도 (°C)", value=28, step=1)
    ref_grade = st.selectbox("냉장고 에너지효율등급", options=[1, 2, 3, 4, 5], index=2)
    door_open_before = st.slider("하루 냉장고 문 여는 횟수 (회)", 0, 40, 20)

with col_b3:
    st.markdown("##### 🖥️ PC/TV & 드라이어")
    pc_hours_before = st.slider("하루 PC/TV 사용 시간 (시간)", 0.0, 12.0, 4.0, step=0.5)
    dryer_min_before = st.slider("하루 드라이어 사용 시간 (분)", 0, 60, 12, step=2)

with col_b4:
    st.markdown("##### 🔌 대기전력이 높은 가전")
    standby_selected_before = st.multiselect(
        "대기전력이란? 전자기기가 콘센트에 꽂혀만 있고 꺼진 상태에서도 기기가 소비하는 전력",
        options=["셋톱박스 (12.3W)", "전자레인지 (2.2W)", "인덕션 (1.5W)", "전기밥솥 (3.5W)"],
        default=["셋톱박스 (12.3W)", "전자레인지 (2.2W)", "전기밥솥 (3.5W)"]
    )

# -----------------------------------------------------------------------------
# 3. [과학적 연산 로직] Before 상태 계산
# -----------------------------------------------------------------------------
# 상수
CO2_PER_KWH = 0.478         # 전력 탄소배출계수 (kgCO2/kWh)
COST_PER_KWH = 200          # 평균 전력 단가 (원/kWh)
TREE_CO2_YEAR = 6.6         # 소나무 1그루당 연간 CO2 흡수량 (kg)
REF_GRADE_WH = {1: 19.7, 2: 25.1, 3: 20.7, 4: 20.7, 5: 17.1}
STANDBY_W_DICT = {"셋톱박스 (12.3W)": 12.3, "전자레인지 (2.2W)": 2.2, "인덕션 (1.5W)": 1.5, "전기밥솥 (3.5W)": 3.5}

# 냉장고 열유입 연산 (Q = V * rho * cp * dT / COP)
dT_ref = max(1, room_temp - 4)
wh_per_open = (0.5 * 0.6 * 1.205 * 1005 * dT_ref / 2.0) / 3600.0
ref_wh_base = REF_GRADE_WH.get(ref_grade, 20.7)
ref_kwh_before = ((ref_wh_base * 24 * 30) + (wh_per_open * door_open_before * 30)) / 1000.0

# 에어컨 연산 (Q_cooling = k * Delta T)
dT_ac_before = max(1, outdoor_temp - ac_temp_before)
ac_power_base = 1800  # 스탠드 에어컨 기준
ac_kwh_before = (ac_power_base * ac_hours_before * 30) / 1000.0

# PC 및 드라이어 연산
pc_kwh_before = (250 * pc_hours_before * 30) / 1000.0
dryer_kwh_before = (1600 * (dryer_min_before / 60.0) * 30) / 1000.0

# 대기전력 연산 (P = V * I)
total_standby_w_before = sum([STANDBY_W_DICT[dev] for dev in standby_selected_before])
standby_kwh_before = (total_standby_w_before * 24 * 30) / 1000.0

# Before 총합
total_kwh_before = ref_kwh_before + ac_kwh_before + pc_kwh_before + dryer_kwh_before + standby_kwh_before
total_co2_before = total_kwh_before * CO2_PER_KWH
total_cost_before = total_kwh_before * COST_PER_KWH

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. 탄소 다이어트 미션 조작 (Step 2: Simulation)
# -----------------------------------------------------------------------------
st.markdown("#### 🎯 Step 2: 나만의 에너지 다이어트 시뮬레이션 (After)")
st.caption("아래 행동 미션을 슬라이더와 체크박스로 조작하며 과학적 감축 효과를 확인하세요!")

col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown("##### 🔬 [미션 A & B] 온도 조절 및 습관 개선")
    
    # 미션 1: 에어컨 온도 높이기
    m1_ac_temp = st.slider(
        "✅ [미션 1] 에어컨 설정 온도 높이기 (°C)",
        min_value=ac_temp_before, max_value=28, value=max(ac_temp_before, 26)
    )
    m1_ac_hours = st.slider(
        "✅ [미션 1-2] 에어컨 사용 시간 줄이기 (시간)",
        0.0, ac_hours_before, max(0.0, ac_hours_before - 1.0), step=0.5
    )
    
    # 미션 2: 냉장고 문 여는 횟수 줄이기
    m2_door_open = st.slider(
        "✅ [미션 2] 냉장고 문 여는 횟수 줄이기 (회)",
        0, door_open_before, int(door_open_before * 0.5)
    )

with col_m2:
    st.markdown("##### 🔬 [미션 C & D] 시간 단축 및 대기전력 차단")
    
    # 미션 3: PC/TV 사용 시간 줄이기
    m3_pc_hours = st.slider(
        "✅ [미션 3] PC/TV 사용 시간 줄이기 (시간)",
        0.0, pc_hours_before, max(0.0, pc_hours_before - 1.0), step=0.5
    )
    
    # 미션 4: 대기전력 차단 멀티탭 끄기
    m4_cut_standby = st.checkbox("✅ [미션 4] 자는 동안 대기전력 차단 멀티탭 전원 끄기", value=True)

# -----------------------------------------------------------------------------
# 5. [과학적 연산 로직] After 상태 연산
# -----------------------------------------------------------------------------
# 냉장고 After
ref_kwh_after = ((ref_wh_base * 24 * 30) + (wh_per_open * m2_door_open * 30)) / 1000.0

# 에어컨 After (온도차 비례 소비전력 감축 적용)
dT_ac_after = max(1, outdoor_temp - m1_ac_temp)
ac_power_after = ac_power_base * (dT_ac_after / dT_ac_before)
ac_kwh_after = (ac_power_after * m1_ac_hours * 30) / 1000.0

# PC 및 드라이어 After
pc_kwh_after = (250 * m3_pc_hours * 30) / 1000.0
dryer_kwh_after = dryer_kwh_before

# 대기전력 After
standby_kwh_after = 0.0 if m4_cut_standby else standby_kwh_before

# After 총합
total_kwh_after = ref_kwh_after + ac_kwh_after + pc_kwh_after + dryer_kwh_after + standby_kwh_after
total_co2_after = total_kwh_after * CO2_PER_KWH
total_cost_after = total_kwh_after * COST_PER_KWH

# 감축량 계산
co2_saved = total_co2_before - total_co2_after
kwh_saved = total_kwh_before - total_kwh_after
cost_saved = total_cost_before - total_cost_after
trees_planted = (co2_saved * 12) / TREE_CO2_YEAR
reduction_rate = (co2_saved / total_co2_before) * 100 if total_co2_before > 0 else 0

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. 시뮬레이션 결과 리포트 (Step 3: After 결과)
# -----------------------------------------------------------------------------
st.markdown("#### 📊 Step 3: 시뮬레이션 결과 및 환경 환산 리포트")

r1, r2, r3, r4 = st.columns(4)
r1.metric("🟢 다이어트 후 탄소 배출량", f"{total_co2_after:.1f} kgCO₂", f"-{co2_saved:.1f} kgCO₂")
r2.metric("📉 탄소 감축률", f"{reduction_rate:.1f} %")
r3.metric("💰 월간 절약 전기요금", f"{int(cost_saved):,} 원")
r4.metric("🌳 연간 소나무 심기 효과", f"{trees_planted:.1f} 그루")

# Before vs After 비교 차트
col_c1, col_c2 = st.columns([2, 1])

with col_c1:
    chart_df = pd.DataFrame({
        "구분": ["다이어트 전 (Before)", "다이어트 후 (After)"],
        "탄소 배출량 (kgCO2)": [total_co2_before, total_co2_after],
        "전기에너지 (kWh)": [total_kwh_before, total_kwh_after]
    })
    
    fig = px.bar(
        chart_df,
        x="구분",
        y="탄소 배출량 (kgCO2)",
        color="구분",
        text="탄소 배출량 (kgCO2)",
        title="<b>월간 탄소 배출량 비교 (Before vs After)</b>",
        color_discrete_sequence=["#FF4B4B", "#6BCB77"]
    )
    fig.update_traces(texttemplate='%{text:.1f} kgCO₂', textposition='outside')
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_c2:
    st.markdown("##### 🔬 적용된 과학 원리")
    
    # 💡 [추가 위치] 냉장고 감축량 및 금액 데이터 계산
    ref_kwh_saved = ref_kwh_before - ref_kwh_after
    ref_cost_saved = ref_kwh_saved * COST_PER_KWH
    
    st.info(
        f"* **에어컨:** 온도차(ΔT)가 **{dT_ac_before}°C → {dT_ac_after}°C**로 줄어 소비전력 약 **{((ac_power_base - ac_power_after)/ac_power_base)*100:.1f}%** 절감!\n"
        f"* **냉장고:** 문 여는 횟수를 **{door_open_before}회 → {m2_door_open}회**로 줄여 월간 전기에너지 **약 {ref_kwh_saved:.2f} kWh** ({int(ref_cost_saved):,}원) 절감!\n"
        f"* **대기전력:** 미세 누설전류 차단으로 **{total_standby_w_before:.1f}W** 완전 차단!"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. 나의 에너지 절약 다짐문 (Step 4: 포트폴리오 저장)
# -----------------------------------------------------------------------------
st.markdown("#### 📝 Step 4: 나의 에너지 절약 다짐문")

st.markdown("""
여러 가지 전기 기구와 시뮬레이션 결과를 참고하여, 내가 실천할 수 있는 에너지 절약 행동 목록을 작성해 봅시다.
""")

action_plan = st.text_area(
    "나의 실천 다짐 및 시뮬레이션 소감:",
    height=150,
    placeholder=f"예: 시뮬레이션을 돌려보니 에어컨 온도를 26도로 높이고 자는 동안 셋톱박스 플러그를 뽑는 것만으로도 월간 탄소를 {co2_saved:.1f}kg이나 줄일 수 있음을 알게 되었습니다. 오늘부터...",
    label_visibility="collapsed",
)