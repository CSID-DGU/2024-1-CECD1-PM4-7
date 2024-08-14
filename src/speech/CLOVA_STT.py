import sys
import json
from pathlib import Path
import requests
from common.auth_ import getKey

def stt_clova(file: Path):
    client_id = getKey("CLOVA-STT-CLIENT")
    client_secret = getKey("CLOVA-STT-SECRET")
    url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor"

    # 요청 헤더
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }

    data = open(file, 'rb')
    response = requests.post(url, headers=headers, data=data)

    # 응답 처리
    if response.status_code == 200:
        result = response.json()
        if "text" in result:
            text_result = result["text"]
            return text_result
    else:
        print("Error:", response.status_code)
        print(response.text)
        sys.exit()
