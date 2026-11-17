
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor


# ======================================
# 1. 페이지 설정
# ======================================

st.set_page_config(
    page_title="AI 기온 예측 비교",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 인공지능 기온 예측 알고리즘 비교")
st.write("세 가지 알고리즘으로 미래의 평균 기온을 예측하고 비교합니다.")

st.divider()


# ======================================
# 2. 데이터 불러오기
# ======================================

@st.cache_data
def load_data():

    try:
        df = pd.read_csv("temperature.csv", encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv("temperature.csv", encoding="utf-8-sig")

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    df["연도"] = df["일시"].apply(
        lambda x: 2000 + int(x.split("-")[1])
    )

    df["월"] = df["일시"].apply(
        lambda x: month_map[x.split("-")[0]]
    )

    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# ======================================
# 3. 사용자 입력
# ======================================

st.subheader("📌 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월",
        range(1, 13),
        format_func=lambda x: f"{x}월"
    )

with col2:
    prediction_year = st.number_input(
        "예측할 연도",
        min_value=2026,
        max_value=2100,
        value=2027,
        step=1
    )


# ======================================
# 4. 실제 데이터 추출
# 2025년까지만 사용
# ======================================

month_data = df[
    (df["월"] == selected_month) &
    (df["연도"] <= 2025) &
    (df["평균기온(℃)"].notna())
].copy()

month_data = month_data.sort_values("연도")

if len(month_data) < 3:
    st.error("예측할 데이터가 부족합니다.")
    st.stop()


# ======================================
# 5. 학습 데이터 준비
# ======================================

X = month_data[["연도"]].values
y = month_data["평균기온(℃)"].values

base_year = int(month_data["연도"].min())

X_train = X - base_year

X_predict = np.array([
    [int(prediction_year) - base_year]
])


# ======================================
# 6. 세 가지 알고리즘 학습
# ======================================

# ① 선형회귀
linear_model = LinearRegression()

linear_model.fit(X_train, y)


# ② 다항회귀
polynomial_model = make_pipeline(
    PolynomialFeatures(degree=2),
    LinearRegression()
)

polynomial_model.fit(X_train, y)


# ③ 랜덤 포레스트
forest_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=4,
    random_state=42
)

forest_model.fit(X_train, y)


# ======================================
# 7. 세 가지 알고리즘 예측
# ======================================

predictions = {
    "선형회귀": linear_model.predict(X_predict)[0],
    "다항회귀": polynomial_model.predict(X_predict)[0],
    "랜덤 포레스트": forest_model.predict(X_predict)[0]
}


# ======================================
# 8. 예측값 한눈에 비교
# ======================================

st.divider()

st.subheader(
    f"🌡️ {prediction_year}년 {selected_month}월 예측 결과"
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "① 선형회귀",
        f"{predictions['선형회귀']:.2f} ℃"
    )

with c2:
    st.metric(
        "② 다항회귀",
        f"{predictions['다항회귀']:.2f} ℃"
    )

with c3:
    st.metric(
        "③ 랜덤 포레스트",
        f"{predictions['랜덤 포레스트']:.2f} ℃"
    )


# ======================================
# 9. 그래프 위 알고리즘 선택
# ======================================

st.divider()

st.subheader("📈 알고리즘 선택 및 그래프 비교")

selected_algorithm = st.radio(
    "그래프에서 강조할 알고리즘을 선택하세요.",
    [
        "선형회귀",
        "다항회귀",
        "랜덤 포레스트"
    ],
    horizontal=True,
    key="algorithm_choice"
)

st.success(
    f"선택한 알고리즘: {selected_algorithm} / "
    f"예측 기온: {predictions[selected_algorithm]:.2f} ℃"
)


# ======================================
# 10. 그래프 데이터 생성
# ======================================

min_year = int(month_data["연도"].min())

line_end_year = max(
    2025,
    int(prediction_year)
)

line_years = np.linspace(
    min_year,
    line_end_year,
    300
)

line_X = (line_years - base_year).reshape(-1, 1)

linear_line = linear_model.predict(line_X)
polynomial_line = polynomial_model.predict(line_X)
forest_line = forest_model.predict(line_X)


# ======================================
# 11. 그래프 작성
# ======================================

fig = go.Figure()


# 실제 기온
fig.add_trace(
    go.Scatter(
        x=month_data["연도"],
        y=month_data["평균기온(℃)"],
        mode="markers+lines",
        name="실제 평균 기온",
        marker=dict(
            color="#3498DB",
            size=8
        ),
        line=dict(
            color="#85C1E9",
            width=2
        )
    )
)


# 선택한 알고리즘을 굵게 표시
line_settings = {
    "선형회귀": {
        "color": "#FF4B91",
        "dash": "solid",
        "width": 5 if selected_algorithm == "선형회귀" else 2
    },
    "다항회귀": {
        "color": "#9B59B6",
        "dash": "dash",
        "width": 5 if selected_algorithm == "다항회귀" else 2
    },
    "랜덤 포레스트": {
        "color": "#2ECC71",
        "dash": "dot",
        "width": 5 if selected_algorithm == "랜덤 포레스트" else 2
    }
}


# 선형회귀
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=linear_line,
        mode="lines",
        name="선형회귀",
        line=line_settings["선형회귀"]
    )
)


