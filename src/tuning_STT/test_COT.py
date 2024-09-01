# LLaMA모델의 COT 각 단계를 개별적으로 학습하기 위한 코드
import json

import pandas as pd

from common.info import getPrompt, open_dialog


# COT 1단계: 문장의 의도파악
def stt_correction_LLaMA_COT1():
    PROMPT = getPrompt("stt_correction")
    # DataFrame
    filepath = open_dialog(False)
    df = pd.read_csv(filepath)

    json_list = []
    for index, row in df.iterrows():
        user_input = f'질문: {row["Question"]}, 답변: {row["STT Result"]}'
        output = (row["Assistant Content 1"])
        
        message = {
            "instruction": '질문에 대한 답변을 분석하라.',
            "input": user_input,
            "output": output,
        }
        
        json_list.append(json.dumps(message, ensure_ascii=False, indent=4))
    output_file_path = filepath.with_suffix('.json')

    # Write the JSON data to the output file
    with output_file_path.open('w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')

if __name__ == '__main__':
    stt_correction_LLaMA_COT1()