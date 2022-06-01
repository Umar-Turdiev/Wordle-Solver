from unittest import TestCase

from main import Logic


class TestGameLogic(TestCase):
    def test_game_logic(self):
        self.assertEqual('20202', Logic.game_logic('seize', 'slide'))
        self.assertEqual('20110', Logic.game_logic('shoot', 'socko'))
        self.assertEqual('12200', Logic.game_logic('dodge', 'soddy'))
        self.assertEqual('02201', Logic.game_logic('hodad', 'soddy'))
        self.assertEqual('01101', Logic.game_logic('beret', 'trend'))
