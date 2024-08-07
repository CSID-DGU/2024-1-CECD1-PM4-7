import sys
sys.path.append("C:\\Users\\Kimjemin\\Desktop\\대학 관련 파일\\4-1\\2024-1-CECD1-PM4-7\\src\\common")
from openai import OpenAI
import info
from auth_ import getKey
from client import send_request
import pandas as pd

PROMPT = info.getPrompt("playground_summary")
KEY = getKey('STT')
client = OpenAI(api_key=KEY)

# 대화 기록을 저장할 DataFrame 초기화
conversation_df = pd.DataFrame(columns=['User', 'Assistant'])

print("요약이 필요한 대화 내용 전문을 입력해주세요.")
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

conversation_df.to_csv('Summary_history.csv', index=False, encoding="utf-8-sig")
