# STT 평가모델 학습데이터 생성
from common.info import getPrompt, getModelName, open_dialog
from common.auth_ import getKey
from playground.client import send_request_without_history, send_request_with_history
from openai import OpenAI
import pandas as pd
import numpy as np
import json
import re
import random

KEY = getKey('OPENAI')
client = OpenAI(api_key=KEY)


# prompt = getPrompt("stt_validation_241015")

# 1. 교정모델 학습용 데이터를 기반으로 생성
def makeData_byCorrectionModel():
    prompt = """
    프롬프트: User문장은 원문이고, Correct문장은 너가 평가해야할 문장이다.
    서로 의미가 {같다고}/{다르다고} 평가되었을 때, 문장 간 의미가 정말로 같다면 "통과"를 출력하라.
    문장 간 의미가 다르다면 "불충분(어색한 부분: )"을 출력하여 어느 부분에서 수정이 필요한지 출력하라.
    문장의 의미가 완전히 파괴되었다면 "완전손상"을 출력하라.
    
    아래는 그 예시이다.
    User: 인플루엔자 예방접종을 맞고왔어
    Correct: 인플루엔자 예방 접종을 받고 왔어
    모범 출력: 통과
    
    User: 허튼 말해서 분란을 일으키지 마
    Correct: 버튼을 말해서 분란을 일으키지 마
    모범 출력: 불충분(어색한 부분: 버튼을)
    
    User: 뱃속이 쿡쿡 쑤시는 느낌이야
    Correct: 뱃속에 구슬은 느낌이야
    모범 출력: 완전손상
    """

    filePath = open_dialog(isfolder=False, filetypes=[("Excel Files", "*.xlsx")])
    df = pd.read_excel(filePath)

    result = []
    for index, row in df.iterrows():
        correct = "같다고" if row["Correct"] == '1' else "다르다고"
        prompt1 = prompt.replace("{같다고}/{다르다고}", correct)
        user_input = f'User: {row["User content"]}, Correct: row["Corrected"]'

        response = send_request_without_history(client, prompt1, user_input, "chatgpt-4o-latest")
        print(f"{index + 1}: {response}")
        result.append(response)

    df["validated"] = result
    df.to_excel(filePath.with_stem(filePath.stem + "_validated"), index=False)


# 1. 교정모델 기반 데이터로 모델 학습 데이터 생성
def makeTrainData_byCorrectionModel():
    prompt = """
            제시된 문장을 평가하라.
            문장이 자연스럽다면 "통과"를 출력한다.
            문장에서 부자연스러운 부분이 있다면 "불충분(어색한 부분: )"을 통해 문제된 부분을 서술한다.
            문장이 완전히 손상되었다고 판단될 경우 "완전손상"을 출력한다.
    """
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    filePath = open_dialog(isfolder=False, filetypes=[("Excel Files", "*.xlsx")])
    df = pd.read_excel(filePath)

    json_list = []

    for index, row in df.iterrows():
        message = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": row['Corrected']},
                {"role": "assistant", "content": row['validated']}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))

    output_file_path = filePath.with_suffix('.jsonl')

    with output_file_path.open('w', encoding='utf-8') as f:
        for item in json_list:
            f.write(item + '\n')


# 2. 대화모델 학습용 데이터를 기반으로 생성
def makeData_byChatModel():
    # 성능이 별로라 분리만 하고 수기로 수정할 계획
    filePath = open_dialog(isfolder=False, filetypes=[("Excel Files", "*.xlsx")])
    df = pd.read_excel(filePath, header=None)
    prompt = "다음 질문과 답변은 전체 대화의 일부에 속한다. 질문과 답변이 매끄럽게 이어진다면 '통과'를, 그렇지 않다면 '부족'을 출력하라.질문에 대한 단답형 답변은 통과로 간주한다."

    question = []
    answer = []
    result = []

    for index, row in df.iterrows():
        column = 2
        try:
            while True:
                if len(row[column]) != 0 and len(row[column + 1]) != 0:
                    question.append(row[column])
                    answer.append(row[column + 1])
                    user_input = f'질문: {row[column]}, 답변: {row[column + 1]}'
                    print(user_input)
                    response = send_request_without_history(client, prompt, user_input, "gpt-4o-mini")
                    print(response + "\n")
                    result.append(response)
                    column += 2
                else:
                    break
        except Exception as e:
            continue

    df2 = pd.DataFrame(zip(question, answer, result), columns=["Question", "Answer", "Assistant"])
    df2.to_excel(filePath.with_stem(filePath.stem + "_trainData"), index=False)


# 3. 대화모델 반복 호출로 긍정/부정 답변을 다수 생성
def processQuestion(question: str) -> str:
    last_sentence = question.split('.')[-1]
    return last_sentence.strip()

