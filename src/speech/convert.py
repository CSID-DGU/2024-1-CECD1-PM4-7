import ffmpeg
from pathlib import Path
import pandas as pd

from tuning.convert import convert_stt_result

# 폴더 내 모든 파일을 탐색하여 .wav파일로 변환
# 변환된 파일의 샘플레이트는 16000hz로 고정함
def convert_audio_files(path, isFolder) -> list:
    converted_files = []
    path = Path(path)

    filepaths = path.iterdir() if isFolder else [path]

    for filepath in filepaths:
        if filepath.suffix.lower() in ['.mp3', '.m4a']:
            converted_files.append(convert_file(filepath))
        elif filepath.suffix.lower() == '.wav':
            converted_files.append(filepath)

    return converted_files

# .wav로 변환하는 함수
def convert_file(filepath: Path) -> Path:
    new_filepath = filepath.with_suffix('.wav')
    (
        ffmpeg
        .input(str(filepath))
        .output(str(new_filepath), ar=16000)  # 16000Hz로 샘플레이트 설정
        .run(cmd='C:/ffmpeg/bin/ffmpeg.exe', quiet=True, overwrite_output=True)
    )
    print(f"변환 완료: {new_filepath}")
    return new_filepath

# 변환된 텍스트파일 가공
def convert_text_data(fileList: list, data: list, to_jsonl: bool, excel=None):
    final_result = []
    for i, filepath in enumerate(fileList):
        sttResult = data[i]

        # "" 원소 제거
        sttResult = [ele.strip() for ele in sttResult if ele.strip() != '']
        for ele in sttResult:
            final_result.append(ele)

        if excel is None:
            new_filepath = filepath.with_suffix('.csv')
            df = pd.DataFrame(sttResult, columns=['STT'])
            df.to_csv(new_filepath, index=False, encoding='utf-8')

    if excel:  # STT 학습용 데이터 생성
        return convert_stt_result(final_result, excel, to_jsonl)

