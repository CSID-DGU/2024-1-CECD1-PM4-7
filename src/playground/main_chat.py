"""
from openai import OpenAI
import random
import common.info
from common.auth_ import getKey
from saveFile import makeAssistFile, applyChat
from client import send_request_with_history

PROMPT = common.info.getPrompt("playground_chat")
KEY = getKey('OPENAI')
MODEL = common.info.getModelName("Chat")
MODEL_4o = common.info.getModelName("Chat_4o")
NAME = "홍길동"
EMERGENCY = ["요금체납", "주거위기", "고용위기", "급여/서비스 탈락", "긴급상황 위기", "건강위기", "에너지위기"]
END_SIGNAL = "종료하겠습니다"

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
print("Assistant: ", send_request_with_history(client, conversation_history, first_ment, MODEL))
while True:
    user_input = input("You: ")
    if user_input == '':
        break
    gpt_output = send_request_with_history(client, conversation_history, user_input, MODEL)
    print("Assistant:", gpt_output)

    if END_SIGNAL in gpt_output:
        break

apply = input('\n대화를 클라우드에 기록할까요?(ㅇ/ㄴ)')
if apply == 'ㅇ':
    names = ["", "jh", "jm", "sp", "sy"]
    name = int(input("자신에 해당하는 번호 입력\n1.김준혁 2.김제민 3.박상은 4.성시윤\n--> "))
    # gb = int(input("Good: 1번, Bad: 2번 입력\n--> "))

    sheetname = names[name]  # + ("_Good" if gb == 1 else "_Bad")
    applyChat("Chat model", sheetname, conversation_history)
    applyChat("Chat model(Backup)", sheetname, conversation_history)
    # makeAssistFile(PROMPT, conversation_history)
"""
# TEMP CODE FOR EXPERIMENT
from openai import OpenAI
import random
import common.info
from common.auth_ import getKey
from saveFile import makeAssistFile, applyChat
from client import send_request_with_history

PROMPT = common.info.getPrompt("playground_chat")
KEY = getKey('OPENAI')
MODEL_mini = common.info.getModelName("Chat")
MODEL_4o = common.info.getModelName("Chat_4o")
MODEL_base = 'gpt-4o-mini'
NAME = "홍길동"
EMERGENCY = ["요금체납", "주거위기", "고용위기", "급여/서비스 탈락", "긴급상황 위기", "건강위기", "에너지위기"]
END_SIGNAL = "종료하겠습니다"

client = OpenAI(api_key=KEY)

# 위기유형 랜덤 선택 (한 번만 수행)
numbers = [1, 2, 3, 3, 3, 3, 3, 3, 3, 4]
EMERGENCY_COUNT = random.sample(numbers, 1)[0]
EMERGENCY_LIST = random.sample(EMERGENCY, EMERGENCY_COUNT)

# 초기 입력 생성
first_ment = f"{NAME}: " + ", ".join(EMERGENCY_LIST)

# mini와의 대화
conversation_history_model = [
    {
        "role": "system",
        "content": PROMPT
    }
]

print("아무것도 입력하지 않고 전송 시 종료됩니다.\n")

print("=== mini와의 대화 ===")
print(f"You: {first_ment}")

response_model = send_request_with_history(client, conversation_history_model, first_ment, MODEL_mini)
print("mini:", response_model)

while True:
    user_input = input("You: ")
    if user_input == '':
        break
    response_model = send_request_with_history(client, conversation_history_model, user_input, MODEL_mini)
    print("mini:", response_model)
    if END_SIGNAL in response_model:
        break

# 4o와의 대화
conversation_history_model_4o = [
    {
        "role": "system",
        "content": PROMPT
    }
]

print("\n=== 4o와의 대화 ===")
print(f"You: {first_ment}")

response_model_4o = send_request_with_history(client, conversation_history_model_4o, first_ment, MODEL_4o)
print("4o:", response_model_4o)

while True:
    user_input = input("You: ")
    if user_input == '':
        break
    response_model_4o = send_request_with_history(client, conversation_history_model_4o, user_input, MODEL_4o)
    print("4o:", response_model_4o)
    if END_SIGNAL in response_model_4o:
        break

# base와의 대화
conversation_history_model_base = [
    {
        "role": "system",
        "content": PROMPT
    }
]

print("\n=== base와의 대화 ===")
print(f"You: {first_ment}")

response_model_base = send_request_with_history(client, conversation_history_model_base, first_ment, MODEL_base)
print("base:", response_model_base)

while True:
    user_input = input("You: ")
    if user_input == '':
        break
    response_model_base = send_request_with_history(client, conversation_history_model_base, user_input, MODEL_base)
    print("base:", response_model_base)
    if END_SIGNAL in response_model_base:
        break
