from openai import OpenAI
from common.info import getPrompt, getModelName, open_dialog
from common.auth_ import getKey
from playground.client import send_request
import pandas as pd

def stt_validation_test():
    PROMPT = getPrompt("stt_validate")
    MODEL = getModelName("stt_validate")
    KEY = getKey('STT')
    client = OpenAI(api_key=KEY)

    # DataFrame 초기화
    filepath = open_dialog(False)
    conversation_df = pd.read_excel(filepath)
    question = "건강 문제가 있으십니까?"

    result = []
    for stt_output in conversation_df["STT Result"]:
        user_input = f'질문: "{question}", 답변: "{stt_output}"'
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
        assistant_response = send_request(client, conversation_history, user_input, MODEL)

        # 응답 출력
        print("Assistant:", assistant_response)
        result.append(assistant_response)

    conversation_df["Validate Result"] = result
    conversation_df.to_excel(str(filepath).replace(".xlsx", "_validated.xlsx"), index=False)
    conversation_df.to_csv(str(filepath).replace(".xlsx", "_validated.csv"), index=False)