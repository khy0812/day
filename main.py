import streamlit as st
import pandas as pd
from datetime import date

st.title("📚 맞춤형 시험 D-Day & 학습 스케줄러")

# 1. 입력 영역 구현
exam_date = st.date_input("시험 시작 날짜를 선택하세요", min_value=date.today())
daily_hours = st.number_input("하루 평균 공부 가능 시간 (시간)", min_value=1.0, max_value=24.0, value=5.0)

# 과목 데이터 입력 예시 (수학, 영어, 국어)
subjects_data = [
    {"과목": "수학", "목표점수": 90, "난이도": 5},
    {"과목": "영어", "목표점수": 85, "난이도": 4},
    {"과목": "국어", "목표점수": 95, "난이도": 3}
]

# 2. 핵심 연산 구현
d_day = (exam_date - date.today()).days

if d_day > 0:
    df = pd.DataFrame(subjects_data)
    # 과목별 중요도 가중치 계산
    df['중요도'] = df['목표점수'] * df['난이도']
    total_weight = df['중요도'].sum()
    
    # 일일 권장 공부 시간 계산 (소수점 첫째자리까지)
    df['일일 공부시간(시간)'] = (df['중요도'] / total_weight * daily_hours).round(1)
    
    # 3. 출력 영역 구현
    st.metric(label="시험까지 남은 기간", value=f"D-{d_day}일")
    st.subheader("📊 과목별 추천 일일 공부 시간")
    st.dataframe(df[['과목', '목표점수', '난이도', '일일 공부시간(시간)']])
    st.bar_chart(data=df, x='과목', y='일일 공부시간(시간)')
