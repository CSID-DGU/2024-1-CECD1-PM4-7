import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from common.info import open_dialog

# 변화량 그래프 그리기
def draw_graph(filePath: Path, list1Name: str, list2Name: str, imageName: str):
    # 엑셀 파일 데이터 읽기
    data = pd.read_excel(filePath)

    # 'correct' 값이 '1'인 데이터만 필터링
    filtered_data = data[data['correct'] == 1]

    # 리스트 A와 B 데이터 추출
    A = filtered_data[list1Name].tolist()
    B = filtered_data[list2Name].tolist()

    # A 값을 기준으로 오름차순 정렬
    sorted_A_B = sorted(zip(A, B), key=lambda x: x[0])
    A_sorted, B_sorted = zip(*sorted_A_B)

    # A와 B의 차이 계산
    difference = [b - a for a, b in zip(A_sorted, B_sorted)]

    # 그래프 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(A_sorted, difference, label=imageName, marker='o')
    plt.xlabel(imageName + "(STT)")
    plt.ylabel("Difference")
    plt.title(f"{imageName} Difference Graph")
    plt.legend()

    # 그래프 저장
    imagePath = filePath.stem + '_' + imageName + '.png'
    plt.savefig(imagePath)
    plt.close()


if __name__ == '__main__':
    draw_graph(open_dialog(False), 'SER(u-a)', 'SER(u-g)', 'SER')