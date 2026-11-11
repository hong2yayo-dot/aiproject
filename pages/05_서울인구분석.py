
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ----------------------------------------
# 1. 페이지 설정
# ----------------------------------------
st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 자치구별 인구 분석")
st.caption("연령대별 자치구 순위 및 남녀 인구 비교")

# ----------------------------------------
# 2. CSV 파일 불러오기
# ----------------------------------------
@st.cache_data
def load_data():

    # 현재 파일 위치: pages 폴더
    current_dir = Path(__file__).resolve().parent

    # 상위 폴더 위치
    parent_dir = current_dir.parent

    # CSV 파일 경로
    file_path = parent_dir / "population (1).csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {file_path}"
        )

    # 한글 인코딩 처리
    try:
        data = pd.read_csv(
            file_path,
            encoding="cp949"
        )
    except UnicodeDecodeError:
        data = pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류 발생: {e}")
    st.stop()

# ----------------------------------------
# 3. 데이터 전처리
# ----------------------------------------

# 행정구역에서 자치구 이름 추출
df["구"] = df["행정구역"].astype(str).str.extract(
    r"서울특별시\s*(.*?)\s*\("
)[0].str.strip()

# 서울시 전체 제외
df = df[
    df["구"].notna() &
    (df["구"] != "")
].copy()

# 숫자 데이터 변환
for col in df.columns:
    if col not in ["행정구역", "구"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ""),
            errors="coerce"
        )

# ----------------------------------------
# 4. 분석에 사용할 연도와 연령대
# ----------------------------------------

years = [
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025"
]

ages = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]

districts = sorted(df["구"].unique().tolist())

# ----------------------------------------
# 5. 사이드바 선택 메뉴
# ----------------------------------------

st.sidebar.header("🔍 분석 조건 선택")

selected_year = st.sidebar.selectbox(
    "연도 선택",
    years,
    index=5
)

selected_age = st.sidebar.selectbox(
    "연령대 선택",
    ages,
    index=0
)

selected_district = st.sidebar.selectbox(
    "자치구 선택",
    districts
)

# ----------------------------------------
# 6. 첫 번째 그래프
#    연령대별 인구가 많은 자치구 순위
# ----------------------------------------

st.header("1️⃣ 연령대별 인구 자치구 순위")

st.write(
    f"**{selected_year}년 {selected_age} 인구가 "
    f"많은 자치구 순위**"
)

# 해당 연령대의 전체 인구 컬럼
total_col = f"{selected_year}년_거주자_{selected_age}"

if total_col not in df.columns:
    st.error(f"데이터 컬럼을 찾을 수 없습니다: {total_col}")
    st.stop()

# 자치구별 인구 데이터 추출
rank_df = df[["구", total_col]].copy()

rank_df = rank_df.rename(
    columns={total_col: "인구수"}
)

rank_df["인구수"] = rank_df["인구수"].fillna(0)

# 인구가 많은 순서대로 정렬
rank_df = rank_df.sort_values(
    by="인구수",
    ascending=False
)

# 순위 추가
rank_df["순위"] = range(1, len(rank_df) + 1)

# 막대그래프
fig1 = px.bar(
    rank_df,
    x="구",
    y="인구수",
    text="인구수",
    title=f"{selected_year}년 {selected_age} 자치구별 인구 순위",
    color_discrete_sequence=["green"]
)

fig1.update_traces(
    texttemplate="%{y:,.0f}",
    textposition="outside",
    marker_line_width=0,
    hovertemplate=(
        "자치구: %{x}<br>"
        "인구수: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig1.update_layout(
    template="plotly_white",
    height=550,
    xaxis_title="자치구",
    yaxis_title="인구수 (명)",
    xaxis=dict(
        categoryorder="array",
        categoryarray=rank_df["구"].tolist()
    ),
    yaxis=dict(
        tickformat=",d",
        rangemode="tozero"
    ),
    font=dict(
        family="Malgun Gothic, NanumGothic, sans-serif",
        size=12
    )
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# 순위 데이터 표
with st.expander("📋 자치구별 인구 순위표 보기"):

    display_rank = rank_df.copy()

    display_rank["인구수"] = display_rank["인구수"].map(
        lambda x: f"{x:,.0f}명"
    )

    st.dataframe(
        display_rank,
        use_container_width=True,
        hide_index=True
    )

# ----------------------------------------
# 7. 두 번째 그래프
#    선택한 자치구의 남녀 인구 비교
# ----------------------------------------

st.divider()

st.header("2️⃣ 자치구별 남녀 연령대 인구 비교")

st.write(
    f"**{selected_district} {selected_year}년 "
    f"남녀 연령대별 인구 비교**"
)

# 남녀 데이터 컬럼명
male_columns = [
    f"{selected_year}년_남_거주자_{age}"
    for age in ages
]

female_columns = [
    f"{selected_year}년_여_거주자_{age}"
    for age in ages
]

# 컬럼 확인
missing = [
    col for col in male_columns + female_columns
    if col not in df.columns
]

if missing:
    st.error(f"데이터 컬럼을 찾을 수 없습니다: {missing}")
    st.stop()

# 선택한 자치구 데이터
district_data = df[
    df["구"] == selected_district
].iloc[0]

# 남성 인구
male_population = district_data[male_columns].fillna(0).values

# 여성 인구
female_population = district_data[female_columns].fillna(0).values

# 그래프 데이터 생성
gender_df = pd.DataFrame({
    "연령대": ages * 2,
    "성별": ["남성"] * len(ages) + ["여성"] * len(ages),
    "인구수": list(male_population) + list(female_population)
})

# 남녀 비교 막대그래프
fig2 = px.bar(
    gender_df,
    x="연령대",
    y="인구수",
    color="성별",
    barmode="group",
    title=f"{selected_district} {selected_year}년 남녀 연령대별 인구",
    color_discrete_map={
        "남성": "#FF69B4",
        "여성": "#2E8B57"
    },
    category_orders={
        "연령대": ages,
        "성별": ["남성", "여성"]
    },
    text_auto=False
)

fig2.update_traces(
    hovertemplate=(
        "연령대: %{x}<br>"
        "성별: %{fullData.name}<br>"
        "인구수: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    template="plotly_white",
    height=550,
    xaxis_title="나이",
    yaxis_title="인구수 (명)",
    barmode="group",
    legend_title="성별",
    font=dict(
        family="Malgun Gothic, NanumGothic, sans-serif",
        size=12
    ),
    yaxis=dict(
        tickformat=",d",
        rangemode="tozero"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ----------------------------------------
# 8. 남녀 인구 합계
# ----------------------------------------

male_total = sum(male_population)
female_total = sum(female_population)

st.subheader("📌 남녀 인구 합계")

col1, col2, col3 = st.columns(3)

col1.metric(
    "남성 인구",
    f"{male_total:,.0f}명"
)

col2.metric(
    "여성 인구",
    f"{female_total:,.0f}명"
)

col3.metric(
    "전체 인구",
    f"{male_total + female_total:,.0f}명"
)

st.caption(
    "자료: 서울시 인구 통계 CSV 파일"
)
