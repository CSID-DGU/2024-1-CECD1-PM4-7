# Cos, SER계산
import re
from torch.nn.functional import cosine_similarity
from transformers import BertModel, BertTokenizerFast

# 토크나이저와 모델 로딩
def load_models():
    tokenizer_bert = BertTokenizerFast.from_pretrained("kykim/bert-kor-base")
    model_bert = BertModel.from_pretrained("kykim/bert-kor-base")
    return tokenizer_bert, model_bert

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
def calculate_ser(text1: str, text2: str):
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)

    levenshtein_distance = calculate_levenshtein_distance(text1, text2)
    total_syllables = max(len(text1), len(text2))
    ser = levenshtein_distance / total_syllables
    return round(ser, 3)

# Cosine 유사도(배열로)
def calculate_cos(tokenizer_bert, model_bert, original_text: str, stt_text: str):
    contents = [original_text, stt_text]

    # 문장들을 인코딩하고 모델을 통해 임베딩 추출
    encoded_contents = [tokenizer_bert.encode_plus(content, return_tensors='pt', max_length=512,
                                                   truncation=True, padding='max_length') for content in contents]
    # `CLS` 토큰의 출력을 사용
    embeddings = [model_bert(**encoded_input).last_hidden_state[:, 0, :] for encoded_input in encoded_contents]

    # 코사인 유사도를 계산하고 유사도 값만 반환
    similarity = cosine_similarity(embeddings[0], embeddings[1])

    # 유사도 값을 반환 (0-dim tensor일 경우 .item()으로 변환)
    return round(similarity.item(), 3)

