
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
    page_icon="🇰🇷",
    layout="wide"
)

SPOTS = [
    {"name": "경복궁", "en": "Gyeongbokgung Palace", "lat": 37.5796, "lon": 126.9770, "description": "조선 왕조의 대표 궁궐입니다. 한복을 입고 전통 건축과 정원을 둘러볼 수 있습니다."},
    {"name": "명동", "en": "Myeongdong", "lat": 37.5636, "lon": 126.9869, "description": "화장품과 패션 쇼핑, 다양한 길거리 음식으로 유명한 번화가입니다."},
    {"name": "남산서울타워", "en": "N Seoul Tower", "lat": 37.5512, "lon": 126.9882, "description": "서울의 아름다운 전경과 야경을 감상할 수 있는 대표 전망 명소입니다."},
    {"name": "북촌한옥마을", "en": "Bukchon Hanok Village", "lat": 37.5826, "lon": 126.9830, "description": "전통 한옥이 모여 있는 마을로 한국의 옛 주거 문화를 느낄 수 있습니다."},
    {"name": "인사동", "en": "Insadong", "lat": 37.5710, "lon": 126.9850, "description": "전통 공예품과 기념품 상점, 전통 찻집이 모여 있는 거리입니다."},
    {"name": "창덕궁", "en": "Changdeokgung Palace", "lat": 37.5794, "lon": 126.9910, "description": "유네스코 세계유산으로 지정된 궁궐로 아름다운 후원이 유명합니다."},
    {"name": "홍대거리", "en": "Hongdae", "lat": 37.5563, "lon": 126.9236, "description": "젊은 문화와 음악, 공연, 개성 있는 상점으로 유명한 거리입니다."},
    {"name": "동대문디자인플라자", "en": "Dongdaemun Design Plaza", "lat": 37.5669, "lon": 127.0095, "description": "독특한 건축물과 전시 공간으로 유명한 서울의 디자인 명소입니다."},
    {"name": "청계천", "en": "Cheonggyecheon Stream", "lat": 37.5692, "lon": 126.9788, "description": "서울 도심을 가로지르는 하천으로 산책과 야경 감상에 좋습니다."},
    {"name": "롯데월드타워·서울스카이", "en": "Lotte World Tower & Seoul Sky", "lat": 37.5125, "lon": 127.1025, "description": "서울의 대표적인 초고층 랜드마크로 전망대에서 멋진 도시 전망을 볼 수 있습니다."}
]

RESTAURANTS = [
    {"name": "토속촌 삼계탕", "lat": 37.5770, "lon": 126.9718, "description": "경복궁 인근의 삼계탕 전문점.", "day": "1일차", "meal": "점심"},
    {"name": "광장시장 먹거리 구역", "lat": 37.5700, "lon": 126.9997, "description": "빈대떡과 김밥 등 한국 길거리 음식을 즐길 수 있는 곳.", "day": "1일차", "meal": "저녁"},
    {"name": "명동교자 본점", "lat": 37.5637, "lon": 126.9850, "description": "칼국수와 만두로 잘 알려진 명동의 식당.", "day": "2일차", "meal": "점심"},
    {"name": "홍대 주변 식당가", "lat": 37.5560, "lon": 126.9238, "description": "한식, 분식, 면 요리 등 다양한 식당이 모여 있는 지역.", "day": "2일차", "meal": "저녁"}
]

st.title("🇰🇷 외국인 관광객 추천 서울 명소 TOP 10")
st.write("서울의 대표 관광지와 1박 2일 추천 여행 일정을 확인해 보세요.")
st.caption("※ 관광지는 공식 통계 순위가 아닌 추천 목록입니다.")

