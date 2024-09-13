# 데이터 확장기능 관련 모듈
import re
from pathlib import Path

import pandas as pd

from common.info import open_dialog


# 중복된 데이터 제거
def remove_duplication(filePath=None) -> Path:
    if filePath is None:
        filePath = open_dialog(False)
    try:
        filetype = "csv"
        df = pd.read_csv(filePath, encoding='utf-8')
    except:
        filetype = "xlsx"
        df = pd.read_excel(filePath)

    # # 1. 모든 행의 User 입력 통일
    # first_column_first_value = df.iloc[0, 0]
    # df.iloc[1:, 0] = first_column_first_value

    original_row_count = len(df)

    # 2. 2열의 데이터 공백 통일
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: re.sub(r'\s*:\s*', ': ', x))

    # 3. 결과 열의 중복 제거 및 NaN 제거
    df = df.dropna(subset=[df.columns[1]])
    df = df.drop_duplicates(subset=[df.columns[1]]).reset_index(drop=True)
    df = df.dropna(subset=[df.columns[1]])

    final_row_count = len(df)

    # 4. 저장
    new_file_path = filePath.with_name(f"{filePath.stem}_cleaned{filePath.suffix}")
    
    if filetype == "csv":
        df.to_csv(new_file_path, index=False, encoding='utf-8-sig')
    else:
        df.to_excel(new_file_path, index=False)
    print(f"중복 데이터 {original_row_count - final_row_count}개 제거 완료")

    return new_file_path

# 학습 데이터 생성 - 형식 맞추기
def postprocess():
    path = open_dialog(False, "선택", [("Csv files", "*.csv")])
    df = pd.read_csv(path, encoding='utf-8')
    result_df = pd.DataFrame()
    
    # 1. 질문
    question = input("질문: ")

    # 2. 데이터
    raw_data = df['Completion'].apply(lambda x: x.split(':')[1].strip())
    
    result_df['Question'] = [question] * len(df)
    result_df['STT Result'] = raw_data
    
    original_path = Path(path)
    save_path = original_path.with_stem(original_path.stem + '_GPTinput')
    
    # 결과를 CSV 파일로 저장
    result_df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"결과가 {save_path}에 저장되었습니다.")


if __name__ == '__main__':
    remove_duplication()
    # postprocess()