import json
from typing import TextIO
from math import log, e
from sys import argv
from wordfreq import zipf_frequency


class Logic:
    @staticmethod
    def game_logic(word_to_check: str, word_to_compare: str):
        length = len(word_to_check)
        used_chars = {i: {'character': '', 'result': ''} for i in range(length)}
        allowed_char_usage = {}
        result = ''

        for char in word_to_compare:
            if char not in allowed_char_usage.keys():
                allowed_char_usage[char] = 1
            else:
                allowed_char_usage[char] += 1

        for index in range(length):
            char = word_to_check[index]
            used_chars[index]['character'] = char

            # If character is in the word and in the right position.
            if char == word_to_compare[index]:
                allowed_char_usage[char] -= 1
                used_chars[index]['result'] = '2'

            # If character is in the word but in the wrong position.
            elif char in word_to_compare:
                allowed_char_usage[char] -= 1
                used_chars[index]['result'] = '1'

            # If character it's not in the word.
            else:
                used_chars[index]['result'] = '0'

        # For each character, check if it has been used more than permitted times.
        for char in allowed_char_usage.keys():
            index = length - 1
            while allowed_char_usage[char] < 0 and index > -1:
                if used_chars[index]['character'] == char and used_chars[index]['result'] != '2':
                    used_chars[index]['result'] = '0'
                    allowed_char_usage[char] += 1

                index -= 1

        for index in range(length):
            result += used_chars[index]['result']

        return result


class Entropy:
    @staticmethod
    def entropy_math(data: dict, base: float = e) -> float:
        """
        Calculate the entropy of the given data.

        :param data: Dictionary with each result possibility as key and probability of occurrence as value.
        :param base: Logarithmic base to use, defaults value is e (natural logarithm).
        :return: Calculated entropy.
        """

        result = 0

        for value in data.values():
            result += value * log(value, base)

        return result * -1


class Converter:
    @staticmethod
    def text_to_json(input_file: TextIO, output_file: TextIO) -> None:
        """
        Convert allowed guesses in plain text into a JSON file.
        """

        word_dictionary = {
            'Words': []
        }

        word = input_file.readline()

        while word != '':
            word = word[:-1]  # Remove '\n' at the end of the line.

            new_word = {
                'Word': word,
                'Entropy': None
            }

            word_dictionary['Words'].append(new_word)

            word = input_file.readline()

        json.dump(word_dictionary, output_file, indent=4)


class Solver:
    def __init__(self, raw_allowed_guesses_path, raw_allowed_answers_path, allowed_guesses_path, allowed_answers_path):
        self.raw_allowed_guesses_path = raw_allowed_guesses_path
        self.raw_allowed_answers_path = raw_allowed_answers_path
        self.allowed_guesses_path = allowed_guesses_path
        self.allowed_answers_path = allowed_answers_path

    def _parse_allowed_guesses(self) -> None:
        """
        Parse raw allowed guesses to json.
        """

        with open(self.raw_allowed_guesses_path, 'r') as reader:
            with open(self.allowed_guesses_path, 'w') as writer:
                Converter.text_to_json(input_file=reader, output_file=writer)

    def _parse_allowed_answers(self) -> None:
        """
        Parse raw allowed guesses to json.
        """

        with open(self.raw_allowed_answers_path, 'r') as reader:
            with open(self.allowed_answers_path, 'w') as writer:
                Converter.text_to_json(input_file=reader, output_file=writer)

    @staticmethod
    def calculate_entropy(words_list: list) -> None:
        for word in words_list:
            word['Entropy'] = Solver.calculate_single_word_entropy(word, words_list)
            print(f"{word['Word']}: {word['Entropy']}")

    @staticmethod
    def calculate_single_word_entropy(word: dict, data: list) -> float:
        """
        Calculate entropy for each word using word data passed into this function.

        :param word:
        :param data:
        :return:
        """

        """
        Store result pattern as key and each pattern's probability. 
        
        i.e.
        {
            '<pattern>': <probability of pattern>,
            '<pattern>': <probability of pattern>,
            ...
        }
        """
        results = {}

        """
        Store result pattern as key and sub dictionary as value.
        Sub dictionary: each matching pattern as key and each pattern's matching words in a list as value.
        
        i.e.
        {
            '<pattern>': {
                {
                    'Entropy': <entropy of this pattern>,
                    'Words': [<list of matching words>]
                }        
            },
            '<pattern>': {
                {
                    'Entropy': <entropy of this pattern>,
                    'Words': [<list of matching words>]
                }        
            },
            ...
        }
        """
        all_matched_words = {}

        for d in data:
            result = Logic.game_logic(word['Word'], d['Word'])

            if result not in results:
                results[result] = 1
                all_matched_words[result] = [float(1), []]
            else:
                results[result] += 1
                all_matched_words[result][0] += 1

            all_matched_words[result][1].append(d['Word'])

        for key in results.keys():
            all_matched_words[key][0] = round(log((len(data) / all_matched_words[key][0]), 2), 2)
            results[key] /= len(data)

        # word['Results'] = dict(sorted(all_matched_words.items(), key=lambda x: x[1][0], reverse=True))
        # word['Results'] = dict(sorted(all_matched_words.items(), key=lambda x: x[1][0], reverse=True))

        return round(Entropy.entropy_math(results, 2), 2)

    def setup(self) -> None:
        self._parse_allowed_guesses()
        self._parse_allowed_answers()

        with open(self.allowed_answers_path, 'r') as reader:
            allowed_guesses = dict(json.load(reader))

            with open(self.allowed_answers_path, 'w') as writer:
                Solver.calculate_entropy(allowed_guesses['Words'])  # Calculate opening entropy.

                # Calculate word frequency for each word.
                for word in allowed_guesses['Words']:
                    word['Frequency'] = zipf_frequency(word['Word'], 'en')

                # allowed_guesses['Words'] = sorted(allowed_guesses['Words'], key=lambda d: d['Entropy'], reverse=True)

                json.dump(allowed_guesses, writer, indent=4)

    def play(self) -> None:
        with open(self.raw_allowed_answers_path, 'r') as reader:
            word = reader.readline()

            while word is not None:
                word = reader.readline()


if __name__ == '__main__':
    solver = Solver(raw_allowed_guesses_path='./data/_allowed_guesses.txt',
                    raw_allowed_answers_path='./data/_allowed_answers.txt',
                    allowed_guesses_path='./data/allowed_guesses.json',
                    allowed_answers_path='./data/allowed_answers.json')

    if len(argv) > 1:
        if argv[1] == 'init_setup':
            solver.setup()
    else:
        solver.play()
