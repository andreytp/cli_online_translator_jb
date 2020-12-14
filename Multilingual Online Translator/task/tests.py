from hstest.stage_test import StageTest
from hstest.test_case import TestCase
from hstest.check_result import CheckResult
import requests
from itertools import chain
from bs4 import BeautifulSoup
import sys
import os


if sys.platform.startswith("win"):
    import _locale

    # pylint: disable=protected-access
    _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

CheckResult.correct = lambda: CheckResult(True, '')
CheckResult.wrong = lambda feedback: CheckResult(False, feedback)


languages = ["arabic", "german", "english", "spanish", "french",
             "hebrew", "japanese", "dutch", "polish", "portuguese",
             "romanian", "russian", "turkish"]


class TranslatorTest(StageTest):
    def generate(self):
        return [
            TestCase(args=['english', 'all', 'love'], attach='english\nall\nlove'),
            TestCase(args=['spanish', 'english', 'derechos'], attach='spanish\nenglish\nderechos')
        ]

    def check_output(self, output, true_results):
        output = output.lower()

        for language in true_results:
            translations_title = '{} translation'.format(language).lower()
            if translations_title not in output:
                return False, 'The title \"{0} translation\" was not found.'.format(language)
            examples_title = "{0} example".format(language).lower()
            translations = output[output.index(translations_title):].strip()

            if examples_title not in translations.lower():
                return False, 'The title \"{0}\" was not found.\n' \
                              'Make sure you output this title before example sentences for this language,\n' \
                              'and that you output it after translations for it.'.format(examples_title)

            # the beginning of the section with context examples
            examples_index = translations.index(examples_title)
            try:
                # the end of the section with context examples
                examples_end = translations.index('translation', examples_index)
            except ValueError:
                # if the language is last in the list, the end of the context examples is the end of the output
                examples_end = None
            examples = translations[examples_index:examples_end].split('\n')
            translations = translations[:examples_index].strip().split('\n')
            examples = [line for line in examples if line and examples_title not in line]
            translations = [line for line in translations if line and translations_title not in line]

            if len(translations) == 0:
                return False, "No translations for {0} are found.\n" \
                              "Make sure that each translated word is placed in a new line\n" \
                              "and that translations precede examples.".format(language)

            if len(examples) == 0:
                return False, "No context examples for {0} are found.\n" \
                              "Make sure that your context examples follow the translations\n" \
                              "and that each example is placed in a new line.".format(language)

            true_translations, true_examples = true_results[language]

            translations_intersection = [True for user_translation in translations
                                         if user_translation in true_translations]
            if not translations_intersection:
                return False, "No correct translations for {0} are found.\n" \
                              "Please, output the first found translation " \
                              "of the given word for this language if you output one translation.".format(language)

            examples_intersection = [True for user_example in examples if user_example in true_examples]
            if not examples_intersection:
                return False, "No correct examples for {0} are found.\n" \
                              "If you output only one example for each language,\n" \
                              "please, use the first example that you find on the web page.".format(language)

        return True, ''

    def check(self, reply, attach):
        l1, l2, word = attach.split("\n")
        result_dict = get_results(l1, l2, word)

        file_name = word + '.txt'
        if not os.path.exists(file_name):
            return CheckResult.wrong("Looks like you didn't create a file named <word>.txt \n"
                                     "where <word> is the word that should be translated.")

        with open(file_name, 'r', encoding='utf-8') as fh:
            try:
                output = fh.read()
            except UnicodeDecodeError:
                return CheckResult.wrong("UnicodeDecodeError occurred while reading your file. \n"
                                         "Perhaps you used the wrong encoding? Please, use utf-8 encoding.")

        if output.lower() not in reply.lower():
            return CheckResult.wrong("The output to the terminal does not seem to contain the content of the file.\n"
                                     "Please make sure that you output the results to the terminal as well.")

        is_correct, feedback = self.check_output(output, result_dict)
        if not is_correct:
            feedback = 'A problem occurred while reading the file that you created.\n' + feedback
            return CheckResult.wrong(feedback)

        try:
            os.remove(file_name)
        except:
            return CheckResult.wrong("An error occurred while your file was being removed.\n"
                                     "Please make sure that you close all the files after writing the results in them.")

        return CheckResult.correct()


def get_results(l1, l2, word):
    if l2 == 'all':
        target_languages = [language for language in languages if language != l1]
    else:
        target_languages = [l2]

    result_dict = {}

    for lang_to in target_languages:
        url = f"https://context.reverso.net/translation/{l1}-{lang_to}/{word}"
        user_agent = 'Mozilla/5.0'
        response = requests.get(url, headers={'User-Agent': user_agent})

        raw_contents = BeautifulSoup(response.content, 'html.parser')
        translations = raw_contents.find_all('a', {"class": 'translation'})
        sentences_src, sentences_target = \
            raw_contents.find_all('div', {"class": "src ltr"}), \
            raw_contents.find_all('div', {"class": ["trg ltr", "trg rtl arabic", "trg rtl"]})

        translation_list = [translation.get_text().strip().lower() for translation in translations]
        sentence_list = [sentence.get_text().strip().lower() for sentence in
                         list(chain(*[sentence_pair for sentence_pair in zip(sentences_src, sentences_target)]))]
        result_dict[lang_to] = [set(translation_list), set(sentence_list)]

    return result_dict


if __name__ == '__main__':
    TranslatorTest('translator.translator').run_tests()
