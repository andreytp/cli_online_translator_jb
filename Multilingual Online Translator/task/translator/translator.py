import requests
from bs4 import BeautifulSoup as bs
import sys
from typing import TextIO


class NotSuccessRequest(Exception):
    pass


class NotEnoughParameters(Exception):
    pass


def lang_by_num(num: int) -> str:
    return ['Arabic',
            'German',
            'English',
            'Spanish',
            'French',
            'Hebrew',
            'Japanese',
            'Dutch',
            'Polish',
            'Portuguese',
            'Romanian',
            'Russian',
            'Turkish',
            ][num - 1]


def num_by_lang(lang: str) -> int:
    return ['All',
            'Arabic',
            'German',
            'English',
            'Spanish',
            'French',
            'Hebrew',
            'Japanese',
            'Dutch',
            'Polish',
            'Portuguese',
            'Romanian',
            'Russian',
            'Turkish',
            ].index(lang.lower().capitalize())


def get_translate_direction(from_lang: int, to_lang: int) -> str:
    return lang_by_num(from_lang) + '-' + lang_by_num(to_lang)


def find_by_selector(selector: str, soup: bs) -> list:
    founded_example = (item for item in soup.select(selector))
    founded_texts = (word.text.replace('\n', '').strip() for word in founded_example)
    return [item for item in founded_texts]


def get_translate_parameters_interact() -> (int, int, str):
    greeting_text = '''
                    Hello, you're welcome to the translator. Translator supports:
                    0. All 
                    1. Arabic
                    2. German
                    3. English
                    4. Spanish
                    5. French
                    6. Hebrew
                    7. Japanese
                    8. Dutch
                    9. Polish
                    10. Portuguese
                    11. Romanian
                    12. Russian
                    13. Turkish
                    Type the number of your language:
                    '''
    print(greeting_text)
    from_language = int(input())
    print('Type the number of a language you want to translate to or "0" to translate to all languages:')
    to_language = int(input())
    print('Type the word you want to translate:')
    word = input()
    return from_language, to_language, word


def get_translate_range(lang_num: int) -> range:
    if lang_num == 0:
        return range(1, 14)

    return range(lang_num, lang_num + 1)


def get_translate_count(lang_num: int) -> int:
    if lang_num == 0:
        return 1
    return 5


def print_word_examples(f: TextIO, soup: bs, target_lang: str, translate_count: int) -> None:
    print(file=f)
    print(f'{target_lang} Examples:', file=f)
    examples = find_by_selector(' #examples-content .ltr,.rtl .text', soup)[:translate_count * 2]
    for i in range(translate_count):
        print(examples[i * 2], ':', file=f)
        print(examples[i * 2 + 1], file=f)
        print(file=f)


def print_word_translate(f: TextIO, soup: bs, target_lang: str, translate_count: int) -> None:
    print(file=f)
    print(f'{target_lang} Translations:', file=f)
    for item in find_by_selector(' .translation', soup)[1:translate_count + 1]:
        print(item, file=f)


def translate_word(from_language: int, to_language: int, word: str, translate_range: range) -> None:
    with open(word + '.txt', 'w') as f:
        for to_lang in translate_range:

            if to_lang == from_language:
                continue

            lang_direct = get_translate_direction(from_language, to_lang)

            link = f'https://context.reverso.net/translation/{lang_direct.lower()}/{word.lower()}'
            response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})

            if response.status_code != 200:
                raise NotSuccessRequest

            soup = bs(response.content, 'html.parser')

            target_lang = lang_by_num(to_lang)
            translate_count = get_translate_count(to_language)

            print_word_translate(f, soup, target_lang, translate_count)
            print_word_examples(f, soup, target_lang, translate_count)

    with open(word + '.txt', 'r') as f:
        print(f.read())


if __name__ == '__main__':
    argv = sys.argv

    if len(argv) > 3:
        from_language = num_by_lang(argv[1])
        to_language = num_by_lang(argv[2])
        word = ' '.join(argv[3:])
    else:
        if len(argv) == 1:
            from_language, to_language, word = get_translate_parameters_interact()
        else:
            raise NotEnoughParameters

translate_range = get_translate_range(to_language)
translate_word(from_language, to_language, word, translate_range)
