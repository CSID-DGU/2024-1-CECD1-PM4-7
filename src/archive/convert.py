import json

import pandas as pd
from openai import OpenAI

from common.auth_ import getKey
from common.info import getModelName, getPrompt, open_dialog


# STT 교정모델 학습 데이터 생성 함수(.xlsx -> .jsonl)
# OpenAI GPT모델용
def stt_correction_trainData_OpenAI():
    PROMPT = getPrompt("stt_correction")
    MODEL = getModelName("stt_correction")
    # Todo: 학습된 모델에서 STT Result, Question만을 사용하여 데이터 생성
    KEY = getKey('STT')
    client = OpenAI(api_key=KEY)

    # DataFrame
    filepath = open_dialog(False)
    df = pd.read_excel(filepath)

    json_list = []
    for index, row in df.iterrows():
        user_content = f'질문: {row["Question"]}, 답변: {row["STT Result"]}'
        assistant_content = (f'1.{row["Assistant content 1"]}\n'
                             f'2.{row["Assistant content 2"]}\n'
                             f'3.{row["Assistant content 3"]}')
        message = {
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))

    output_file_path = filepath.with_suffix('.json')

    with output_file_path.open('w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')


def stt_correction_trainData_OpenAI2():
    # DataFrame
    filepath = open_dialog(False)
    df = pd.read_excel(filepath)

    json_list = []
    for index, row in df.iterrows():
        PROMPT = f"다음은 STT를 이용하여 음성을 텍스트로 전사한 결과와 오류율이다. 이를 올바르게 수정하라. 오류율은 {row['SER(User-STT)']*100}%이다."
        user_content = row["STT Result"]
        assistant_content = row["User content"]
        message = {
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))

    output_file_path = filepath.with_name('trainData').with_suffix('.jsonl')

    with output_file_path.open('w', encoding='utf-8') as f:
        for item in json_list:
            f.write(item + '\n')

# STT 교정모델 학습 데이터 생성 함수(.xlsx -> .jsonl)
# LLaMA 모델용
def stt_correction_trainData_LLaMA():
    PROMPT = getPrompt("stt_correction")
    MODEL = getModelName("stt_correction")
    # DataFrame
    filepath = open_dialog(False)
    df = pd.read_excel(filepath)

    json_list = []
    for index, row in df.iterrows():
        user_input = f'질문: {row["Question"]}, 답변: {row["STT Result"]}'
        output = (f'1. {row["Assistant content 1"]}\n'
                f'2. {row["Assistant content 2"]}\n'
                f'3. {row["Assistant content 3"]}')
        
        message = {
            "instruction": '.'.join(PROMPT.split('.')[1:]),
            "input": user_input,
            "output": output,
            "system": PROMPT.split('.')[0]
        }
        
        json_list.append(json.dumps(message, ensure_ascii=False, indent=4))

    # Define the output file path with the same name as the input but with .json extension
    output_file_path = filepath.with_suffix('.json')

    # Write the JSON data to the output file
    with output_file_path.open('w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')


        
if __name__ == '__main__':
    stt_correction_trainData_OpenAI2()