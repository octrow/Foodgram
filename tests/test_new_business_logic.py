import unittest
from unittest.mock import Mock

from src import new_business_logic


class TestNewBusinessLogic(unittest.TestCase):
    def setUp(self):
        self.mock_data = Mock()

    def tearDown(self):
        self.mock_data.reset_mock()

    def test_function1(self):
        self.mock_data.return_value = "expected value"
        result = new_business_logic.function1(self.mock_data)
        self.assertEqual(result, "expected value")

    def test_function2(self):
        self.mock_data.return_value = "expected value"
        result = new_business_logic.function2(self.mock_data)
        self.assertEqual(result, "expected value")

    def test_function3(self):
        self.mock_data.return_value = "expected value"
        result = new_business_logic.function3(self.mock_data)
        self.assertEqual(result, "expected value")