# 다항회귀
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=polynomial_line,
        mode="lines",
        name="다항회귀",
        line=line_settings["다항회귀"]
    )
)


# 랜덤 포레스트
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=forest_line,
        mode="lines",
        name="랜덤 포레스트",
        line=line_settings["랜덤 포레스트"]
    )
)


# ======================================
# 12. 미래 예측 지점 표시
# ======================================

marker_colors = {
    "선형회귀": "#FF4B91",
    "다항회귀": "#9B59B6",
    "랜덤 포레스트": "#2ECC71"
}

# 세 알고리즘 예측값을 모두 표시
for name, value in predictions.items():

    is_selected = name == selected_algorithm

    fig.add_trace(
        go.Scatter(
            x=[prediction_year],
            y=[value],
            mode="markers+text",
            name=f"{name} 예측값",
            text=[
                f"{name}: {value:.2f}℃"
            ],
            textposition="top center",
            marker=dict(
                color=marker_colors[name],
                size=17 if is_selected else 12,
                symbol="star" if is_selected else "diamond",
                line=dict(width=1, color="white")
            )
        )
    )


# ======================================
# 13. 그래프 디자인
# ======================================

fig.update_layout(
    title=f"{selected_month}월 실제 기온 및 세 가지 알고리즘 예측",
    xaxis_title="연도",
    yaxis_title="평균 기온 (℃)",
    template="plotly_white",
    height=650,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)

fig.update_xaxes(
    dtick=2,
    range=[min_year - 0.5, line_end_year + 1],
    showgrid=True
)

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ======================================
# 14. 알고리즘 선택에 따른 설명
# ======================================

st.divider()

st.subheader("🔍 선택한 알고리즘 알아보기")

if selected_algorithm == "선형회귀":

    st.markdown("""
    ### ① 선형회귀 (Linear Regression)

    과거 기온 데이터의 전체적인 추세를 직선으로 표현합니다.

    - 연도와 평균 기온의 관계를 학습합니다.
    - 기울기와 절편을 계산합니다.
    - 직선을 이용하여 미래 기온을 예측합니다.
    """)

    st.latex(r"y = ax + b")


elif selected_algorithm == "다항회귀":

    st.markdown("""
    ### ② 다항회귀 (Polynomial Regression)

    과거 기온 데이터의 변화가 직선이 아닌 곡선 형태일 때
    곡선을 이용하여 학습합니다.

    - 기온의 곡선 형태 변화를 학습합니다.
    - 이번 프로그램은 2차 다항식을 사용합니다.
    - 복잡한 변화 패턴을 표현할 수 있습니다.
    """)

    st.latex(r"y = ax^2 + bx + c")


else:

    st.markdown("""
    ### ③ 랜덤 포레스트 (Random Forest)

    여러 개의 의사결정나무를 결합하는 알고리즘입니다.

    - 여러 의사결정나무를 학습시킵니다.
    - 각 나무가 기온을 예측합니다.
    - 예측값의 평균을 최종 결과로 사용합니다.
    """)

    st.write(
        f"사용한 의사결정나무: {forest_model.n_estimators}개"
    )


# ======================================
# 15. 알고리즘별 결정계수
# ======================================

st.subheader("📊 학습 데이터 결정계수 비교")

r2_results = {
    "선형회귀": linear_model.score(X_train, y),
    "다항회귀": polynomial_model.score(X_train, y),
    "랜덤 포레스트": forest_model.score(X_train, y)
}

r2_df = pd.DataFrame({
    "알고리즘": list(r2_results.keys()),
    "결정계수 (R²)": list(r2_results.values())
})

st.dataframe(
    r2_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "결정계수는 학습에 사용한 과거 데이터에 대한 적합도입니다. "
    "미래 예측의 정확도를 직접 보장하지는 않습니다."
)


# ======================================
# 16. 알고리즘 특징 설명
# ======================================

st.divider()

st.subheader("📚 세 가지 알고리즘 비교")

comparison = pd.DataFrame({
    "알고리즘": [
        "선형회귀",
        "다항회귀",
        "랜덤 포레스트"
    ],
    "학습 방식": [
        "직선",
        "곡선",
        "여러 의사결정나무"
    ],
    "특징": [
        "전체적인 상승 및 하락 추세",
        "곡선 형태의 변화",
        "복잡한 데이터 패턴"
    ],
    "주의점": [
        "복잡한 변화 표현이 어려움",
        "미래 곡선이 실제와 다를 수 있음",
        "학습 범위 밖의 추세 예측에 한계"
    ]
})

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)


# ======================================
# 17. 실제 데이터 확인
# ======================================

with st.expander("📋 실제 기온 데이터 확인"):

    st.dataframe(
        month_data[
            ["일시", "연도", "평균기온(℃)"]
        ],
        use_container_width=True,
        hide_index=True
    )


# ======================================
# 18. 마무리
# ======================================

st.divider()

st.info("""
💡 학습 활동

같은 월과 예측 연도를 유지한 상태에서
그래프 위의 알고리즘 선택 버튼을 바꾸어 보세요.

세 알고리즘이 어떤 방식으로 다른 예측선을 만드는지,
그리고 미래 예측값이 얼마나 차이 나는지 비교할 수 있습니다.
""")

st.caption(
    "실제 관측 데이터는 2025년까지만 사용합니다. "
    "2026년 이후의 값은 알고리즘이 계산한 예측값입니다."
)
