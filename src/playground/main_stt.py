from openai import OpenAI
from common.info import getPrompt, getModelName, open_dialog
from common.auth_ import getKey
from client import send_request
import pandas as pd

PROMPT = getPrompt("playground_stt")
MODEL = getModelName("STTv2")
KEY = getKey('STT')
client = OpenAI(api_key=KEY)

# 대화 기록을 저장할 DataFrame 초기화
conversation_df = pd.DataFrame(columns=['User', 'Assistant'])
isFile = input("파일 사용시 1번, 텍스트 입력시 2번: ")

# 파일 사용
if isFile == '1':
    filePath = open_dialog(False, "파일을 선택하세요")
    df = pd.read_excel(filePath)
    length = len(df)
    answer = []
    for i in range(length):
        st = df["STT Result"][i]

        # 대화 기록 초기화
        conversation_history = [
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": st
            }
        ]

        # OpenAI API 요청 및 응답 받기
        assistant_response = send_request(client, conversation_history, st, MODEL)

        # 응답 출력
        print(assistant_response)
        answer.append(assistant_response)
    df["Corrected"] = answer

    newFilePath = str(filePath).replace(".xlsx", "_corrected.xlsx")
    df.to_excel(newFilePath)

# 텍스트 입력
elif isFile == '2':
    print("아무것도 입력하지 않고 전송 시 종료됩니다.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == '':  # 종료
            break

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

        # DataFrame에 질문과 답변 저장
        new_row = pd.DataFrame({'User': [user_input], 'Assistant': [assistant_response]})
        conversation_df = pd.concat([conversation_df, new_row], ignore_index=True)

    # conversation_df.to_csv('conversation_history.csv', index=False)
