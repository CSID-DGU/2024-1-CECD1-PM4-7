# 기존 데이터를 분석하는 코드
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

# 한글 폰트 설정
font_path = "C:/Windows/Fonts/malgun.ttf"  # 폰트 경로를 시스템에 맞게 설정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

# 패키지 내의 파일 경로 가져오기
test_csv_path = os.path.join(os.getcwd(), '..', '..', 'public', 'AI_bokji_result_final.csv')
try:
    df = pd.read_csv(test_csv_path, encoding='euc-kr', index_col=0)
except UnicodeError:
    df = pd.read_csv(test_csv_path, encoding='utf-8', index_col=0)

# STT 전처리 - 앞뒤 공백 및 줄바꿈 문자 제거
df['STT_TRNF_RSLT_CN'] = df['STT_TRNF_RSLT_CN'].str.strip()

# 1. 'VOC_SDRC_DCD' 값이 'RX'인 데이터만 추출
df_rx = df[df['VOC_SDRC_DCD'] == 'RX'].copy()

# 2. 'STT_TRNF_RSLT_CN' 값 분석 (공백 및 줄바꿈 문자 제거)
df_rx['STT_TRNF_RSLT_CN'] = df_rx['STT_TRNF_RSLT_CN'].str.strip()

# 3. 중복된 데이터의 수 계산
stt_counts = df_rx['STT_TRNF_RSLT_CN'].value_counts().reset_index()
stt_counts.columns = ['STT_TRNF_RSLT_CN', 'count']

# 4. 개수가 1개인 데이터는 '기타' 항목으로 분류
def categorize_stt(row):
    if row['STT_TRNF_RSLT_CN'].startswith('눌러야') or row['STT_TRNF_RSLT_CN'].startswith('눌라야')\
            or row['STT_TRNF_RSLT_CN'].startswith('놀라야') or '녹음' in row['STT_TRNF_RSLT_CN']\
            or '번호' in row['STT_TRNF_RSLT_CN'] or '남기' in row['STT_TRNF_RSLT_CN']:
                return '기타'
    else:
        return row['STT_TRNF_RSLT_CN']

stt_counts['STT_TRNF_RSLT_CN'] = stt_counts.apply(categorize_stt, axis=1)

# 최종 결과를 데이터프레임으로 다시 정리
final_counts = stt_counts.groupby('STT_TRNF_RSLT_CN')['count'].sum().reset_index()

# Count 기준 내림차순 정렬
final_counts = final_counts.sort_values(by='count', ascending=False)

# 시각화
plt.figure(figsize=(10, 8))
plt.barh(final_counts['STT_TRNF_RSLT_CN'], final_counts['count'], color='skyblue')
plt.xlabel('Count')
plt.ylabel('STT_TRNF_RSLT_CN')
plt.title('STT_TRNF_RSLT_CN Count')
plt.gca().invert_yaxis()  # y축을 뒤집어 큰 값이 위로 오도록 설정

# 이미지 파일로 저장
image_path = os.path.join(os.path.dirname(test_csv_path), 'result.png')
plt.savefig(image_path, bbox_inches='tight')
plt.close()

# 최종 결과를 CSV 파일로 저장
result_csv_path = os.path.join(os.path.dirname(test_csv_path), 'AI_bokji_result_answers.csv')
final_counts.to_csv(result_csv_path, index=False, encoding='euc-kr')
print("파일이 성공적으로 저장되었습니다.", image_path)
