# Cos, SER계산
import re
from torch.nn.functional import cosine_similarity
from transformers import BertModel, BertTokenizerFast

# 초성 리스트. 00 ~ 18
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
# 중성 리스트. 00 ~ 20
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ',
                 'ㅣ']
# 종성 리스트. 00 ~ 27 + 1(1개 없음)
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
                 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


def seperate_sentence(sentence: str):
    r_lst = []
    for w in list(sentence.strip()):
        ## 영어인 경우 구분해서 작성함.
        if '가' <= w <= '힣':
            ## 588개 마다 초성이 바뀜.
            ch1 = (ord(w) - ord('가')) // 588
            ## 중성은 총 28가지 종류
            ch2 = ((ord(w) - ord('가')) - (588 * ch1)) // 28
            ch3 = (ord(w) - ord('가')) - (588 * ch1) - 28 * ch2
            r_lst.append([CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]])
        else:
            r_lst.append([w])
    return r_lst


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

# 개선된 SER
def calculate_weighted_levenshtein(r_lst1, r_lst2, w_cho=0.4, w_mid=0.4, w_fin=0.2):
    try:
        len1, len2 = len(r_lst1), len(r_lst2)

        # Create a distance matrix
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        # Initialize base cases
        for i in range(1, len1 + 1):
            dp[i][0] = i
        for j in range(1, len2 + 1):
            dp[0][j] = j

        # Fill the distance matrix with weighted differences
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                char1 = r_lst1[i - 1]
                char2 = r_lst2[j - 1]

                if len(char1) < 3:
                    char1 = char1 + [' ', ' ', ' ']
                if len(char2) < 3:
                    char2 = char2 + [' ', ' ', ' ']

                if char1 == char2:
                    dp[i][j] = dp[i - 1][j - 1]  # No change needed
                else:
                    # Calculate weighted differences for each part (초성, 중성, 종성)
                    cho_diff = 0 if char1[0] == char2[0] else w_cho
                    mid_diff = 0 if char1[1] == char2[1] else w_mid
                    fin_diff = 0 if char1[2] == char2[2] else w_fin

                    # Total weighted distance for substitution
                    weighted_substitution = cho_diff + mid_diff + fin_diff

                    dp[i][j] = min(
                        dp[i - 1][j] + 1,  # Deletion
                        dp[i][j - 1] + 1,  # Insertion
                        dp[i - 1][j - 1] + weighted_substitution  # Substitution with weights
                    )

        return dp[len1][len2]

    except IndexError as e:
        print(f"Error occurred with input: r_lst1={r_lst1}, r_lst2={r_lst2}")
        raise e

# SER 계산
def calculate_ser(text1: str, text2: str):
    text1 = seperate_sentence(preprocess_text(text1))
    text2 = seperate_sentence(preprocess_text(text2))

    levenshtein_distance = calculate_weighted_levenshtein(text1, text2)
    total_syllables = max(len(text1), len(text2))
    ser = levenshtein_distance / total_syllables
    return round(ser, 5)

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
    return round(similarity.item(), 5)
