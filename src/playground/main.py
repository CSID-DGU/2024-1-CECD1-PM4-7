"""
What to do
1. Auth
2.
"""
from pathlib import Path
from openai import OpenAI

import common.info
from common.auth_ import getKey
from saveFile import makeAssistFile
from client import send_request

PROMPT = common.info.getPrompt("playground")
KEY = getKey('STT')
client = OpenAI(api_key=KEY)

# 대화 기록
conversation_history = [
    {
        "role": "system",
        "content": PROMPT
    }
]

# 대화 진행
print("아무것도 입력하지 않고 전송 시 종료됩니다.")
while True:
    user_input = input("You: ")
    if user_input.lower() == '':  # 종료
        makeAssistFile(PROMPT, conversation_history)
        break
    print("Assistant:", send_request(client, conversation_history, user_input))