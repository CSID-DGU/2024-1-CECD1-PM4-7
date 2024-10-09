# API 키 임포트
import base64
import hashlib
import hmac
import json
import os
import sys
import time
from pathlib import Path

import requests

project_dir = Path(__file__).resolve().parent.parent.parent
key_folder = project_dir / 'key'


# Auth - get Keys from key.json
def getKey(title: str):
    key_path = str(key_folder / "key.json")
    with open(key_path, 'r', encoding='utf-8') as f:
        key_data = json.load(f)

    try:
        if key_data["VERSION"] != "1.1":
            raise Exception
    except Exception as e:
        print("UPDATE KEY FILE!!")
        print("EXIT.")
        sys.exit()
    return key_data[title]

# Auth - google
def googleAuth(filename="vocal-entity-420406-b9648ba69fca.json"):
    key_path = str(key_folder / filename)
    # 서비스 계정 키 파일의 경로를 환경 변수로 설정
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path


# Auth - CLOVA
class CreateTaskExecutor:
    def __init__(self, host, uri, method, iam_access_key, secret_key, request_id):
        self._host = host
        self._uri = uri
        self._method = method
        self._api_gw_time = str(int(time.time() * 1000))
        self._iam_access_key = iam_access_key
        self._secret_key = secret_key
        self._request_id = request_id

    def _make_signature(self):
        secret_key = bytes(self._secret_key, 'UTF-8')
        message = self._method + " " + self._uri + "\n" + self._api_gw_time + "\n" + self._iam_access_key
        message = bytes(message, 'UTF-8')
        signing_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
        return signing_key

    def _send_request(self, create_request):

        headers = {
            'X-NCP-APIGW-TIMESTAMP': self._api_gw_time,
            'X-NCP-IAM-ACCESS-KEY': self._iam_access_key,
            'X-NCP-APIGW-SIGNATURE-V2': self._make_signature(),
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }
        result = requests.post(self._host + self._uri, json=create_request, headers=headers).json()
        return result

    def execute(self, create_request):
        res = self._send_request(create_request)
        if 'status' in res and res['status']['code'] == '20000':
            return res['result']
        else:
            return res


