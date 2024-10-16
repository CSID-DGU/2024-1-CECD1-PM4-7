# xlsx, csv, json(jsonl)파일 결합 및 분리관련 모듈
import json
import os
from pathlib import Path
import random
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


def merge_excel_files(sort=True) -> Path:
    fileList = []
    
    # 파일 선택 및 추가
    while True:
        filepath = open_dialog(False)
        if filepath.suffix != '.xlsx':
            break
        fileList.append(filepath)
    
    merged_df = pd.DataFrame()
    for file in fileList:
        df = pd.read_excel(file)
        merged_df = pd.concat([merged_df, df], ignore_index=True)
    
    # 정렬 여부
    if sort:
        merged_df = merged_df.sort_values(by=merged_df.columns.tolist())
    
    # 저장 파일 경로 설정
    common_prefix = os.path.commonprefix([os.path.basename(file) for file in fileList])
    output_filename = fileList[0].parent / f"{common_prefix}_merged.xlsx"
    
    # 파일 저장
    merged_df.to_excel(output_filename, index=False)
    
    print(f"병합된 파일이 {output_filename}로 저장되었습니다.")
    return output_filename


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


def sep_json_files(train_data_ratio=0.7):
    file_path = open_dialog(isfolder=False, filetypes=[("JSON Files", "*.json"), ("JSONL Files", "*.jsonl")])

    # read file
    with open(file_path, 'r', encoding='utf-8') as file:
        if file_path.suffix == ".json":
            data = json.load(file)
        elif file_path.suffix == ".jsonl":
            data = [json.loads(line) for line in file]

    train_size = int(len(data) * train_data_ratio)
    train_data = random.sample(data, train_size)
    test_data = [item for item in data if item not in train_data]

    # 학습 데이터 저장
    train_file_path = file_path.with_name(file_path.stem + "_train" + file_path.suffix)
    with open(train_file_path, 'w', encoding='utf-8') as train_file:
        if file_path.suffix == ".json":
            json.dump(train_data, train_file, ensure_ascii=False, indent=4)
        elif file_path.suffix == ".jsonl":
            for entry in train_data:
                train_file.write(json.dumps(entry, ensure_ascii=False) + '\n')

    # 테스트 데이터 저장
    test_file_path = file_path.with_name(file_path.stem + "_test" + file_path.suffix)
    with open(test_file_path, 'w', encoding='utf-8') as test_file:
        if file_path.suffix == ".json":
            json.dump(test_data, test_file, ensure_ascii=False, indent=4)
        elif file_path.suffix == ".jsonl":
            for entry in test_data:
                test_file.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print("json파일 분리 완료")

if __name__ == '__main__':
    sep_json_files(train_data_ratio=0.7)
    # fp = merge_excel_files(True)
    # remove_duplication(fp)