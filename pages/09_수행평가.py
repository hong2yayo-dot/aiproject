
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import os
import json

from pathlib import Path
from streamlit_folium import st_folium


# --------------------------------------------------
# 1. 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="철도역 이용객 분석",
    page_icon="🚆",
    layout="wide"
)

# pages 폴더의 상위 폴더 경로
BASE_DIR = Path(__file__).resolve().parent.parent

st.title("🚆 철도역별 이용객 분석")
st.write("철도역별 승하차 인원과 이용객 순위를 확인할 수 있습니다.")


# --------------------------------------------------
# 2. CSV 파일 경로 설정
# --------------------------------------------------

PASSENGER_FILE = (
    BASE_DIR / "한국철도공사_역별 승하차 현황_20251231.csv"
)

# 역 위치 파일 후보
STATION_CANDIDATES = [
    BASE_DIR / "station_info.csv",
    BASE_DIR / "국가철도공단_철도역 정보_20250711.csv"
]


# --------------------------------------------------
# 3. CSV 파일 읽기
# --------------------------------------------------

@st.cache_data
def load_csv(file_path):

    encodings = ["utf-8-sig", "cp949", "euc-kr"]

    for encoding in encodings:

        try:
            return pd.read_csv(
                file_path,
                encoding=encoding
            )

        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"CSV 인코딩을 확인할 수 없습니다: {file_path.name}"
    )


# --------------------------------------------------
# 4. 승하차 데이터 불러오기
# --------------------------------------------------

if not PASSENGER_FILE.exists():

    st.error("승하차 데이터 파일을 찾을 수 없습니다.")

    st.write("프로그램이 찾는 폴더:")
    st.code(str(BASE_DIR))

    st.write("필요한 파일:")
    st.write(PASSENGER_FILE.name)

    st.stop()


try:

    passenger_df = load_csv(PASSENGER_FILE)

except Exception as e:

    st.error(f"승하차 데이터 읽기 오류: {e}")
    st.stop()


# --------------------------------------------------
# 5. 역 위치 데이터 불러오기
# --------------------------------------------------

STATION_FILE = next(
    (file for file in STATION_CANDIDATES if file.exists()),
    None
)

if STATION_FILE is None:

    st.error("역 위치 데이터 파일을 찾을 수 없습니다.")

    st.write("프로그램이 찾는 폴더:")
    st.code(str(BASE_DIR))

    st.write("현재 폴더에 있는 파일:")
    st.write([
        file.name
        for file in BASE_DIR.iterdir()
    ])

    st.info(
        "GitHub 저장소 최상위 폴더에 "
        "station_info.csv 또는 "
        "국가철도공단_철도역 정보_20250711.csv를 올려주세요."
    )

    st.stop()


try:

    location_df = load_csv(STATION_FILE)

except Exception as e:

    st.error(f"역 위치 데이터 읽기 오류: {e}")
    st.stop()


# --------------------------------------------------
# 6. 역 위치 데이터 컬럼 통일
# --------------------------------------------------

# station_info.csv 형식
if {"역명", "위도", "경도", "노선"}.issubset(location_df.columns):

    location_df = location_df.copy()

# 국가철도공단 원본 CSV 형식
elif {"역이름", "위도좌표", "경도좌표"}.issubset(location_df.columns):

    location_df = location_df.rename(
        columns={
            "역이름": "역명",
            "위도좌표": "위도",
            "경도좌표": "경도",
            "관련노선": "노선",
            "주소": "주소"
        }
    )

else:

    st.error("역 위치 데이터의 컬럼 구성이 올바르지 않습니다.")
    st.write("현재 컬럼:", list(location_df.columns))
    st.stop()


# --------------------------------------------------
# 7. 데이터 정리
# --------------------------------------------------

required_columns = [
    "역명",
    "승차인원",
    "하차인원"
]

if not set(required_columns).issubset(passenger_df.columns):

    st.error("승하차 데이터의 컬럼을 확인해 주세요.")
    st.write("필요한 컬럼:", required_columns)
    st.write("현재 컬럼:", list(passenger_df.columns))
    st.stop()


passenger_df = passenger_df.copy()
location_df = location_df.copy()

# 숫자 데이터 변환
passenger_df["승차인원"] = pd.to_numeric(
    passenger_df["승차인원"],
    errors="coerce"
).fillna(0)

passenger_df["하차인원"] = pd.to_numeric(
    passenger_df["하차인원"],
    errors="coerce"
).fillna(0)

location_df["위도"] = pd.to_numeric(
    location_df["위도"],
    errors="coerce"
)

location_df["경도"] = pd.to_numeric(
    location_df["경도"],
    errors="coerce"
)


