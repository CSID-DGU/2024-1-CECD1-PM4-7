# 문장의 오류를 검사
import util

# 1. 후음 'ㅎ'
def check_h(sep: list):
    error_index_list = []

    # 각 단어에 대해 'ㅎ'가 포함되어 있는지 확인
    for i in range(1, len(list)-1):
        letter = sep[i]
        if letter == 'ㅎ':
            

            error_index_list.append()

    if len(error_index_list) != 0:
        return error_index_list
    else:
        return False