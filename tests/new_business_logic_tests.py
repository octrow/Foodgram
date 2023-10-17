import unittest

from src.new_business_logic import NewBusinessLogic


class TestNewBusinessLogic(unittest.TestCase):
    def setUp(self):
        self.logic = NewBusinessLogic()
        self.test_data = {"key": "value"}

    def tearDown(self):
        del self.logic
        del self.test_data

    def test_method1(self):
        result = self.logic.method1(self.test_data)
        self.assertEqual(result, "expected_result")

    def test_method1_edge_case(self):
        result = self.logic.method1({})
        self.assertEqual(result, "expected_result_for_empty_input")

    def test_method2(self):
        result = self.logic.method2(self.test_data)
        self.assertEqual(result, "expected_result")

    def test_method2_edge_case(self):
        result = self.logic.method2({"key": "very_large_value"})
        self.assertEqual(result, "expected_result_for_large_input")