# 역 이름 비교를 위한 정리
def normalize_station_name(name):

    name = str(name).strip()
    name = name.replace(" ", "")
    name = name.replace("역", "")

    return name


passenger_df["역이름_비교"] = (
    passenger_df["역명"].apply(normalize_station_name)
)

location_df["역이름_비교"] = (
    location_df["역명"].apply(normalize_station_name)
)


# --------------------------------------------------
# 8. 역별 승하차 인원 합계
# --------------------------------------------------

ranking_df = (
    passenger_df
    .groupby("역이름_비교", as_index=False)
    .agg({
        "승차인원": "sum",
        "하차인원": "sum"
    })
)

ranking_df["총이용객"] = (
    ranking_df["승차인원"] +
    ranking_df["하차인원"]
)


# 역 이름 다시 연결
station_names = (
    passenger_df[
        ["역이름_비교", "역명"]
    ]
    .drop_duplicates("역이름_비교")
)

ranking_df = ranking_df.merge(
    station_names,
    on="역이름_비교",
    how="left"
)


# 이용객 순위 계산
ranking_df = ranking_df.sort_values(
    "총이용객",
    ascending=False
).reset_index(drop=True)

ranking_df["순위"] = ranking_df.index + 1


# --------------------------------------------------
# 9. 역 위치와 승하차 데이터 결합
# --------------------------------------------------

location_df = location_df.dropna(
    subset=["위도", "경도"]
)

# 역 위치 데이터에서 중복 역 제거
location_df = location_df.drop_duplicates(
    subset=["역이름_비교"]
)

merged_df = pd.merge(
    ranking_df,
    location_df,
    on="역이름_비교",
    how="left",
    suffixes=("", "_위치")
)


# --------------------------------------------------
# 10. 이용객 순위 그래프
# --------------------------------------------------

st.subheader("📊 철도역별 이용객 순위")

top_count = st.slider(
    "그래프에 표시할 역 개수",
    min_value=5,
    max_value=30,
    value=15
)

top_df = ranking_df.head(top_count).copy()

fig = px.bar(
    top_df.sort_values("총이용객"),
    x="총이용객",
    y="역명",
    orientation="h",
    text="총이용객",
    title=f"철도역 이용객 TOP {top_count}",
    labels={
        "총이용객": "승차 + 하차 인원",
        "역명": "철도역"
    }
)

fig.update_traces(
    marker_color="#FFD700",
    texttemplate="%{text:,.0f}명",
    textposition="outside"
)

fig.update_layout(
    height=650,
    xaxis_tickformat=",",
    yaxis_title="역 이름"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 11. 역 선택
# --------------------------------------------------

st.subheader("🔎 역별 상세 이용객 정보")

station_options = ranking_df["역명"].tolist()

selected_station = st.selectbox(
    "확인할 역을 선택하세요.",
    station_options
)

selected_row = ranking_df[
    ranking_df["역명"] == selected_station
].iloc[0]


col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "승차 인원",
        f"{selected_row['승차인원']:,.0f}명"
    )

with col2:

    st.metric(
        "하차 인원",
        f"{selected_row['하차인원']:,.0f}명"
    )

with col3:

    st.metric(
        "총 이용객",
        f"{selected_row['총이용객']:,.0f}명"
    )

st.write(f"**이용객 순위: {int(selected_row['순위'])}위**")


# --------------------------------------------------
# 12. 서울 지역 역 지도 데이터
# --------------------------------------------------

# 서울 및 수도권 중심 지도 범위
map_df = merged_df[
    (merged_df["위도"] >= 37.30) &
    (merged_df["위도"] <= 37.85) &
    (merged_df["경도"] >= 126.60) &
    (merged_df["경도"] <= 127.30)
].copy()

map_df = map_df.dropna(
    subset=["위도", "경도"]
)


# --------------------------------------------------
# 13. 철도 노선 데이터 가져오기
# --------------------------------------------------

@st.cache_data(ttl=86400, show_spinner=False)
def load_rail_lines():

    try:

        import osmnx as ox

        tags = {
            "railway": [
                "rail",
                "subway",
                "light_rail",
                "tram"
            ]
        }

        rail_gdf = ox.features_from_bbox(
            bbox=(
                126.60,
                37.30,
                127.30,
                37.85
            ),
            tags=tags
        )

        if rail_gdf.empty:
            return None

        # 선 형태의 철도 데이터만 사용
        rail_gdf = rail_gdf[
            rail_gdf.geometry.geom_type.isin(
                ["LineString", "MultiLineString"]
            )
        ]

        if rail_gdf.empty:
            return None

        return rail_gdf.to_json()

    except Exception:
        return None


