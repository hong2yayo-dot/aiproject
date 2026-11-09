
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# 1. 페이지 설정
# --------------------------------

st.set_page_config(
    page_title="세계 국가별 MBTI 분석",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 세계 국가별 MBTI 비율 분석")
st.write("국가를 선택하면 해당 국가의 MBTI 유형별 비율을 분석합니다.")

# --------------------------------
# 2. CSV 데이터 불러오기
# --------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# MBTI 유형 열 추출
mbti_columns = [
    col for col in df.columns
    if col != "Country"
]

# --------------------------------
# 3. 국가 선택
# --------------------------------

country_list = sorted(df["Country"].unique())

selected_country = st.selectbox(
    "국가를 선택하세요",
    country_list
)

# --------------------------------
# 4. 선택 국가 데이터 분석
# --------------------------------

country_data = df[
    df["Country"] == selected_country
]

# 가로 형태 데이터를 세로 형태로 변환
chart_data = country_data[
    mbti_columns
].melt(
    var_name="MBTI",
    value_name="비율"
)

# 백분율 변환
chart_data["비율"] = chart_data["비율"] * 100

# 높은 비율 순서대로 정렬
chart_data = chart_data.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)

# --------------------------------
# 5. 그래프 색상 설정
# --------------------------------

colors = [
    "#E53935",  # 1위 빨간색
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

chart_data["색상"] = colors[:len(chart_data)]

# --------------------------------
# 6. Plotly 막대그래프
# --------------------------------

fig = px.bar(
    chart_data,
    x="MBTI",
    y="비율",
    color="MBTI",
    color_discrete_map={
        row["MBTI"]: row["색상"]
        for _, row in chart_data.iterrows()
    },
    text="비율",
    title=f"{selected_country}의 MBTI 유형별 비율"
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    cliponaxis=False
)

fig.update_layout(
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    showlegend=False,
    template="plotly_white",
    height=550
)

fig.update_yaxes(
    rangemode="tozero"
)

# --------------------------------
# 7. 그래프 화면 출력
# --------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------
# 8. 가장 높은 MBTI 유형
# --------------------------------

top_mbti = chart_data.iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric(
    "선택 국가",
    selected_country
)

col2.metric(
    "가장 높은 MBTI",
    top_mbti["MBTI"]
)

col3.metric(
    "최고 비율",
    f'{top_mbti["비율"]:.2f}%'
)

# --------------------------------
# 9. 상세 데이터 표
# --------------------------------

st.subheader("📊 MBTI 유형별 상세 비율")

st.dataframe(
    chart_data[["MBTI", "비율"]].style.format(
        {"비율": "{:.2f}%"}
    ),
    use_container_width=True,
    hide_index=True
)
