import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

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

# 입력 섹션
st.markdown("### 📝 Step 1: 제품 정보 입력하기")

# 데이터 편집기
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

# 입력 데이터 업데이트
st.session_state.appliance_data = edited_df

# 입력 완료 버튼
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("✅ 입력 완료", use_container_width=True):
        # 입력 데이터 검증
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
    
    # 에너지 종류별 색상 정의
    energy_colors = {
        "열": "#FF6B6B",      # 빨강
        "빛": "#FFD93D",       # 노랑
        "운동": "#6BCB77",     # 초록
        "음": "#4D96FF",       # 파랑
        "전기": "#FF8C42",     # 주황
        "자기": "#9D84B7",     # 보라
    }
    
    df = st.session_state.appliance_data.copy()
    
    # 막대 그래프 생성
    fig = go.Figure()
    
    # 에너지 종류별로 막대 추가
    for energy_type in df["전환되는 에너지"].unique():
        energy_data = df[df["전환되는 에너지"] == energy_type]
        color = energy_colors.get(energy_type, "#95A5A6")  # 기본 색상
        
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
    아래에 당신이 분석하여 알게 된 결과를 적어주세요.
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
    
    # 분석 결과 자동 저장
    st.session_state.analysis_result = analysis_text

else:
    st.info("📌 위에서 전기제품 정보를 입력하고 '입력 완료' 버튼을 눌러주세요.")

st.markdown("---")

