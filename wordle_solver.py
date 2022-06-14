import json
import matplotlib.pyplot as plt
from typing import TextIO
from math import log, e
from random import choice
from sys import argv
from wordfreq import zipf_frequency


class ConsoleColor:
    NONE = '\033[0m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'


class PatternConverter:
    @staticmethod
    def convert(pattern: str, replacement: dict) -> str:
        """
        Convert each characters in "pattern" into corresponding replacements.

        :param pattern: Pattern to convert.
        :param replacement: Dictionary containing each characters in "pattern" as keys, replacement character as values.
        :return: New pattern with replaced character applied.
        """
        new_pattern = ''

        for i in range(len(pattern)):
            new_pattern += replacement[pattern[i]]

        return new_pattern


class GameLogic:
    @staticmethod
    def check_answer(word_to_check: str, word_to_compare: str) -> str:
        """
        Wordle game logic.

        :param word_to_check: Word to check.
        :param word_to_compare: Word to compare.
        :return: Result pattern, in Wordle game speaking, 'green' = '2', 'yellow' = '2','gray' = '0'.
        """

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
        :param base: Logarithmic base to use, defaults value is "e" (natural logarithm).
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

        word_dictionary = {}

        word = input_file.readline()

        while word != '':
            word = word[:-1]  # Remove '\n' at the end of the line.
            word_dictionary[word] = [0] * 2
            word = input_file.readline()

        json.dump(word_dictionary, output_file, indent=4)


