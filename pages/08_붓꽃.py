
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
# 3. 데이터 준비
# =====================================

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]


# =====================================
# 4. KNN 알고리즘 모델 생성 및 학습
# =====================================

model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)

model.fit(X, y)


# =====================================
# 5. 입력 가능 범위 설정
# =====================================

length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())


# =====================================
# 6. 알고리즘 설명 화면
# =====================================

st.subheader("🤖 사용한 인공지능 알고리즘")

st.success("KNN (K-Nearest Neighbors) : K-최근접 이웃 알고리즘")

st.write(
    """
    이 프로그램은 **KNN 알고리즘**을 사용합니다.

    KNN은 새로운 데이터와 가장 가까운 기존 데이터들을 찾아서
    어떤 종류에 속하는지 판단하는 인공지능 알고리즘입니다.

    예를 들어 새로운 붓꽃의 꽃잎 길이와 너비가 입력되면,
    기존 붓꽃 중에서 가장 비슷한 꽃 5개를 찾아 품종을 비교합니다.
    """
)

with st.expander("📖 KNN 알고리즘 작동 방법 자세히 알아보기", expanded=True):

    st.markdown(
        """
        ### KNN은 어떻게 작동할까요?

        **1단계. 기존 데이터 학습하기**

        기존에 수집된 150개의 붓꽃 데이터를 준비합니다.
        각각의 꽃잎 길이, 꽃잎 너비, 품종을 확인합니다.

        **2단계. 새로운 데이터 입력하기**

        사용자가 새로운 붓꽃의 꽃잎 길이와 너비를 입력합니다.

        **3단계. 가까운 이웃 5개 찾기**

        입력한 붓꽃과 기존 붓꽃 데이터 사이의 거리를 계산합니다.
        그리고 가장 가까운 데이터 5개를 찾습니다.

        **4단계. 주변 이웃의 품종 비교하기**

        가까운 붓꽃 5개의 품종을 비교합니다.
        어떤 품종이 가장 많이 나왔는지 확인합니다.

        **5단계. 최종 품종 예측하기**

        가장 많이 나온 품종을 새로운 붓꽃의 품종으로 예측합니다.
        """
    )

st.info(
    """
    💡 쉽게 이해하기!

    새로운 학생의 성격을 알고 싶을 때,
    그 학생과 성격이 비슷한 친구 5명을 찾아보는 것과 같습니다.

    친구 5명 중 3명이 A 유형이고 2명이 B 유형이라면
    새로운 학생을 A 유형으로 판단하는 방식입니다.
    """
)

st.caption(
    "이 프로그램은 K=5를 사용하며, "
    "꽃잎 길이와 너비는 표준화한 후 거리를 계산합니다."
)

st.divider()


# =====================================
# 7. 사용자 입력 화면
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
# 8. 예측 버튼
# =====================================

if st.button("🔍 붓꽃 품종 예측하기", type="primary"):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    # 품종 예측
    prediction = model.predict(input_data)[0]

    # 가장 가까운 이웃 5개 확인
    scaled_X = model.named_steps["standardscaler"].transform(X)

    scaled_input = model.named_steps["standardscaler"].transform(
        input_data
    )

    distances, indices = model.named_steps[
        "kneighborsclassifier"
    ].kneighbors(
        scaled_input,
        n_neighbors=5
    )

    nearest_data = df.iloc[indices[0]].copy()

    nearest_data["거리"] = distances[0]

    st.divider()

    # =================================
    # 9. 예측 결과
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
            "사용한 알고리즘",
            "KNN (K=5)"
        )

    st.write(f"꽃잎 길이: {petal_length} cm")
    st.write(f"꽃잎 너비: {petal_width} cm")

    st.divider()

    # =================================
    # 10. 가까운 이웃 데이터 확인
    # =================================

    st.subheader("🔎 3. 가장 가까운 붓꽃 데이터 5개")

    st.write(
        "KNN 알고리즘이 입력한 꽃과 가장 비슷하다고 판단한 "
        "기존 붓꽃 5개입니다."
    )

    st.dataframe(
        nearest_data[
            ["꽃잎 길이", "꽃잎 너비", "품종", "거리"]
        ].reset_index(drop=True),
        use_container_width=True
    )

    st.write("가까운 이웃 5개의 품종별 개수")

    vote_counts = nearest_data["품종"].value_counts()

    for species, count in vote_counts.items():
        st.write(
            f"- {species_names.get(species, species)}: {count}개"
        )

    st.info(
        f"가장 많은 표를 얻은 품종인 "
        f"{species_names.get(prediction, prediction)}을 예측 결과로 선택했습니다."
    )

    st.divider()

    # =================================
    # 11. 그래프
    # =================================

    st.subheader("📊 4. 붓꽃 데이터 분포 및 입력 위치")

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

    # 사용자가 입력한 위치
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

    # 그래프 설정
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

    # =================================
    # 12. 최종 알고리즘 설명
    # =================================

    st.subheader("🧠 5. 이번 예측은 어떻게 이루어졌을까요?")

    st.write(
        f"""
        이번 예측에서는 **KNN 알고리즘**을 사용했습니다.

        ① 사용자가 꽃잎 길이 {petal_length}cm,
        꽃잎 너비 {petal_width}cm를 입력했습니다.

        ② 기존 데이터에서 가장 가까운 붓꽃 5개를 찾았습니다.

        ③ 가까운 5개의 품종을 비교했습니다.

        ④ 가장 많이 나타난 품종인
        **{species_names.get(prediction, prediction)}**을
        최종 예측 결과로 선택했습니다.
        """
    )

    st.success("KNN 알고리즘을 이용한 붓꽃 품종 예측이 완료되었습니다!")

else:

    # =================================
    # 13. 예측 전 기본 그래프
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