# 활동 2: 전기 주전자 비교하기
if st.session_state.data_submitted:
    st.title("🫖 활동 2. 고심이는 어떤 전기 주전자를 사는 게 좋을까?")
    st.markdown(
        """
    ### 📖 활동 소개
    전기 주전자를 사러 온 고심이! 여러 가지 전기 주전자를 직접 비교해 보고, 성능과 소비전력을 함께 살펴봅시다.
    """
    )

    kettle_data = pd.DataFrame(
        [
            {"제품": "A", "소비전력(W)": 1800, "특징": "물은 빨리 끓지만 전력을 많이 사용함"},
            {"제품": "B", "소비전력(W)": 1400, "특징": "A와 성능은 같고 소비전력은 더 낮음"},
            {"제품": "C", "소비전력(W)": 900, "특징": "소비전력은 낮지만 성능이 조금 낮음"},
        ]
    )

    if "kettle_choice" not in st.session_state:
        st.session_state.kettle_choice = "B"

    if "kettle_reason" not in st.session_state:
        st.session_state.kettle_reason = ""

    if "kettle_lesson" not in st.session_state:
        st.session_state.kettle_lesson = ""

    if "kettle_power_revealed" not in st.session_state:
        st.session_state.kettle_power_revealed = []

    st.markdown("#### Step 1: 성능 확인하기")
    st.caption("같은 양의 물을 끓일 때, 주전자마다 얼마나 빨리 끓는지 확인해 봅시다.")

    if "kettle_water_amount" not in st.session_state:
        st.session_state.kettle_water_amount = 500

    if "kettle_boiling_started" not in st.session_state:
        st.session_state.kettle_boiling_started = False

    if "kettle_performance_result" not in st.session_state:
        st.session_state.kettle_performance_result = None

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
                {"제품": "B", "물의 양(mL)": water_amount, "끓는 시간(초)": round(boiling_base * 18 + 8, 1)},
                {"제품": "C", "물의 양(mL)": water_amount, "끓는 시간(초)": round(boiling_base * 22 + 10, 1)},
            ]
        )

    if st.session_state.kettle_boiling_started:
        st.info("(A~C로 물을 끓이고 있습니다.)")
        if st.session_state.kettle_performance_result is not None:
            st.markdown("##### 끓인 결과")
            st.dataframe(st.session_state.kettle_performance_result, use_container_width=True, hide_index=True)

            fastest_row = st.session_state.kettle_performance_result.loc[
                st.session_state.kettle_performance_result["끓는 시간(초)"] .astype(float).idxmin()
            ]
            st.success(f"{fastest_row['제품']} 주전자가 가장 빨리 끓습니다. 같은 조건에서 더 빨리 끓는 주전자가 성능이 더 좋습니다.")
    else:
        st.info("물의 양을 입력하고 입력 완료 버튼을 눌러 주세요.")

    st.markdown("#### Step 2: 소비전력 확인하기")
    st.caption("A~C 주전자를 하나씩 클릭해서 소비전력을 확인해 보세요. 모두 확인하면 아래 표로 정리됩니다.")

    kettle_image_paths = [
        Path(__file__).resolve().parent.parent / "data" / "kettle_a.png",
        Path(__file__).resolve().parent.parent / "data" / "kettle_b.png",
        Path(__file__).resolve().parent.parent / "data" / "kettle_c.png",
    ]

    def image_to_data_uri(image_path):
        if not image_path.exists():
            return None

        with image_path.open("rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        suffix = image_path.suffix.lower().lstrip(".")
        mime_type = f"image/{'jpeg' if suffix in ['jpg', 'jpeg'] else suffix}"
        return f"data:{mime_type};base64,{encoded_image}"

    def render_kettle_card(title, subtitle, color, image_path):
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
            <div style="font-size: 15px; color: #475569; line-height: 1.5; min-height: 48px;">{subtitle}</div>
        </div>
        """

    card_col1, card_col2, card_col3 = st.columns(3)
    kettle_cards = [
        (card_col1, "전기 주전자 A", "A 제품의 전력을 확인해 보세요.", 1800, "#2563eb"),
        (card_col2, "전기 주전자 B", "B 제품의 전력을 확인해 보세요.", 1400, "#0f766e"),
        (card_col3, "전기 주전자 C", "C 제품의 전력을 확인해 보세요.", 900, "#d97706"),
    ]
    for column, title, subtitle, power, color in kettle_cards:
        with column:
            card_index = int(title.split()[-1].replace("A", "0").replace("B", "1").replace("C", "2"))
            st.markdown(
                render_kettle_card(
                    title=title,
                    subtitle=subtitle,
                    color=color,
                    image_path=kettle_image_paths[card_index],
                ),
                unsafe_allow_html=True,
            )

            if st.button(f"{title} 소비전력 확인", key=f"show_power_{card_index}", use_container_width=True):
                product = title.split()[-1]
                if product not in st.session_state.kettle_power_revealed:
                    st.session_state.kettle_power_revealed.append(product)

            with st.popover(f"{title} 소비전력 팝업", use_container_width=True):
                st.metric("소비전력", f"{power}W")
                st.caption("성능이 같다면 소비전력이 더 낮은 쪽이 더 효율적입니다.")

    st.markdown("##### 소비전력 정리 표")
    if len(st.session_state.kettle_power_revealed) == 3:
        power_summary_df = kettle_data.copy()
        power_summary_df["소비전력 확인 여부"] = power_summary_df["제품"].apply(lambda product: "확인함" if product in st.session_state.kettle_power_revealed else "미확인")
        st.dataframe(power_summary_df[["제품", "소비전력(W)", "소비전력 확인 여부", "특징"]], use_container_width=True, hide_index=True)
        st.success("세 주전자의 소비전력을 모두 확인했습니다.")
    else:
        remaining = [product for product in ["A", "B", "C"] if product not in st.session_state.kettle_power_revealed]
        st.info(f"아직 {', '.join(remaining)} 주전자의 소비전력을 확인하지 않았습니다.")

    st.markdown("#### Step 3: 어떤 제품을 사면 좋을까?")
    st.markdown(
        """
    고심이가 고를 제품을 선택하고, 그렇게 생각한 이유와 이번 활동에서 배운 교훈을 적어 봅시다.
    """
    )

    answer_col, reason_col = st.columns([1, 2])
    with answer_col:
        selected_kettle = st.selectbox(
            "고심이가 사면 좋을 제품은?",
            ["A", "B", "C"],
            index=["A", "B", "C"].index(st.session_state.kettle_choice),
            key="kettle_choice_select",
        )
        st.session_state.kettle_choice = selected_kettle

        if selected_kettle == "B":
            st.success("잘 골랐습니다. 같은 성능이라면 소비전력이 더 낮은 B가 더 효율적입니다.")
        elif selected_kettle == "A":
            st.warning("A와 B는 성능이 같지만, B가 소비전력이 더 낮습니다. 다시 비교해 보세요.")
        else:
            st.info("C는 소비전력은 낮지만 성능이 A, B보다 조금 낮습니다. 먼저 성능을 확인해 보세요.")

    with reason_col:
        reason_text = st.text_area(
            "그렇게 생각한 이유를 적어 보세요.",
            value=st.session_state.kettle_reason,
            height=140,
            placeholder="예: A와 B는 성능이 같아서 소비전력이 더 낮은 B를 고르는 것이 더 효율적이라고 생각했다.",
            key="kettle_reason_input",
        )
        st.session_state.kettle_reason = reason_text

    st.markdown("#### 활동의 교훈을 완성해 보세요")
    st.caption("빈칸을 알맞게 채우면 정답 메시지가 나옵니다.")
    lesson_col1, lesson_col2 = st.columns([1, 1])

    with lesson_col1:
        blank_one = st.text_input(
            "첫 번째 빈칸",
            value=st.session_state.get("kettle_lesson_blank_one", ""),
            placeholder="소비전력",
            key="kettle_lesson_blank_one_input",
        )
        st.session_state.kettle_lesson_blank_one = blank_one

    with lesson_col2:
        blank_two = st.text_input(
            "두 번째 빈칸",
            value=st.session_state.get("kettle_lesson_blank_two", ""),
            placeholder="낮은",
            key="kettle_lesson_blank_two_input",
        )
        st.session_state.kettle_lesson_blank_two = blank_two

    normalized_one = blank_one.replace(" ", "")
    normalized_two = blank_two.replace(" ", "")

    st.markdown("성능이 같을 때는, (소비전력)이 더 (낮)은 전기기구가 더 효율적이다.")

    if normalized_one == "소비전력" and normalized_two == "낮은":
        st.success("잘했습니다. 정답입니다.")
    elif normalized_one or normalized_two:
        st.warning("빈칸을 다시 확인해 보세요. 첫 번째는 '소비전력', 두 번째는 '낮은'입니다.")

st.markdown("---")

# 화면 저장 섹션
if st.session_state.data_submitted:
    st.markdown("### 📥 학습지 저장하기")
    st.caption("작성한 학습지를 저장하여 제출합니다.")

    base_dir = Path(__file__).resolve().parent.parent
    font_regular_path = base_dir / "fonts" / "NotoSansKR-Regular.ttf"
    font_bold_path = base_dir / "fonts" / "NotoSansKR-Bold.ttf"

    def load_font(size, bold=False):
        font_path = font_bold_path if bold else font_regular_path
        try:
            return ImageFont.truetype(str(font_path), size)
        except OSError:
            return ImageFont.load_default()

    def text_width(draw, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    def wrap_text(draw, text, font, max_width):
        wrapped_lines = []
        for paragraph in str(text).splitlines() or [""]:
            if not paragraph:
                wrapped_lines.append("")
                continue

            current_line = ""
            for char in paragraph:
                trial_line = current_line + char
                if text_width(draw, trial_line, font) <= max_width:
                    current_line = trial_line
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = char

            if current_line:
                wrapped_lines.append(current_line)

        return wrapped_lines or [""]

    def draw_wrapped_text(draw, text, x, y, font, fill, max_width, line_gap=8):
        for line in wrap_text(draw, text, font, max_width):
            draw.text((x, y), line, font=font, fill=fill)
            y += font.size + line_gap if hasattr(font, "size") else 20
        return y

    def create_result_image():
        df = st.session_state.appliance_data.copy()
        analysis_text = st.session_state.analysis_result.strip() or "분석 결과가 아직 작성되지 않았습니다."
        width = 1400
        height = 2100
        image = Image.new("RGB", (width, height), "#F5F7FB")
        draw = ImageDraw.Draw(image)

        title_font = load_font(46, bold=True)
        section_font = load_font(28, bold=True)
        body_font = load_font(22)
        small_font = load_font(18)

        def rounded_box(x1, y1, x2, y2, fill, outline=None, radius=24):
            draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=2 if outline else 0)

        def section_header(y, title, subtitle=None):
            draw.text((80, y), title, font=section_font, fill="#16324F")
            if subtitle:
                draw.text((80, y + 40), subtitle, font=small_font, fill="#5B677A")

        rounded_box(50, 40, width - 50, 220, fill="#DCEBFF", outline="#9DBBEA", radius=32)
        draw.text((90, 80), "🏠 활동 1. 고심이네 집 제품 조사하기", font=title_font, fill="#103A71")
        draw.text((90, 145), f"작성 날짜: {datetime.now().strftime('%Y년 %m월 %d일')}", font=body_font, fill="#355C7D")
        draw.text((90, 180), "결과 화면을 이미지와 PDF로 저장할 수 있습니다.", font=small_font, fill="#5B677A")

        section_header(260, "요약 정보", "입력한 전기제품의 개수와 소비전력 정보를 한눈에 볼 수 있습니다.")
        rounded_box(70, 330, width - 70, 520, fill="#FFFFFF", outline="#D9E2EF", radius=28)

        total_count = len(df)
        average_power = df["소비전력(W)"].mean() if total_count else 0
        max_row = None
        min_row = None
        if total_count:
            max_idx = df["소비전력(W)"].idxmax()
            min_idx = df["소비전력(W)"].idxmin()
            max_row = df.loc[max_idx]
            min_row = df.loc[min_idx]

        summary_texts = [
            f"총 제품 수: {total_count}개",
            f"평균 소비전력: {average_power:.1f}W" if total_count else "평균 소비전력: -",
            f"최대 소비전력: {int(max_row['소비전력(W)'])}W / {max_row['전기 기구 종류']}" if total_count else "최대 소비전력: -",
            f"최소 소비전력: {int(min_row['소비전력(W)'])}W / {min_row['전기 기구 종류']}" if total_count else "최소 소비전력: -",
        ]

        info_x = 110
        info_y = 375
        for index, text in enumerate(summary_texts):
            draw.text((info_x, info_y + index * 36), text, font=body_font, fill="#22313F")

        section_header(560, "입력된 전기제품", "화면에 입력한 내용을 그대로 정리한 표입니다.")
        rounded_box(70, 630, width - 70, 860, fill="#FFFFFF", outline="#D9E2EF", radius=28)

        row_top = 680
        row_height = 58
        header_fill = "#356AE6"
        draw.rounded_rectangle((110, row_top - 8, 1290, row_top + row_height - 8), radius=14, fill=header_fill)
        for x, text in zip([150, 580, 980], ["전기 기구 종류", "전환되는 에너지", "소비전력(W)"]):
            draw.text((x, row_top + 10), text, font=body_font, fill="#FFFFFF")

        table_y = row_top + 70
        for index, (_, row) in enumerate(df.iterrows()):
            y1 = table_y + index * 52
            y2 = y1 + 46
            fill = "#F8FBFF" if index % 2 == 0 else "#EEF4FF"
            draw.rounded_rectangle((110, y1, 1290, y2), radius=12, fill=fill, outline="#D5DEEA")
            draw.text((140, y1 + 10), str(row["전기 기구 종류"]), font=small_font, fill="#22313F")
            draw.text((570, y1 + 10), str(row["전환되는 에너지"]), font=small_font, fill="#22313F")
            draw.text((995, y1 + 10), f"{int(row['소비전력(W)'])} W", font=small_font, fill="#22313F")

        chart_y = 900
        section_header(chart_y, "소비전력 비교", "화면에 보이는 그래프를 이미지로 다시 그려 넣었습니다.")
        rounded_box(70, chart_y + 70, width - 70, 1600, fill="#FFFFFF", outline="#D9E2EF", radius=28)

        chart_left = 170
        chart_top = chart_y + 160
        chart_width = 1080
        chart_height = 520
        chart_bottom = chart_top + chart_height
        draw.line((chart_left, chart_bottom, chart_left + chart_width, chart_bottom), fill="#4A5568", width=3)
        draw.line((chart_left, chart_top, chart_left, chart_bottom), fill="#4A5568", width=3)

        energy_colors = {
            "열": "#FF6B6B",
            "빛": "#FFD93D",
            "운동": "#6BCB77",
            "음": "#4D96FF",
            "전기": "#FF8C42",
            "자기": "#9D84B7",
        }
        max_power = max(float(df["소비전력(W)"].max()), 1.0) if total_count else 1.0
        legend_x = 900
        legend_y = chart_y + 100
        draw.text((legend_x, legend_y - 34), "범례", font=body_font, fill="#22313F")
        for offset, energy_type in enumerate(sorted(df["전환되는 에너지"].astype(str).unique())):
            color = energy_colors.get(energy_type, "#95A5A6")
            cy = legend_y + offset * 34
            draw.ellipse((legend_x, cy, legend_x + 18, cy + 18), fill=color, outline=color)
            draw.text((legend_x + 28, cy - 2), energy_type, font=small_font, fill="#22313F")

        if total_count:
            row_gap = 72
            start_y = chart_top + 20
            for index, (_, row) in enumerate(df.iterrows()):
                item_y = start_y + index * row_gap
                label = str(row["전기 기구 종류"])
                label_lines = wrap_text(draw, label, small_font, 220)[:2]
                label_height = len(label_lines) * 22
                current_y = item_y + max(0, (18 - label_height) // 2)
                for line in label_lines:
                    draw.text((chart_left - 80, current_y), line, font=small_font, fill="#22313F")
                    current_y += 22

                bar_width = int((float(row["소비전력(W)"]) / max_power) * (chart_width - 220))
                color = energy_colors.get(str(row["전환되는 에너지"]), "#95A5A6")
                bar_y1 = item_y + 6
                bar_y2 = item_y + 36
                draw.rounded_rectangle((chart_left, bar_y1, chart_left + bar_width, bar_y2), radius=12, fill=color)
                draw.text((chart_left + bar_width + 12, bar_y1 - 1), f"{int(row['소비전력(W)'])}W", font=small_font, fill="#22313F")

        section_header(1640, "분석 결과", "작성한 생각을 함께 저장합니다.")
        rounded_box(70, 1710, width - 70, 1990, fill="#FFFFFF", outline="#D9E2EF", radius=28)
        draw_wrapped_text(draw, analysis_text, 110, 1750, body_font, "#22313F", max_width=1180, line_gap=10)

        

        image_buffer = BytesIO()
        image.save(image_buffer, format="PNG")
        image_buffer.seek(0)
        return image_buffer

    def create_pdf_from_image(image_buffer):
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        page_width, page_height = A4
        image = ImageReader(image_buffer)
        image_width, image_height = image.getSize()
        scale = min(page_width / image_width, page_height / image_height)
        draw_width = image_width * scale
        draw_height = image_height * scale
        x = (page_width - draw_width) / 2
        y = (page_height - draw_height) / 2
        c.drawImage(image, x, y, width=draw_width, height=draw_height)
        c.showPage()
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer

    image_buffer = create_result_image()
    pdf_buffer = create_pdf_from_image(image_buffer)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    image_col, pdf_col = st.columns(2)
    with image_col:
        st.download_button(
            label="🖼️ PNG 이미지로 저장",
            data=image_buffer.getvalue(),
            file_name=f"활동1_전기제품조사_{timestamp}.png",
            mime="image/png",
            use_container_width=True,
            key="download_png"
        )
    with pdf_col:
        st.download_button(
            label="📄 PDF로 저장",
            data=pdf_buffer,
            file_name=f"활동1_전기제품조사_{timestamp}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="download_pdf"
        )
