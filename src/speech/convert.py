from pathlib import Path

import ffmpeg
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
        .output(str(new_filepath), ar=16000, ac=1)  # 16000Hz로 샘플레이트 설정
        .run(cmd='C:/ffmpeg/bin/ffmpeg.exe', quiet=True, overwrite_output=True)
    )
    print(f"변환 완료: {new_filepath}")
    return new_filepath

# 변환된 텍스트파일 가공
def convert_text_data(fileList: list, data: list, to_jsonl: bool, excel=None, suffix='') -> Path:
    final_result = []
    for i, filepath in enumerate(fileList):
        sttResult = data[i]

        # "" 원소 제거
        sttResult = [ele.strip() for ele in sttResult if ele.strip() != '']
        for ele in sttResult:
            final_result.append(ele)

    if excel and to_jsonl:  # STT 학습용 데이터 생성
        return convert_stt_result(final_result, excel, to_jsonl)
    
    elif excel and not to_jsonl: # 단순 데이터 생성
        df = pd.read_excel(excel)
        len_final_result = len(final_result)
        len_df = len(df)
        if len_final_result < len_df:
            # final_result가 짧으면 빈 문자열로 채움
            final_result += [''] * (len_df - len_final_result)
        elif len_final_result > len_df:
            # df가 짧으면 df에 빈 행 추가
            extra_rows = pd.DataFrame(index=range(len_final_result - len_df), columns=df.columns)
            df = pd.concat([df, extra_rows], ignore_index=True)
        df['STT Result'] = final_result
        output_file = excel.with_stem(excel.stem + f"_{suffix}")
        df.to_excel(output_file, index=False)

        return output_file