# --------------------------------------------------
# 14. 지도 만들기
# --------------------------------------------------

st.subheader("🗺️ 서울 지역 철도역 및 노선 지도")

st.caption(
    "노란색 선은 지도 서비스에서 가져온 철도 선로 정보이며, "
    "노란색 별표는 역 위치입니다."
)

rail_geojson = None

with st.spinner("철도 노선 정보를 불러오는 중입니다..."):

    rail_geojson = load_rail_lines()


rail_map = folium.Map(
    location=[37.55, 126.98],
    zoom_start=11,
    tiles="OpenStreetMap"
)


# --------------------------------------------------
# 15. 철도 노선 노란색으로 표시
# --------------------------------------------------

if rail_geojson:

    folium.GeoJson(
        data=rail_geojson,
        name="철도 노선",
        style_function=lambda feature: {
            "color": "#FFD700",
            "weight": 5,
            "opacity": 0.9
        }
    ).add_to(rail_map)

else:

    st.warning(
        "철도 노선 정보를 불러오지 못했습니다. "
        "지도 서비스 연결 상태를 확인해 주세요."
    )


# --------------------------------------------------
# 16. 역을 노란색 별표로 표시
# --------------------------------------------------

for _, row in map_df.iterrows():

    station_name = str(row["역명"])

    is_selected = (
        normalize_station_name(station_name)
        ==
        normalize_station_name(selected_station)
    )

    # 선택한 역은 별을 더 크게 표시
    star_size = 42 if is_selected else 28

    star_color = "#FFB800" if is_selected else "#FFD700"

    popup_html = f"""
    <div style="width:190px; font-size:14px;">
        <h4>{station_name}</h4>
        <hr>
        <b>승차 인원:</b> {row['승차인원']:,.0f}명<br>
        <b>하차 인원:</b> {row['하차인원']:,.0f}명<br>
        <b>총 이용객:</b> {row['총이용객']:,.0f}명<br>
        <b>이용객 순위:</b> {int(row['순위'])}위
    </div>
    """

    folium.Marker(
        location=[
            row["위도"],
            row["경도"]
        ],

        popup=folium.Popup(
            popup_html,
            max_width=250
        ),

        tooltip=station_name,

        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size:{star_size}px;
                color:{star_color};
                text-shadow:
                    -2px -2px 2px black,
                    2px 2px 2px black;
                text-align:center;
                width:45px;
                height:45px;
                line-height:45px;
            ">
                ★
            </div>
            """,

            icon_size=(45, 45),
            icon_anchor=(22, 22)
        )

    ).add_to(rail_map)


# 지도 범례
legend_html = """
<div style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    width: 150px;
    background-color: white;
    border: 2px solid grey;
    z-index: 9999;
    font-size: 14px;
    padding: 10px;
">
<b>지도 범례</b><br>
<span style="color:#FFD700;">━━</span> 철도 노선<br>
<span style="color:#FFB800;">★</span> 선택 역<br>
<span style="color:#FFD700;">★</span> 일반 역
</div>
"""

rail_map.get_root().html.add_child(
    folium.Element(legend_html)
)


folium.LayerControl().add_to(rail_map)


# 지도 화면 출력
st_folium(
    rail_map,
    width=None,
    height=650,
    key="railway_map"
)


# --------------------------------------------------
# 17. 선택한 역의 위치 정보
# --------------------------------------------------

selected_location = merged_df[
    merged_df["역이름_비교"] ==
    normalize_station_name(selected_station)
]

if not selected_location.empty:

    location_row = selected_location.iloc[0]

    if pd.notna(location_row["위도"]) and pd.notna(location_row["경도"]):

        st.subheader("📍 선택한 역 위치 정보")

        st.write(f"**역 이름:** {selected_station}")

        if "노선" in location_row.index:

            st.write(
                f"**노선:** {location_row['노선']}"
            )

        if "주소" in location_row.index:

            st.write(
                f"**주소:** {location_row['주소']}"
            )

    else:

        st.info(
            "선택한 역의 위치 정보가 위치 데이터에 없습니다."
        )


# --------------------------------------------------
# 18. 전체 데이터 표
# --------------------------------------------------

st.subheader("📋 전체 철도역 이용객 순위표")

display_df = ranking_df[
    [
        "순위",
        "역명",
        "승차인원",
        "하차인원",
        "총이용객"
    ]
].copy()

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 19. 데이터 안내
# --------------------------------------------------

st.divider()

st.caption(
    "자료: 한국철도공사 역별 승하차 현황 및 "
    "국가철도공단 철도역 위치 정보"
)

st.caption(
    "지도에 표시되는 철도 선로는 OpenStreetMap의 "
    "지도 데이터를 이용합니다."
)
