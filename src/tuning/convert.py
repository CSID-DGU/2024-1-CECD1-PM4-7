# jsonl 변환 파일
import json
import pandas as pd
import numpy as np
import common.info
from pathlib import Path


# 학습 데이터 형태를 갖춘 엑셀파일을 사용
# 일반 프롬프트 - 사용자 입력 - 모범 답안 형식의 경우 사용
def completed_xlsx_to_jsonl(promptName: str, filepath: Path) -> Path:
    df_conv = pd.read_excel(filepath)
    json_list = []
    prompt = common.info.getPrompt(promptName)

    for index, row in df_conv.iterrows():
        message = {
            "messages": [
                {"role": "system", "content": prompt},
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


# 대화모델 jsonl파일 생성용
def chat_xlsx_to_jsonl(filepath: Path) -> Path:
    df_conv = pd.read_excel(filepath)
    json_list = []
    for i, row in df_conv.iterrows():
        msg = []
        for index, value in enumerate(row):
            if pd.isna(value):
                break

            if index == 0:
                msg.append({"role": "system", "content": row[index]})
            elif index%2 == 1:
                msg.append({"role" : "user", "content": row[index]})
            else:
                msg.append({"role" : "assistant", "content": row[index]})

        message = {"messages": msg}
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

    # 프롬프트
    prompt = common.info.getPrompt("playground_stt")

    if to_jsonl:
        # JSONL 데이터 생성
        json_list = []
        for i in range(len(df2)):
            if i == 0:
                continue
            ac = ""
            ac += f'1. {df.iloc[i]["User content"].replace(" ", "")}\n'
            ac += f'2. {df2.iloc[i]["User content"]}'
            try:
                uc = sttResult[i - 1]
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
    len_user_content = len(df2["User content"])
    len_stt_result = len(sttResult)
    if len_user_content > len_stt_result:
        sttResult.extend([np.nan] * (len_user_content - len_stt_result))
    elif len_user_content < len_stt_result:
        df2["User content"] = df2["User content"].tolist() + [np.nan] * (len_stt_result - len_user_content)
    else:
        df_stt = pd.DataFrame({
            "User content": df2["User content"],
            "STT Result": sttResult,
        })

        output_file_path = excelPath.with_stem(excelPath.stem + '_STT').with_suffix('.xlsx')
        df_stt.to_excel(output_file_path, index=False)

    print("STT 학습 데이터 생성 완료.")
    return output_file_path


if __name__ == '__main__':
    filepath = common.info.open_dialog(False,  filetypes=[("Excel Files", "*.xlsx")])
    chat_xlsx_to_jsonl(filepath)
