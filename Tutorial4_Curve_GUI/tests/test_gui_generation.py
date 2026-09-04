import unittest
from unittest.mock import Mock, patch

from PyQt5.QtWidgets import QApplication

from test import MainWindow


class GuiGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def make_window(self):
        window = MainWindow()
        self.addCleanup(window.close)
        return window

    def test_parameter_has_default_and_knots_row_follows_curve_mode(self):
        window = self.make_window()

        self.assertEqual(window.tableWidget_2.item(0, 0).text(), "100")
        self.assertTrue(window.tableWidget_2.isRowHidden(1))

        window.comboBox.setCurrentText("B-Spline")
        self.assertFalse(window.tableWidget_2.isRowHidden(1))

        window.comboBox_2.setCurrentText("Interpolation")
        self.assertTrue(window.tableWidget_2.isRowHidden(1))

    def test_generate_button_draws_bezier_curve_from_table_values(self):
        window = self.make_window()
        window.comboBox_3.setCurrentText("3")
        window.tableWidget_2.item(0, 0).setText("20")
        rows = [
            ("0", "0", "0"),
            ("1", "2", "0"),
            ("2", "2", "0"),
            ("3", "0", "0"),
        ]
        for values in rows:
            window.pushButton_3.click()
            row = window.tableWidget.rowCount() - 1
            for column, value in enumerate(values, start=1):
                window.tableWidget.item(row, column).setText(value)

        window.pushButton.click()

        self.assertIsNotNone(window.last_curve_result)
        self.assertEqual(len(window.axes.lines), 3)
        self.assertIn("Bezier Build Curve", window.axes.get_title())
        self.assertIn("완료", window.statusbar.currentMessage())

    def test_invalid_input_is_reported_without_running_algorithm(self):
        window = self.make_window()

        with patch("test.QtWidgets.QMessageBox.warning") as warning:
            window.pushButton.click()

        self.assertIsNone(window.last_curve_result)
        self.assertIn("CP 또는 POC", window.last_error_message)
        warning.assert_called_once()

    def test_failed_generation_clears_previous_curve(self):
        window = self.make_window()
        window.comboBox_3.setCurrentText("1")
        window.tableWidget_2.item(0, 0).setText("10")
        for values in (("0", "0", "0"), ("1", "1", "0")):
            window.pushButton_3.click()
            row = window.tableWidget.rowCount() - 1
            for column, value in enumerate(values, start=1):
                window.tableWidget.item(row, column).setText(value)
        window.pushButton.click()
        self.assertEqual(len(window.axes.lines), 3)

        window.tableWidget.item(0, 1).setText("invalid")
        with patch("test.QtWidgets.QMessageBox.warning"):
            window.pushButton.click()

        self.assertEqual(len(window.axes.lines), 0)

    def test_algorithm_overflow_is_reported_as_input_error(self):
        window = self.make_window()
        window.comboBox_3.setCurrentText("1")
        window.tableWidget_2.item(0, 0).setText("10")
        for values in (("0", "0", "0"), ("1", "1", "0")):
            window.pushButton_3.click()
            row = window.tableWidget.rowCount() - 1
            for column, value in enumerate(values, start=1):
                window.tableWidget.item(row, column).setText(value)
        window.curve_model.calculate = Mock(
            side_effect=OverflowError("계산 범위를 초과했습니다.")
        )

        with patch("test.QtWidgets.QMessageBox.warning") as warning:
            window.pushButton.click()

        self.assertIn("계산 범위", window.last_error_message)
        warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
