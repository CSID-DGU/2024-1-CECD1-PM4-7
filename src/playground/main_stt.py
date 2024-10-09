import pandas as pd
from client import send_request
from openai import OpenAI
from tuning_STT.calculate import load_models,calculate_cos,calculate_ser
from common.auth_ import getKey
from common.info import getModelName, getPrompt, open_dialog
from pathlib import Path
import json

PROMPT = getPrompt("stt_correction")
MODEL = getModelName("stt_correction")
KEY = getKey('OPENAI')
client = OpenAI(api_key=KEY)

# 대화 기록을 저장할 DataFrame 초기화
conversation_df = pd.DataFrame(columns=['User', 'Assistant'])
isFile = input("파일 사용시 1번, 텍스트 입력시 2번: ")

# 파일 사용
if isFile == '1':
    filePath = open_dialog(False)

    data = { "system": [], "user": [], "assistant": [], "gpt": [], "correct": [],
            "SER(u-a)": [], "SER(u-g)": [], "COS(u-a)": [], "COS(u-g)": []
    }

    # OpenAI API 호출
    with filePath.open('r', encoding='utf-8') as file:
        count = 1
        for line in file:
            line_data = json.loads(line)
            messages = line_data.get('messages', [])
            for message in messages:
                role = message.get('role')
                content = message.get('content')

                if role == 'system':
                    content = "다음은 STT를 이용하여 음성을 텍스트로 전사한 결과와 오류율이다. 이를 올바르게 수정하라."
                    data["system"].append(content)
                elif role == 'user':
                    data["user"].append(content)
                elif role == 'assistant':
                    data["assistant"].append(content)

            # 1. GPT 교정데이터 추출
            conversation_history = [
                {
                    "role": "system",
                    "content": data["system"][-1]
                },
            ]
            gpt_response = send_request(client, conversation_history, data["user"][-1], MODEL)
            data["gpt"].append(gpt_response)
            
            # 2. GPT 교정데이터 검사
            conversation_history = [
                {
                    "role": "system",
                    "content": "입력하는 두 문장의 의미가 같으면 1, 다르면 0을 출력하라"
                },
            ]
            check = data["assistant"][-1] + "\n" + data["gpt"][-1]
            gpt_response = send_request(client, conversation_history, check, 'chatgpt-4o-latest')
            data["correct"].append(gpt_response)

            # 출력
            print(f"{count}:\t{data['gpt'][-1]}\tCorrect?: {data['correct'][-1]}")
            count += 1

    # SER, COS 계산
    length = len(data["system"])
    tb, mb = load_models()
    for i in range(length):
        data["SER(u-a)"].append(calculate_ser(data["user"][i], data["assistant"][i]))  # SER 계산
        data["SER(u-g)"].append(calculate_ser(data["user"][i], data["gpt"][i]))  # SER 계산 (GPT)
        data["COS(u-a)"].append(calculate_cos(tb, mb, data["user"][i], data["assistant"][i]))  # COS 계산
        data["COS(u-g)"].append(calculate_cos(tb, mb, data["user"][i], data["gpt"][i]))  # COS 계산 (GPT)


    # 엑셀 파일로 저장
    def generate_gpt_file_path(file_path: Path) -> Path:
        return file_path.with_name(f"{file_path.stem}_gpt.xlsx")


    # 파일 경로 생성
    gpt_file_path = generate_gpt_file_path(filePath)

    # 데이터를 pandas DataFrame으로 변환
    data_df = pd.DataFrame(data)

    # 엑셀 파일로 저장
    data_df.to_excel(gpt_file_path, index=False)



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
