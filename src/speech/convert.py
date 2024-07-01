import os
import sys

import pandas as pd
from pydub import AudioSegment

# directory for pyinstaller
if getattr(sys, 'frozen', False):
    program_directory = os.path.dirname(os.path.abspath(sys.executable))
else:
    program_directory = os.path.dirname(os.path.abspath(__file__))

authPath = os.path.abspath(os.path.join(program_directory, '..'))
sys.path.append(authPath)

from tuning.convert import stt_xlsx_to_jsonl


# 폴더 내 모든 파일을 탐색하여 .wav파일로 변환
# 변환된 파일의 샘플레이트는 16000hz로 고정함
def convert_audio_files(path, isFolder) -> list:
    converted_files = []

    if isFolder:
        for filename in os.listdir(path):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in ['.mp3', '.m4a']:
                file_path = os.path.join(path, filename)
                audio = AudioSegment.from_file(file_path)
                audio = audio.set_frame_rate(16000)

                new_filename = os.path.splitext(filename)[0] + '.wav'
                new_file_path = os.path.join(path, new_filename)

                audio.export(new_file_path, format='wav')
                print(f"변환 완료: {file_path} -> {new_file_path}")
                converted_files.append(new_file_path)
    else:
        file_ext = os.path.splitext(path)[1].lower()
        if file_ext in ['.mp3', '.m4a']:
            audio = AudioSegment.from_file(path)
            audio = audio.set_frame_rate(16000)

            new_filename = os.path.splitext(os.path.basename(path))[0] + '.wav'
            new_file_path = os.path.join(os.path.dirname(path), new_filename)

            audio.export(new_file_path, format='wav')
            print(f"변환 완료: {path} -> {new_file_path}")
            converted_files.append(new_file_path)

    return converted_files


# 변환된 텍스트파일 변환

def convert_text_data(fileList: list, data: list, sliceWord: bool, excelPath=None):
    assert len(fileList) == len(data)

    for i, filepath in enumerate(fileList):
        sttResult = data[i]
        if sliceWord:
            sliced = []
            for ele in sttResult:
                sliced.extend(ele.split(' '))
            sttResult = sliced

        # "" 원소 제거
        sttResult = [ele.strip() for ele in sttResult if ele.strip() != '']

        if excelPath is None:
            root, _ = filepath.rsplit('.', 1)
            new_filepath = f"{root}.csv"
            df = pd.DataFrame(sttResult, columns=['STT'])
            df.to_csv(new_filepath, index=False, encoding='utf-8')
        else:  # STT 학습용 데이터 생성
            stt_xlsx_to_jsonl(sttResult, excelPath)


# debug
if __name__ == '__main__':
    convert_path = os.path.abspath(os.path.join(os.getcwd(), 'public'))
    convert_audio_files(convert_path)