def expandData_byChatModel(iter: int):
    PROMPT = getPrompt("playground_chat")
    MODEL = getModelName("Chat")
    END_SIGNAL = "종료하겠습니다"

    numbers = [1, 2, 3, 3, 3, 3, 3, 3, 3, 4]
    EMERGENCY = ["요금체납", "주거위기", "고용위기", "급여/서비스 탈락", "긴급상황 위기", "건강위기", "에너지위기"]

    questions = []
    # iter번만큼 질문 개수를 생성
    for i in range(iter):
        EMERGENCY_COUNT = random.sample(numbers, 1)[0]
        EMERGENCY_LIST = random.sample(EMERGENCY, EMERGENCY_COUNT)
        conversation_history = [
            {
                "role": "system",
                "content": PROMPT
            }
        ]
        first_ment = f"홍길동: " + ", ".join(EMERGENCY_LIST)
        gpt_output = send_request_with_history(client, conversation_history, first_ment, MODEL)
        print(gpt_output)
        questions.append(processQuestion(gpt_output))

        while True:
            user_input = "아니"
            gpt_output = send_request_with_history(client, conversation_history, user_input, MODEL)
            print(gpt_output)
            if END_SIGNAL in gpt_output:
                break
            questions.append(processQuestion(gpt_output))
    """------------------------------------------------------------------------------------------"""
    # 질문 개수만큼 랜덤 답변 생성
    rand = [0, 1]
    yes = ["예", "네", "맞아요", "어"]
    no = ["아니", "아니오", "아니요"]
    answers = []
    extraPrompt = "너는 '질문'에 대한 답변을 생성해야한다. {imok} 답변이고, '{addExtra},'문구로 시작하라. 존댓말/반말 여부는 시작 문구와 맞추고, 총 답변의 길이는 간결하게 작성한다. 쉼표, 마침표는 제거한다."
    for question in questions:
        # 50%의 확률로 긍정
        imok = random.choice(rand)

        # 50%의 확률로 부가설명 추가
        addExtra = random.choice(rand)

        if addExtra: # 모델에 데이터 생성 요청
            p = extraPrompt.replace('{imok}', "긍정" if imok else "부정")
            p = p.replace('{addExtra}', random.choice(yes) if imok else random.choice(no))
            user_input = "질문: " + question
            conversation_history = [
                {
                    "role": "system",
                    "content": p
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=conversation_history,
                temperature=1.0,
                max_tokens=256,
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0
            )
            print(response.choices[0].message.content)
            answers.append(response.choices[0].message.content.replace(',', ''))
        else: # 바로 추가
            answers.append(random.choice(yes) if imok else random.choice(no))

    df = pd.DataFrame({
        'Questions': questions,
        'Answers': answers
    })

    # 엑셀 파일로 저장
    df.to_excel("validation_yesno.xlsx", index=False)


# 4. 모든 데이터를 일정 비율로 섞어서 새로운 데이터셋 생성
def mixToNewData():
    pass1 = open_dialog(isfolder=False, filetypes=[("JSON Lines Files", "*.jsonl")]) # 대화모델기반
    sample_df1 = pd.read_json(pass1, lines=True, encoding='utf-8-sig')
    pass2 = open_dialog(isfolder=False, filetypes=[("JSON Lines Files", "*.jsonl")]) # 평가모델_긍부정
    sample_df2 = pd.read_json(pass2, lines=True, encoding='utf-8')
    notpass = open_dialog(isfolder=False, filetypes=[("JSON Lines Files", "*.jsonl")]) # STT데이터
    df = pd.read_json(notpass, lines=True, encoding='utf-8')

    json_list = []
    """
    데이터 혼합 비율
    1. STT파일의 경우 불충분/완전손상만을 사용, "모범출력:" 항목을 제거
        User항목을 프롬프트와 결합
        최종 데이터 수를 기록
    2. 대화모델 분리파일, 긍부정 파일은 1번의 최종 데이터 수를 기록하여 절반씩 차지, 랜덤 샘플링 
    """
    count = 0
    for index, row in df.iterrows():
        system = row['messages'][0]['content']
        user = row['messages'][1]['content']
        assistant = row['messages'][2]['content']
        if "모범 출력: " in assistant:
            assistant = assistant.replace("모범 출력: ", "")

        if assistant == "통과":
            continue
        else:
            count += 1
            system = f"{system}\n 문장: '{user}'"
            message = {
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "assistant", "content": assistant}
                ]
            }
            json_list.append(json.dumps(message, ensure_ascii=False))

    # 통과 데이터 샘플링
    sample_df1 = sample_df1.sample(n=int(count/2), random_state=1)
    sample_df2 = sample_df2.sample(n=int(count/2), random_state=1)

    for _, row in sample_df1.iterrows():
        json_list.append(json.dumps(row.to_dict(), ensure_ascii=False))

    for _, row in sample_df2.iterrows():
        json_list.append(json.dumps(row.to_dict(), ensure_ascii=False))

    # 저장
    output_path = 'combined_data.jsonl'
    random.shuffle(json_list)
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in json_list:
            f.write(item + '\n')


if __name__ == '__main__':
    # makeData_byCorrectionModel()
    # makeTrainData_byCorrectionModel()
    # makeData_byChatModel()
    # expandData_byChatModel(200)
    mixToNewData()