import re


def decompositeHangul(hangulLetter):
    cho_list = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    jung_list = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
    jong_list = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'

    hangulCode = ord(hangulLetter)
    cho_index = (hangulCode - 0xAC00) // 21 // 28
    jung_index = (hangulCode - 0xAC00 - (cho_index * 21 * 28)) // 28
    jong_index = hangulCode - 0xAC00 - (cho_index * 21 * 28) - (jung_index * 28)

    return (cho_list[cho_index], jung_list[jung_index], jong_list[jong_index])


def checkDueum(last_lastWord, first_yourWord):
    pat = re.compile('^[ㄱ-ㅎ가-힣]+$')
    if not pat.match(last_lastWord) and not pat.match(first_yourWord):
        return False

    lastWordDecompose = decompositeHangul(last_lastWord)
    yourWordDecompose = decompositeHangul(first_yourWord)

    if lastWordDecompose[0] in 'ㄴㄹ':
        if (lastWordDecompose[1] in 'ㅏㅐㅗㅚㅜㅡ') and lastWordDecompose[0] == 'ㄹ':
            if (yourWordDecompose[1:] == lastWordDecompose[1:]) and yourWordDecompose[0] == 'ㄴ':
                return True
            else:
                return False
        elif lastWordDecompose[1] in 'ㅑㅕㅛㅠㅣ':
            if (yourWordDecompose[1:] == lastWordDecompose[1:]) and yourWordDecompose[0] == 'ㅇ':
                return True
            else:
                return False
    else:
        return False

