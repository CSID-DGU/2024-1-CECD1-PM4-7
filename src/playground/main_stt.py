import pandas as pd
from client import send_request
from openai import OpenAI

from common.auth_ import getKey
from common.info import getModelName, getPrompt, open_dialog

PROMPT = getPrompt("stt_correction")
MODEL = getModelName("stt_correction")
KEY = getKey('STT')
client = OpenAI(api_key=KEY)

# 대화 기록을 저장할 DataFrame 초기화
conversation_df = pd.DataFrame(columns=['User', 'Assistant'])
isFile = input("파일 사용시 1번, 텍스트 입력시 2번: ")

# 파일 사용
if isFile == '1':
    filePath = open_dialog(False, "파일을 선택하세요")
    try:
        df = pd.read_excel(filePath)
        filetype = 'xlsx'
    except:
        df = pd.read_csv(filePath)
        filetype = 'csv'

    length = len(df)
    as1 = []
    as2 = []
    as3 = []
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
        print(f"\n{i+1}/{len(df)}")
        print(assistant_response)
        answers = assistant_response.split('\n')

        # 각 응답을 리스트에 추가
        as1.append(answers[0].split('.')[1].strip())
        as2.append(answers[1].split('.')[1].strip())
        as3.append(answers[2].split('.')[1].strip())

    df["Assistant Content 1"] = as1
    df["Assistant Content 2"] = as2
    df["Assistant Content 3"] = as3

    if filetype == 'xlsx':
        newFilePath = str(filePath).replace(".xlsx", "_corrected.xlsx")
        df.to_excel(newFilePath, encoding='utf-8-sig', index=False)
    elif filetype == 'csv':
        newFilePath = str(filePath).replace(".csv", "_corrected.csv")
        df.to_csv(newFilePath, encoding='utf-8-sig', index=False)
    

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
