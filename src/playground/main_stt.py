import pandas as pd
from client import send_request_with_history
from openai import OpenAI
from common.auth_ import getKey
from common.info import open_dialog

KEY = getKey('OPENAI')
client = OpenAI(api_key=KEY)


if __name__ == "__main__":
    prompt = "입력하는 두 문장의 의미가 같으면 1, 다르면 0을 출력하라."
    filePath = open_dialog(False, filetypes=[("Excel Files", "*.xlsx")])
    df = pd.read_excel(filePath)
    correct = []
    count = 1

    for index, row in df.iterrows():
        conversation_history = [
            {
                "role": "system",
                "content": prompt
            }
        ]

        check = f"{df['User content'][index]}, {df['Corrected'][index]}"
        gpt_response = send_request_with_history(client, conversation_history, check, 'chatgpt-4o-latest')
        correct.append(gpt_response)

        # 출력
        print(f"{count}:{check}\t{correct[-1]}")
        count += 1

    # # SER, COS 계산
    # length = len(data["system"])
    # tb, mb = load_models()
    # for i in range(length):
    #     data["SER(u-a)"].append(calculate_ser(data["user"][i], data["assistant"][i]))  # SER 계산
    #     data["SER(u-g)"].append(calculate_ser(data["user"][i], data["gpt"][i]))  # SER 계산 (GPT)
    #     data["COS(u-a)"].append(calculate_cos(tb, mb, data["user"][i], data["assistant"][i]))  # COS 계산
    #     data["COS(u-g)"].append(calculate_cos(tb, mb, data["user"][i], data["gpt"][i]))  # COS 계산 (GPT)

    df.insert(df.columns.get_loc('Corrected') + 1, "Correct", correct)

    # 파일 경로 생성
    gpt_file_path = filePath.with_name(f"{filePath.stem}_gpt.xlsx")

    data_df = pd.DataFrame(df)

    # 엑셀 파일로 저장
    data_df.to_excel(gpt_file_path, index=False)