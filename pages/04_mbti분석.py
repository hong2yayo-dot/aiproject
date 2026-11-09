
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 분석",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 국가별 MBTI 비율 분석")
st.write("국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 확인할 수 있습니다.")

# CSV 파일 읽기
DATA_FILE = Path(__file__).parent / "countriesMBTI_16types.csv"

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    if "Country" not in data.columns:
        raise ValueError("Country 열이 없습니다.")

    mbti_columns = [
        col for col in data.columns
        if col != "Country"
    ]

    if len(mbti_columns) != 16:
        raise ValueError("MBTI 유형은 16개여야 합니다.")

    data["Country"] = data["Country"].astype(str).str.strip()

    for col in mbti_columns:
        data[col] = pd.to_numeric(
            data[col], errors="coerce"
        )

    if data[mbti_columns].isna().any().any():
        raise ValueError("결측치 또는 잘못된 데이터가 있습니다.")

    return data, mbti_columns


# 데이터 불러오기
try:
    df, mbti_types = load_data(DATA_FILE)

except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 CSV 파일을 넣어주세요."
    )
    st.stop()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# 국가 선택
countries = sorted(df["Country"].unique().tolist())

selected_country = st.selectbox(
    "국가를 선택하세요",
    countries
)


# 선택한 국가 데이터 가져오기
row = df[df["Country"] == selected_country].iloc[0]

chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": [
        float(row[t]) * 100
        for t in mbti_types
    ]
})

# 높은 순서대로 정렬
chart_data = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)


# 그래프 색상 설정
# 1위는 빨간색
# 나머지는 파란색에서 연한 파란색으로

blue_shades = [
    "#2563EB",
    "#3475EC",
    "#4387ED",
    "#5299EE",
    "#61A4EF",
    "#70AFF0",
    "#7FB9F2",
    "#8EC4F3",
    "#9DCEF4",
    "#ACD9F5",
    "#BBE3F7",
    "#CAEAF9",
    "#D9F0FB",
    "#E8F6FD",
    "#EFF9FE"
]

bar_colors = ["#E53935"] + blue_shades


# 막대그래프 만들기
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_data["MBTI"],
        y=chart_data["비율"],

        marker=dict(
            color=bar_colors[:len(chart_data)],
            line=dict(width=0)
        ),

        text=[
            f"{v:.2f}%"
            for v in chart_data["비율"]
        ],

        textposition="outside",
        cliponaxis=False,

        hovertemplate=
        "<b>%{x}</b><br>" +
        "비율: %{y:.2f}%<extra></extra>"
    )
)


# 그래프 디자인
fig.update_layout(
    title=f"{selected_country}의 MBTI 유형별 비율",
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    template="plotly_white",
    height=560,
    showlegend=False,
    margin=dict(
        l=30,
        r=30,
        t=80,
        b=40
    )
)

fig.update_yaxes(
    rangemode="tozero",
    ticksuffix="%"
)


# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# 주요 분석 결과
top_type = chart_data.iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택 국가",
    selected_country
)

col2.metric(
    "가장 높은 MBTI",
    top_type["MBTI"]
)

col3.metric(
    "1위 비율",
    f'{top_type["비율"]:.2f}%'
)


# 데이터 표
with st.expander("MBTI 상세 비율 확인하기"):

    display_data = chart_data.copy()

    display_data["비율"] = display_data[
        "비율"
    ].map(lambda x: f"{x:.2f}%")

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


st.caption(
    "원본 CSV 비율을 백분율로 환산하여 표시합니다."
)
