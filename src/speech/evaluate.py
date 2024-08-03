from common import info
import pandas as pd

# 완성된 xlsx파일에서 정답 데이터를 제거
def remove_correct():
    filePath = info.open_dialog(False)
    df = pd.read_excel(filePath)
    user_content = df["User content"]
    stt_result = df["STT Result"]

    current_uc = ''
    before_stt = []
    df2 = pd.DataFrame(columns=["User content", "STT Result"])
    for i in range(len(user_content)):
        if user_content[i][-1] == '.':
            user_content[i] = user_content[i][:-1]

        if user_content[i].replace(" ", "") == current_uc.replace(" ", ""):
            if (user_content[i].replace(" ", "") != stt_result[i].replace(" ", "")
                    and stt_result[i].replace(" ", "") not in before_stt):
                new_row = pd.DataFrame({"User content": [user_content[i]], "STT Result": [stt_result[i]]})
                df2 = pd.concat([df2, new_row], ignore_index=True)
                before_stt.append(stt_result[i])
        else:
            current_uc = user_content[i]
            if stt_result[i].replace(" ", "") == current_uc.replace(" ", ""):
                before_stt = []
            else:
                before_stt = [stt_result[i]]
                new_row = pd.DataFrame({"User content": [user_content[i]], "STT Result": [stt_result[i]]})
                df2 = pd.concat([df2, new_row], ignore_index=True)

    df2.to_excel(filePath, index=False)


if __name__ == '__main__':
    remove_correct()
