import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(page_title="시험 D-Day & 학습 스케줄러", layout="centered")

st.title("📚 맞춤형 시험 D-Day & 학습 스케줄러")
st.write("시험일과 개인별 과목 목표, 난이도를 설정하고 아래 버튼을 눌러 공부 시간을 배분받으세요.")

# ---------------------------------------------------------
# 세션 상태(Session State) 초기화 로직 (오류 없는 안전한 리셋)
# ---------------------------------------------------------
default_data = pd.DataFrame([
    {"과목": "수학", "목표점수": 90, "난이도(1~5)": 5},
    {"과목": "영어", "목표점수": 85, "난이도(1~5)": 4},
    {"과목": "국어", "목표점수": 95, "난이도(1~5)": 3}
])

if "editor_key" not in st.session_state:
    st.session_state["editor_key"] = 0

def reset_data():
    st.session_state["editor_key"] += 1

# ---------------------------------------------------------
# 1. 입력 영역 (시험 날짜 및 하루 공부 가능 시간)
# ---------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    exam_date = st.date_input("시험 시작 날짜", min_value=date.today())
with col2:
    daily_hours = st.number_input("하루 총 공부 가능 시간 (시간)", min_value=1.0, max_value=24.0, value=5.0, step=0.5)

st.divider()

# 과목 정보 입력 헤더 및 초기화 버튼
head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.subheader("📝 과목별 정보 입력 (수정/추가 가능)")
with head_col2:
    st.button("🔄 입력 초기화", on_click=reset_data)

# 동적 데이터 에디터 위젯
edited_df = st.data_editor(
    default_data,
    key=f"data_editor_{st.session_state['editor_key']}",
    num_rows="dynamic",
    column_config={
        "과목": st.column_config.TextColumn("과목명", required=True),
        "목표점수": st.column_config.NumberColumn("목표 점수", min_value=0, max_value=100, step=5),
        "난이도(1~5)": st.column_config.NumberColumn("난이도 (1:쉬움 ~ 5:어려움)", min_value=1, max_value=5, step=1)
    },
    use_container_width=True
)

# ---------------------------------------------------------
# 2. 핵심 연산 및 예외 처리 (버튼 클릭 시에만 실행)
# ---------------------------------------------------------
d_day = (exam_date - date.today()).days

if st.button("🚀 학습 스케줄 계산하기", type="primary"):
    # [예외 처리 1] 시험 날짜 검증
    if d_day <= 0:
        st.error("⚠️ 시험 날짜는 오늘 이후(D-1 이상)로 설정해야 합니다!")[cite: 1]
    
    # [예외 처리 2] 입력 데이터 존재 여부 검증
    elif edited_df.empty or edited_df["과목"].dropna().astype(str).str.strip().eq("").all():
        st.warning("⚠️ 최소 1개 이상의 과목명을 입력해 주세요.")[cite: 1]
    
    else:
        # 데이터 정제 및 타입 변환 (오류 방지)
        df = edited_df.dropna(subset=["과목"]).copy()
        df["과목"] = df["과목"].astype(str).str.strip()
        df = df[df["과목"] != ""]
        df["목표점수"] = pd.to_numeric(df["목표점수"], errors='coerce').fillna(0)
        df["난이도(1~5)"] = pd.to_numeric(df["난이도(1~5)"], errors='coerce').fillna(1)

        # [예외 처리 3] 중복 과목명 검증
        if df["과목"].duplicated().any():
            st.warning("⚠️ 중복된 과목명이 있습니다. 과목 이름을 다르게 설정해 주세요.")
        else:
            # 과목별 중요도 가중치 연산 (목표점수 * 난이도)
            df["중요도"] = df["목표점수"] * df["난이도(1~5)"]
            total_weight = df["중요도"].sum()

            # [예외 처리 4] 중요도 합계 0 방지
            if total_weight == 0:
                st.error("⚠️ 모든 과목의 목표 점수 또는 난이도가 0일 수 없습니다.")
            else:
                # 권장 공부 시간 분배 계산 (소수점 첫째 자리 반올림)
                df["일일 권장 공부시간(시간)"] = (df["중요도"] / total_weight * daily_hours).round(1)

                # ---------------------------------------------------------
                # 3. 결과 시각화 및 출력 영역 (버튼을 눌렀을 때만 표시)
                # ---------------------------------------------------------
                st.divider()
                st.success("🎉 개인 맞춤형 학습 스케줄이 성공적으로 생성되었습니다!")
                
                # 핵심 메트릭 지표
                m1, m2 = st.columns(2)
                m1.metric(label="시험 D-Day", value=f"D-{d_day}일")
                m2.metric(label="시험 전까지 총 공부 가능 시간", value=f"{d_day * daily_hours:.0f}시간")

                # 과목별 배분 시간 결과 표
                st.subheader("📌 과목별 일일 권장 공부 시간")
                st.dataframe(
                    df[["과목", "목표점수", "난이도(1~5)", "일일 권장 공부시간(시간)"]],
                    use_container_width=True
                )

                # 연한 파스텔 핑크색 막대그래프 시각화 (Matplotlib 사용으로 에러 방지)
                st.subheader("📊 과목별 공부 시간 비중 차트")
                
                fig, ax = plt.subplots(figsize=(8, 4))
                bars = ax.bar(df["과목"], df["일일 권장 공부시간(시간)"], color="#FFB6C1", edgecolor="#FF69B4", linewidth=1.2)
                
                # 막대 상단 수치 표시
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height}시간',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3), 
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=10)

                ax.set_ylabel("권장 공부시간 (시간)")
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                
                st.pyplot(fig)
