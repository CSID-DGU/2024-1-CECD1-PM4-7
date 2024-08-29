# LLaMA모델의 COT 각 단계를 개별적으로 학습하기 위한 코드
import json

import pandas as pd

from common.info import getPrompt, open_dialog


# COT 1단계: 문장의 의도파악
def stt_correction_trainData_LLaMA():
    PROMPT = getPrompt("stt_correction")
    # DataFrame
    filepath = open_dialog(False)
    df = pd.read_excel(filepath)

    json_list = []
    for index, row in df.iterrows():
        user_input = f'질문: {row["Question"]},\n답변: {row["STT Result"]}'
        output = (row["Assistant content 1"])
        
        message = {
            "instruction": '답변의 의도를 파악하라.',
            "input": user_input,
            "output": output,
            "system": PROMPT.split('.')[0]
        }
        
        json_list.append(json.dumps(message, ensure_ascii=False, indent=4))
    output_file_path = filepath.with_suffix('.json')

    # Write the JSON data to the output file
    with output_file_path.open('w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')