# 지도 만들기
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 관광지 표시
for index, spot in enumerate(SPOTS, start=1):
    popup = f"""
    <b>{index}. {spot['name']}</b><br>
    {spot['en']}<br><br>
    {spot['description']}
    """

    folium.Marker(
        [spot["lat"], spot["lon"]],
        tooltip=spot["name"],
        popup=folium.Popup(popup, max_width=280),
        icon=folium.DivIcon(
            html=f"""
            <div style="background:#e53935;color:white;
            border:2px solid white;border-radius:50%;
            width:28px;height:28px;line-height:24px;
            text-align:center;font-weight:bold;">
            {index}</div>
            """,
            icon_size=(28, 28),
            icon_anchor=(14, 14)
        )
    ).add_to(m)

# 식당 표시
for restaurant in RESTAURANTS:
    popup = f"""
    <b>🍽️ {restaurant['name']}</b><br>
    {restaurant['day']} · {restaurant['meal']}<br><br>
    {restaurant['description']}
    """

    folium.Marker(
        [restaurant["lat"], restaurant["lon"]],
        tooltip=restaurant["name"],
        popup=folium.Popup(popup, max_width=280),
        icon=folium.Icon(
            color="green",
            icon="cutlery",
            prefix="fa"
        )
    ).add_to(m)

# 지도 출력
st.subheader("📍 서울 관광지 및 식당 지도")
st.write("🔴 빨간색: 관광지 / 🟢 초록색: 식당")

st_folium(
    m,
    use_container_width=True,
    height=560,
    returned_objects=[]
)

# 관광지 소개
st.subheader("🗺️ 관광지 간단 소개")

for i in range(0, len(SPOTS), 2):
    cols = st.columns(2)

    for col, spot in zip(cols, SPOTS[i:i+2]):
        number = SPOTS.index(spot) + 1

        with col:
            st.markdown(f"### {number}. {spot['name']}")
            st.caption(spot["en"])
            st.write(spot["description"])
            st.markdown(
                f"[지도에서 위치 보기](https://www.google.com/maps/search/?api=1&query={spot['lat']},{spot['lon']})"
            )
            st.divider()

# 1박 2일 일정
st.header("🧳 서울 1박 2일 추천 여행 일정")

day1 = [
    ("09:30", "경복궁", "궁궐 관람"),
    ("12:00", "토속촌 삼계탕", "점심 식사"),
    ("13:30", "북촌한옥마을", "한옥 골목 산책"),
    ("15:00", "인사동", "전통 공예품과 기념품 구경"),
    ("17:00", "청계천", "도심 산책"),
    ("18:30", "광장시장", "저녁 식사와 먹거리"),
    ("20:00", "동대문디자인플라자", "야간 경관 감상")
]

day2 = [
    ("09:30", "창덕궁", "궁궐 관람"),
    ("12:00", "명동교자 본점", "점심 식사"),
    ("13:30", "명동", "쇼핑과 거리 구경"),
    ("16:00", "남산서울타워", "서울 전망 감상"),
    ("18:30", "홍대 주변 식당가", "저녁 식사"),
    ("20:00", "홍대거리", "공연과 상점 구경")
]

col1, col2 = st.columns(2)

with col1:
    st.subheader("첫째 날")

    for time, place, detail in day1:
        st.markdown(f"**{time} · {place}**")
        st.write(detail)

with col2:
    st.subheader("둘째 날")

    for time, place, detail in day2:
        st.markdown(f"**{time} · {place}**")
        st.write(detail)

# 식당 상세 소개
st.subheader("🍽️ 일정에 포함된 식당")

for restaurant in RESTAURANTS:
    st.markdown(
        f"**{restaurant['day']} {restaurant['meal']} — {restaurant['name']}**"
    )
    st.write(restaurant["description"])
    st.markdown(
        f"[구글 지도에서 찾기](https://www.google.com/maps/search/?api=1&query={restaurant['lat']},{restaurant['lon']})"
    )
    st.divider()

st.info(
    "여행 일정은 예시입니다. 실제 방문 전 관광지 운영시간과 식당 영업시간을 확인하세요."
)
