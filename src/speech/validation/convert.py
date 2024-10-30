from pathlib import Path
import pandas as pd
import json
from common.info import getPrompt, open_dialog

# 대화 데이터를 각각 분리
def chat_xlsx_to_jsonl_seperation(filepath: Path) -> Path:
    df_conv = pd.read_excel(filepath)
    json_list = []

    for i, row in df_conv.iterrows():
        for index in range(2, len(row)-1, 2):
            msg = []
            if pd.isna(row[index]) or pd.isna(row[index + 1]):
                break
            prompt = getPrompt("stt_validation_241021")
            prompt = prompt.replace("질문: {}", f"질문: \"{row[index]}\"")
            prompt = prompt.replace("답변: {}", f"답변: \"{row[index+1]}\"")

            msg.append({"role": "system", "content": prompt})
            msg.append({"role": "assistant", "content": "통과"})

            message = {"messages": msg}
            json_list.append(json.dumps(message, ensure_ascii=False))

    output_file_path = filepath.with_suffix('.jsonl')

    with output_file_path.open('w', encoding='utf-8') as f:
        for item in json_list:
            f.write(item + '\n')

    return output_file_path

# 평가모델 긍/부정 학습데이터용
def validation_yesno_to_jsonl(filepath: Path):
    df_conv = pd.read_excel(filepath)
    json_list = []
    prompt = getPrompt("stt_validation_241021")

    for index, row in df_conv.iterrows():
        p = prompt.replace("질문: {}", f"질문: '{row['Questions']}'")
        p = p.replace("답변: {}", f"답변: '{row['Answers']}'")
        message = {
            "messages": [
                {"role": "system", "content": p},
                {"role": "assistant", "content": "통과"}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))

    output_file_path = filepath.with_suffix('.jsonl')

    with output_file_path.open('w', encoding='utf-8') as f:
        for item in json_list:
            f.write(item + '\n')


if __name__ == '__main__':
    filepath = open_dialog(False,  filetypes=[("Excel Files", "*.xlsx")])
    # chat_xlsx_to_jsonl_seperation(filepath)
    validation_yesno_to_jsonl(filepath)