# jsonl 변환 파일
import json
import pandas as pd

import common.info
from common import auth_
from pathlib import Path

# 학습 데이터 형태를 갖춘 엑셀파일을 사용
def completed_xlsx_to_jsonl(filepath: Path) -> Path:
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

    output_file_path = filepath.with_suffix('.jsonl')

    with output_file_path.open('w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')

    return output_file_path


# STT 파이프라인을 통해 생성한 학습 데이터일 경우 사용
def convert_stt_result(sttResult: list, excelPath: Path, to_jsonl: bool):
    # Assistant content
    df = pd.read_excel(excelPath)
    df2 = df[['User content']]

    if len(sttResult) != len(df2):
        print("User content와 Assistant content의 길이가 다릅니다.")
        print("데이터 확인이 필요합니다.")

    # 프롬프트
    prompt = common.info.getPrompt("stt_train")

    if to_jsonl:
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
        output_file_path = excelPath.with_suffix('_STT.jsonl')
        with output_file_path.open('w', encoding='utf-8-sig') as f:
            for item in json_list:
                f.write(item + '\n')

    # xlsx
    else:
        df_stt = pd.DataFrame({
            "User content": df2["User content"],
            "STT Result": sttResult,
        })

        output_file_path = excelPath.with_suffix('_STT.xlsx')
        df_stt.to_excel(output_file_path, index=False)

    print("STT 학습 데이터 생성 완료.")
    return output_file_path
