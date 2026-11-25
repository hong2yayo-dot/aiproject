
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from pathlib import Path
import json

st.set_page_config(
    page_title="기차역 승하차 분석",
    page_icon="🚆",
    layout="wide"
)

st.title("🚆 기차역 승하차 인원 분석")
st.caption("2025년 12월 31일 기준 데이터")

# --------------------------------
# 1. 파일 경로
# --------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "한국철도공사_역별 승하차 현황_20251231.csv"
STATION_FILE = BASE_DIR / "station_info.csv"
ROUTE_FILE = BASE_DIR / "railway_routes.geojson"

# --------------------------------
# 2. CSV 파일 읽기
# --------------------------------
@st.cache_data
def load_data(file_path):
    for encoding in ["cp949", "utf-8-sig", "euc-kr"]:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("CSV 인코딩을 확인해 주세요.")

if not DATA_FILE.exists():
    st.error("승하차 데이터 파일을 찾을 수 없습니다.")
    st.code(str(DATA_FILE))
    st.info("CSV 파일을 pages 폴더의 상위 폴더에 넣어 주세요.")
    st.stop()

try:
    df = load_data(DATA_FILE)

except Exception as e:
    st.error(f"승하차 데이터 읽기 오류: {e}")
    st.stop()

# --------------------------------
# 3. 데이터 확인 및 전처리
# --------------------------------
required_columns = ["역명", "승차인원", "하차인원"]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    st.error(f"CSV에 필요한 열이 없습니다: {missing}")
    st.write("현재 CSV 열:", df.columns.tolist())
    st.stop()

df["승차인원"] = pd.to_numeric(
    df["승차인원"], errors="coerce"
).fillna(0)

df["하차인원"] = pd.to_numeric(
    df["하차인원"], errors="coerce"
).fillna(0)

df["총이용객"] = df["승차인원"] + df["하차인원"]

df = df.groupby("역명", as_index=False)[
    ["승차인원", "하차인원", "총이용객"]
].sum()

df = df.sort_values(
    "총이용객", ascending=False
).reset_index(drop=True)

df["순위"] = df.index + 1

# --------------------------------
# 4. 전체 현황
# --------------------------------
st.subheader("📊 전체 이용 현황")

c1, c2, c3 = st.columns(3)

c1.metric("기차역 수", f"{len(df):,}개")
c2.metric("총 승차 인원", f"{df['승차인원'].sum():,.0f}명")
c3.metric("총 하차 인원", f"{df['하차인원'].sum():,.0f}명")

st.divider()

# --------------------------------
# 5. 역 선택
# --------------------------------
st.subheader("🚉 역별 승하차 인원")

station = st.selectbox(
    "기차역을 선택하세요.",
    df["역명"].tolist()
)

selected = df[df["역명"] == station].iloc[0]

c1, c2, c3 = st.columns(3)

c1.metric("승차 인원", f"{selected['승차인원']:,.0f}명")
c2.metric("하차 인원", f"{selected['하차인원']:,.0f}명")
c3.metric("총 이용객", f"{selected['총이용객']:,.0f}명")

st.write(f"**{station}역의 전국 이용객 순위: {int(selected['순위'])}위**")

# 승차 및 하차 그래프
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
    title=f"{station}역 승하차 인원"
)

fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# --------------------------------
# 6. 서울 지도
# --------------------------------
st.subheader("🗺️ 서울 및 수도권 기차역 지도")

if STATION_FILE.exists():

    try:
        location_df = load_data(STATION_FILE)

        # 위치 파일 열 이름 통일
        location_df = location_df.rename(columns={
            "역이름": "역명",
            "위도좌표": "위도",
            "경도좌표": "경도"
        })

        if not {"역명", "위도", "경도"}.issubset(
            location_df.columns
        ):
            st.error(
                "station_info.csv에는 역명, 위도, 경도 열이 필요합니다."
            )
        else:
            location_df["위도"] = pd.to_numeric(
                location_df["위도"], errors="coerce"
            )
            location_df["경도"] = pd.to_numeric(
                location_df["경도"], errors="coerce"
            )

            map_df = pd.merge(
                df,
                location_df,
                on="역명",
                how="inner"
            )

            map_df = map_df.dropna(
                subset=["위도", "경도"]
            )

            # 서울 및 수도권 범위
            map_df = map_df[
                map_df["위도"].between(36.5, 38.2) &
                map_df["경도"].between(126.2, 128.0)
            ]

            if not map_df.empty:

                m = folium.Map(
                    location=[37.5665, 126.9780],
                    zoom_start=9,
                    tiles="CartoDB positron"
                )

                for _, row in map_df.iterrows():

                    color = (
                        "red" if row["역명"] == station
                        else "blue"
                    )

                    folium.CircleMarker(
                        location=[
                            row["위도"],
                            row["경도"]
                        ],
                        radius=8,
                        color=color,
                        fill=True,
                        fill_opacity=0.8,
                        popup=(
                            f"{row['역명']}역<br>"
                            f"승차: {row['승차인원']:,.0f}명<br>"
                            f"하차: {row['하차인원']:,.0f}명<br>"
                            f"합계: {row['총이용객']:,.0f}명"
                        )
                    ).add_to(m)

                # 실제 노선 GeoJSON이 있을 때만 표시
                if ROUTE_FILE.exists():
                    with open(
                        ROUTE_FILE, "r", encoding="utf-8"
                    ) as f:
                        route_data = json.load(f)

                    folium.GeoJson(
                        route_data,
                        tooltip=folium.GeoJsonTooltip(
                            fields=["line_name"],
                            aliases=["노선:"]
                        ),
                        style_function=lambda feature: {
                            "color": "#E53935",
                            "weight": 4
                        }
                    ).add_to(m)

                st_folium(
                    m,
                    use_container_width=True,
                    height=550
                )

            else:
                st.warning("서울 및 수도권에 해당하는 역 위치가 없습니다.")

    except Exception as e:
        st.error(f"지도 데이터 처리 오류: {e}")

else:
    st.info(
        "역 위치 데이터가 아직 없습니다. "
        "station_info.csv를 추가하면 지도에 역 위치가 표시됩니다."
    )

    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=10
    )

    st_folium(
        m,
        use_container_width=True,
        height=450
    )

st.divider()

# --------------------------------
# 7. 이용객 순위 그래프
# --------------------------------
st.subheader("🏆 기차역 이용객 순위")

top_n = st.slider(
    "표시할 역 개수",
    5, min(30, len(df)), min(10, len(df))
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
    title=f"이용객 TOP {top_n}"
)

fig.update_traces(
    texttemplate="%{text:,.0f}명",
    textposition="outside"
)

fig.update_layout(
    showlegend=False,
    xaxis_title="승차 + 하차 인원",
    yaxis_title="기차역"
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------
# 8. 전체 순위표
# --------------------------------
st.subheader("📋 전체 기차역 순위")

st.dataframe(
    df[
        ["순위", "역명", "승차인원", "하차인원", "총이용객"]
    ].style.format({
        "승차인원": "{:,.0f}",
        "하차인원": "{:,.0f}",
        "총이용객": "{:,.0f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.success("분석이 완료되었습니다!")
