import pprint
import wave
from convert import convert_audio_files, convert_text_data
import google.cloud.speech_v1p1beta1 as speech
import google.cloud.storage as storage
from common.info import open_dialog
import re

# STT
def transcribe_audio(file_path):
    client = speech.SpeechClient()

    with file_path.open("rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
    )

    with wave.open(str(file_path), 'rb') as wav_file:
        duration = wav_file.getnframes() / wav_file.getframerate()

    if duration > 60:
        return transcribe_long_audio(file_path)
    else:
        response = client.recognize(config=config, audio=audio)

        transcripts = [result.alternatives[0].transcript for result in response.results]
        return transcripts


# 1분 이상의 STT 처리
def transcribe_long_audio(file_path):
    client = speech.SpeechClient()
    print("1분 이상의 파일이므로 온라인으로 처리합니다...")
    bucket_name = 'stt_test_by_pm4'
    destination_blob_name = file_path.name
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)
    gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
    )
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=180)

    transcripts = [result.alternatives[0].transcript for result in response.results]
    return transcripts

# 폴더 내 객체 정렬을 위한 함수
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def STT_pipeline(askFolder=None, makeTrainData=None):
    convert_result = []
    if askFolder is None:
        askFolder = input("폴더를 선택할까요?(Y/N): ").strip().lower() == 'y'
    if askFolder:
        path = open_dialog(True)
    else:
        path = open_dialog(False, filetypes=[("Audio files", "*.m4a *.mp3 *.wav")])
    fileList = convert_audio_files(path, askFolder)  # wav로 변환
    fileList = sorted(fileList, key=natural_sort_key)

    # STT
    for file in fileList:
        converted = transcribe_audio(file)
        print(f"{file} 변환 결과: ")
        pprint.pprint(converted)
        convert_result.append(converted)

    # 결과
    if makeTrainData is None:
        makeTrainData = input("학습 데이터를 만들까요?(Y/N): ").strip().lower() == 'y'
    if makeTrainData:
        jsonl = input("jsonl데이터로 만들까요?(Y/N): ").strip().lower() == 'y'
        excelPath = open_dialog(False)
        convert_text_data(fileList, convert_result, jsonl, excelPath)
    else:
        convert_text_data(fileList, convert_result, True)

    print("완료.")
