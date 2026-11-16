
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import re

# -----------------------------------
# 1. 페이지 기본 설정
# -----------------------------------
st.set_page_config(
    page_title="월 별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월 별 기온분석")
st.write("원하는 월을 선택하면 1907년부터 2026년까지의 최고기온과 최저기온을 비교합니다.")

# -----------------------------------
# 2. CSV 파일 불러오기
# -----------------------------------
@st.cache_data
def load_data():

    file_path = Path(__file__).parent.parent / "temperature.csv"

    # CSV 인코딩 처리
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    # 날짜 데이터 정리
    df["일시"] = df["일시"].astype(str).str.strip()

    # 월과 연도 분리
    def parse_date(value):

        match = re.match(r"([A-Za-z]{3})-(\d{2})", value)

        if not match:
            return pd.NaT

        month_text = match.group(1)
        year_short = int(match.group(2))

        # 1907~1999년, 2000~2026년 구분
        year = (
            1900 + year_short
            if year_short >= 7
            else 2000 + year_short
        )

        try:
            return pd.to_datetime(
                f"{month_text}-{year}",
                format="%b-%Y"
            )
        except ValueError:
            return pd.NaT

    df["날짜"] = df["일시"].apply(parse_date)

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 기온 데이터 숫자로 변환
    temperature_columns = [
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in temperature_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 날짜 오류 데이터 제거
    df = df.dropna(subset=["날짜"])

    return df


# -----------------------------------
# 3. 데이터 불러오기
# -----------------------------------
try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# -----------------------------------
# 4. 월 선택
# -----------------------------------
month_list = list(range(1, 13))

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    month_list,
    format_func=lambda x: f"{x}월"
)


# -----------------------------------
# 5. 선택한 월의 데이터 추출
# -----------------------------------
month_df = df[
    (df["월"] == selected_month) &
    (df["연도"] >= 1907) &
    (df["연도"] <= 2026)
].copy()

# 연도별 최고기온과 최저기온 평균 계산
result = (
    month_df
    .groupby("연도", as_index=False)
    [["최고기온(℃)", "최저기온(℃)"]]
    .mean()
    .sort_values("연도")
)

# 두 기온이 모두 없는 행 제거
result = result.dropna(
    subset=["최고기온(℃)", "최저기온(℃)"],
    how="all"
)


# -----------------------------------
# 6. 꺾은선 그래프 작성
# -----------------------------------
if result.empty:

    st.warning("선택한 월에 분석할 데이터가 없습니다.")

else:

    fig = go.Figure()

    # 최고기온 - 핫핑크
    fig.add_trace(
        go.Scatter(
            x=result["연도"],
            y=result["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#FF1493",
                width=3
            ),
            marker=dict(size=6),
            connectgaps=False
        )
    )

    # 최저기온 - 하늘색
    fig.add_trace(
        go.Scatter(
            x=result["연도"],
            y=result["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#87CEEB",
                width=3
            ),
            marker=dict(size=6),
            connectgaps=False
        )
    )

    # 그래프 레이아웃
    fig.update_layout(

        title={
            "text": "월 별 기온분석",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 25}
        },

        xaxis=dict(
            title="연도",
            range=[1907, 2026],
            tickmode="linear",
            tick0=1910,
            dtick=10
        ),

        yaxis=dict(
            title="온도 (℃)"
        ),

        legend=dict(
            title="기온 구분",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        hovermode="x unified",

        template="plotly_white",

        height=550
    )

    # 그래프 출력
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------------
    # 7. 분석 데이터 표
    # -----------------------------------
    with st.expander("📊 분석 데이터 확인하기"):

        display_df = result.copy()

        display_df.columns = [
            "연도",
            "최고기온(℃)",
            "최저기온(℃)"
        ]

        st.dataframe(
            display_df,
            use_container_width=True
        )

    # -----------------------------------
    # 8. 분석 결과
    # -----------------------------------
    st.subheader("📌 분석 결과")

    col1, col2 = st.columns(2)

    max_data = result.dropna(
        subset=["최고기온(℃)"]
    )

    min_data = result.dropna(
        subset=["최저기온(℃)"]
    )

    if not max_data.empty:

        max_row = max_data.loc[
            max_data["최고기온(℃)"].idxmax()
        ]

        with col1:
            st.metric(
                "가장 높은 최고기온",
                f"{max_row['최고기온(℃)']:.1f} ℃"
            )

            st.write(
                f"해당 연도: {int(max_row['연도'])}년"
            )

    if not min_data.empty:

        min_row = min_data.loc[
            min_data["최저기온(℃)"].idxmin()
        ]

        with col2:
            st.metric(
                "가장 낮은 최저기온",
                f"{min_row['최저기온(℃)']:.1f} ℃"
            )

            st.write(
                f"해당 연도: {int(min_row['연도'])}년"
            )
