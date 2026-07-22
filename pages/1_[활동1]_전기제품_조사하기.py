import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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

# PDF 저장 섹션
if st.session_state.data_submitted:
    st.markdown("### 📥 PDF로 저장하기")
    
    def generate_pdf():
        """입력된 데이터와 분석 결과를 PDF로 생성"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8
        )
        
        # 제목
        elements.append(Paragraph("🏠 활동 1. 고심이네 집 제품 조사하기", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # 작성 날짜
        today = datetime.now().strftime("%Y년 %m월 %d일")
        elements.append(Paragraph(f"작성 날짜: {today}", normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # 입력된 데이터 표
        elements.append(Paragraph("📝 입력된 전기제품 정보", heading_style))
        
        df = st.session_state.appliance_data.copy()
        data_for_table = [["전기 기구 종류", "전환되는 에너지", "소비전력(W)"]]
        for _, row in df.iterrows():
            data_for_table.append([
                row["전기 기구 종류"],
                row["전환되는 에너지"],
                str(int(row["소비전력(W)"]))
            ])
        
        table = Table(data_for_table, colWidths=[2*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # 통계 정보
        elements.append(Paragraph("📈 통계 정보", heading_style))
        stats_text = f"""
        • 총 제품 수: {len(df)}개<br/>
        • 평균 소비전력: {df['소비전력(W)'].mean():.1f}W<br/>
        • 최대 소비전력: {int(df['소비전력(W)'].max())}W<br/>
        • 최소 소비전력: {int(df['소비전력(W)'].min())}W<br/>
        """
        elements.append(Paragraph(stats_text, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # 분석 결과
        elements.append(Paragraph("🔍 분석 결과", heading_style))
        if st.session_state.analysis_result:
            analysis_text = st.session_state.analysis_result.replace('\n', '<br/>')
            elements.append(Paragraph(analysis_text, normal_style))
        else:
            elements.append(Paragraph("분석 결과가 작성되지 않았습니다.", normal_style))
        
        # PDF 생성
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    # PDF 다운로드 버튼
    pdf_buffer = generate_pdf()
    filename = f"활동1_전기제품조사_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    st.download_button(
        label="� PDF로 저장하기",
        data=pdf_buffer,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
        key="download_pdf"
    )
