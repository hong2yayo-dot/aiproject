
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------
# 1. 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 연령별 인구 분석")
st.write("행정구역, 연도, 성별에 따른 연령대별 인구를 분석합니다.")

# --------------------------------
# 2. CSV 파일 불러오기
# --------------------------------
@st.cache_data
def load_data():

    # 현재 py 파일의 위치
    current_dir = Path(__file__).resolve().parent

    # pages 폴더의 상위 폴더
    parent_dir = current_dir.parent

    # CSV 파일 경로
    file_path = parent_dir / "population (1).csv"

    # 파일 존재 여부 확인
    if not file_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {file_path}"
        )

    # 한글 인코딩 처리
    try:
        df = pd.read_csv(
            file_path,
            encoding="cp949"
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 파일을 읽을 수 없습니다: {e}")
    st.stop()

# --------------------------------
# 3. 데이터 전처리
# --------------------------------

# 행정구역 이름 정리
df["행정구역"] = df["행정구역"].astype(str)

df["지역명"] = df["행정구역"].apply(
    lambda x: x.split("(")[0].strip()
)

df["지역명"] = df["지역명"].replace(
    "서울특별시", "서울특별시 전체"
)

# 숫자 데이터 변환
for col in df.columns:
    if col not in ["행정구역", "지역명"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ""),
            errors="coerce"
        )

# --------------------------------
# 4. 연령대 및 연도 설정
# --------------------------------

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

years = [
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025"
]

# --------------------------------
# 5. 사이드바 선택 메뉴
# --------------------------------

st.sidebar.header("🔍 분석 조건 선택")

# 행정구역 선택
districts = df["지역명"].dropna().unique().tolist()

selected_district = st.sidebar.selectbox(
    "행정구역 선택",
    districts
)

# 연도 선택
selected_year = st.sidebar.selectbox(
    "연도 선택",
    years,
    index=5
)

# 성별 선택
selected_gender = st.sidebar.selectbox(
    "성별 선택",
    ["전체", "남성", "여성"]
)

# --------------------------------
# 6. 선택한 데이터 추출
# --------------------------------

gender_map = {
    "전체": "",
    "남성": "남",
    "여성": "여"
}

gender_code = gender_map[selected_gender]

selected_row = df[
    df["지역명"] == selected_district
].iloc[0]

# 연령대별 컬럼명 생성
if selected_gender == "전체":
    columns = [
        f"{selected_year}년_거주자_{age}"
        for age in ages
    ]
else:
    columns = [
        f"{selected_year}년_{gender_code}_거주자_{age}"
        for age in ages
    ]

# 컬럼 존재 여부 확인
missing_columns = [
    col for col in columns
    if col not in df.columns
]

if missing_columns:
    st.error(
        "데이터 컬럼을 찾을 수 없습니다.\n"
        + ", ".join(missing_columns)
    )
    st.stop()

# 인구 데이터 추출
population = selected_row[columns].fillna(0).values

# 그래프용 데이터 생성
chart_df = pd.DataFrame({
    "연령대": ages,
    "인구수": population
})

# --------------------------------
# 7. 분석 조건 표시
# --------------------------------

st.subheader("📌 분석 조건")

col1, col2, col3 = st.columns(3)

col1.metric(
    "행정구역",
    selected_district
)

col2.metric(
    "선택 연도",
    selected_year + "년"
)

col3.metric(
    "선택 성별",
    selected_gender
)

# --------------------------------
# 8. 꺾은선 그래프
# --------------------------------

st.subheader("📈 연령대별 인구 분포")

fig = px.line(
    chart_df,
    x="연령대",
    y="인구수",
    markers=True,
    title=(
        f"{selected_district} "
        f"{selected_year}년 "
        f"{selected_gender} 연령대별 인구"
    )
)

# 초록색 선과 마커 설정
fig.update_traces(
    line=dict(
        color="green",
        width=3
    ),
    marker=dict(
        color="green",
        size=9
    ),
    hovertemplate=(
        "연령대: %{x}<br>"
        "인구수: %{y:,.0f}명"
        "<extra></extra>"
    )
)

# 그래프 레이아웃
fig.update_layout(
    template="plotly_white",
    height=550,
    hovermode="x unified",
    font=dict(
        family="Malgun Gothic, NanumGothic, sans-serif",
        size=13
    ),
    xaxis=dict(
        title="나이",
        showgrid=False
    ),
    yaxis=dict(
        title="인구수 (명)",
        dtick=1000,
        tickformat=",d",
        rangemode="tozero",
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=1
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# --------------------------------
# 9. 데이터 표 출력
# --------------------------------

st.subheader("📋 연령대별 인구 데이터")

display_df = chart_df.copy()

display_df["인구수"] = display_df["인구수"].map(
    lambda x: f"{x:,.0f}명"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------
# 10. 인구 합계
# --------------------------------

total_population = chart_df["인구수"].sum()

st.success(
    f"선택한 조건의 연령대별 인구 합계: "
    f"{total_population:,.0f}명"
)

st.caption(
    "자료: 서울시 인구 통계 CSV 파일"
)
