# STT main
import os
import sys

# directory for pyinstaller
if getattr(sys, 'frozen', False):
    program_directory = os.path.dirname(os.path.abspath(sys.executable))
else:
    program_directory = os.path.dirname(os.path.abspath(__file__))

authPath = os.path.abspath(os.path.join(program_directory, '..'))
sys.path.append(authPath)
import STT

import auth

# Auth
auth.googleSTTAuth()

# 변환
'''
    askFolder = True: 폴더를 선택하여 하위 모든 항목을 처리
            = False: 파일을 선택하여 처리
    sliceWord = True: 변환된 텍스트를 단어들로 분리
            = False: 분리하지 않음
    makeTrainData = True: 변환 결과를 학습 데이터로도 생성
            = False: 학습 데이터를 생성하지 않음
'''
STT.STT_pipeline(
    askFolder=False,
    sliceWord=False,
    makeTrainData=True
)
