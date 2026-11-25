
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from pathlib import Path
import json

# --------------------------------
# 1. 기본 설정
# --------------------------------
st.set_page_config(
    page_title="기차역 승하차 인원 분석",
    page_icon="🚆",
    layout="wide"
)

st.title("🚆 전국 기차역 승하차 인원 분석")
st.caption("기차역별 이용객 현황과 철도 노선을 확인하는 사이트")

# pages 폴더의 상위 폴더
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "한국철도공사_역별 승하차 현황_20251231.csv"
STATION_FILE = BASE_DIR / "station_info.csv"
ROUTE_FILE = BASE_DIR / "railway_routes.geojson"


# --------------------------------
# 2. CSV 파일 읽기
# --------------------------------
@st.cache_data
def read_csv_file(path):
    for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    return pd.read_csv(path)


try:
    df = read_csv_file(DATA_FILE)

    station_df = read_csv_file(STATION_FILE)

except Exception as e:
    st.error(f"데이터 파일을 읽을 수 없습니다: {e}")
    st.stop()


# --------------------------------
# 3. 판다스 데이터 분석
# --------------------------------
df["승차인원"] = pd.to_numeric(
    df["승차인원"], errors="coerce"
).fillna(0)

df["하차인원"] = pd.to_numeric(
    df["하차인원"], errors="coerce"
).fillna(0)

df["총이용객"] = df["승차인원"] + df["하차인원"]

# 총 이용객 순위
df = df.sort_values(
    "총이용객", ascending=False
).reset_index(drop=True)

df["순위"] = df.index + 1


# --------------------------------
# 4. 역 위치 데이터 정리
# --------------------------------
station_df = station_df.rename(columns={
    "역이름": "역명",
    "위도좌표": "위도",
    "경도좌표": "경도"
})

for col in ["위도", "경도"]:
    station_df[col] = pd.to_numeric(
        station_df[col], errors="coerce"
    )

# 역명에서 '역' 글자 제거
def clean_name(name):
    return str(name).strip().replace("역", "")

df["역명_검색"] = df["역명"].apply(clean_name)
station_df["역명_검색"] = station_df["역명"].apply(clean_name)

# 승하차 데이터와 위치 데이터 결합
merged = pd.merge(
    df,
    station_df,
    on="역명_검색",
    how="inner",
    suffixes=("", "_위치")
)

merged = merged.dropna(
    subset=["위도", "경도"]
)

# 서울 및 수도권 주변 역을 지도에 표시
seoul_stations = merged[
    merged["위도"].between(36.5, 38.2) &
    merged["경도"].between(126.2, 128.0)
].copy()


# --------------------------------
# 5. 전체 이용객 현황
# --------------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "분석 역 개수",
    f"{df['역명'].nunique():,}개"
)

col2.metric(
    "전체 승차 인원",
    f"{df['승차인원'].sum():,.0f}명"
)

col3.metric(
    "전체 하차 인원",
    f"{df['하차인원'].sum():,.0f}명"
)

st.divider()


# --------------------------------
# 6. 역 선택
# --------------------------------
st.subheader("🔍 역별 승하차 인원 확인")

if seoul_stations.empty:
    st.warning("서울 및 수도권 역 위치 자료를 확인해 주세요.")
    st.stop()

station_names = sorted(
    seoul_stations["역명"].unique()
)

selected_station = st.selectbox(
    "확인하고 싶은 기차역을 선택하세요.",
    station_names
)

selected = seoul_stations[
    seoul_stations["역명"] == selected_station
].iloc[0]


# --------------------------------
# 7. 선택 역의 승하차 인원
# --------------------------------
st.markdown(f"### 🚉 {selected_station}역 이용 현황")

c1, c2, c3 = st.columns(3)

c1.metric(
    "승차 인원",
    f"{selected['승차인원']:,.0f}명"
)

c2.metric(
    "하차 인원",
    f"{selected['하차인원']:,.0f}명"
)

c3.metric(
    "총 이용객",
    f"{selected['총이용객']:,.0f}명"
)

st.divider()


# --------------------------------
# 8. 서울 지도와 철도 노선 표시
# --------------------------------
st.subheader("🗺️ 서울 및 수도권 철도 지도")

m = folium.Map(
    location=[selected["위도"], selected["경도"]],
    zoom_start=10,
    tiles="CartoDB positron"
)

# GeoJSON 실제 철도 노선 표시
if ROUTE_FILE.exists():

    with open(ROUTE_FILE, "r", encoding="utf-8") as f:
        route_data = json.load(f)

    route_colors = [
        "#E53935", "#1E88E5", "#43A047",
        "#8E24AA", "#FB8C00", "#00897B",
        "#6D4C41", "#3949AB"
    ]

    def route_style(feature):
        line_name = str(
            feature.get("properties", {}).get(
                "line_name", "철도 노선"
            )
        )

        color_index = sum(
            ord(ch) for ch in line_name
        ) % len(route_colors)

        return {
            "color": route_colors[color_index],
            "weight": 4,
            "opacity": 0.8
        }

    folium.GeoJson(
        route_data,
        name="철도 노선",
        style_function=route_style,
        tooltip=folium.GeoJsonTooltip(
            fields=["line_name"],
            aliases=["노선명:"]
        )
    ).add_to(m)

else:
    st.warning(
        "철도 노선 GeoJSON 파일이 없습니다. "
        "역 위치는 표시하지만 실제 노선은 표시하지 않습니다."
    )


# 역 위치 표시
for _, row in seoul_stations.iterrows():

    is_selected = row["역명"] == selected_station

    color = "red" if is_selected else "blue"

    folium.CircleMarker(
        location=[row["위도"], row["경도"]],
        radius=9 if is_selected else 5,
        color=color,
        fill=True,
        fill_opacity=0.85,
        tooltip=f"{row['역명']}역",
        popup=(
            f"<b>{row['역명']}역</b><br>"
            f"승차: {row['승차인원']:,.0f}명<br>"
            f"하차: {row['하차인원']:,.0f}명<br>"
            f"합계: {row['총이용객']:,.0f}명"
        )
    ).add_to(m)

folium.LayerControl().add_to(m)

st_folium(
    m,
    width=None,
    height=550,
    key="railway_map"
)


# --------------------------------
# 9. 이용객 순위 그래프
# --------------------------------
st.divider()
st.subheader("🏆 기차역별 이용객 순위")

top_n = st.slider(
    "그래프에 표시할 역 개수",
    min_value=5,
    max_value=30,
    value=10
)

top_df = df.head(top_n).sort_values(
    "총이용객", ascending=True
)

fig = px.bar(
    top_df,
    x="총이용객",
    y="역명",
    orientation="h",
    text="총이용객",
    color="총이용객",
    color_continuous_scale="Blues",
    labels={
        "총이용객": "승차 + 하차 인원",
        "역명": "기차역"
    },
    title=f"이용객 상위 {top_n}개 역"
)

fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside"
)

fig.update_layout(
    yaxis_title="기차역",
    xaxis_title="총 이용객 수",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------
# 10. 전체 역 순위표
# --------------------------------
st.divider()
st.subheader("📊 전체 기차역 이용객 순위표")

show_df = df[
    ["순위", "역명", "승차인원", "하차인원", "총이용객"]
].copy()

st.dataframe(
    show_df.style.format({
        "승차인원": "{:,.0f}",
        "하차인원": "{:,.0f}",
        "총이용객": "{:,.0f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.success("기차역 승하차 인원 분석이 완료되었습니다!")
