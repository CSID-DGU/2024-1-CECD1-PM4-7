# 문장 분리 및 결합
import re
from jamo import h2j, j2hcj

# 문장을 문자단위로 분리함
def sep_sentence(sentence: str) -> list:
    result = []
    for char in sentence:
        if re.match('[가-힣]', char):
            jamo_char = j2hcj(h2j(char))
            result.extend(list(jamo_char))
        else:
            result.append(char)

    return result

# 분리한 문장을 다시 합침
def rev_sentence(jamo_list):
    result = []
    jamo_buffer = []

    def join_jamos(jamo_chars):
        # 초성, 중성, 종성 유니코드 값
        CHO = 0x1100
        JUNG = 0x1161
        JONG = 0x11A7

        if len(jamo_chars) == 2:
            return chr(((ord(jamo_chars[0]) - CHO) * 588) + ((ord(jamo_chars[1]) - JUNG) * 28) + 44032)
        elif len(jamo_chars) == 3:
            return chr(((ord(jamo_chars[0]) - CHO) * 588) + ((ord(jamo_chars[1]) - JUNG) * 28) + (
                        ord(jamo_chars[2]) - JONG) + 44032)
        else:
            raise ValueError("Invalid Jamo characters")

    for char in jamo_list:
        if re.match('[ㅏ-ㅣㄱ-ㅎ]', char):
            jamo_buffer.append(char)
        else:
            if jamo_buffer:
                result.append(join_jamos(jamo_buffer))
                jamo_buffer = []
            result.append(char)

    if jamo_buffer:
        result.append(join_jamos(jamo_buffer))

    return ''.join(result)

# 문자가 한글인지 확인
def is_hangul(char):
    return '가' <= char <= '힣'

# debug
if __name__ == '__main__':
    sentence = "안녕하세요, 반값습니다."
    print(sep_sentence(sentence))
    print(rev_sentence(sentence))
