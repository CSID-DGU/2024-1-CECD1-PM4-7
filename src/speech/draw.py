import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from common.info import open_dialog
import numpy as np

# 변화량 그래프 그리기
def draw_graph(filePath: Path, list1Name: str, list2Name: str, imageName: str, correct=False, target=0, num_bins=20):
    """
    correct: True일 경우 'correct' 값이 1인 데이터만 필터링
    target: 기준선 값 (0 또는 1)
    num_bins: 구간 수
    """
    # 엑셀 파일 데이터 읽기
    data = pd.read_excel(filePath)

    # 'correct'가 True라면 정답인 데이터만 필터링
    if correct:
        filtered_data = data[data['correct'] == 1]
    else:
        filtered_data = data

    # 리스트 A와 B 데이터 추출
    A = filtered_data[list1Name].tolist()
    B = filtered_data[list2Name].tolist()

    # A 값을 기준으로 오름차순 정렬
    sorted_A_B = sorted(zip(A, B), key=lambda x: x[0])
    A_sorted, B_sorted = zip(*sorted_A_B)

    # A와 B의 차이 계산 및 기준선(target)과의 절대값으로 변화량 측정
    difference = [b - a for a, b in zip(A_sorted, B_sorted)]
    # A 값을 기준으로 n개의 구간으로 나누기
    A_bins = np.array_split(A_sorted, num_bins)
    diff_bins = np.array_split(difference, num_bins)

    # 각 구간의 평균 A 값과 평균 변화량을 계산
    avg_A_values = [np.mean(bin) for bin in A_bins]
    avg_diff_values = [np.mean(bin) for bin in diff_bins]

    # 그래프 그리기
    plt.figure(figsize=(10, 6))

    # 구간별 평균 변화량 그래프
    plt.plot(avg_A_values, avg_diff_values, label=f"{imageName} Average Difference", marker='o', color='b')

    # target에 따른 기준선 추가
    if target == 0:
        # target이 0인 경우 y = -x 그래프 추가
        plt.plot(avg_A_values, [-x for x in avg_A_values], linestyle='--', color='gray')
    elif target == 1:
        # target이 1인 경우 x + y = 1 그래프 추가 (y = 1 - x)
        plt.plot(avg_A_values, [1 - x for x in avg_A_values], linestyle='--', color='gray')

    plt.xlabel(imageName + " (STT)")
    plt.ylabel("Average Difference")
    plt.title(f"{imageName} Average Difference_{'only Correct' if correct else 'All'}")
    plt.legend()


    # 그래프 저장
    imagePath = filePath.with_name(f"{filePath.stem}_{imageName}_{correct}.png")
    plt.savefig(imagePath)
    plt.close()


if __name__ == '__main__':
    filePath = open_dialog(isfolder=False, filetypes=[("Excel Files", "*.xlsx")])
    draw_graph(filePath, 'SER(u-a)', 'SER(u-g)', 'SER', correct=True, target=0, num_bins=30)
    draw_graph(filePath, 'SER(u-a)', 'SER(u-g)', 'SER', correct=False, target=0, num_bins=30)
    draw_graph(filePath, 'COS(u-a)', 'COS(u-g)', 'COS', correct=True, target=1, num_bins=30)
    draw_graph(filePath, 'COS(u-a)', 'COS(u-g)', 'COS', correct=False, target=1, num_bins=30)