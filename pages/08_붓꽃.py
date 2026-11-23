
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="붓꽃 품종 예측 프로그램",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 인공지능 붓꽃 품종 예측 프로그램")

st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "인공지능이 붓꽃의 품종을 예측합니다."
)

st.divider()


# =====================================
# 2. CSV 데이터 불러오기
# =====================================

@st.cache_data
def load_data():

    # app.py가 pages 폴더에 있고
    # Iris.csv는 그 상위 폴더에 있는 경우
    file_path = Path(__file__).parent.parent / "Iris.csv"

    data = pd.read_csv(
        file_path,
        encoding="cp949"
    )

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 파일을 불러올 수 없습니다: {e}")
    st.stop()


# =====================================
# 3. 데이터 확인
# =====================================

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]


# =====================================
# 4. KNN 알고리즘 모델 생성
# =====================================

model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)

# 모델 학습
model.fit(X, y)


# =====================================
# 5. 입력 가능 범위 설정
# =====================================

length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())


# =====================================
# 6. 사용자 입력 화면
# =====================================

st.subheader("📏 1. 꽃잎 정보 입력")

st.info(
    f"""
    **입력 가능한 범위**

    - 꽃잎 길이: {length_min} ~ {length_max} cm
    - 꽃잎 너비: {width_min} ~ {width_max} cm

    위 범위 안에서 값을 입력해주세요.
    """
)

col1, col2 = st.columns(2)

with col1:

    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=3.0,
        step=0.1,
        format="%.1f"
    )

with col2:

    petal_width = st.number_input(
        "🌷 꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=1.0,
        step=0.1,
        format="%.1f"
    )


# =====================================
# 7. 예측 버튼
# =====================================

if st.button("🔍 붓꽃 품종 예측하기", type="primary"):

    # 사용자 입력 데이터 생성
    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    # 품종 예측
    prediction = model.predict(input_data)[0]

    st.divider()

    # =================================
    # 8. 예측 결과 출력
    # =================================

    st.subheader("🎯 2. 인공지능 예측 결과")

    species_names = {
        "Iris-setosa": "세토사 (Setosa)",
        "Iris-versicolor": "버시컬러 (Versicolor)",
        "Iris-virginica": "버지니카 (Virginica)"
    }

    st.success(
        f"예측된 붓꽃 품종은 {species_names.get(prediction, prediction)} 입니다!"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "예측 품종",
            species_names.get(prediction, prediction)
        )

    with col2:
        st.metric(
            "입력 꽃잎 길이",
            f"{petal_length} cm"
        )

    st.write(
        f"입력한 꽃잎 너비: {petal_width} cm"
    )

    st.divider()

    # =================================
    # 9. 그래프 그리기
    # =================================

    st.subheader("📊 3. 붓꽃 데이터 분포 및 입력 위치")

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {
        "Iris-setosa": "blue",
        "Iris-versicolor": "green",
        "Iris-virginica": "red"
    }

    names = {
        "Iris-setosa": "Setosa",
        "Iris-versicolor": "Versicolor",
        "Iris-virginica": "Virginica"
    }

    # 기존 붓꽃 데이터 표시
    for species in df["품종"].unique():

        species_data = df[df["품종"] == species]

        ax.scatter(
            species_data["꽃잎 길이"],
            species_data["꽃잎 너비"],
            color=colors[species],
            label=names[species],
            alpha=0.7,
            s=60
        )

    # 사용자 입력 위치를 노란색 별로 표시
    ax.scatter(
        petal_length,
        petal_width,
        color="yellow",
        marker="*",
        edgecolors="black",
        linewidths=1.5,
        s=450,
        label="Your Input",
        zorder=10
    )

    # 그래프 축 설정
    ax.set_xlabel(
        "Petal Length (cm)",
        fontsize=12
    )

    ax.set_ylabel(
        "Petal Width (cm)",
        fontsize=12
    )

    ax.set_title(
        "Iris Species Classification",
        fontsize=15
    )

    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)

    plt.close(fig)

    st.caption(
        "노란색 별(★)은 사용자가 입력한 꽃잎의 위치입니다."
    )

    st.divider()

    # =================================
    # 10. 알고리즘 설명
    # =================================

    st.subheader("🤖 4. 사용한 인공지능 알고리즘")

    st.write(
        """
        **KNN (K-Nearest Neighbors, K-최근접 이웃 알고리즘)**

        1. 기존 붓꽃 데이터를 학습합니다.
        2. 사용자가 입력한 꽃잎 길이와 너비를 확인합니다.
        3. 입력값과 가장 가까운 데이터 5개를 찾습니다.
        4. 주변 5개 데이터 중 가장 많은 품종을 선택합니다.
        5. 선택된 품종을 예측 결과로 보여줍니다.

        입력 변수는 표준화 과정을 거쳐 분석합니다.
        """
    )

else:

    # =================================
    # 11. 예측 전 기본 데이터 그래프
    # =================================

    st.subheader("📊 2. 붓꽃 품종별 데이터 분포")

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {
        "Iris-setosa": "blue",
        "Iris-versicolor": "green",
        "Iris-virginica": "red"
    }

    for species in df["품종"].unique():

        species_data = df[df["품종"] == species]

        ax.scatter(
            species_data["꽃잎 길이"],
            species_data["꽃잎 너비"],
            color=colors[species],
            label=species,
            alpha=0.7,
            s=60
        )

    ax.set_xlabel("Petal Length (cm)")
    ax.set_ylabel("Petal Width (cm)")

    ax.set_title("Iris Dataset")

    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)

    plt.close(fig)

    st.info(
        "꽃잎 길이와 너비를 입력하고 "
        "'붓꽃 품종 예측하기' 버튼을 눌러보세요!"
    )
