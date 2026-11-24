
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="붓꽃 품종 인공지능 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 인공지능 붓꽃 품종 예측 프로그램")

st.write(
    "꽃잎 길이와 너비를 입력하면 "
    "3가지 인공지능 알고리즘이 각각 품종을 예측합니다."
)

st.divider()


# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    # app.py는 pages 폴더 안에 있고
    # Iris.csv는 상위 폴더에 있음
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


# ==========================================
# 3. 데이터 준비
# ==========================================

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

species_names = {
    "Iris-setosa": "Setosa (세토사)",
    "Iris-versicolor": "Versicolor (버시컬러)",
    "Iris-virginica": "Virginica (버지니카)"
}


# ==========================================
# 4. 3가지 알고리즘 생성
# ==========================================

# 알고리즘 1 : KNN
knn_model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)

# 알고리즘 2 : Decision Tree
tree_model = DecisionTreeClassifier(
    max_depth=4,
    random_state=42
)

# 알고리즘 3 : Random Forest
forest_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=4,
    random_state=42
)


# ==========================================
# 5. 모델 학습
# ==========================================

models = {
    "KNN": knn_model,
    "Decision Tree": tree_model,
    "Random Forest": forest_model
}

for model in models.values():
    model.fit(X, y)


# ==========================================
# 6. 입력 범위 설정
# ==========================================

length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())


# ==========================================
# 7. 알고리즘 소개
# ==========================================

st.subheader("🤖 사용한 분류 알고리즘 3가지")

st.write(
    "서로 다른 방식으로 작동하는 세 가지 알고리즘을 "
    "이용하여 붓꽃 품종을 예측합니다."
)

with st.expander("① KNN - K 최근접 이웃 알고리즘", expanded=True):

    st.markdown(
        """
        **작동 원리**

        1. 기존 붓꽃 데이터의 꽃잎 길이와 너비를 확인합니다.
        2. 새로 입력한 꽃과 기존 꽃 사이의 거리를 계산합니다.
        3. 가장 가까운 붓꽃 5개를 찾습니다.
        4. 5개 중 가장 많이 등장한 품종을 선택합니다.

        **쉽게 이해하기**

        새로운 학생과 성격이 비슷한 친구 5명을 찾는 것과 같습니다.
        친구들이 가장 많이 속한 유형을 새로운 학생의 유형으로 판단합니다.
        """
    )

with st.expander("② Decision Tree - 의사결정나무 알고리즘"):

    st.markdown(
        """
        **작동 원리**

        1. 꽃잎 길이와 너비를 기준으로 데이터를 나눕니다.
        2. 어떤 기준으로 나누면 품종을 잘 구분할 수 있는지 학습합니다.
        3. 여러 가지 질문을 순서대로 거칩니다.
        4. 마지막에 도착한 결과를 품종으로 예측합니다.

        **쉽게 이해하기**

        스무고개와 비슷합니다.

        예를 들어 꽃잎 길이가 일정 기준보다 긴가?
        꽃잎 너비가 일정 기준보다 큰가?
        이런 질문을 차례대로 하면서 정답을 찾아갑니다.
        """
    )

with st.expander("③ Random Forest - 랜덤 포레스트 알고리즘"):

    st.markdown(
        """
        **작동 원리**

        1. 여러 개의 의사결정나무를 만듭니다.
        2. 각각의 나무가 학습 데이터를 바탕으로 품종을 예측합니다.
        3. 여러 나무의 예측 결과를 모읍니다.
        4. 가장 많은 나무가 선택한 품종을 최종 결과로 결정합니다.

        **쉽게 이해하기**

        여러 명의 선생님에게 같은 문제를 풀게 한 뒤,
        가장 많은 선생님이 선택한 답을 최종 정답으로 정하는 것과 같습니다.
        """
    )

st.info(
    "세 알고리즘은 모두 꽃잎 길이와 꽃잎 너비 두 가지 정보를 사용합니다. "
    "다만 품종을 판단하는 방법이 서로 다릅니다."
)

st.divider()


# ==========================================
# 8. 사용자 입력
# ==========================================

st.subheader("📏 1. 꽃잎 정보 입력")

