# 결과 데이터의 Cos, SER계산
from pathlib import Path
import re
import matplotlib.pyplot as plt
from torch.nn.functional import cosine_similarity
from transformers import BertModel, BertTokenizerFast
import pandas as pd

tokenizer_bert = None
model_bert = None

# 토크나이저와 모델 로딩
def load_models():
    global tokenizer_bert, model_bert
    tokenizer_bert = BertTokenizerFast.from_pretrained("kykim/bert-kor-base")
    model_bert = BertModel.from_pretrained("kykim/bert-kor-base")

# Cosine 유사도
def calculate_cos(original_text, stt_text, corrected_text):
    contents = [original_text, stt_text, corrected_text]

    # 문장들을 인코딩하고 모델을 통해 임베딩 추출
    encoded_contents = [tokenizer_bert.encode_plus(content, return_tensors='pt', max_length=512,
                                                   truncation=True, padding='max_length') for content in contents]
    # `CLS` 토큰의 출력을 사용
    embeddings = [model_bert(**encoded_input).last_hidden_state[:,0,:] for encoded_input in encoded_contents]

    return cosine_similarity(embeddings[0], embeddings[1]), cosine_similarity(embeddings[0], embeddings[2])

# 텍스트 정제
def preprocess_text(text):
    return re.sub(r'[,.\s]', '', text)

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
def draw_result(df: pd.DataFrame, filePath: Path):
    outputPath = filePath / 'output.png'

    # 점 그래프 그리기
    plt.figure(figsize=(14, 7))

    # SER 점 그래프
    plt.subplot(1, 2, 1)
    plt.scatter(df.index, df['SER(ORI, STT)'], label='SER(ORI, STT)', color='blue')
    plt.scatter(df.index, df['SER(ORI, Cor)'], label='SER(ORI, Cor)', color='green')
    plt.xlabel('Index')
    plt.ylabel('SER Value')
    plt.title('SER Comparison')
    plt.legend()

    # Cosine 유사도 점 그래프
    plt.subplot(1, 2, 2)
    plt.scatter(df.index, df['Cosine(ORI, STT)'], label='Cosine(ORI, STT)', color='blue')
    plt.scatter(df.index, df['Cosine(ORI, Cor)'], label='Cosine(ORI, Cor)', color='green')
    plt.xlabel('Index')
    plt.ylabel('Cosine Similarity')
    plt.title('Cosine Similarity Comparison')
    plt.legend()

    # 레이아웃 조정
    plt.tight_layout()

    # 그래프를 png 파일로 저장
    plt.savefig(outputPath, format='png')
    plt.close()

def calculate_accuracy(df: pd.DataFrame, SER=True, COS=True) -> pd.DataFrame:
    load_models()
    original_text = df['original_text'].tolist()
    stt_output = df['stt_output'].tolist()
    corrected_text = df['corrected_text'].tolist()

    # SER 유사도
    if SER:
        ser = [calculate_ser(orig, stt, cor) for orig, stt, cor in zip(original_text, stt_output, corrected_text)]
        df['SER(ORI, STT)'] = [item[0] for item in ser]
        df['SER(ORI, COR)'] = [item[1] for item in ser]

    # 코사인 유사도
    if COS:
        cos = [calculate_cos(orig, stt, cor) for orig, stt, cor in zip(original_text, stt_output, corrected_text)]
        df['COS(ORI, STT)'] = [item[0] for item in cos]
        df['COS(ORI, COR)'] = [item[1] for item in cos]

    return df
