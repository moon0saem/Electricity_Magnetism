import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 페이지 설정
st.set_page_config(page_title="활동 1: 전기제품 조사하기", layout="wide")

# 제목
st.title("🏠 활동 1. 고심이네 집 제품 조사하기")

# 활동 목표
st.markdown("""
### 📖 활동 소개
소비전력의 개념을 배운 고심이!
집에 있는 여러 전기제품들의 소비전력은 어떨까 조사해보려고 합니다.
고심이네 집의 전기제품들을 잘 살펴보고, 정리하여 어떤 특징이 있는지 알아봅시다.
""")

st.markdown("---")

# 세션 상태 초기화
if "appliance_data" not in st.session_state:
    st.session_state.appliance_data = pd.DataFrame({
        "전기 기구 종류": ["", "", ""],
        "전환되는 에너지": ["", "", ""],
        "소비전력(W)": [0, 0, 0]
    })

if "data_submitted" not in st.session_state:
    st.session_state.data_submitted = False

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""

if "analysis_submitted" not in st.session_state:
    st.session_state.analysis_submitted = False

# 입력 섹션
st.markdown("### 📝 Step 1: 제품 정보 입력하기")

edited_df = st.data_editor(
    st.session_state.appliance_data,
    num_rows="dynamic",
    key="appliance_input",
    column_config={
        "전기 기구 종류": st.column_config.TextColumn(
            "전기 기구 종류",
            help="예: 냉장고, 에어컨, 전자레인지 등"
        ),
        "전환되는 에너지": st.column_config.TextColumn(
            "전환되는 에너지",
            help="예: 열, 빛, 운동 등"
        ),
        "소비전력(W)": st.column_config.NumberColumn(
            "소비전력(W)",
            help="소비전력의 단위는 와트(W)입니다",
            format="%d"
        ),
    },
    use_container_width=True,
    height=300
)

st.session_state.appliance_data = edited_df

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("✅ 입력 완료", use_container_width=True):
        valid_data = edited_df[
            (edited_df["전기 기구 종류"].notna()) &
            (edited_df["전기 기구 종류"] != "") &
            (edited_df["전환되는 에너지"].notna()) &
            (edited_df["전환되는 에너지"] != "") &
            (edited_df["소비전력(W)"] > 0)
        ]

        if len(valid_data) > 0:
            st.session_state.data_submitted = True
            st.session_state.appliance_data = valid_data.reset_index(drop=True)
            st.success(f"✨ {len(valid_data)}개의 전기제품 정보가 저장되었습니다!")
        else:
            st.error("⚠️ 입력된 데이터가 없습니다. 전기 기구 정보를 입력해주세요.")

st.markdown("---")

