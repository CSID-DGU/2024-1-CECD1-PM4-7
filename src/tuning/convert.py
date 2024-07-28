# jsonl 변환 파일
import json
import pandas as pd
import numpy as np
import common.info
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

# 대화모델 jsonl파일 생성용
def chat_xlsx_to_jsonl(filepath: Path) -> Path:
    df_conv = pd.read_excel(filepath)
    json_list = []
    msg = [{"role": "system", "content": df_conv.loc[0]['System content']}]

    for index, row in df_conv.iterrows():
        msg.append({"role": "user", "content": row['User content']})
        msg.append({"role": "assistant", "content": row['Assistant content']})

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


# 완성된 xlsx파일에서 정답 데이터를 제거
def remove_correct():
    filePath = common.info.open_dialog(False)
    df = pd.read_excel(filePath)
    user_content = df["User content"]
    stt_result = df["STT Result"]

    current_uc = ''
    before_stt = []
    df2 = pd.DataFrame(columns=["User content", "STT Result"])
    for i in range(len(user_content)):
        if user_content[i][-1] == '.':
            user_content[i] = user_content[i][:-1]

        if user_content[i].replace(" ", "") == current_uc.replace(" ", ""):
            if (user_content[i].replace(" ", "") != stt_result[i].replace(" ", "")
                    and stt_result[i].replace(" ", "") not in before_stt):
                df2 = df2.append({"User content": user_content[i],
                                  "STT Result": stt_result[i]}, ignore_index=True)
                before_stt.append(stt_result[i])
        else:
            current_uc = user_content[i]
            if stt_result[i].replace(" ", "") == current_uc.replace(" ", ""):
                before_stt = []
            else:
                before_stt = [stt_result[i]]
                df2 = df2.append({"User content": user_content[i],
                                  "STT Result": stt_result[i]}, ignore_index=True)

    df2.to_excel(filePath, index=False)


if __name__ == '__main__':
    remove_correct()
