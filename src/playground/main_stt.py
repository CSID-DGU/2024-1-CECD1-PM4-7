from openai import OpenAI
import common.info
from common.auth_ import getKey
from client import send_request
import pandas as pd

PROMPT = common.info.getPrompt("playground_stt")
KEY = getKey('STT')
client = OpenAI(api_key=KEY)

# 대화 기록을 저장할 DataFrame 초기화
conversation_df = pd.DataFrame(columns=['User', 'Assistant'])

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
    assistant_response = send_request(client, conversation_history, user_input)

    # 응답 출력
    print("Assistant:", assistant_response)

    # DataFrame에 질문과 답변 저장
    new_row = pd.DataFrame({'User': [user_input], 'Assistant': [assistant_response]})
    conversation_df = pd.concat([conversation_df, new_row], ignore_index=True)

# conversation_df.to_csv('conversation_history.csv', index=False)
