import requests
from bs4 import BeautifulSoup as bs


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


def get_translate_direction(from_lang, to_lang) -> str:
    return lang_by_num(from_lang) + '-' + lang_by_num(to_lang)


def find_by_selector(selector):
    founded_example = (item for item in soup.select(selector))
    founded_texts = (word.text.replace('\n', '').strip() for word in founded_example)
    return [item for item in founded_texts]


class NotSuccessRequest(Exception):
    pass


greeting_text = '''
Hello, you're welcome to the translator. Translator supports: 
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

translate_range = range(to_language, to_language + 1)
if to_language == 0:
    translate_range = range(1, 14)
with open(word + '.txt', 'w') as f:
    for to_lang in translate_range:

        if to_lang == from_language:
            continue

        lang_direct = get_translate_direction(from_language, to_lang)

        link = f'https://context.reverso.net/translation/{lang_direct.lower()}/{word.lower()}'
        responce = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})

        if responce.status_code != 200:
            raise NotSuccessRequest
        # else:
        # print(responce.status_code, 'OK')

        soup = bs(responce.content, 'html.parser')

        # print('Context examples:')

        target_lang = lang_by_num(to_lang)

        print(file=f)
        print(f'{target_lang} Translations:', file=f)
        for item in find_by_selector(' .translation')[1:2]:
            print(item, file=f)

        print(file=f)
        print(f'{target_lang} Examples:', file=f)
        examples = find_by_selector(' #examples-content .ltr,.rtl .text')[:2]
        for i in range(1):
            print(examples[i * 2], ':', file=f)
            print(examples[i * 2 + 1], file=f)
            print(file=f)

with open(word + '.txt', 'r') as f:
    print(f.read())
