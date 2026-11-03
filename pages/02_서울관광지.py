
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)

# 서울 주요 관광지 TOP 10
SPOTS = [
    {
        "name": "경복궁",
        "en": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선 왕조의 대표 궁궐입니다. 한복을 입고 전통 건축과 정원을 둘러볼 수 있습니다."
    },
    {
        "name": "명동",
        "en": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9869,
        "description": "화장품과 패션 쇼핑, 다양한 길거리 음식으로 유명한 번화가입니다."
    },
    {
        "name": "남산서울타워",
        "en": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "서울의 아름다운 전경과 야경을 감상할 수 있는 대표적인 전망 명소입니다."
    },
    {
        "name": "북촌한옥마을",
        "en": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥이 모여 있는 마을로 한국의 옛 주거 문화를 느낄 수 있습니다."
    },
    {
        "name": "인사동",
        "en": "Insadong",
        "lat": 37.5710,
        "lon": 126.9850,
        "description": "전통 공예품과 기념품 상점, 전통 찻집이 모여 있는 거리입니다."
    },
    {
        "name": "창덕궁",
        "en": "Changdeokgung Palace",
        "lat": 37.5794,
        "lon": 126.9910,
        "description": "유네스코 세계유산으로 지정된 궁궐로 아름다운 후원이 유명합니다."
    },
    {
        "name": "홍대거리",
        "en": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "description": "젊은 문화와 음악, 공연, 개성 있는 상점으로 유명한 거리입니다."
    },
    {
        "name": "동대문디자인플라자",
        "en": "Dongdaemun Design Plaza",
        "lat": 37.5669,
        "lon": 127.0095,
        "description": "독특한 건축물과 전시 공간으로 유명한 서울의 디자인 명소입니다."
    },
    {
        "name": "청계천",
        "en": "Cheonggyecheon Stream",
        "lat": 37.5692,
        "lon": 126.9788,
        "description": "서울 도심을 가로지르는 하천으로 산책과 야경 감상에 좋습니다."
    },
    {
        "name": "롯데월드타워·서울스카이",
        "en": "Lotte World Tower & Seoul Sky",
        "lat": 37.5125,
        "lon": 127.1025,
        "description": "서울의 대표적인 초고층 랜드마크로 전망대에서 멋진 도시 전망을 볼 수 있습니다."
    }
]

# 제목
st.title("🇰🇷 외국인 관광객 추천 서울 명소 TOP 10")

st.write(
    "서울을 방문하는 외국인 관광객에게 추천하는 "
    "대표 관광지 10곳을 지도에서 확인해 보세요!"
)

st.caption(
    "※ 공식 통계 순위가 아닌 대표 관광 명소 추천 목록입니다."
)

# 서울 지도 생성
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 지도에 관광지 마커 표시
for index, spot in enumerate(SPOTS, start=1):

    popup_html = f"""
    <div style="width:230px">
        <b>{index}. {spot['name']}</b><br>
        <i>{spot['en']}</i><br><br>
        {spot['description']}
    </div>
    """

    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        tooltip=f"{index}. {spot['name']}",
        popup=folium.Popup(
            popup_html,
            max_width=280
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#e53935;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:28px;
                height:28px;
                line-height:24px;
                text-align:center;
                font-weight:bold;
                box-shadow:0 1px 4px #555;">
                {index}
            </div>
            """,
            icon_size=(28, 28),
            icon_anchor=(14, 14)
        )
    ).add_to(m)

# 지도 출력
st.subheader("📍 서울 주요 관광지 지도")

st_folium(
    m,
    use_container_width=True,
    height=560,
    returned_objects=[]
)

# 관광지 설명
st.subheader("🗺️ 관광지 간단 소개")

for i in range(0, len(SPOTS), 2):

    cols = st.columns(2)

    for col, spot in zip(cols, SPOTS[i:i+2]):

        number = SPOTS.index(spot) + 1

        with col:

            st.markdown(
                f"### {number}. {spot['name']}"
            )

            st.caption(spot["en"])

            st.write(spot["description"])

            st.markdown(
                f"[지도에서 위치 보기](https://www.google.com/maps/search/?api=1&query={spot['lat']},{spot['lon']})"
            )

            st.divider()

st.info(
    "서울의 주요 관광지를 지도와 설명으로 확인할 수 있습니다."
)
