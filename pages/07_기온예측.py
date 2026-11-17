
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

# ----------------------------------
# 1. 페이지 설정
# ----------------------------------

st.set_page_config(
    page_title="월별 평균 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균 기온 예측 프로그램")

st.write(
    "과거 기온 데이터를 학습하여 선형회귀 알고리즘으로 "
    "미래의 평균 기온을 예측합니다."
)

st.divider()


# ----------------------------------
# 2. CSV 파일 불러오기
# ----------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
        "temperature.csv",
        encoding="cp949"
    )

    # 영문 월을 숫자로 변환
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    # 연도 추출
    df["연도"] = df["일시"].apply(
        lambda x: 2000 + int(x.split("-")[1])
    )

    # 월 추출
    df["월"] = df["일시"].apply(
        lambda x: month_map[x.split("-")[0]]
    )

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# ----------------------------------
# 3. 사용자 입력
# ----------------------------------

st.subheader("📌 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "예측할 월을 선택하세요",
        list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

with col2:

    prediction_year = st.number_input(
        "예측할 연도를 입력하세요",
        min_value=2026,
        max_value=2100,
        value=2027,
        step=1
    )

st.divider()


# ----------------------------------
# 4. 선택한 월의 실제 데이터 추출
# 2025년까지만 사용
# ----------------------------------

month_data = df[
    (df["월"] == selected_month) &
    (df["연도"] <= 2025) &
    (df["평균기온(℃)"].notna())
].copy()

month_data = month_data.sort_values("연도")

if len(month_data) < 2:

    st.error("예측을 위한 데이터가 부족합니다.")
    st.stop()


# ----------------------------------
# 5. 선형회귀 모델 학습
# ----------------------------------

# 입력 데이터: 연도
X = month_data[["연도"]]

# 정답 데이터: 평균 기온
y = month_data["평균기온(℃)"]

# 선형회귀 모델 생성
model = LinearRegression()

# 모델 학습
model.fit(X, y)

# 미래 기온 예측
predicted_temp = model.predict(
    pd.DataFrame({
        "연도": [prediction_year]
    })
)[0]

# 기울기와 절편
slope = model.coef_[0]
intercept = model.intercept_

# 결정계수
r2 = model.score(X, y)


# ----------------------------------
# 6. 예측 결과 출력
# ----------------------------------

st.subheader(
    f"🌡️ {selected_month}월 평균 기온 예측 결과"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "예측 연도",
        f"{prediction_year}년"
    )

with col2:

    st.metric(
        "예측 평균 기온",
        f"{predicted_temp:.2f} ℃"
    )

with col3:

    st.metric(
        "결정계수 (R²)",
        f"{r2:.3f}"
    )


# ----------------------------------
# 7. 그래프 데이터 생성
# ----------------------------------

# 실제 데이터 시작 연도
min_year = int(month_data["연도"].min())

# 실제 데이터는 2025년까지만
max_year = 2025

# 회귀선은 예측 연도까지 연장
line_end_year = max(
    max_year,
    int(prediction_year)
)

line_years = np.linspace(
    min_year,
    line_end_year,
    200
)

# 회귀선을 이용한 기온 계산
line_temps = model.predict(
    pd.DataFrame({
        "연도": line_years
    })
)


# ----------------------------------
# 8. 그래프 그리기
# ----------------------------------

st.subheader("📈 과거 기온 및 미래 기온 예측 그래프")

fig = go.Figure()


# 실제 평균 기온
fig.add_trace(
    go.Scatter(
        x=month_data["연도"],
        y=month_data["평균기온(℃)"],
        mode="markers",
        name="실제 평균 기온",
        marker=dict(
            color="#3498DB",
            size=9
        ),
        hovertemplate=
        "%{x}년<br>실제 기온: %{y:.2f}℃<extra></extra>"
    )
)


# 실제 기온 변화 연결선
fig.add_trace(
    go.Scatter(
        x=month_data["연도"],
        y=month_data["평균기온(℃)"],
        mode="lines",
        name="실제 기온 변화",
        line=dict(
            color="#85C1E9",
            width=1.5
        ),
        hoverinfo="skip"
    )
)


# 선형회귀 예측선
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_temps,
        mode="lines",
        name="선형회귀 예측선",
        line=dict(
            color="#FF4B91",
            width=3
        )
    )
)


# 예측 기온 표시
fig.add_trace(
    go.Scatter(
        x=[prediction_year],
        y=[predicted_temp],
        mode="markers+text",
        name="미래 예측 기온",
        text=[f"{predicted_temp:.2f}℃"],
        textposition="top center",
        marker=dict(
            color="red",
            size=16,
            symbol="star"
        ),
        hovertemplate=
        "%{x}년<br>예측 기온: %{y:.2f}℃<extra></extra>"
    )
)


