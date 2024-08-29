# expand모듈을 통해 확장한 데이터에서 오류 가능성을 검출
from konlpy.tag import Okt
import pandas as pd
from common.info import open_dialog
import re

def find_h_char_positions(text):
    okt = Okt()
    words = okt.pos(text, norm=True, stem=True)

    # 명사, 형용사, 동사만 추출
    filtered_words = [word for word, pos in words if pos in ['Noun', 'Verb', 'Adjective']]

    results = []

    for word in filtered_words:
        if 'ㅎ' in word:
            first_pos = word.index('ㅎ')
            if first_pos == 0:
                position_type = '맨 앞'
            else:
                position_type = '중간'
            results.append((word, first_pos, position_type))
        else:
            results.append((word, -1, '없음'))

    return results

def extract_sentence(text):
    # 정규 표현식을 사용하여 "assistant: "을 제거하고 문장만 추출
    return re.sub(r'^assistant\s*:\s*', '', text)


if __name__ == '__main__':
    # path = open_dialog(False, "선택", [("Csv files", "*.csv")])
    # df = pd.read_csv(path, encoding='utf-8')
    #
    # # 2열의 학습 데이터만을 추출
    # df["Completion"] = df["Completion"].apply(extract_sentence)
    #
    # # 각 문장에서 단어만을 추출(find_h_char_positions 사용)

    test = "좋은 날에 아기를 낳았다고 사람들이 많이 모여 교회에서 대화를 한다."
    okt = Okt()
    print(okt.morphs(test))
    print(okt.nouns(test))
    print(okt.phrases(test))
    print(okt.pos(test))
