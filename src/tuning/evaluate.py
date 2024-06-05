import os
import re

import matplotlib.pyplot as plt
import pandas as pd
from torch.nn.functional import cosine_similarity
from transformers import BertModel, BertTokenizerFast


# 토크나이저와 모델 로딩
def load_models():
    tokenizer_bert = BertTokenizerFast.from_pretrained("kykim/bert-kor-base")
    model_bert = BertModel.from_pretrained("kykim/bert-kor-base")
    return tokenizer_bert, model_bert

# Cosine Similarity
def calculate_cos(original_text, stt_text, corrected_text):
    tokenizer_bert, model_bert = load_models()
    contents = [original_text, stt_text, corrected_text]

    # 문장들을 인코딩하고 모델을 통해 임베딩 추출
    encoded_contents = [tokenizer_bert.encode_plus(content, return_tensors='pt', max_length=512, truncation=True, padding='max_length') for content in contents]
    # `CLS` 토큰의 출력을 사용
    embeddings = [model_bert(**encoded_input).last_hidden_state[:,0,:] for encoded_input in encoded_contents]  

    return cosine_similarity(embeddings[0], embeddings[1]), cosine_similarity(embeddings[0], embeddings[2])

# 텍스트 정제
def preprocess_text(text):
    return re.sub(r'[,\.\s]', '', text)

# 두 string의 lavenshtein distance를 계산
def calculate_levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))
        distances = new_distances
    return distances[-1]

# SER 계산
def calculate_ser(original_text, stt_text, corrected_text):
    original_text = preprocess_text(original_text)
    stt_text = preprocess_text(stt_text)
    corrected_text = preprocess_text(corrected_text)

    levenshtein_distance = calculate_levenshtein_distance(original_text, stt_text)
    total_syllables = len(original_text)
    ser1_2 = levenshtein_distance / total_syllables

    levenshtein_distance = calculate_levenshtein_distance(original_text, corrected_text)
    total_syllables = len(original_text)
    ser1_3 = levenshtein_distance / total_syllables

    return ser1_2, ser1_3


# 그래프 그리기 및 저장
def draw_result(filePath):
    # CSV 파일 읽기
    df = pd.read_csv(filePath)

    # 파일 경로에서 .csv를 제거하고 .png로 변경
    outputPath = os.path.splitext(filePath)[0] + '.png'

    # 점 그래프 그리기
    plt.figure(figsize=(14, 7))

    # SER 점 그래프
    plt.subplot(1, 2, 1)
    plt.scatter(df.index, df['SER(ori, STT)'], label='SER(ori, STT)', color='blue')
    plt.scatter(df.index, df['SER(ori, Cor)'], label='SER(ori, Cor)', color='green')
    plt.xlabel('Index')
    plt.ylabel('SER Value')
    plt.title('SER Comparison')
    plt.legend()

    # Cosine 유사도 점 그래프
    plt.subplot(1, 2, 2)
    plt.scatter(df.index, df['Cosine(Ori, STT)'], label='Cosine(Ori, STT)', color='blue')
    plt.scatter(df.index, df['Cosine(ori, Cor)'], label='Cosine(ori, Cor)', color='green')
    plt.xlabel('Index')
    plt.ylabel('Cosine Similarity')
    plt.title('Cosine Similarity Comparison')
    plt.legend()

    # 레이아웃 조정
    plt.tight_layout()

    # 그래프를 png 파일로 저장
    plt.savefig(outputPath, format='png')
    plt.show()


# 사용 예시
if __name__ == '__main__':
    # 처리할 문장들
    original_text = "원래 문장"
    stt_output = "음성 인식 결과"
    corrected_text = "교정된 문장"

    # SER 유사도 계산
    ser_1_2, ser_1_3 = calculate_ser(original_text, stt_output, corrected_text)

    # 코사인 유사도 계산
    similarity_1_2, similarity_1_3 = calculate_cos(original_text, stt_output, corrected_text)

    # 결과 출력
    print("SER between Original and STT Output:\t\t", ser_1_2)
    print("SER between Original and Corrected Text:\t\t", ser_1_3)
    print("Cosine Similarity between Original and STT Output:\t", similarity_1_2.item())
    print("Cosine Similarity between Original and Corrected Text:\t", similarity_1_3.item())