
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import osmnx as ox
import json
from pathlib import Path
from streamlit_folium import st_folium

# ----------------------------------
# 1. 기본 설정
# ----------------------------------
st.set_page_config(
    page_title="기차역 승하차 분석",
    page_icon="🚆",
    layout="wide"
)

st.title("🚆 기차역 승하차 인원 분석")
st.caption("기차역 위치, 철도 노선 및 승하차 인원 분석")

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "한국철도공사_역별 승하차 현황_20251231.csv"
STATION_FILE = BASE_DIR / "station_info.csv"


# ----------------------------------
# 2. CSV 파일 읽기
# ----------------------------------
@st.cache_data
def load_csv(path):
    for encoding in ["utf-8-sig", "cp949", "euc-kr"]:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("CSV 인코딩 오류")


if not DATA_FILE.exists():
    st.error("승하차 CSV 파일이 없습니다.")
    st.code(str(DATA_FILE))
    st.stop()

if not STATION_FILE.exists():
    st.error("station_info.csv 파일이 없습니다.")
    st.stop()

try:
    df = load_csv(DATA_FILE)
    location_df = load_csv(STATION_FILE)

except Exception as e:
    st.error(f"데이터 읽기 오류: {e}")
    st.stop()


# ----------------------------------
# 3. 승하차 데이터 분석
# ----------------------------------
required = ["역명", "승차인원", "하차인원"]

if not all(c in df.columns for c in required):
    st.error("승하차 CSV의 열 이름을 확인해 주세요.")
    st.write(df.columns.tolist())
    st.stop()

df["승차인원"] = pd.to_numeric(
    df["승차인원"], errors="coerce"
).fillna(0)

df["하차인원"] = pd.to_numeric(
    df["하차인원"], errors="coerce"
).fillna(0)

# 역별 합계
df = df.groupby("역명", as_index=False)[
    ["승차인원", "하차인원"]
].sum()

df["총이용객"] = (
    df["승차인원"] + df["하차인원"]
)

df = df.sort_values(
    "총이용객", ascending=False
).reset_index(drop=True)

df["순위"] = df.index + 1


# ----------------------------------
# 4. 위치 데이터 전처리
# ----------------------------------
location_df = location_df.rename(columns={
    "역명": "위치역명",
    "위도좌표": "위도",
    "경도좌표": "경도",
    "관련노선": "노선"
})

required_location = [
    "위치역명", "위도", "경도"
]

if not all(c in location_df.columns for c in required_location):
    st.error("역 위치 CSV의 열 이름을 확인해 주세요.")
    st.write(location_df.columns.tolist())
    st.stop()

location_df["위도"] = pd.to_numeric(
    location_df["위도"], errors="coerce"
)

location_df["경도"] = pd.to_numeric(
    location_df["경도"], errors="coerce"
)

def clean_name(name):
    return str(name).strip().replace("역", "")

df["검색역명"] = df["역명"].apply(clean_name)

location_df["검색역명"] = location_df[
    "위치역명"
].apply(clean_name)

# 위치 데이터와 승하차 데이터 결합
map_df = pd.merge(
    df,
    location_df,
    on="검색역명",
    how="inner"
)

map_df = map_df.dropna(
    subset=["위도", "경도"]
)

# 서울 및 수도권 범위
map_df = map_df[
    map_df["위도"].between(36.5, 38.2) &
    map_df["경도"].between(126.2, 128.0)
].copy()

map_df = map_df.drop_duplicates(
    subset=["역명"]
)


# ----------------------------------
# 5. 전체 이용 현황
# ----------------------------------
st.subheader("📊 전체 기차역 이용 현황")

c1, c2, c3 = st.columns(3)

c1.metric("전체 역 개수", f"{len(df):,}개")

c2.metric(
    "전체 승차 인원",
    f"{df['승차인원'].sum():,.0f}명"
)

c3.metric(
    "전체 하차 인원",
    f"{df['하차인원'].sum():,.0f}명"
)

st.divider()


# ----------------------------------
# 6. 역 선택 및 승하차 인원
# ----------------------------------
st.subheader("🚉 역별 승하차 인원")

selected_station = st.selectbox(
    "기차역을 선택하세요.",
    df["역명"].tolist()
)

selected = df[
    df["역명"] == selected_station
].iloc[0]

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

st.write(
    f"**전국 이용객 순위: {int(selected['순위'])}위**"
)

chart_df = pd.DataFrame({
    "구분": ["승차 인원", "하차 인원"],
    "인원": [
        selected["승차인원"],
        selected["하차인원"]
    ]
})

fig = px.bar(
    chart_df,
    x="구분",
    y="인원",
    color="구분",
    text="인원",
    color_discrete_map={
        "승차 인원": "#FF69B4",
        "하차 인원": "#4DA6FF"
    },
    title=f"{selected_station}역 승하차 인원"
)

fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()


# ----------------------------------
# 7. 서울 및 수도권 철도 지도
# ----------------------------------
st.subheader("🗺️ 서울 및 수도권 철도 노선도")

if map_df.empty:
    st.warning("지도에 표시할 역 위치가 없습니다.")
    st.stop()

map_station = st.selectbox(
    "지도에서 확인할 역을 선택하세요.",
    map_df["역명"].tolist(),
    key="map_station"
)

