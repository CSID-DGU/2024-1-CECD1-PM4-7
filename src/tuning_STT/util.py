# 오류 가능성을 검사

# 1. 후음 'ㅎ'
def check_h_presence(sent: str):
    error_index_list = []
    words = sent.split()

    # 각 단어에 대해 'ㅎ'가 포함되어 있는지 확인
    for word in words:
        if 'ㅎ' in word:
            # 'ㅎ'의 위치를 저장
            indices = [i for i, char in enumerate(word) if char == 'ㅎ']
            error_index_list.extend(indices)

    if len(error_index_list) != 0:
        return error_index_list
    else:
        return False


# 테스트할 문장
sentence = "좋은, 낳아, 대화, 교회, 많이 같이 후음 'ㅎ'가 존재하는 경우가 문장에 있는지 검사할 수 있어?"

print(check_h_presence(sentence))
