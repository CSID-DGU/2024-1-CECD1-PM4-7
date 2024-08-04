# STT 데이터를 수정
import json
from pathlib import Path
import pandas as pd

from common.info import open_dialog, getPrompt

def test():
    excelPath = Path(open_dialog(isfolder=False))
    df = pd.read_excel(excelPath)

    prompt = getPrompt("playground_stt")
    json_list = []
    results = []

    for i in range(len(df)):
        uc = df["STT Result"][i].replace(" ", "")
        ac = f'1. {df["STT Result"][i].replace(" ", "")}\n2. {df["User content"][i]}'

        # JSONL 데이터 생성
        message = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": uc},
                {"role": "assistant", "content": ac}
            ]
        }
        json_list.append(json.dumps(message, ensure_ascii=False))
        results.append({"User content": uc, "Assistant content": ac})

    # JSONL 파일 저장
    jsonl_output_file_path = excelPath.with_name(excelPath.stem + '_STT.jsonl')
    with jsonl_output_file_path.open('w', encoding='utf-8-sig') as f:
        for item in json_list:
            f.write(item + '\n')

    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(results)

    # 엑셀 파일 저장
    excel_output_file_path = excelPath.with_name(excelPath.stem + '_STT.xlsx')
    results_df.to_excel(excel_output_file_path, index=False)


if __name__ == '__main__':
    test()
