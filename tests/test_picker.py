from unittest import TestCase
from picker import Picker


class TestPicker(TestCase):
    def setUp(self):
        self.picker = Picker()

    def test_get_not_entering__when_no_not_entering_users__expect_empty_string(self):
        result = self.picker._get_not_entering()

        self.assertEqual(result, '')

    def test_get_not_entering__when_not_entering_users__expect_non_empty_string(self):
        users = ['UserA', 'UserB', 'UserC']
        self.picker.args.verbose = True
        self.picker.not_entering.extend(users)

        result = self.picker._get_not_entering()

        self.assertNotEqual(result, '')

    def test_get_not_entering__when_not_entering_users__expect_message_string(self):
        users = ['UserA', 'UserB', 'UserC']
        self.picker.args.verbose = True
        self.picker.not_entering.extend(users)

        result = self.picker._get_not_entering()

        message = 'Not entering: UserA, UserB, UserC.\n'
        self.assertEqual(result, message)
