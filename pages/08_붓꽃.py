
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="붓꽃 품종 예측 프로그램",
    page_icon="🌸",
    layout="wide"
)

# 제목
st.title("🌸 인공지능 붓꽃 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 인공지능이 붓꽃 품종을 예측합니다.")

# 데이터 불러오기
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "Iris.csv"
    data = pd.read_csv(file_path, encoding="cp949")
    return data

try:
    df = load_data()

except Exception as e:
    st.error(f"데이터 파일을 불러올 수 없습니다: {e}")
    st.stop()

# 사용할 데이터
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# KNN 모델 생성
model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)

# 모델 학습
model.fit(X, y)

# 입력 범위 설정
petal_length_min = float(df["꽃잎 길이"].min())
petal_length_max = float(df["꽃잎 길이"].max())

petal_width_min = float(df["꽃잎 너비"].min())
petal_width_max = float(df["꽃잎 너비"].max())

# 화면 구성
st.divider()

st.subheader("📏 1. 붓꽃 정보 입력")

st.info(
    f"""
    입력 가능한 범위를 확인하세요.

    - 꽃잎 길이: {petal_length_min} ~ {petal_length_max} cm
    - 꽃잎 너비: {petal_width_min} ~ {petal_width_max} cm

    """
)

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=petal_length_min,
        max_value=petal_length_max,
        value=3.0,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=petal_width_min,
        max_value=petal_width_max,
        value=1.0,
        step=0.1,
        format="%.1f"
    )

# 예측 버튼
if st.button("🔍 붓꽃 품종 예측하기", type="primary"):

    # 사용자 입력 데이터
    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    # 품종 예측
    prediction = model.predict(input_data)[0]

    st.divider()

    st.subheader("🎯 2. 인공지능 예측 결과")

    st.success(f"예측된 붓꽃 품종은 **{prediction}** 입니다!")

    # 품종별 이름 설명
    species_names = {
        "Iris-setosa": "세토사 (Setosa)",
        "Iris-versicolor": "버시컬러 (Versicolor)",
        "Iris-virginica": "버지니카 (Virginica)"
    }

    st.metric(
        label="예측된 붓꽃 품종",
        value=species_names.get(prediction, prediction)
    )

    st.write(
        f"입력한 꽃잎 길이: {petal_length} cm"
    )
    st.write(
        f"입력한 꽃잎 너비: {petal_width} cm"
    )

    st.divider()

    # 그래프
    st.subheader("📊 3. 붓꽃 데이터 분포 및 입력 위치")

    fig, ax = plt.subplots(figsize=(10, 6))

    # 품종별 기존 데이터 표시
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

    for species in df["품종"].unique():

        species_data = df[df["품종"] == species]

        ax.scatter(
            species_data["꽃잎 길이"],
            species_data["꽃잎 너비"],
            color=colors[species],
            label=names[species],
            alpha=0.7,
            s=55
        )

    # 사용자가 입력한 위치를 노란색 별로 표시
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

    # 축 설정
    ax.set_xlabel("Petal Length (cm)", fontsize=12)
    ax.set_ylabel("Petal Width (cm)", fontsize=12)

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

    st.subheader("🤖 4. 사용한 인공지능 알고리즘")

    st.write("""
    **KNN (K-Nearest Neighbors)**

    - 가장 가까운 데이터 5개를 찾습니다.
    - 주변 데이터의 품종을 비교합니다.
    - 가장 많이 나타난 품종으로 예측합니다.
    - 꽃잎 길이와 너비를 표준화하여 학습합니다.
    """)

else:
    st.divider()
    st.subheader("📊 붓꽃 품종별 데이터 미리보기")

    st.write("아래 그래프에서 세 가지 붓꽃의 분포를 확인할 수 있습니다.")

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
            s=55
        )

    ax.set_xlabel("Petal Length (cm)")
    ax.set_ylabel("Petal Width (cm)")
    ax.set_title("Iris Dataset")
    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)
