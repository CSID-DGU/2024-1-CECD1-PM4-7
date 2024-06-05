"""
What to do
1. Auth
2.
"""
import sys
import os
from openai import OpenAI
# directory for pyinstaller
if getattr(sys, 'frozen', False):
    program_directory = os.path.dirname(os.path.abspath(sys.executable))
else:
    program_directory = os.path.dirname(os.path.abspath(__file__))

authPath = os.path.abspath(os.path.join(program_directory, '..'))
sys.path.append(authPath)

import auth
from saveFile import makeAssistFile
from client import send_request

PROMPT = auth.getPlaygroundPrompt()
KEY = auth.openAIAuth()
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