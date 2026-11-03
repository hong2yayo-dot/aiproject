
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="한국인을 위한 도쿄 관광지도",
    page_icon="🗼",
    layout="wide"
)

# 도쿄 인기 관광지 TOP 10
places = [
    {
        "rank": 1,
        "name": "센소지(아사쿠사)",
        "lat": 35.7148,
        "lon": 139.7967,
        "desc": "도쿄에서 가장 오래된 사찰로 알려진 명소입니다. 가미나리몬과 나카미세 거리에서 일본 전통 간식과 기념품 쇼핑을 즐겨보세요."
    },
    {
        "rank": 2,
        "name": "시부야 스크램블 교차로",
        "lat": 35.6595,
        "lon": 139.7005,
        "desc": "수많은 사람이 한꺼번에 건너는 도쿄의 대표적인 풍경입니다. 주변 쇼핑몰과 전망 명소도 함께 둘러보기 좋습니다."
    },
    {
        "rank": 3,
        "name": "도쿄 스카이트리",
        "lat": 35.7101,
        "lon": 139.8107,
        "desc": "높이 634m의 도쿄 랜드마크입니다. 전망대에서 도쿄 시내를 내려다보고 쇼핑도 즐길 수 있습니다."
    },
    {
        "rank": 4,
        "name": "도쿄 타워",
        "lat": 35.6586,
        "lon": 139.7454,
        "desc": "붉고 흰 색상이 상징적인 도쿄의 대표 전망 타워입니다. 밤에는 아름다운 야경을 감상할 수 있습니다."
    },
    {
        "rank": 5,
        "name": "팀랩 플래닛",
        "lat": 35.6491,
        "lon": 139.7894,
        "desc": "빛과 영상, 공간을 활용한 몰입형 디지털 아트 전시 공간입니다."
    },
    {
        "rank": 6,
        "name": "메이지 신궁",
        "lat": 35.6764,
        "lon": 139.6993,
        "desc": "도심 한가운데 울창한 숲길이 이어지는 신사입니다. 하라주쿠와 함께 방문하기 좋습니다."
    },
    {
        "rank": 7,
        "name": "하라주쿠 다케시타 거리",
        "lat": 35.6716,
        "lon": 139.7030,
        "desc": "개성 있는 패션 매장과 디저트 가게가 모여 있는 활기찬 거리입니다."
    },
    {
        "rank": 8,
        "name": "아키하바라",
        "lat": 35.6984,
        "lon": 139.7731,
        "desc": "전자제품, 게임, 애니메이션 관련 상점이 모여 있는 거리입니다."
    },
    {
        "rank": 9,
        "name": "신주쿠 교엔",
        "lat": 35.6852,
        "lon": 139.7100,
        "desc": "넓은 잔디밭과 일본식 정원을 갖춘 도심 공원입니다. 계절마다 다른 풍경을 감상할 수 있습니다."
    },
    {
        "rank": 10,
        "name": "오다이바 해변공원",
        "lat": 35.6298,
        "lon": 139.7765,
        "desc": "도쿄만과 레인보우 브리지를 바라볼 수 있는 해변 산책 명소입니다."
    }
]

# 제목
st.title("🗼 한국인을 위한 도쿄 인기 관광지도")
st.write("도쿄의 주요 관광지 TOP 10을 지도에서 확인해 보세요!")

st.info(
    "※ 공식 방문객 수 순위가 아닌 "
    "한국인 여행객에게 친숙한 대표 관광지 추천 목록입니다."
)

# 도쿄 지도 만들기
tokyo_map = folium.Map(
    location=[35.6812, 139.7671],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 지도에 관광지 마커 표시
for p in places:

    popup_html = f"""
    <div style="width:220px">
        <h4>TOP {p['rank']}. {p['name']}</h4>
        <p>{p['desc']}</p>
    </div>
    """

    # 번호가 표시된 빨간색 마커
    icon = folium.DivIcon(
        html=f"""
        <div style="
            background:#e53935;
            color:white;
            border:2px solid white;
            border-radius:50%;
            width:30px;
            height:30px;
            line-height:26px;
            text-align:center;
            font-weight:bold;
            font-size:13px;
            box-shadow:0 1px 5px rgba(0,0,0,.45);
        ">{p['rank']}</div>
        """,
        icon_size=(30, 30),
        icon_anchor=(15, 15)
    )

    folium.Marker(
        location=[p["lat"], p["lon"]],
        tooltip=f"TOP {p['rank']} - {p['name']}",
        popup=folium.Popup(
            popup_html,
            max_width=280
        ),
        icon=icon
    ).add_to(tokyo_map)

# 지도 화면 출력
st.subheader("📍 도쿄 관광지 TOP 10 지도")

st_folium(
    tokyo_map,
    width=None,
    height=600,
    use_container_width=True
)

# 관광지 설명
st.subheader("🧭 관광지 소개")

st.write(
    "지도에 표시된 번호와 아래 관광지 번호가 서로 연결됩니다."
)

# 2열로 관광지 설명 출력
for start in range(0, len(places), 2):

    cols = st.columns(2)

    for col, p in zip(cols, places[start:start + 2]):

        with col:

            with st.container(border=True):

                st.markdown(
                    f"### {p['rank']}. {p['name']}"
                )

                st.write(p["desc"])

                # 구글 지도 연결
                google_url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    f"{p['lat']},{p['lon']}"
                )

                st.link_button(
                    "Google 지도에서 보기",
                    google_url
                )

st.divider()

st.caption(
    "지도 데이터: OpenStreetMap | "
    "관광지 운영시간과 입장료는 방문 전에 확인하세요."
)