# 그래프 시각화 섹션
if st.session_state.data_submitted and len(st.session_state.appliance_data) > 0:
    st.markdown("### 📊 Step 2: 제품별 소비전력 비교하기")

    energy_colors = {
        "열": "#FF6B6B",
        "빛": "#FFD93D",
        "운동": "#6BCB77",
        "음": "#4D96FF",
        "전기": "#FF8C42",
        "자기": "#9D84B7",
    }

    df = st.session_state.appliance_data.copy()
    fig = go.Figure()

    for energy_type in df["전환되는 에너지"].unique():
        energy_data = df[df["전환되는 에너지"] == energy_type]
        color = energy_colors.get(energy_type, "#95A5A6")

        fig.add_trace(go.Bar(
            x=energy_data["전기 기구 종류"],
            y=energy_data["소비전력(W)"],
            name=energy_type,
            marker_color=color,
            text=energy_data["소비전력(W)"],
            textposition="auto",
        ))

    fig.update_layout(
        title="제품별 소비전력 비교",
        xaxis_title="전기 기구",
        yaxis_title="소비전력 (W)",
        barmode="group",
        hovermode="x unified",
        height=400,
        showlegend=True,
        legend=dict(
            title="전환되는 에너지",
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

# 분석 결과 입력 섹션
if st.session_state.data_submitted:
    st.markdown("### 🔍 Step 3: 분석 결과 작성")
    
    st.markdown("""
    분석하여 알게 된 결과를 적어봅시다.
    - 어떤 전기제품의 소비전력이 가장 컸나요?
    - 에너지 종류에 따라 소비전력에 패턴이 있나요?
    """)
    
    analysis_text = st.text_area(
        "분석 결과 작성",
        value=st.session_state.analysis_result,
        height=200,
        placeholder="여기에 분석 결과를 작성해주세요...",
        key="analysis_input"
    )

    st.session_state.analysis_result = analysis_text

    if st.button("✅ Step 3 입력 완료", key="analysis_submit_button", use_container_width=True):
        if analysis_text.strip():
            st.session_state.analysis_submitted = True
            st.success("잘 분석해주었습니다! 이제 아래 활동 2를 진행해 보세요.")
        else:
            st.session_state.analysis_submitted = False
            st.error("분석 결과를 작성한 뒤 입력 완료를 눌러주세요.")

else:
    st.info("📌 위에서 전기제품 정보를 입력하고 '입력 완료' 버튼을 눌러주세요.")

st.markdown("---")

# 활동 2: 전기 주전자 비교하기

if st.session_state.data_submitted and st.session_state.analysis_submitted:
    st.title("🫖 활동 2. 고심이는 어떤 전기 주전자를 사는 게 좋을까?")
    st.markdown(
        """
    ### 📖 활동 소개
    전기 주전자를 사러 온 고심이! 여러 가지 전기 주전자를 직접 비교해서 가장 적합한 제품을 선택해 봅시다.
    """
    )

    kettle_data = pd.DataFrame(
        [
            {"제품": "A", "소비전력(W)": 1800},
            {"제품": "B", "소비전력(W)": 1400},
            {"제품": "C", "소비전력(W)": 900},
        ]
    )

    if "kettle_choice" not in st.session_state:
        st.session_state.kettle_choice = "B"

    if "kettle_reason" not in st.session_state:
        st.session_state.kettle_reason = ""

    if "kettle_lesson" not in st.session_state:
        st.session_state.kettle_lesson = ""

    if "kettle_performance_relation_submitted" not in st.session_state:
        st.session_state.kettle_performance_relation_submitted = False

    if "kettle_power_revealed" not in st.session_state:
        st.session_state.kettle_power_revealed = []

    kettle_image_paths = [
        Path(__file__).resolve().parent.parent / "data" / "kettle_a.png",
        Path(__file__).resolve().parent.parent / "data" / "kettle_b.png",
        Path(__file__).resolve().parent.parent / "data" / "kettle_c.png",
    ]
    kettles_overview_path = Path(__file__).resolve().parent.parent / "data" / "kettles.png"

    def image_to_data_uri(image_path):
        if not image_path.exists():
            return None

        with image_path.open("rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        suffix = image_path.suffix.lower().lstrip(".")
        mime_type = f"image/{'jpeg' if suffix in ['jpg', 'jpeg'] else suffix}"
        return f"data:{mime_type};base64,{encoded_image}"

    def render_kettle_card(title, color, image_path):
        image_data_uri = image_to_data_uri(image_path)
        image_html = (
            f'<img src="{image_data_uri}" style="width:100%; height:220px; object-fit:contain; display:block; margin:0 auto 14px auto; border-radius:18px; background:#ffffff; padding:10px;" />'
            if image_data_uri
            else (
                '<div style="'
                'background:#f8fafc; border:1px dashed #cbd5e1; border-radius:18px; '
                'padding:72px 16px; text-align:center; color:#64748b; font-size:42px; '
                'margin-bottom:14px;">🫖</div>'
            )
        )

        return f"""
        <div style="
            background: linear-gradient(180deg, #ffffff 0%, {color}18 100%);
            border: 2px solid {color}40;
            border-radius: 24px;
            padding: 18px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            min-height: 350px;
        ">
            <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 12px;">{title}</div>
            {image_html}
        </div>
        """

    if kettles_overview_path.exists():
        left_spacer, image_col, right_spacer = st.columns([1, 2, 1])
        with image_col:
            st.image(str(kettles_overview_path), use_container_width=True)
    else:
        st.warning("kettles.png 파일을 찾을 수 없습니다. data 폴더를 확인해 주세요.")

    st.markdown("#### Step 1: 성능 확인하기")
    st.caption("같은 양의 물을 끓일 때, 주전자마다 얼마나 빨리 끓는지 확인해 봅시다.")

    if "kettle_water_amount" not in st.session_state:
        st.session_state.kettle_water_amount = 500

    if "kettle_boiling_started" not in st.session_state:
        st.session_state.kettle_boiling_started = False

    if "kettle_performance_result" not in st.session_state:
        st.session_state.kettle_performance_result = None

    control_col, result_col = st.columns([1, 1])

    with control_col:
        water_amount = st.slider(
            "끓일 물의 양(mL)",
            min_value=100,
            max_value=1000,
            value=int(st.session_state.kettle_water_amount),
            step=100,
            key="kettle_water_amount_slider",
        )
        st.session_state.kettle_water_amount = water_amount

        if st.button("✅ 입력 완료", key="kettle_performance_submit", use_container_width=True):
            st.session_state.kettle_boiling_started = True
            boiling_base = water_amount / 100
            st.session_state.kettle_performance_result = pd.DataFrame(
                [
                    {"제품": "A", "물의 양(mL)": water_amount, "끓는 시간(초)": round(boiling_base * 18 + 6, 1)},
                    {"제품": "B", "물의 양(mL)": water_amount, "끓는 시간(초)": round(boiling_base * 19 + 7, 1)},
                    {"제품": "C", "물의 양(mL)": water_amount, "끓는 시간(초)": round(boiling_base * 18 + 6, 1)},
                ]
            )

        if st.session_state.kettle_boiling_started:
            st.info("(A~C로 물을 끓이고 있습니다.)")
        else:
            st.info("물의 양을 입력하고 입력 완료 버튼을 눌러 주세요.")

    with result_col:
        if st.session_state.kettle_boiling_started and st.session_state.kettle_performance_result is not None:
            st.markdown("##### 끓인 결과")
            st.dataframe(st.session_state.kettle_performance_result, use_container_width=True, hide_index=True)

            fastest_row = st.session_state.kettle_performance_result.loc[
                st.session_state.kettle_performance_result["끓는 시간(초)"] .astype(float).idxmin()
            ]
        else:
            st.info("입력 완료 후 오른쪽에 끓인 결과가 표시됩니다.")

    st.markdown("##### 주전자의 성능 비교하기")
    st.caption("Step 1 결과를 바탕으로 알파벳과 기호를 모두 입력하세요.")

    relation_col1, relation_col2, relation_col3, relation_col4, relation_col5 = st.columns([1, 1, 1, 1, 1])
    with relation_col1:
        relation_left = st.selectbox("주전자 종류", ["", "A", "B", "C"], key="kettle_relation_left")
    with relation_col2:
        relation_ac = st.selectbox("등호/부등호 고르기", ["", "=", ">", "<"], key="kettle_relation_ac")
    with relation_col3:
        relation_mid = st.selectbox("주전자 종류", ["", "A", "B", "C"], key="kettle_relation_mid")
    with relation_col4:
        relation_cb = st.selectbox("등호/부등호 고르기", ["", "=", ">", "<"], key="kettle_relation_cb")
    with relation_col5:
        relation_right = st.selectbox("주전자 종류", ["", "A", "B", "C"], key="kettle_relation_right")

    if st.button("✅ 성능 비교 입력 완료", key="kettle_performance_relation_submit", use_container_width=True):
        if relation_left == "A" and relation_ac == "=" and relation_mid == "C" and relation_cb == ">" and relation_right == "B":
            st.session_state.kettle_performance_relation_submitted = True
            st.success("정답입니다. Step 2를 진행해 보세요.")
        elif relation_left == "C" and relation_ac == "=" and relation_mid == "A" and relation_cb == ">" and relation_right == "B":
                    st.session_state.kettle_performance_relation_submitted = True
                    st.success("정답입니다. Step 2를 진행해 보세요.")
        else:
            st.session_state.kettle_performance_relation_submitted = False
            st.error("다시 생각해볼까요? 같은 물을 끓일 때 시간이 더 적게 걸릴수록 성능이 좋은 것입니다!")

    if st.session_state.kettle_performance_relation_submitted:
        st.markdown("#### Step 2: 소비전력 확인하기")
        st.caption("각 주전자 카드를 클릭하면 소비전력 팝업이 뜹니다. A~C를 모두 확인하면 아래 정리표가 나타납니다.")

        select_col1, select_col2, select_col3 = st.columns(3)
        step2_kettle_cards = [
            (select_col1, "A", "전기 주전자 A", "#2563eb", kettle_image_paths[0], 1800),
            (select_col2, "B", "전기 주전자 B", "#0f766e", kettle_image_paths[1], 1400),
            (select_col3, "C", "전기 주전자 C", "#d97706", kettle_image_paths[2], 900),
        ]

        for col, product, title, color, image_path, power in step2_kettle_cards:
            with col:
                st.markdown(
                    render_kettle_card(
                        title=title,
                        color=color,
                        image_path=image_path,
                    ),
                    unsafe_allow_html=True,
                )

                if product in st.session_state.kettle_power_revealed:
                    st.info(f"소비전력: {power}W")
                else:
                    if st.button(f"{title}의 소비전력 확인하", key=f"step2_select_{product}", use_container_width=True):
                        if product not in st.session_state.kettle_power_revealed:
                            st.session_state.kettle_power_revealed.append(product)
                        st.rerun()

        revealed_set = set(st.session_state.kettle_power_revealed)

        if len(revealed_set) == 3:
            st.markdown("##### 성능 및 소비전력 정리 표")

            performance_labels = {"A": "-", "B": "-", "C": "-"}
            if st.session_state.kettle_performance_result is not None and not st.session_state.kettle_performance_result.empty:
                perf_df = st.session_state.kettle_performance_result.copy()
                perf_df["끓는 시간(초)"] = perf_df["끓는 시간(초)"].astype(float)
                min_time = perf_df["끓는 시간(초)"].min()
                for _, row in perf_df.iterrows():
                    product = str(row["제품"])
                    performance_labels[product] = "높음" if float(row["끓는 시간(초)"]) == float(min_time) else "낮음"

            summary_df = pd.DataFrame(
                {
                    "성능": [performance_labels["A"], performance_labels["B"], performance_labels["C"]],
                    "소비전력": ["1800W", "1400W", "900W"],
                },
                index=["A", "B", "C"],
            )
            st.dataframe(summary_df, use_container_width=True)
        else:
            remaining = [p for p in ["A", "B", "C"] if p not in revealed_set]

    st.markdown("#### Step 3: 어떤 제품을 사면 좋을까?")

    if "kettle_choice_submitted" not in st.session_state:
        st.session_state.kettle_choice_submitted = False

    if "kettle_choice_feedback_type" not in st.session_state:
        st.session_state.kettle_choice_feedback_type = ""

    if "kettle_choice_feedback_message" not in st.session_state:
        st.session_state.kettle_choice_feedback_message = ""

    choice_col, submit_col, feedback_col = st.columns([1.7, 0.9, 2.4])

    with choice_col:
        selected_kettle = st.radio(
            "고심이에게 가장 적합한 제품은?",
            ["A", "B", "C"],
            index=["A", "B", "C"].index(st.session_state.kettle_choice),
            key="kettle_choice_radio",
            horizontal=True,
        )
        st.session_state.kettle_choice = selected_kettle

    with submit_col:
        if st.button("✅ 입력 완료", key="kettle_choice_submit", use_container_width=False):
            st.session_state.kettle_choice_submitted = True
            if selected_kettle == "C":
                st.session_state.kettle_choice_feedback_type = "success"
                st.session_state.kettle_choice_feedback_message = "정답입니다!"
            elif selected_kettle == "A":
                st.session_state.kettle_choice_feedback_type = "warning"
                st.session_state.kettle_choice_feedback_message = "A도 성능이 좋지만... 소비전력도 고려해볼까요?"
            else:
                st.session_state.kettle_choice_feedback_type = "info"
                st.session_state.kettle_choice_feedback_message = "B가 정말 최선일까요?!?! 다시 생각해봅시다."

    with feedback_col:
        if st.session_state.kettle_choice_submitted:
            if st.session_state.kettle_choice_feedback_type == "success":
                st.success(st.session_state.kettle_choice_feedback_message)
            elif st.session_state.kettle_choice_feedback_type == "warning":
                st.warning(st.session_state.kettle_choice_feedback_message)
            else:
                st.info(st.session_state.kettle_choice_feedback_message)

    st.markdown("#### [정리] 오늘 수업 내용 요약하기")

    qa_cols = [0.4, 4.2, 0.5, 1.3]

    q1_col1, q1_col2, q1_col3, q1_col4 = st.columns(qa_cols, gap="small")
    with q1_col1:
        st.markdown("<p style='margin-top: 0.55rem;'>1.</p>", unsafe_allow_html=True)
    with q1_col2:
        st.markdown("<p style='margin-top: 0.55rem;'>1초 동안 사용하는 전기 에너지의 양은?</p>", unsafe_allow_html=True)
    with q1_col3:
        st.markdown("<p style='margin-top: 0.55rem; text-align:right;'>답:</p>", unsafe_allow_html=True)
    with q1_col4:
        lesson1_blank = st.text_input(
            "1번 빈칸",
            value=st.session_state.get("kettle_lesson1_blank", ""),
            key="kettle_lesson1_blank_input",
            label_visibility="collapsed",
        )
        st.session_state.kettle_lesson1_blank = lesson1_blank

    q2_col1, q2_col2, q2_col3, q2_col4 = st.columns(qa_cols, gap="small")
    with q2_col1:
        st.markdown("<p style='margin-top: 0.55rem;'>2.</p>", unsafe_allow_html=True)
    with q2_col2:
        st.markdown("<p style='margin-top: 0.55rem;'>소비 전력이 큰 전기 기구는 전기 에너지를 주로 어떤 에너지로 전환하여 사용하는가?</p>", unsafe_allow_html=True)
    with q2_col3:
        st.markdown("<p style='margin-top: 0.55rem; text-align:right;'>답:</p>", unsafe_allow_html=True)
    with q2_col4:
        lesson2_blank = st.text_input(
            "2번 빈칸",
            value=st.session_state.get("kettle_lesson2_blank", ""),
            key="kettle_lesson2_blank_input",
            label_visibility="collapsed",
        )
        st.session_state.kettle_lesson2_blank = lesson2_blank

    q3_col1, q3_col2, q3_col3, q3_col4, q3_col5, q3_col6 = st.columns([0.4, 1.8, 1.0, 0.3, 0.8, 2.5], gap="small")
    with q3_col1:
        st.markdown("<p style='margin-top: 0.55rem;'>3.</p>", unsafe_allow_html=True)
    with q3_col2:
        st.markdown("<p style='margin-top: 0.55rem;'>성능이 동일하다면</p>", unsafe_allow_html=True)
    with q3_col3:
        lesson3_blank_one = st.text_input(
            "3번 첫 빈칸",
            value=st.session_state.get("kettle_lesson3_blank_one", ""),
            key="kettle_lesson3_blank_one_input",
            label_visibility="collapsed",
        )
        st.session_state.kettle_lesson3_blank_one = lesson3_blank_one
    with q3_col4:
        st.markdown("<p style='margin-top: 0.55rem; text-align:center;'>이</p>", unsafe_allow_html=True)
    with q3_col5:
        lesson3_blank_two = st.text_input(
            "3번 둘째 빈칸",
            value=st.session_state.get("kettle_lesson3_blank_two", ""),
            key="kettle_lesson3_blank_two_input",
            label_visibility="collapsed",
        )
        st.session_state.kettle_lesson3_blank_two = lesson3_blank_two
    with q3_col6:
        st.markdown("<p style='margin-top: 0.55rem;'>제품을 사용하는 것이 더 효율적이다.</p>", unsafe_allow_html=True)

    if st.button("✅ 정답 확인", key="kettle_lesson_check_submit", use_container_width=False):
        # 띄어쓰기 제거 후 유연한 정답 판정
        q1_ans = lesson1_blank.replace(" ", "")
        q2_ans = lesson2_blank.replace(" ", "")
        q3_ans1 = lesson3_blank_one.replace(" ", "")
        q3_ans2 = lesson3_blank_two.replace(" ", "")

        q1_correct = q1_ans in ["소비전력", "소비 전력"]
        q2_correct = q2_ans in ["열", "열에너지", "열 에너지"]
        q3_correct = (q3_ans1 in ["소비전력", "소비 전력"]) and (q3_ans2 in ["작은", "적은", "낮은"])

        if q1_correct and q2_correct and q3_correct:
            st.success("🎉 축하합니다! 모든 빈칸을 정확하게 채웠습니다!")
            st.balloons()
        else:
            st.warning("⚠️ 틀린 부분이 있습니다. 다시 확인해보세요!")
            if not q1_correct:
                st.info("1번 문제를 다시 확인해보세요.")
            if not q2_correct:
                st.info("2번 문제를 다시 확인해보세요.")
            if not q3_correct:
                st.info("3번 문제를 다시 확인해보세요.")

    st.markdown("---")
