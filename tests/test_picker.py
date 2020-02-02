from unittest import TestCase
from app.picker.picker import Picker, Args
from unittest.mock import patch
import io


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

        self.assertEqual(result, 'Not entering: UserA, UserB, UserC.\n')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_validate_args__when_number_less_than_1__expect_error_string(self, mock_stdout):
        args = Args()
        args.number = 0

        Picker._validate_args(args)

        error = 'Error: invalid value of --number argument (must be >= 1).\n'
        self.assertEqual(mock_stdout.getvalue(), error)

    def test_validate_args__when_number_less_than_1__expect_false(self):
        args = Args()
        args.number = 0

        result = Picker._validate_args(args)

        self.assertFalse(result)

    def test_validate_args__when_number_equals_1__expect_true(self):
        args = Args()
        args.number = 1

        result = Picker._validate_args(args)

        self.assertTrue(result)

    def test_validate_args__when_number_greater_than_1__expect_true(self):
        args = Args()
        args.number = 2

        result = Picker._validate_args(args)

        self.assertTrue(result)

    def test_validate_args__when_number_is_none__expect_type_error_exception(self):
        args = Args()
        args.number = None

        self.assertRaises(TypeError, Picker._validate_args, args)
