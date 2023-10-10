from typing import List


def frequent_letter(word_list: List[str]) -> str:
    letters = []
    if len(word_list) == 1:
        letters += list(word_list[0])
    else:
        for word in word_list:
            letters += list(set(word))
    return max(letters, key=lambda x: letters.count(x))
