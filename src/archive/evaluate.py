# 모델 테스트 및 결과 추출
import pandas as pd
import openai
from pathlib import Path
from common.auth_ import getKey
from common.info import open_dialog
from calculate import calculate_accuracy, draw_result

# 모델 호출
def call_openai_model(prompt: str, user_input: str, model_name: str) -> str:
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.5,
        max_tokens=50,
        top_p=0.5,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n\n"]
    )
    return response.choices[0].message['content'].strip()

# 검증 프로세스
def evaluation(model_name: str):
    project_dir = Path(__file__).resolve().parent.parent.parent
    public_dir = project_dir / 'public'
    # 키
    openai.api_key = getKey('STT')

    # 검증 파일
    file_path: Path = open_dialog(False, "검증 파일 선택", [("Excel files", "*.xlsx")])

    # 1. 데이터를 읽어와 DataFrame으로 저장
    df = pd.read_excel(file_path)
    assert len(df) >= 1

    # 2. 결과를 "corrected_output"에 저장
    corrected_outputs = []
    for idx, row in df.iterrows():
        prompt = row["system_content"]
        user_input = row["stt_output"]
        corrected_output = call_openai_model(prompt, user_input, model_name)
        corrected_outputs.append(corrected_output)

    df["corrected_text"] = corrected_outputs

    # 3. 정확도 계산
    df = calculate_accuracy(df)
    
    # 4. 결과를 저장함
    draw_result(df, public_dir)
    df.to_excel(public_dir / 'output.xlsx', index=False)
