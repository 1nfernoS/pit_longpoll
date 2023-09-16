from typing import List


def frequent_letter(word_list: List[str]) -> str:
    letters = []
    for word in word_list:
        letters += list(set(word))
    return max(letters, key=lambda x: letters.count(x))
