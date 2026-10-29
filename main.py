import streamlit as st
import pandas as pd
from datetime import date

# 페이지 기본 설정
st.set_page_config(page_title="시험 D-Day & 학습 스케줄러", layout="centered")

st.title("📚 맞춤형 시험 D-Day & 학습 스케줄러")
st.write("시험일과 개인별 과목 목표, 난이도를 설정하여 최적의 공부 시간을 배분받으세요.")

# ---------------------------------------------------------
# 1. 입력 영역 (날짜 및 총 공부 시간)
# ---------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    exam_date = st.date_input("시험 시작 날짜", min_value=date.today())
with col2:
    daily_hours = st.number_input("하루 총 공부 가능 시간 (시간)", min_value=1.0, max_value=24.0, value=5.0, step=0.5)

st.divider()
st.subheader("📝 과목별 정보 입력 (직접 수정/추가 가능)")

# 기본 과목 데이터 프레임 생성
default_data = pd.DataFrame([
    {"과목": "수학", "목표점수": 90, "난이도(1~5)": 5},
    {"과목": "영어", "목표점수": 85, "난이도(1~5)": 4},
    {"과목": "국어", "목표점수": 95, "난이도(1~5)": 3}
])

# 사용자가 직접 행을 추가/삭제/수정할 수 있는 데이터 에디터 위젯
edited_df = st.data_editor(
    default_data,
    num_rows="dynamic", # 사용자 행 추가/삭제 허용
    column_config={
        "과목": st.column_config.TextColumn("과목명", required=True),
        "목표점수": st.column_config.NumberColumn("목표 점수", min_value=0, max_value=100, step=5),
        "난이도(1~5)": st.column_config.NumberColumn("난이도 (1:쉬움 ~ 5:어려움)", min_value=1, max_value=5, step=1)
    },
    use_container_width=True
)

# ---------------------------------------------------------
# 2. 핵심 연산 및 예외 처리
# ---------------------------------------------------------
d_day = (exam_date - date.today()).days

if st.button("🚀 학습 스케줄 계산하기"):
    if d_day <= 0:
        st.error("⚠️ 시험 날짜는 오늘 이후로 설정해야 합니다!")[cite: 1]
    elif edited_df.empty or edited_df["과목"].dropna().empty:
        st.warning("⚠️ 최소 1개 이상의 과목 정보를 입력해 주세요.")[cite: 1]
    else:
        # 결측치 제거
        df = edited_df.dropna(subset=["과목"]).copy()
        
        # 과목별 중요도 가중치 계산 (목표점수 * 난이도)
        df["중요도"] = df["목표점수"] * df["난이도(1~5)"]
        total_weight = df["중요도"].sum()

        if total_weight == 0:
            st.error("⚠️ 과목의 목표 점수와 난이도 합이 0일 수 없습니다.")
        else:
            # 일일 권장 공부 시간 연산 (소수점 첫째자리까지 표시)
            df["일일 권장 공부시간(시간)"] = (df["중요도"] / total_weight * daily_hours).round(1)

            # ---------------------------------------------------------
            # 3. 결과 출력 영역
            # ---------------------------------------------------------
            st.divider()
            st.success("🎉 학습 스케줄이 성공적으로 생성되었습니다!")
            
            # 메트릭 요약 표시
            m1, m2 = st.columns(2)
            m1.metric(label="시험 D-Day", value=f"D-{d_day}일")
            m2.metric(label="시험 전까지 총 남은 공부시간", value=f"{d_day * daily_hours:.0f}시간")

            # 과목별 시간 배분 결과 표
            st.subheader("📌 과목별 일일 권장 공부 시간")
            st.dataframe(
                df[["과목", "목표점수", "난이도(1~5)", "일일 권장 공부시간(시간)"]],
                use_container_width=True
            )

            # 시각화 그래프
            st.subheader("📊 과목별 공부 시간 비중 차트")
            st.bar_chart(data=df, x="과목", y="일일 권장 공부시간(시간)")
