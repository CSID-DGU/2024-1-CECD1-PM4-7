import requests
from bs4 import BeautifulSoup
from common.info import open_dialog
import pandas as pd

def getPronunciation(text: str):
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
        return

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
                "입력 어절": input_word,
                "변환 결과": conversion_result,
                "표준발음법 및 도움말": help_info
            })

    # 데이터 출력
    for row in data:
        print(f"입력 어절: {row['입력 어절']}, 변환 결과: {row['변환 결과']}, 표준발음법 및 도움말: {row['표준발음법 및 도움말']}")


if __name__ == '__main__':
    fp = open_dialog(False)
    data = pd.read_excel(fp).drop_duplicates(subset=['User content'])
    
    # 1. data각 문장에 대해 단어 분리(라이브러리 사용)
    # 2. getPro..()함수를 사용하여 발음 가져오기 + 표준 발음 및 근거항 저장
    # 3. 엑셀로 저장
    # 4. 이미 처리된 엑셀파일에 추가한 열을 추가로 저장(원문 비교로 삽입)
