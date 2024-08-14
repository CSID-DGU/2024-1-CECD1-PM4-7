import json
from openai import OpenAI
from common.info import getPrompt, getModelName, open_dialog
from common.auth_ import getKey
import pandas as pd


# STT 교정모델 학습 데이터 생성 함수(.xlsx -> .jsonl)
def stt_correction_trainData():
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

    output_file_path = filepath.with_suffix('.jsonl')

    with output_file_path.open('w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')


if __name__ == '__main__':
    stt_correction_trainData()