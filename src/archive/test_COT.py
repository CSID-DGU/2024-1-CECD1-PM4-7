# LLaMA모델의 COT 각 단계를 개별적으로 학습하기 위한 코드
import json

import pandas as pd
from openai import OpenAI

from common.auth_ import getKey
from common.info import getModelName, open_dialog
from playground.client import send_request_with_history


# GPT Playground를 사용하여 학습 데이터 생성
def createData_fromGPT():
    PROMPT = '"질문"에 의거하여 "답변"을 키워드 위주로 분석하라. 다음은 그 예시이다.\n질문: 건강 문제가 있으신가요?, 답변: 만성질환으로 몸이 아파\n예시 출력: 답변자는 "건강 문제"에 관한 질문에 "만성질환"으로 인해 "몸"이 아프다고 답변하였다.'
    MODEL = "gpt-4o-mini"
    KEY = getKey('STT')
    client = OpenAI(api_key=KEY)

    filePath = open_dialog(False, "파일을 선택하세요")
    df = pd.read_csv(filePath)
    result = []
    for index, row in df.iterrows():
        user_input = f'질문: {row["Question"]}, 답변: {row["STT Result"]}'

        # 대화 기록 초기화
        conversation_history = [
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        # OpenAI API 요청 및 응답 받기
        assistant_response = send_request_with_history(client, conversation_history, user_input, MODEL)

        # 응답 출력
        print(f"\n{index+1}/{len(df)}")
        print(assistant_response)
        result.append(assistant_response)

    df["Assistant Content 1"] = result
    newFilePath = str(filePath).replace(".csv", "_corrected.csv")
    df.to_csv(newFilePath, encoding='utf-8-sig', index=False)


# COT 1단계: 문장의 의도파악
def stt_correction_LLaMA_COT1():
    # DataFrame 불러오기
    filepath = open_dialog(False)
    df = pd.read_csv(filepath)

    json_list = []
    for index, row in df.iterrows():
        user_input = f'질문: {row["Question"]}, 답변: {row["STT Result"]}'
        output = (row["Assistant Content 1"])
        
        message = {
            "instruction": '"질문"에 의거하여 "답변"을 키워드 위주로 분석하라.',
            "input": user_input,
            "output": output,
        }
        
        json_list.append(message)

    # JSON 배열로 결과물 저장
    output_file_path = filepath.with_suffix('.json')
    with output_file_path.open('w', encoding='utf-8-sig') as f:
        json.dump(json_list, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # createData_fromGPT()
    stt_correction_LLaMA_COT1()