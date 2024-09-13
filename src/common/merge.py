import json
import os
from pathlib import Path

import pandas as pd

from common.info import open_dialog


def merge_json(filename: str):
    file_amount = int(input("합치려는 파일 수: "))

    result = []
    for i in range(file_amount):
        filePath = open_dialog(False)  # False: 파일 열기
        with filePath.open('r', encoding='utf-8-sig') as f:
            data = json.load(f)
            # 각각의 JSON 데이터를 리스트에 추가
            if isinstance(data, list):
                result.extend(data)
            else:
                result.append(data)
    
    folderPath = open_dialog(True)  # True: 폴더 선택
    filePath = folderPath / f'{filename}.json'
    
    with open(filePath, 'w', encoding='utf-8-sig') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def merge_excel_files(directory, output_file, file_pattern, start, end):
    combined_df = pd.DataFrame()

    for i in range(start, end + 1):
        input_file = os.path.join(directory, file_pattern.format(i))
        if os.path.exists(input_file):
            df = pd.read_excel(input_file)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        else:
            print(f"File {input_file} does not exist and will be skipped.")

    output_path = os.path.join(directory, output_file)
    combined_df.to_excel(output_path, index=False)

def merge_jsonl_files(directory, output_file, file_pattern, start, end):
    output_path = os.path.join(directory, output_file)
    with open(output_path, 'w', encoding='UTF-8') as outfile:
        for i in range(start, end + 1):
            input_file = os.path.join(directory, file_pattern.format(i))
            if os.path.exists(input_file):
                with open(input_file, 'r', encoding='UTF-8') as infile:
                    for line in infile:
                        outfile.write(line)
            else:
                print(f"File {input_file} does not exist and will be skipped.")


if __name__ == '__main__':
    merge_json('stt_train')