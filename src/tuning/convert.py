# jsonl 변환 파일
import json
import os
import sys

import pandas as pd

# directory for pyinstaller
if getattr(sys, 'frozen', False):
    program_directory = os.path.dirname(os.path.abspath(sys.executable))
else:
    program_directory = os.path.dirname(os.path.abspath(__file__))

authPath = os.path.abspath(os.path.join(program_directory, '..'))
sys.path.append(authPath)

from common import auth_

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
def stt_xlsx_to_jsonl(sttResult: list, excelPath: str):
    # Assistant content
    df = pd.read_excel(excelPath)
    df2 = df[['User content']]

    if len(sttResult) != len(df2):
        print("User content와 Assistant content의 길이가 다릅니다.")
        print("데이터 확인이 필요합니다.")

    # 프롬프트
    prompt = auth_.getPrompt("stt_correction")

    # JSONL 데이터 생성
    json_list = []
    for i in range(len(df2)):
        if i == 0:
            continue
        ac = df2.iloc[i]["User content"]
        try:
            uc = sttResult[i-1]
        except IndexError:
            uc = ""
        message = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": uc},
                {"role": "assistant", "content": ac}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))

    # JSONL 파일 저장
    output_file_path = os.path.splitext(excelPath)[0] + '_STT.jsonl'
    with open(output_file_path, 'w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')

    print("STT 학습 데이터 생성 완료.")
    return output_file_path


if __name__ == '__main__':
    stt_xlsx_to_jsonl("건강1.csv")
