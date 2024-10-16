# STT 검증모델용

from common.info import getPrompt, open_dialog
from common.auth_ import getKey
from playground.client import send_request_without_history
from openai import OpenAI
import pandas as pd
import json
import re

KEY = getKey('OPENAI')
client = OpenAI(api_key=KEY)

# prompt = getPrompt("stt_validation_241015")

# 1. 교정모델 학습용 데이터를 기반으로 생성
def makeData_byCorrectionModel():
    prompt = """
    프롬프트: User문장은 원문이고, Correct문장은 너가 평가해야할 문장이다.
    서로 의미가 {같다고}/{다르다고} 평가되었을 때, 문장 간 의미가 정말로 같다면 "통과"를 출력하라.
    문장 간 의미가 다르다면 "불충분(어색한 부분: )"을 출력하여 어느 부분에서 수정이 필요한지 출력하라.
    문장의 의미가 완전히 파괴되었다면 "완전손상"을 출력하라.
    
    아래는 그 예시이다.
    User: 인플루엔자 예방접종을 맞고왔어
    Correct: 인플루엔자 예방 접종을 받고 왔어
    모범 출력: 통과
    
    User: 허튼 말해서 분란을 일으키지 마
    Correct: 버튼을 말해서 분란을 일으키지 마
    모범 출력: 불충분(어색한 부분: 버튼을)
    
    User: 뱃속이 쿡쿡 쑤시는 느낌이야
    Correct: 뱃속에 구슬은 느낌이야
    모범 출력: 완전손상
    """

    filePath = open_dialog(isfolder=False, filetypes=[("Excel Files", "*.xlsx")])
    df = pd.read_excel(filePath)

    result = []
    for index, row in df.iterrows():
        correct = "같다고" if row["Correct"] == '1' else "다르다고"
        prompt1 = prompt.replace("{같다고}/{다르다고}", correct)
        user_input = f'User: {row["User content"]}, Correct: row["Corrected"]'

        response = send_request_without_history(client, prompt1, user_input, "chatgpt-4o-latest")
        print(f"{index+1}: {response}")
        result.append(response)

    df["validated"] = result
    df.to_excel(filePath.with_stem(filePath.stem + "_validated"), index=False)

# 1. 교정모델 기반 데이터로 모델 학습 데이터 생성
def makeTrainData_byCorrectionModel():
    prompt = """
            제시된 문장을 평가하라.
            문장이 자연스럽다면 "통과"를 출력한다.
            문장에서 부자연스러운 부분이 있다면 "불충분(어색한 부분: )"을 통해 문제된 부분을 서술한다.
            문장이 완전히 손상되었다고 판단될 경우 "완전손상"을 출력한다.
    """
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    filePath = open_dialog(isfolder=False, filetypes=[("Excel Files", "*.xlsx")])
    df = pd.read_excel(filePath)

    json_list = []

    for index, row in df.iterrows():
        message = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": row['Corrected']},
                {"role": "assistant", "content": row['validated']}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))

    output_file_path = filePath.with_suffix('.jsonl')

    with output_file_path.open('w', encoding='utf-8') as f:
        for item in json_list:
            f.write(item + '\n')

if __name__ == '__main__':
    # makeData_byCorrectionModel()
    makeTrainData_byCorrectionModel()


