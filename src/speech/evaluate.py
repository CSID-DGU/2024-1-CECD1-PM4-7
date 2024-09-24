import pandas as pd
import sys
from common import info
from playground.client import send_request
from tuning_STT.calculate import calculate_levenshtein_distance
from pathlib import Path

# 완성된 xlsx파일에서 정답 데이터를 제거
def remove_correct(filePath=None) -> Path:
    if filePath is None:
        filePath = info.open_dialog(False)
    df = pd.read_excel(filePath)
    user_content = df["User content"]
    stt_result = df["STT Result"]

    current_uc = ''
    before_stt = []

    # 기존 DataFrame의 구조를 유지한 채로 새로운 DataFrame 생성
    df2 = pd.DataFrame(columns=df.columns)

    for i in range(len(user_content)):
        if user_content[i][-1] == '.':
            user_content[i] = user_content[i][:-1]

        if user_content[i].replace(" ", "") == current_uc.replace(" ", ""):
            if (user_content[i].replace(" ", "") != stt_result[i].replace(" ", "")
                    and stt_result[i].replace(" ", "") not in before_stt):
                new_row = df.iloc[[i]]  # 현재 행을 그대로 새로운 df2에 추가
                df2 = pd.concat([df2, new_row], ignore_index=True)
                before_stt.append(stt_result[i])
        else:
            current_uc = user_content[i]
            if stt_result[i].replace(" ", "") == current_uc.replace(" ", ""):
                before_stt = []
            else:
                before_stt = [stt_result[i]]
                new_row = df.iloc[[i]]  # 현재 행을 그대로 새로운 df2에 추가
                df2 = pd.concat([df2, new_row], ignore_index=True)

    newFilePath = filePath.with_name(f"{filePath.stem}_onlyError{filePath.suffix}")
    df2.to_excel(newFilePath, index=False)
    print("정답 데이터 제거 완료.")
    return newFilePath


# 완성된 엑셀 파일에서 SER을 계산
def evaluate_SER(filePath=None) -> Path:
    if filePath is None:
        filePath = info.open_dialog(False)
    df = pd.read_excel(filePath)
    df2 = pd.DataFrame(columns=["User content", "STT Result"])

    df2["User content"] = df["User content"].str.replace(" ", "")
    df2["STT Result"] = df["STT Result"].str.replace(" ", "")

    # SER 계산
    try:
        df['SER'] = [calculate_levenshtein_distance(orig, stt)/len(orig)
                     for orig, stt in zip(df2["User content"], df2["STT Result"])]
    except:
        print("오류 발생!")
        sys.exit()

    newFilePath = filePath.with_name(f"{filePath.stem}_SER{filePath.suffix}")
    df.to_excel(newFilePath, index=False)
    print("SER 계산완료.")
    return newFilePath

# 평가모델
def evaluation_model():
    pass

if __name__ == '__main__':
    evaluate_SER()
