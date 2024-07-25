# 데이터 확장 기능에서 중복을 제거하는 모듈
import pandas as pd
from common.info import open_dialog
import re

if __name__ == '__main__':
    path = open_dialog(False, "선택", [("Csv files", "*.csv")])
    df = pd.read_csv(path, encoding='utf-8')

    # 1. 모든 행의 User 입력 통일
    first_column_first_value = df.iloc[0, 0]
    df.iloc[1:, 0] = first_column_first_value

    original_row_count = len(df)

    # 2. 2열의 데이터 공백 통일
    df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: re.sub(r'\s*:\s*', ': ', x))

    # 3. 결과 열의 중복 제거 및 NaN 제거
    df = df.dropna(subset=[df.columns[1]])
    df = df.drop_duplicates(subset=[df.columns[1]]).reset_index(drop=True)
    df = df.dropna(subset=[df.columns[1]])

    final_row_count = len(df)

    # 4. 저장
    file_stem = path.stem
    match = re.match(r'(.*)_(\d+)_augm', file_stem)
    topic = match.group(1)
    number = int(match.group(2))
    new_file_name = f"{topic}_{number+1}.csv"
    new_file_path = path.with_name(new_file_name)
    df.to_csv(new_file_path, index=False, encoding='utf-8-sig')

    print(f"{new_file_path}에 파일 저장 완료")
    print(f"{original_row_count - final_row_count}개 데이터 삭제됨")
