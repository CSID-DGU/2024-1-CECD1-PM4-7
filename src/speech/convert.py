import os

import pandas as pd
from pydub import AudioSegment


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


# 변환된 텍스트파일을 csv파일로 출력
def convert_text_data(fileList: list, data: list, sliceWord: bool):
    assert len(fileList) == len(data)

    for i, filepath in enumerate(fileList):
        sttResult = data[i]
        if sliceWord:
            sliced = []
            for ele in sttResult:
                sliced.extend(ele.split(' '))
            sttResult = sliced

        # "" 원소 제거
        sttResult = [ele for ele in sttResult if ele != '']

        root, _ = filepath.rsplit('.', 1)
        new_filepath = f"{root}.csv"

        df = pd.DataFrame(sttResult, columns=['STT'])
        df.to_csv(new_filepath, index=False)

# debug
if __name__ == '__main__':
    convert_path = os.path.abspath(os.path.join(os.getcwd(), 'public'))
    convert_audio_files(convert_path)