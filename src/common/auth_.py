# API 키 임포트
import os
import json
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent.parent
key_folder = project_dir / 'key'


# openAI Auth
def openAIAuth():
    with open('key/STT.json', 'r', encoding='utf-8') as f:
        key_data = json.load(f)

    return key_data["STT"]

# prompt
def getPrompt(name: str):
    promptPath = str(key_folder / 'prompt.json')
    with open(promptPath, 'r', encoding='utf-8') as f:
        prompt_data = json.load(f)
    prompt = prompt_data[name]
    return prompt

# google Auth
def googleSTTAuth():
    key_path = str(key_folder / "vocal-entity-420406-b9648ba69fca.json")
    # 서비스 계정 키 파일의 경로를 환경 변수로 설정
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    
def googleTTSAuth():
    pass