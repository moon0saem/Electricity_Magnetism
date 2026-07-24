# Electricity_Magnetism

전기와 에너지 절약 개념을 학습하는 Streamlit 기반 활동형 학습 앱입니다.

## 앱 구성

- 1차시: 전기 기구 조사하기
- 2차시-1: 소비전력만 보고 판단할 수 있을까?
- 2차시-2: 나의 에너지 다이어트 계획 세우기

각 활동은 pages 폴더의 개별 페이지로 구성되어 있으며, 사용자가 입력한 값으로 전기에너지 사용량, 탄소배출량, 절감 효과를 시뮬레이션합니다.

## 실행 방법

1. 의존성 설치

   pip install -r requirements.txt

2. 앱 실행

   streamlit run streamlit_app.py

3. 브라우저에서 표시된 로컬 주소 접속

## 주요 의존성

- streamlit
- pandas
- plotly
- reportlab