selected_map = map_df[
    map_df["역명"] == map_station
].iloc[0]

# 지도 생성
m = folium.Map(
    location=[
        selected_map["위도"],
        selected_map["경도"]
    ],
    zoom_start=10,
    tiles="CartoDB positron"
)


# ----------------------------------
# 8. 실제 철도 선로 가져오기
# ----------------------------------
@st.cache_data(ttl=86400)
def get_railway_lines():

    ox.settings.timeout = 180

    lines = ox.features_from_bbox(
        bbox=(
            126.6,
            37.3,
            127.3,
            37.85
        ),
        tags={
            "railway": [
                "rail",
                "subway",
                "light_rail",
                "tram"
            ]
        }
    )

    lines = lines[
        lines.geometry.geom_type.isin([
            "LineString",
            "MultiLineString"
        ])
    ]

    return json.loads(lines.to_json())


try:
    with st.spinner("실제 철도 노선을 불러오고 있습니다..."):

        railway_data = get_railway_lines()

    # 노란색 철도 선로
    folium.GeoJson(
        railway_data,
        name="철도 노선",
        style_function=lambda feature: {
            "color": "#FFD700",
            "weight": 5,
            "opacity": 0.95
        },
        tooltip="철도 선로"
    ).add_to(m)

    st.success("철도 노선을 불러왔습니다.")

except Exception as e:
    st.warning(
        "철도 노선을 불러오지 못했습니다. "
        "인터넷 연결 또는 지도 데이터 상태를 확인해 주세요."
    )
    st.caption(str(e))


# ----------------------------------
# 9. 역을 노란색 별로 표시
# ----------------------------------
for _, row in map_df.iterrows():

    is_selected = row["역명"] == map_station

    size = 32 if is_selected else 23

    star_icon = folium.DivIcon(
        html=f"""
        <div style="
            color: #FFD700;
            font-size: {size}px;
            font-weight: bold;
            text-shadow:
                -2px -2px 2px black,
                2px 2px 2px black;
            text-align: center;
            width: 35px;
            height: 35px;
        ">★</div>
        """,
        icon_size=(35, 35),
        icon_anchor=(17, 17)
    )

    folium.Marker(
        location=[
            row["위도"],
            row["경도"]
        ],
        icon=star_icon,
        tooltip=f"{row['역명']}역",
        popup=folium.Popup(
            f"""
            <b>{row['역명']}역</b><br>
            승차: {row['승차인원']:,.0f}명<br>
            하차: {row['하차인원']:,.0f}명<br>
            합계: {row['총이용객']:,.0f}명<br>
            노선: {row.get('노선', '정보 없음')}
            """,
            max_width=300
        )
    ).add_to(m)


# ----------------------------------
# 10. 지도 범례
# ----------------------------------
legend_html = """
<div style="
position: fixed;
bottom: 30px;
left: 30px;
z-index: 9999;
background: white;
padding: 12px;
border: 2px solid gray;
border-radius: 8px;
font-size: 14px;
">
<b>지도 범례</b><br>
<span style="color:#FFD700;
font-size:24px;
text-shadow:1px 1px 2px black;">★</span>
기차역<br>
<span style="color:#FFD700;
font-size:22px;">━━━━</span>
철도 노선
</div>
"""

m.get_root().html.add_child(
    folium.Element(legend_html)
)

folium.LayerControl().add_to(m)

st_folium(
    m,
    use_container_width=True,
    height=650,
    key="railway_map"
)

st.caption(
    "철도 선로 출처: © OpenStreetMap contributors"
)

# 선택 역 정보
st.markdown(f"### ⭐ {map_station}역")

c1, c2, c3 = st.columns(3)

c1.metric(
    "승차 인원",
    f"{selected_map['승차인원']:,.0f}명"
)

c2.metric(
    "하차 인원",
    f"{selected_map['하차인원']:,.0f}명"
)

c3.metric(
    "총 이용객",
    f"{selected_map['총이용객']:,.0f}명"
)

st.divider()


# ----------------------------------
# 11. 이용객 순위 그래프
# ----------------------------------
st.subheader("🏆 기차역 이용객 순위")

top_n = st.slider(
    "표시할 역 개수",
    min_value=5,
    max_value=min(30, len(df)),
    value=min(10, len(df))
)

top_df = df.head(top_n).sort_values(
    "총이용객",
    ascending=True
)

fig = px.bar(
    top_df,
    x="총이용객",
    y="역명",
    orientation="h",
    text="총이용객",
    color="총이용객",
    color_continuous_scale="Blues",
    title=f"이용객 TOP {top_n}"
)

fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside"
)

fig.update_layout(
    xaxis_title="승차 + 하차 인원",
    yaxis_title="기차역",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ----------------------------------
# 12. 전체 순위표
# ----------------------------------
st.subheader("📋 전체 기차역 이용객 순위")

st.dataframe(
    df[
        ["순위", "역명", "승차인원",
         "하차인원", "총이용객"]
    ].style.format({
        "승차인원": "{:,.0f}",
        "하차인원": "{:,.0f}",
        "총이용객": "{:,.0f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.success("기차역 승하차 분석이 완료되었습니다!")