class Solver:
    def __init__(self, raw_allowed_guesses_path, raw_allowed_answers_path, allowed_guesses_path, allowed_answers_path):
        """
        Initialize Wordle solver.

        :param raw_allowed_guesses_path: Path to file storing raw allowed guesses.
        :param raw_allowed_answers_path: Path to file storing raw allowed answers.
        :param allowed_guesses_path: Path to file storing allowed guesses.
        :param allowed_answers_path: Path to file storing allowed answers.
        """

        self._raw_allowed_guesses_path = raw_allowed_guesses_path
        self._raw_allowed_answers_path = raw_allowed_answers_path
        self._allowed_guesses_path = allowed_guesses_path
        self._allowed_answers_path = allowed_answers_path
        self._possible_guesses: dict = {}
        self._load_allowed_guesses(fail_limit=2)
        self._last_used_word = ''
        self._used_words = []
        self._pattern_replacement = {
            '2': '🟩',
            '1': '🟨',
            '0': '⬛️',
        }

        self.opening_word: str = ''

    def _parse_allowed_guesses(self) -> None:
        """
        Parse raw allowed guesses to json.
        """

        with open(self._raw_allowed_guesses_path, 'r') as reader:
            with open(self._allowed_guesses_path, 'w') as writer:
                Converter.text_to_json(input_file=reader, output_file=writer)

    def _parse_allowed_answers(self) -> None:
        """
        Parse raw allowed guesses to json.
        """

        with open(self._raw_allowed_answers_path, 'r') as reader:
            with open(self._allowed_answers_path, 'w') as writer:
                Converter.text_to_json(input_file=reader, output_file=writer)

    def _load_allowed_guesses(self, fail_limit) -> None:
        """
        Load allowed guesses json file into "self._possible_guesses".

        :param fail_limit: How many times to try before exiting the app.
        """

        if fail_limit > 0:
            fail_limit -= 1

            # with open(self._allowed_guesses_path, 'r') as reader:
            with open(self._allowed_answers_path, 'r') as reader:
                try:
                    self._possible_guesses = dict(json.load(reader))
                except json.decoder.JSONDecodeError:
                    self.setup()
                    self._load_allowed_guesses(fail_limit)
        else:
            print('Failed to load "allowed answers" for too many times. Exiting...')
            exit()

    @staticmethod
    def _calculate_entropy(word_dict: dict) -> None:
        for word in word_dict.keys():
            word_dict[word][0] = Solver._calculate_single_word_entropy(word, list(word_dict.keys()))
            # print(f"{word}: {word_dict[word]}")

    @staticmethod
    def _calculate_single_word_entropy(word: str, words: list) -> float:
        """
        Calculate entropy for each word using word data passed into this function.

        :param word: Word to calculate entropy.
        :param words: List with words to compare.
        :return: Entropy of the selected word.
        """

        results = {}

        for d in words:
            result = GameLogic.check_answer(word, d)

            if result not in results:
                results[result] = 1
            else:
                results[result] += 1

        for key in results.keys():
            results[key] /= len(words)

        return round(Entropy.entropy_math(results, 2), 2)

    @staticmethod
    def _calculate_word_frequencies(data: dict) -> None:
        """
        Calculate word frequency for each word in data.

        :param data: Dictionary with words to check as keys, list with size of 2 as values.
        """

        for word in data.keys():
            data[word][1] = zipf_frequency(word, 'en')

    @staticmethod
    def _get_reduced_words(word: str, data: dict, matching_pattern: str) -> dict:
        """
        """

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
            }
        }
        """
        all_matched_words = {matching_pattern: [0.0, []]}

        for d in data.keys():
            if GameLogic.check_answer(word, d) == matching_pattern:
                all_matched_words[matching_pattern][0] += 1
                all_matched_words[matching_pattern][1].append(d)

        all_matched_words[matching_pattern][0] = round(log((len(data) / all_matched_words[matching_pattern][0]), 2), 2)

        return all_matched_words

    def setup(self) -> None:
        self._parse_allowed_guesses()
        self._parse_allowed_answers()

        self.recalculate_opening_data()

    def recalculate_opening_data(self) -> None:
        with open(self._allowed_answers_path, 'r') as reader:
            allowed_guesses = dict(json.load(reader))

            with open(self._allowed_answers_path, 'w') as writer:
                self._calculate_entropy(allowed_guesses)  # Calculate opening entropy.
                self._calculate_word_frequencies(allowed_guesses)
                allowed_guesses = dict(sorted(allowed_guesses.items(), key=lambda d: d[1], reverse=True))

                json.dump(allowed_guesses, writer, indent=4)

    def reload(self):
        self._load_allowed_guesses(fail_limit=2)
        self._last_used_word = ''
        self._used_words = []

    def evaluate(self, pattern: str) -> None:
        result = self._get_reduced_words(self._last_used_word, self._possible_guesses, pattern)
        print(PatternConverter.convert(pattern, self._pattern_replacement), end='\t')
        print(f'Expected entropy for '
              f'"{self._last_used_word}": {self._possible_guesses[self._last_used_word][0]}, '
              f'actual: {result[pattern][0]}')

        new_possible_guesses = {}
        for key in self._possible_guesses.keys():
            if key in result[pattern][1]:
                new_possible_guesses[key] = [0, 0]

        self._possible_guesses = new_possible_guesses
        del new_possible_guesses

        self._calculate_entropy(self._possible_guesses)
        self._calculate_word_frequencies(self._possible_guesses)
        self._possible_guesses = dict(sorted(self._possible_guesses.items(), key=lambda d: d[1][0], reverse=True))

    def get_next_word(self) -> str:
        if self.opening_word == '':
            self._last_used_word = next(iter(self._possible_guesses))
        else:
            self._last_used_word = (self.opening_word + '.')[:-1]
            self.opening_word = ''

        self._used_words.append(self._last_used_word)

        return self._last_used_word


class WordleGame:
    def __init__(self, answer_list: list, allowed_words_list: list, game_logic, round_limit: int = 6,
                 input_injector=None, output_receiver=None, designated_answer: str = None,
                 output_game_result_to_receiver_enabled: bool = True, result_pattern_pretty_print: bool = True):
        """
        Wordle game initializer.

        :param answer_list: List of correct answers for the game to pick random answer from.
        :param allowed_words_list: List of allowed guesses.
        :param game_logic: Game logic for Wordle game to check the guesses. Signature: func(guess: str, answer: str)
        :param round_limit: Number of rounds before the game quits itself.
        :param input_injector: (optional) Custom function to pass in a new input. Signature: func() -> str.
        :param output_receiver: (optional) Custom function to receive each round's result. Signature: func(str).
        :param designated_answer: (optional) Designated answer instead of a randomly generated one.
        :param output_game_result_to_receiver_enabled: (optional) Flag to enable outputting results to console.
        :param result_pattern_pretty_print: (optional) Whether to return result in number pattern format or not.
        """

        self._answer_list = answer_list
        self._allowed_words_list = allowed_words_list
        self._game_logic = game_logic
        self._round_limit = round_limit
        self._input = input if (input_injector is None) else input_injector
        self._output = print if (output_receiver is None) else output_receiver
        self._answer = self._pick_answer() if (designated_answer is None) else designated_answer
        self._is_output_game_result_to_receiver_enabled = output_game_result_to_receiver_enabled
        self._result_pattern_pretty_print = result_pattern_pretty_print
        self._word_length = len(self._answer)
        self._guessed_answers = []
        self._pattern_replacement = {
            '2': '🟩',
            '1': '🟨',
            '0': '⬛️',
        }

    def _pick_answer(self) -> str:
        """
        Pick a random word from self._answer_list as answer.

        :return: Answer word for this current round of game.
        """

        return choice(self._answer_list)

    def _validate_input(self, input_content: str) -> bool:
        """
        Validation for the input word. Check if the word matched all the requirements.

        :param input_content: The input text.
        :return: True when input_content is valid.
        """

        is_valid = True

        if len(input_content) != self._word_length:
            is_valid = False
            print(f'Incorrect word length. Expected {self._word_length} but got {len(input_content)}.')

        if input_content in self._guessed_answers:
            is_valid = False
            print(f'You\'ve used the word "{input_content}", use a different word instead.')

        if input_content not in self._allowed_words_list:
            is_valid = False
            print(f'The word "{input_content}" does not exist or not permitted, use a different word instead.')

        return is_valid

    def play(self) -> int:
        """
        Play the Wordle game for self._round_limit rounds, if player guessed the correct answer the game will quit.

        :return: Number of times used to guess the correct answer.
        """

        for i in range(1, self._round_limit + 1):
            guess = self._input()

            # Re get input if the input is invalid.
            while not self._validate_input(guess):
                guess = self._input()

            self._guessed_answers.append(guess)

            result = self._game_logic(guess, self._answer)

            if self._result_pattern_pretty_print:
                self._output(PatternConverter.convert(result, self._pattern_replacement))
            else:
                self._output(result)

            if result == '2' * self._word_length:
                if self._is_output_game_result_to_receiver_enabled:
                    self._output(f'You won. Congrats 🥳')

                return i

        if self._is_output_game_result_to_receiver_enabled:
            self._output(f'You lost. The answer was: {self._answer}')

        return -1

    def restart(self, designated_answer: str = None) -> int:
        """
        Start a new Wordle game for self._round_limit rounds, if player guessed the correct answer the game will quit.

        :param designated_answer: (optional) Provide a designated answer instead of a randomly generated one.
        :return: Number of times used to guess the correct answer.
        """

        self._answer = self._pick_answer() if (designated_answer is None) else designated_answer
        self._word_length = len(self._answer)
        self._guessed_answers = []
        print(f'Answer: {self._answer}')

        return self.play()


class Simulator:
    def __init__(self, allowed_answers: list, solver: Solver, wordle_game: WordleGame):
        self._allowed_answers = allowed_answers
        self._solver = solver
        self._wordle_game = wordle_game
        # self._game_record = {i: [0, []] for i in range(-1, 7) if i}
        self._game_record = {i: 0 for i in range(-1, 7) if i}

    def simulate(self):
        while len(self._allowed_answers) > 0:
            answer = self._allowed_answers.pop()
            result = self._wordle_game.restart(answer)
            self._game_record[result] += 1
            # self._game_record[result][0] += 1
            # self._game_record[result][1].append(answer)
            self._solver.reload()

        self._game_record['Average'] = \
            sum([key * self._game_record[key] for key in list(self._game_record.keys())[1:]]) / \
            sum(list(self._game_record.values())[1:])

    def dump_result(self, output_path: str = './simulation.json'):
        with open(output_path, 'w') as file:
            json.dump(self._game_record, file)

        print('Simulation result dumped.')

    def load_result(self, output_path: str = './simulation.json'):
        with open(output_path, 'r') as file:
            self._game_record = json.load(file)

        print('Simulation result loaded.')

    def draw_chart(self):
        # x = self._game_record.keys()
        y = [i[0] for i in self._game_record.values()]

        fig, ax = plt.subplots()
        width = 0.8
        ind = [i for i in range(len(y))]

        ax.barh(ind, y, width)

        for i, v in enumerate(y):
            ax.text(v + 3, i - 0.1, str(v), color='blue', fontweight='bold')

        plt.show()


def main():
    solver = Solver(raw_allowed_guesses_path='./data/_allowed_guesses.txt',
                    raw_allowed_answers_path='./data/_allowed_answers.txt',
                    allowed_guesses_path='./data/allowed_guesses.json',
                    allowed_answers_path='./data/allowed_answers.json')

    if len(argv) > 1:
        if argv[1] == 'setup':
            solver.setup()

        elif argv[1] == 'refresh':
            solver.recalculate_opening_data()

        elif argv[1] == 'sim':
            with open('./data/allowed_answers.json', 'r') as allowed_answers_file:
                allowed_answers = dict(json.load(allowed_answers_file))

                with open('./data/allowed_guesses.json', 'r') as allowed_guesses_file:
                    allowed_guesses = dict(json.load(allowed_guesses_file))

                    wordle_game = WordleGame(list(allowed_answers.keys()), list(allowed_guesses.keys()),
                                             GameLogic.check_answer, input_injector=solver.get_next_word,
                                             output_receiver=solver.evaluate,
                                             output_game_result_to_receiver_enabled=False,
                                             result_pattern_pretty_print=False)

                    simulator = Simulator(list(allowed_answers.keys()), solver, wordle_game)
                    simulator.simulate()
                    simulator.dump_result()

                    # Simulate and evaluate list of different openers.
                    # words_to_sim = ['along', 'atone', 'audio', 'blind', 'canoe', 'carte', 'crane', 'cough', 'media',
                    #                 'lance', 'least', 'notes', 'roast', 'radio', 'resin', 'slice', 'slate', 'slant',
                    #                 'steam', 'stone', 'trace', 'tried']
                    #
                    # while words_to_sim:
                    #     word_to_sim = words_to_sim.pop()
                    #
                    #     solver.opening_word = word_to_sim
                    #     simulator = Simulator(list(allowed_answers.keys()), solver, wordle_game)
                    #     simulator.simulate()
                    #     simulator.dump_result(f'./simulations/{word_to_sim}.json')

        elif argv[1] == 'assist':
            for i in range(6):
                print(solver.get_next_word())
                solver.evaluate(input())
    else:
        with open('./data/allowed_answers.json', 'r') as allowed_answers_file:
            allowed_answers = dict(json.load(allowed_answers_file))

            with open('./data/allowed_guesses.json', 'r') as allowed_guesses_file:
                allowed_guesses = dict(json.load(allowed_guesses_file))

                wordle_game = WordleGame(list(allowed_answers.keys()), list(allowed_guesses.keys()),
                                         GameLogic.check_answer)

                wordle_game.play()


if __name__ == '__main__':
    main()
