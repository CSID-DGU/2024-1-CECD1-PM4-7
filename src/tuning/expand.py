import pandas as pd
from common.info import open_dialog
from pathlib import Path

if __name__ == '__main__':
    path = open_dialog(False, "선택", [("Csv files", "*.csv")])
    df = pd.read_csv(path, encoding='utf-8')

    # 1. 모든 행의 User 입력 통일
    first_column_first_value = df.iloc[0, 0]
    df.iloc[1:, 0] = first_column_first_value

    # 2. 결과 열의 중복 제거 및 NaN 제거
    df = df.dropna(subset=[df.columns[1]])
    df = df.drop_duplicates(subset=[df.columns[1]]).reset_index(drop=True)
    df = df.dropna(subset=[df.columns[1]])

    # 3. 저장
    new_file_path = path.with_name(path.stem + '_removed.csv')
    df.to_csv(new_file_path, index=False, encoding='utf-8-sig')
    print(f"Modified DataFrame saved to {new_file_path}")
