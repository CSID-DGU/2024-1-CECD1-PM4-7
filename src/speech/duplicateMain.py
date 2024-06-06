# 같은 문장을 여러 번 녹음하는 경우 사용
import os
import sys
program_directory = os.path.dirname(os.path.abspath(__file__))
authPath = os.path.abspath(os.path.join(program_directory, '..'))
sys.path.append(authPath)
import STT
import convert
import auth_
import pprint
import pandas as pd
from tuning.convert import complete_xlsx_to_jsonl

# Auth
auth_.googleSTTAuth()

# 변환
System_content = []
User_content = []
Assistant_content = []
path = STT.open_folder_dialog()

# 프롬프트
prompt = auth_.getPrompt("stt_correction")

# wav로 변환
fileList = convert.convert_audio_files(path, True)
if len(fileList) == 0:
    print("변환된 파일 없음!!")
    sys.exit()

# STT
for file in fileList:
    converted = STT.transcribe_audio(file)
    print(f"{file}변환 결과: ")
    pprint.pprint(converted)
    User_content += converted
    ac = input("위 파일의 원문: ").strip()
    for i in range(len(converted)):
        Assistant_content.append(ac)
        System_content.append(prompt)

dir_path = os.path.dirname(fileList[0])
excelPath = os.path.join(dir_path, 'train_STT.xlsx')

df = pd.DataFrame({'System content': System_content, 'User content': User_content, 'Assistant content': Assistant_content})
df.to_excel(excelPath, index=False, encoding='utf-8')

complete_xlsx_to_jsonl(excelPath)
