import os

import auth
import evaluate
import pandas as pd
from openai import OpenAI


def add_data(df, original_text, stt_output, corrected_text, ser_ori_stt, ser_ori_cor, cosine_ori_stt, cosine_ori_cor):
    new_data = {
        'original_text': [original_text],
        'stt_output': [stt_output],
        'corrected_text': [corrected_text],
        'SER(ori, STT)': [ser_ori_stt],
        'SER(ori, Cor)': [ser_ori_cor],
        'Cosine(Ori, STT)': [cosine_ori_stt],
        'Cosine(ori, Cor)': [cosine_ori_cor]
    }
    new_df = pd.DataFrame(new_data)
    df = pd.concat([df, new_df], ignore_index=True)
    return df


if __name__ == '__main__':
    key = auth.openAIAuth()
    
    df = pd.DataFrame(columns=[
        'original_text', 'stt_output', 'corrected_text',
        'SER(ori, STT)', 'SER(ori, Cor)',
        'Cosine(Ori, STT)', 'Cosine(ori, Cor)'
    ])

    file_path = "This is Dummy Path"

    # 엑셀 파일을 읽어 데이터프레임으로 구성
    df_data = pd.read_excel(file_path)

    # 'user_content'와 'assistant_content' 컬럼의 데이터를 각각 리스트로 저장
    questions = df_data['User content'].tolist()
    origins = df_data['Assistant content'].tolist()

    # 결과 출력
    print("Questions:", questions)
    print("Origin:", origins)

    messages = [
        [{"role": "user", "content": question}] for question in questions
    ]

    for message, origin, question in zip(messages, origins, questions):
        response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:personal::9EdV2QBZ",
        messages= message,
        temperature=1,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n\n"]
        )
        original_text = origin
        stt_output = question
        corrected_text = response.choices[0].message.content
        contents = [original_text, stt_output, corrected_text]

        ser_1_2, ser_1_3 = evaluate.calculate_ser(original_text, stt_output, corrected_text)
        cos_1_2, cos_1_3 = evaluate.calculate_cos(original_text, stt_output, corrected_text)

        df = add_data(df, original_text, stt_output, corrected_text,
                        ser_1_2, ser_1_3, cos_1_2.item(), cos_1_3.item())

df.to_excel('output.xlsx', index=False)
print("Dataframe saved to 'output.xlsx'")