st.info(
    f"""
    **입력 가능한 값의 범위**

    - 꽃잎 길이: {length_min} ~ {length_max} cm
    - 꽃잎 너비: {width_min} ~ {width_max} cm
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


# ==========================================
# 9. 예측 실행
# ==========================================

if st.button("🔍 3가지 알고리즘으로 품종 예측하기",
             type="primary"):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    results = {}
    probability_data = {}

    # 세 알고리즘 각각 예측
    for name, model in models.items():

        prediction = model.predict(input_data)[0]

        probabilities = model.predict_proba(input_data)[0]

        classes = (
            model.named_steps["kneighborsclassifier"].classes_
            if name == "KNN"
            else model.classes_
        )

        results[name] = prediction

        probability_data[name] = dict(
            zip(classes, probabilities)
        )

    st.divider()


    # ======================================
    # 10. 세 알고리즘 예측 결과
    # ======================================

    st.subheader("🎯 2. 알고리즘별 예측 결과 비교")

    st.write(
        f"입력한 꽃잎 길이: **{petal_length} cm**"
    )

    st.write(
        f"입력한 꽃잎 너비: **{petal_width} cm**"
    )

    col1, col2, col3 = st.columns(3)

    result_columns = [col1, col2, col3]

    for (name, prediction), column in zip(
        results.items(), result_columns
    ):

        with column:

            st.markdown(f"**{name}**")

            st.success(
                species_names.get(prediction, prediction)
            )

            st.caption("예측 결과")


    # ======================================
    # 11. 결과 비교표
    # ======================================

    st.subheader("📋 3. 세 알고리즘 결과 비교표")

    comparison = []

    for name, prediction in results.items():

        confidence = probability_data[name][prediction] * 100

        comparison.append({
            "알고리즘": name,
            "예측 품종": species_names.get(
                prediction, prediction
            ),
            "예측 품종의 모델 확률": f"{confidence:.1f}%"
        })

    comparison_df = pd.DataFrame(comparison)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # 모든 알고리즘의 예측이 같은지 확인
    if len(set(results.values())) == 1:

        st.success(
            "🎉 세 알고리즘이 모두 같은 품종을 예측했습니다!"
        )

    else:

        st.warning(
            "알고리즘마다 예측 결과가 다릅니다. "
            "각 알고리즘의 판단 방식을 비교해 보세요."
        )

    st.caption(
        "예측 품종의 모델 확률은 각 모델이 해당 품종에 부여한 확률입니다. "
        "실제 예측 정확도와는 다른 값입니다."
    )


    # ======================================
    # 12. 품종별 예측 확률 비교
    # ======================================

    st.divider()

    st.subheader("📊 4. 품종별 예측 확률 비교")

    probability_df = pd.DataFrame(
        probability_data
    )

    probability_df.index = [
        species_names.get(x, x)
        for x in probability_df.index
    ]

    probability_df = probability_df * 100

    st.bar_chart(
        probability_df,
        y_label="예측 확률 (%)",
        x_label="붓꽃 품종"
    )

    st.write(
        "각 알고리즘이 세 가지 품종에 부여한 확률을 비교할 수 있습니다."
    )


    # ======================================
    # 13. KNN 가까운 이웃 확인
    # ======================================

    st.divider()

    st.subheader("🔎 5. KNN이 찾은 가까운 데이터 5개")

    scaled_X = knn_model.named_steps[
        "standardscaler"
    ].transform(X)

    scaled_input = knn_model.named_steps[
        "standardscaler"
    ].transform(input_data)

    distances, indices = knn_model.named_steps[
        "kneighborsclassifier"
    ].kneighbors(
        scaled_input,
        n_neighbors=5
    )

    nearest_data = df.iloc[indices[0]][
        ["꽃잎 길이", "꽃잎 너비", "품종"]
    ].copy()

    nearest_data["거리"] = distances[0]

    st.dataframe(
        nearest_data.reset_index(drop=True),
        use_container_width=True
    )

    st.caption(
        "거리가 작을수록 입력한 꽃과 더 비슷한 데이터입니다."
    )


    # ======================================
    # 14. 붓꽃 데이터 그래프
    # ======================================

    st.divider()

    st.subheader("📍 6. 붓꽃 데이터 분포와 사용자 입력 위치")

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

    # 기존 데이터 표시
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

    # 사용자 입력 위치 표시
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


    # ======================================
    # 15. 알고리즘별 작동 원리 비교
    # ======================================

    st.divider()

    st.subheader("🧠 7. 세 가지 알고리즘 작동 원리 비교")

    st.markdown(
        """
        | 알고리즘 | 판단하는 방법 | 쉽게 설명하면 |
        |---|---|---|
        | KNN | 가까운 데이터 5개 비교 | 주변 친구들의 의견 듣기 |
        | Decision Tree | 조건에 따라 단계별 분류 | 스무고개 |
        | Random Forest | 여러 나무의 결과 투표 | 여러 선생님의 다수결 |

        **KNN**

        새로운 데이터와 가까운 기존 데이터들을 비교합니다.

        **Decision Tree**

        꽃잎 길이와 너비에 관한 조건을 차례대로 확인합니다.

        **Random Forest**

        여러 의사결정나무의 판단을 종합하여 최종 품종을 선택합니다.
        """
    )

    st.success(
        "3가지 인공지능 알고리즘의 품종 예측과 비교가 완료되었습니다!"
    )

else:

    # ======================================
    # 16. 예측 전 기본 그래프
    # ======================================

    st.subheader("📊 붓꽃 품종별 데이터 분포")

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
        "'3가지 알고리즘으로 품종 예측하기' 버튼을 눌러보세요!"
    )
