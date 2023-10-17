import unittest

from src import main


class TestNewBusinessLogic(unittest.TestCase):
    def setUp(self):
        self.data = {"key1": "value1", "key2": "value2", "key3": "value3"}

    def test_function1(self):
        result = main.function1(self.data)
        self.assertEqual(result, "expected_result1")

    def test_function2(self):
        result = main.function2(self.data)
        self.assertEqual(result, "expected_result2")

    def test_function3(self):
        result = main.function3(self.data)
        self.assertEqual(result, "expected_result3")


if __name__ == "__main__":
    unittest.main()
