# 모델 테스트 코드
from openai import OpenAI
from common.info import getPrompt, getModelName, open_dialog
from common.auth_ import getKey
from playground.client import send_request_with_history
import pandas as pd

def stt_correction_test():
    PROMPT = getPrompt("stt_correction")
    MODEL = getModelName("stt_correction")
    KEY = getKey('STT')
    client = OpenAI(api_key=KEY)

    # DataFrame 초기화
    filepath = open_dialog(False)
    df = pd.read_excel(filepath)

    ar1 = []
    ar2 = []
    ar3 = []
    for index, row in df.iterrows():
        user_input = f"질문: {row['Question']}, 답변: {row['STT Result']}"

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
        print("Assistant:", assistant_response)
        result = assistant_response.split('\n')
        ar1.append(result[0].split('.')[1])
        ar2.append(result[1].split('.')[1])
        ar3.append(result[2].split('.')[1])

    df["Correction Result 1"] = ar1
    df["Correction Result 2"] = ar2
    df["Correction Result 3"] = ar3
    df.to_excel(str(filepath).replace(".xlsx", "_corrected.xlsx"), index=False)


def stt_validation_test():
    PROMPT = getPrompt("stt_validate")
    MODEL = getModelName("stt_validate")
    KEY = getKey('STT')
    client = OpenAI(api_key=KEY)

    # DataFrame 초기화
    filepath = open_dialog(False)
    df = pd.read_excel(filepath)

    result = []
    for index, row in df.iterrows():
        user_input = f"질문: {row['Question']}, 답변: {row['Correction Result 3']}"
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
        print("Assistant:", assistant_response)
        result.append(assistant_response)

    df["Validate Result"] = result
    df.to_excel(str(filepath).replace(".xlsx", "_validated.xlsx"), index=False)


if __name__ == '__main__':
    # stt_correction_test()
    stt_validation_test()