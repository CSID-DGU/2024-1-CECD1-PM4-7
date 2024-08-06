from openai import OpenAI
import random
import common.info
from common.auth_ import getKey
from saveFile import makeAssistFile, applyChat
from client import send_request

PROMPT = common.info.getPrompt("playground_chat")
KEY = getKey('STT')
MODEL = 'gpt-4o-mini'
NAME = "홍길동"
EMERGENCY = ["요금체납", "주거위기", "고용위기", "급여/서비스 탈락", "긴급상황 위기", "건강위기", "에너지위기"]

client = OpenAI(api_key=KEY)

# 대화 기록
conversation_history = [
    {
        "role": "system",
        "content": PROMPT
    }
]

# 위기유형 랜덤화
# 85%의 확률로 3개, 5%의 확률로 1/2/4개
numbers = [1, 2, 3, 3, 3, 3, 3, 3, 3, 4]
EMERGENCY_COUNT = random.sample(numbers, 1)[0]
EMERGENCY_LIST = random.sample(EMERGENCY, EMERGENCY_COUNT)

# 초기 입력
first_ment = f"{NAME}: " + ", ".join(EMERGENCY_LIST)

# 대화 진행
print("아무것도 입력하지 않고 전송 시 종료됩니다.\n")

print(f"You: {first_ment}")
print("Assistant: ", send_request(client, conversation_history, first_ment, MODEL))
while True:
    user_input = input("You: ")
    if user_input.lower() == '':  # 종료

        applyChat("Chat model", conversation_history)
        # makeAssistFile(PROMPT, conversation_history)
        break
    print("Assistant:", send_request(client, conversation_history, user_input, MODEL))