# STT main
import auth
import STT

# Auth
auth.googleSTTAuth()

# 변환
'''
    askFolder = True: 폴더를 선택하여 하위 모든 항목을 처리
            = False: 파일을 선택하여 처리
    sliceWord = True: 변환된 텍스트를 단어들로 분리
            = False: 분리하지 않음
    
'''
STT.STT_pipeline(
    askFolder=True,
    sliceWord=False
)