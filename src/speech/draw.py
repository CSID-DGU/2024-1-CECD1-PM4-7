import matplotlib.pyplot as plt
import numpy as np

# 분포도를 저장하는 함수
def save_difference_histogram(list1, list2, filename="difference_histogram.png"):
    # 두 리스트의 길이가 같은지 확인
    if len(list1) != len(list2):
        raise ValueError("두 리스트의 길이가 같아야 합니다.")

    # 변화폭 계산
    difference = [y - x for x, y in zip(list1, list2)]

    # 히스토그램 그리기
    plt.figure(figsize=(10, 6))
    plt.hist(difference, bins=30, color='b', alpha=0.7)
    plt.title('Distribution of Differences (Histogram)')
    plt.xlabel('Difference')
    plt.ylabel('Frequency')
    plt.grid(True)

    # 그림 저장
    plt.savefig(filename)
    plt.close()  # 저장 후 창 닫기


def plot_relative_change(list1, list2, filename):
    # 두 리스트의 길이가 같은지 확인
    if len(list1) != len(list2):
        raise ValueError("두 리스트의 길이가 같아야 합니다.")

    # 0으로 나누는 것을 방지하기 위해 list1에서 0이 아닌 값들만 상대적 변화율 계산
    relative_change = [(y - x) / x * 100 if x != 0 else 0 for x, y in zip(list1, list2)]

    # 변화율을 그래프로 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(relative_change, marker='o', label='Relative Change (%)')

    # 제목 및 레이블 설정
    plt.title('Relative Change between List1 and List2')
    plt.xlabel('Index')
    plt.ylabel('Relative Change (%)')
    plt.grid(True)
    plt.legend()

    # 그림 저장
    plt.savefig(filename)
    plt.close()  # 저장 후 창 닫기


# 이동 평균 함수
def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')


# 상대적 변화율 계산 및 이동 평균 적용 후 그래프 그리기
def plot_relative_change_with_smoothing(list1, list2, filename, window_size=50):
    if len(list1) != len(list2):
        raise ValueError("두 리스트의 길이가 같아야 합니다.")

    # 0으로 나누는 것을 방지하고, 변화율 계산
    relative_change = [(y - x) / x * 100 if x != 0 else 0 for x, y in zip(list1, list2)]

    # 이동 평균 적용
    relative_change_smooth = moving_average(relative_change, window_size)

    # 그래프 그리기
    plt.figure(figsize=(10, 6))

    # 원래 변화율의 이동 평균 그래프
    plt.plot(relative_change_smooth, label=f'Moving Average (Window={window_size})', color='blue')
    plt.title('Smoothed Relative Change between List1 and List2')
    plt.xlabel('Index')
    plt.ylabel('Relative Change (%)')
    plt.grid(True)
    plt.legend()

    # y축 제한을 두어 너무 큰 변화를 억제
    plt.ylim(-100, 100)

    # 그림 저장
    plt.savefig(filename)
    plt.close()  # 저장 후 창 닫기