# 실제 기온과 회귀선 사이의 오차 표시
for _, row in month_data.iterrows():

    fitted_temp = model.predict(
        pd.DataFrame({
            "연도": [row["연도"]]
        })
    )[0]

    fig.add_trace(
        go.Scatter(
            x=[row["연도"], row["연도"]],
            y=[
                row["평균기온(℃)"],
                fitted_temp
            ],
            mode="lines",
            line=dict(
                color="gray",
                width=1,
                dash="dot"
            ),
            showlegend=False,
            hoverinfo="skip"
        )
    )


# 그래프 디자인
fig.update_layout(
    title=f"{selected_month}월 평균 기온과 선형회귀 예측",
    xaxis_title="연도",
    yaxis_title="평균 기온 (℃)",
    template="plotly_white",
    hovermode="closest",
    height=600,
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
    showgrid=True,
    range=[
        min_year - 0.5,
        line_end_year + 1
    ]
)

fig.update_yaxes(
    showgrid=True,
    zeroline=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ----------------------------------
# 9. 선형회귀 분석 결과
# ----------------------------------

st.subheader("🔍 선형회귀 알고리즘 분석")

st.write("### 선형회귀 계산식")

st.latex(
    r"y = ax + b"
)

st.write(
    f"**기울기(a):** {slope:.4f}"
)

st.write(
    f"**절편(b):** {intercept:.4f}"
)

st.write(
    f"**회귀식:** "
    f"y = {slope:.4f} × 연도 + ({intercept:.4f})"
)

st.write(
    f"**결정계수(R²):** {r2:.4f}"
)


# 기울기 해석
if slope > 0:

    st.info(
        f"📈 기울기가 양수({slope:.4f})입니다. "
        "과거 데이터에서는 시간이 지날수록 "
        "해당 월의 평균 기온이 상승하는 경향이 있습니다."
    )

elif slope < 0:

    st.info(
        f"📉 기울기가 음수({slope:.4f})입니다. "
        "과거 데이터에서는 시간이 지날수록 "
        "해당 월의 평균 기온이 하락하는 경향이 있습니다."
    )

else:

    st.info(
        "기울기가 0이므로 평균 기온에 "
        "선형적인 변화 경향이 없습니다."
    )


# ----------------------------------
# 10. 선형회귀 알고리즘 쉽게 설명
# ----------------------------------

st.divider()

st.subheader("📚 선형회귀 알고리즘 쉽게 이해하기")

st.markdown("""
### ① 선형회귀란?

선형회귀는 과거에 수집된 데이터를 이용해서
미래의 값을 예측하는 인공지능 학습 방법입니다.

이번 프로그램에서는 다음과 같이 학습합니다.

- 입력 데이터(X): 연도
- 정답 데이터(Y): 해당 월의 평균 기온
- 학습 방법: 선형회귀 알고리즘
- 예측 결과: 사용자가 선택한 연도의 평균 기온

### ② 어떻게 학습할까요?

1. 과거의 해당 월 평균 기온 데이터를 모읍니다.
2. 각 연도를 X축, 평균 기온을 Y축에 표시합니다.
3. 여러 데이터 점을 가장 잘 설명하는 직선을 찾습니다.
4. 이 직선을 이용하여 새로운 연도의 기온을 계산합니다.

### ③ 그래프 읽는 방법

- 🔵 파란색 점: 실제로 관측된 평균 기온
- 연한 파란색 선: 실제 기온 변화
- 💗 핑크색 선: 선형회귀가 찾아낸 최적의 직선
- ⭐ 빨간색 별: 사용자가 입력한 연도의 예측 기온
- 회색 점선: 실제 기온과 회귀선 사이의 차이(오차)

### ④ 가장 잘 맞는 직선은 어떻게 찾을까요?

선형회귀는 실제 데이터와 직선 사이의 차이를
제곱하여 모두 더한 값이 가장 작아지도록
기울기와 절편을 결정합니다.

이 방법을 최소제곱법이라고 합니다.

### ⑤ 주의할 점

선형회귀는 과거의 변화 경향이 앞으로도 이어진다고
가정하여 계산합니다.

따라서 실제 미래 기온과 예측 결과는 다를 수 있습니다.

특히 과거 데이터 범위를 크게 벗어난 연도를
예측할 때는 주의해야 합니다.
""")


# ----------------------------------
# 11. 실제 데이터 확인
# ----------------------------------

with st.expander("📋 선택한 월의 실제 기온 데이터 확인"):

    display_data = month_data[
        ["일시", "평균기온(℃)"]
    ].copy()

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ----------------------------------
# 12. 안내 문구
# ----------------------------------

st.divider()

st.caption(
    "※ 실제 관측 데이터는 2025년까지만 사용합니다. "
    "2026년 이후의 기온은 선형회귀 알고리즘으로 계산한 예측값입니다."
)
