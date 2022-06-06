from unittest import TestCase

from wordle_solver import GameLogic


class TestGameLogic(TestCase):
    def test_check_answer(self):
        self.assertEqual('20202', GameLogic.check_answer('seize', 'slide'))
        self.assertEqual('20110', GameLogic.check_answer('shoot', 'socko'))
        self.assertEqual('12200', GameLogic.check_answer('dodge', 'soddy'))
        self.assertEqual('02201', GameLogic.check_answer('hodad', 'soddy'))
        self.assertEqual('01101', GameLogic.check_answer('beret', 'trend'))
