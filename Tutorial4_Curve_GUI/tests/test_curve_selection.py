import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from test import (
    MainWindow,
    build_method_to_model_value,
    curve_type_to_model_value,
    degree_to_model_value,
)


class CurveTypeSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_bezier_display_name_maps_to_model_value(self):
        self.assertEqual(curve_type_to_model_value("BezierCurve"), "BezierCurve")

    def test_bspline_display_name_maps_to_model_value(self):
        self.assertEqual(curve_type_to_model_value("B-Spline"), "Bspline")

    def test_unknown_display_name_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "지원하지 않는 커브 종류"):
            curve_type_to_model_value("Circle")

    def test_combobox_selection_updates_model_curve_type(self):
        window = MainWindow()
        self.addCleanup(window.close)

        self.assertEqual(window.selected_curve_type, "BezierCurve")

        window.comboBox.setCurrentText("B-Spline")

        self.assertEqual(window.selected_curve_type, "Bspline")

    def test_build_method_display_name_maps_to_model_value(self):
        self.assertEqual(build_method_to_model_value("BuildCurve"), "BuildCurve")
        self.assertEqual(
            build_method_to_model_value("Interpolation"), "Interpolation"
        )

    def test_build_method_combobox_updates_selected_method(self):
        window = MainWindow()
        self.addCleanup(window.close)

        window.comboBox_2.setCurrentText("Interpolation")

        self.assertEqual(window.selected_build_method, "Interpolation")

    def test_degree_display_text_is_converted_to_integer(self):
        self.assertEqual(degree_to_model_value("3"), 3)

    def test_degree_combobox_updates_selected_degree(self):
        window = MainWindow()
        self.addCleanup(window.close)

        window.comboBox_3.setCurrentText("5")

        self.assertEqual(window.selected_degree, 5)

    def test_field_title_line_edits_are_read_only_and_non_focusable(self):
        window = MainWindow()
        self.addCleanup(window.close)

        for field in (
            window.lineEdit_3,
            window.lineEdit_2,
            window.lineEdit,
        ):
            self.assertTrue(field.isReadOnly())
            self.assertEqual(
                field.focusPolicy(),
                Qt.FocusPolicy.NoFocus,
            )

        for combo_box in (
            window.comboBox,
            window.comboBox_2,
            window.comboBox_3,
        ):
            self.assertTrue(combo_box.isEnabled())

    def test_add_button_creates_editable_xyz_row_with_cp_name(self):
        window = MainWindow()
        self.addCleanup(window.close)

        window.pushButton_3.click()

        self.assertEqual(window.tableWidget.rowCount(), 1)
        self.assertEqual(window.tableWidget.item(0, 0).text(), "cp0")
        self.assertFalse(
            window.tableWidget.item(0, 0).flags()
            & Qt.ItemFlag.ItemIsEditable
        )
        for column in range(1, 4):
            item = window.tableWidget.item(0, column)
            self.assertIsNotNone(item)
            self.assertTrue(item.flags() & Qt.ItemFlag.ItemIsEditable)

    def test_interpolation_selection_renames_existing_rows_as_poc(self):
        window = MainWindow()
        self.addCleanup(window.close)
        window.pushButton_3.click()
        window.pushButton_3.click()

        window.comboBox_2.setCurrentText("Interpolation")

        self.assertEqual(window.tableWidget.item(0, 0).text(), "poc0")
        self.assertEqual(window.tableWidget.item(1, 0).text(), "poc1")

    def test_bspline_build_disables_existing_xz_and_preserves_y(self):
        window = MainWindow()
        self.addCleanup(window.close)
        window.pushButton_3.click()
        window.tableWidget.item(0, 1).setText("5")
        window.tableWidget.item(0, 2).setText("6")
        window.tableWidget.item(0, 3).setText("7")

        window.comboBox.setCurrentText("B-Spline")

        self.assertEqual(window.tableWidget.item(0, 1).text(), "0")
        self.assertEqual(window.tableWidget.item(0, 2).text(), "6")
        self.assertEqual(window.tableWidget.item(0, 3).text(), "0")
        for column in (1, 3):
            flags = window.tableWidget.item(0, column).flags()
            self.assertFalse(flags & Qt.ItemFlag.ItemIsEnabled)
            self.assertFalse(flags & Qt.ItemFlag.ItemIsEditable)
        y_flags = window.tableWidget.item(0, 2).flags()
        self.assertTrue(y_flags & Qt.ItemFlag.ItemIsEnabled)
        self.assertTrue(y_flags & Qt.ItemFlag.ItemIsEditable)

    def test_bspline_build_new_row_xz_reenable_as_zero_in_interpolation(self):
        window = MainWindow()
        self.addCleanup(window.close)
        window.comboBox.setCurrentText("B-Spline")

        window.pushButton_3.click()

        for column in (1, 3):
            item = window.tableWidget.item(0, column)
            self.assertEqual(item.text(), "0")
            self.assertFalse(item.flags() & Qt.ItemFlag.ItemIsEnabled)
            self.assertFalse(item.flags() & Qt.ItemFlag.ItemIsEditable)

        window.comboBox_2.setCurrentText("Interpolation")

        for column in (1, 3):
            item = window.tableWidget.item(0, column)
            self.assertEqual(item.text(), "0")
            self.assertTrue(item.flags() & Qt.ItemFlag.ItemIsEnabled)
            self.assertTrue(item.flags() & Qt.ItemFlag.ItemIsEditable)

    def test_remove_button_deletes_selected_row_and_reindexes_names(self):
        window = MainWindow()
        self.addCleanup(window.close)
        for _ in range(3):
            window.pushButton_3.click()

        window.tableWidget.selectRow(1)
        window.pushButton_2.click()

        self.assertEqual(window.tableWidget.rowCount(), 2)
        self.assertEqual(window.tableWidget.item(0, 0).text(), "cp0")
        self.assertEqual(window.tableWidget.item(1, 0).text(), "cp1")


if __name__ == "__main__":
    unittest.main()
