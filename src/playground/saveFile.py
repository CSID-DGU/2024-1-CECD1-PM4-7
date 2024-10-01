# Assist content생성
import random
import time

import pandas as pd
from pathlib import Path
from tuning.convert import chat_xlsx_to_jsonl
from common.auth_ import googleAuth
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import APIError

project_dir = Path(__file__).resolve().parent.parent.parent
public_folder = project_dir / 'public'


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
    filePath = public_folder / (filename + ".xlsx")
    df.to_excel(filePath, index=False)
    print(f"대화 기록 {filename}.xlsx 생성 완료.")
    print("STT학습 데이터 생성에 사용할 수 있습니다.\n")
    chat_xlsx_to_jsonl(filePath)
    print(f"대화모델용 학습데이터 {filename}.jsonl 저장 완료.")

# Google spreadsheet 수정
def applyChat(filename: str, sheetname: str, conversation_history: list):
    # 인증
    googleAuth()

    # 구글 시트와 연결하기 위한 인증 설정
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scope)
    client = gspread.authorize(creds)

    # 스프레드시트 열기
    spreadsheet = client.open(filename)

    # 다시 시도 설정
    max_retries = 5

    for i in range(max_retries):
        try:
            try:
                worksheet = spreadsheet.worksheet(sheetname)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheetname, rows=100, cols=20)

            # 데이터 형식 수정
            res = []
            for line in conversation_history:
                res.append(line['content'])

            # 반영
            worksheet.append_row(res)
            print(f"파일 {filename}에 데이터 추가 완료.")
            break  # 성공하면 반복 종료

        except APIError as e:
            wait_time = (2 ** i) + random.uniform(0, 1)  # 지수적 백오프
            print(f"오류 발생: {e}. {wait_time:.2f}초 후 다시 시도합니다.")
            time.sleep(wait_time)

            if i == max_retries - 1:
                print(f"최대 재시도 횟수 {max_retries}회 도달. 작업 실패.")