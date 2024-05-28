import io
import os
import pprint
import tkinter as tk
import wave
from tkinter import filedialog

import convert
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage


# STT
def transcribe_audio(file_path):
    client = speech.SpeechClient()

    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
    )

    with wave.open(file_path, 'rb') as wav_file:
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
    
    bucket_name = 'stt_test_by_pm4'
    destination_blob_name = os.path.basename(file_path)
    gcs_uri = upload_to_gcs(bucket_name, file_path, destination_blob_name)

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

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    return f"gs://{bucket_name}/{destination_blob_name}"

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path

def open_folder_dialog():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    return folder_path


def STT_pipeline(askFolder=True, sliceWord=True):
    convert_result = []
    if(askFolder):
        path = open_folder_dialog()
    else:
        path = open_file_dialog()
    
    # wav로 변환
    fileList = convert.convert_audio_files(path, askFolder)

    # STT
    for file in fileList:
        converted = transcribe_audio(file)
        print(f"{file}변환 결과: ")
        pprint.pprint(converted)
        convert_result.append(converted)
    
    # 결과
    convert.convert_text_data(fileList, convert_result, sliceWord)