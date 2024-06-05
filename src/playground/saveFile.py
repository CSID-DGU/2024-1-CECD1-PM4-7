# Assist content생성
import pandas as pd
import os
import sys
if getattr(sys, 'frozen', False):
    program_directory = os.path.dirname(os.path.abspath(sys.executable))
else:
    program_directory = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.abspath(os.path.join(program_directory, '..', '..', 'public'))
temp = os.path.abspath(os.path.join(program_directory, '..', '..', 'tuning'))
sys.path.append(temp)
from tuning.convert import complete_xlsx_to_jsonl


def makeAssistFile(PROMPT: str, conversation_history: list):
    system_content = []
    user_content = []
    assist_content = []

    for i in range(1, len(conversation_history), 2):
        system_content.append(PROMPT)
        user_content.append(conversation_history[i]['content'])
        if i + 1 < len(conversation_history):
            assist_content.append(conversation_history[i + 1]['content'])
        else:
            assist_content.append("")

    df = pd.DataFrame({
        "System content": system_content,
        "User content": user_content,
        "Assistant content": assist_content
    })

    filename = input("파일 이름: ")
    filePath = os.path.join(folder_path, filename + ".xlsx")
    df.to_excel(filePath, index=False)
    print(f"대화 기록 {filename}.xlsx 생성 완료.")
    print("STT학습 데이터 생성에 사용할 수 있습니다.\n")
    complete_xlsx_to_jsonl(filePath)
    print(f"대화모델용 학습데이터 {filename}.jsonl 저장 완료.")

