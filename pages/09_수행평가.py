
# 역 위치 파일 자동 찾기
station_candidates = [
    BASE_DIR / "station_info.csv",
    BASE_DIR / "국가철도공단_철도역 정보_20250711.csv",
]

STATION_FILE = next(
    (p for p in station_candidates if p.exists()),
    None
)

if STATION_FILE is None:
    st.error("역 위치 데이터 파일을 찾을 수 없습니다.")

    st.write("프로그램이 찾는 폴더:")
    st.code(str(BASE_DIR))

    st.write("현재 폴더에 있는 파일:")
    st.write([
        p.name for p in BASE_DIR.iterdir()
    ])

    st.info(
        "GitHub 저장소의 최상위 폴더에 "
        "station_info.csv를 업로드해 주세요."
    )
    st.stop()
