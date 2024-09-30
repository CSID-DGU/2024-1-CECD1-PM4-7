# git clone https://github.com/ssut/py-hanspell.git
# pip install -e.
import requests
from bs4 import BeautifulSoup
from common.info import open_dialog
import pandas as pd
from konlpy.tag import Kkma, Okt
from pathlib import Path
import re
from hanspell.spell_checker import check

def test():
    kkma = Kkma()
    sent = "배갯잇을새로하니새거같아보여"
    sentences = kkma.sentences(sent)
    print(sentences[0])
    print(kkma.pos(sent, flatten=False))
    print(kkma.pos(sent, flatten=True))
    getPronunciation(sentences[0])

def checktest():
    result = check("나는사과를좋아해")
    print(type(result))


# GET request를 통해 발음 데이터를 가져오는 함수
def getPronunciation(text: str) -> list:
    url = "http://pronunciation.cs.pusan.ac.kr/pronunc2.asp"

    # 요청 파라미터
    params = {
        "text1": text.encode('euc-kr'),
        "submit1": "%C8%AE%C0%CE%C7%CF%B1%E2"
    }

    # GET 요청을 보냅니다 (디코딩 없이 바로 사용)
    response = requests.get(url, params=params)

    # BeautifulSoup 객체 생성 (디코딩 없이 content를 파싱)
    soup = BeautifulSoup(response.content, 'html.parser')

    # "입력 어절" 텍스트를 포함하는 <td> 요소를 찾음
    input_word_td = soup.find('td', string="입력 어절")

    if not input_word_td:
        print("입력 어절을 포함하는 테이블을 찾을 수 없습니다.")
        return [{"orig": text, "pron": '', "rule": ''}]

    # 해당 <td> 요소의 부모 테이블을 찾음
    title_table = input_word_td.find_parent('table')

    if not title_table:
        print("제목 테이블을 찾을 수 없습니다.")
        return

    # 제목 테이블 다음에 나오는 첫 번째 데이터 테이블을 찾음
    data_table = title_table.find_next_sibling('table')

    if not data_table:
        print("데이터 테이블을 찾을 수 없습니다.")
        return

    # 테이블에서 행 추출
    rows = data_table.find_all('tr')

    # 데이터 저장을 위한 리스트
    data = []

    # 각 행에서 '입력 어절', '변환 결과', '표준발음법 및 도움말'을 추출
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:  # 최소 3개의 열이 있어야 함
            # 각 셀의 텍스트를 euc-kr로 디코딩
            input_word = cols[0].text.strip()
            conversion_result = cols[1].text.strip()
            help_info = cols[2].text.strip()

            # 데이터 저장
            data.append({
                "orig": input_word,
                "pron": conversion_result,
                "rule": help_info
            })

    # 데이터 출력
    for row in data:
        print(f"입력 어절: {row['orig']:<10}, 변환 결과: {row['pron']:<10} ", end='')
        rule_numbers = re.findall(r'\d+', row['rule'])  # \d+는 숫자를 의미
        rule_text = ', '.join(rule_numbers)  # 숫자들을 쉼표로 연결
        print(f"표준발음법 및 도움말: {rule_text}")

    return data


def append_data(orig: list, pron: list, rule: list, ele: dict):
    orig.append(ele['orig'])
    pron.append(ele['pron'])
    rule.append(ele['rule'])


checktest()
# if __name__ == '__main__':
#     kkma = Kkma()
#     fp = open_dialog(False)
#     data = pd.read_excel(fp).drop_duplicates(subset=['User content'])
#
#     orig = []
#     pron = []
#     rule = []
#     # 1. data각 문장에 대해 단어 분리(라이브러리 사용)
#     # 2. getPronunciation()을 통해 발음 저장
#     for sentence in data['User content']:
#         sent = kkma.sentences(sentence.replace(' ', ''))[0]
#         result = getPronunciation(sent)
#         # 문장 전체의 발음검사가 불가능한 경우 띄어쓰기로 분리하여 진행
#         if len(result) == 1:
#             words = sent.split()
#             for word in words:
#                 result = getPronunciation(word)
#                 for ele in result:
#                     # # 띄어쓰기로 분리했지만 발음이 나오지 않은경우
#                     # if ele['pron'] == '':
#                     #     elements = kkma.sentences(ele['orig'])
#                     #     for element in elements:
#                     #         result_2nd = getPronunciation(element)
#                     #         for e in result_2nd:
#                     #             append_data(orig, pron, rule, e)
#                     # else:
#                     #     for e in ele:
#                     #         append_data(orig, pron, rule, e)
#                     append_data(orig, pron, rule, ele)
#         else:
#             for ele in result:
#                 append_data(orig, pron, rule, ele)
#
#
#         orig.append('---')
#         pron.append('---')
#         rule.append('---')
#
#     # 3. 엑셀로 저장
#     df = pd.DataFrame({'orig': orig, 'pron': pron, 'rule': rule})
#     df.to_excel(fp.with_stem(fp.stem + '_pronunciation'), index=False)
