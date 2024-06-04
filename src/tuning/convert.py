# jsonl 변환 파일
import json
import pandas as pd
import os

# 이미 완성된 xlsx인 경우 사용
def complete_xlsx_to_jsonl(filepath: str):
    df_conv = pd.read_excel(filepath)
    json_list = []

    for index, row in df_conv.iterrows():
        message = {
            "messages": [
                {"role": "system", "content": row['System content']},
                {"role": "user", "content": row['User content']},
                {"role": "assistant", "content": row['Assistant content']}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))

    output_file_path = os.path.splitext(filepath)[0] + '.jsonl'

    with open(output_file_path, 'w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')

    return output_file_path


# STT 결과 파일인 경우 사용
def stt_xlsx_to_jsonl(filepath: str):
    # 프롬프트
    promptPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'public', 'prompt.json')
    promptPath = os.path.abspath(promptPath)
    with open(promptPath, 'r', encoding='utf-8') as f:
        prompt_data = json.load(f)
    prompt = prompt_data["stt_correction"]

    # user input
    df_user_input = pd.read_csv(filepath, usecols=[0])
    user_input = df_user_input.iloc[:, 0]

    # Todo: Assistant content

    # JSONL 데이터 생성
    json_list = []
    for user_text in user_input:
        message = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": ""}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))

    # JSONL 파일 저장
    output_file_path = os.path.splitext(filepath)[0] + '.jsonl'
    with open(output_file_path, 'w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')

    return output_file_path


if __name__ == '__main__':
    stt_xlsx_to_jsonl("건강1.csv")
