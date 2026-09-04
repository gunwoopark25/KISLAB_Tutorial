import sys
from pathlib import Path
from typing import cast

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets, uic

from model import CurveModel, InputDataConverter, Visualize


# 커브 종류 선택 (토글)
CURVE_TYPE_MAP = {
    "BezierCurve": "BezierCurve",
    "B-Spline": "Bspline",
}


# 커브 생성 작업 방식 (토글)
BUILD_METHOD_MAP = {
    "BuildCurve": "BuildCurve",
    "Interpolation": "Interpolation",
}

NAME_ITEM_FLAGS = cast(
    QtCore.Qt.ItemFlags,
    (
        QtCore.Qt.ItemFlag.ItemIsSelectable
        | QtCore.Qt.ItemFlag.ItemIsEnabled
    ),
)

COORDINATE_EDITABLE_FLAGS = cast(
    QtCore.Qt.ItemFlags,
    (
        QtCore.Qt.ItemFlag.ItemIsSelectable
        | QtCore.Qt.ItemFlag.ItemIsEditable
        | QtCore.Qt.ItemFlag.ItemIsEnabled
    ),
)

COORDINATE_DISABLED_FLAGS = cast(
    QtCore.Qt.ItemFlags,
    QtCore.Qt.ItemFlag.NoItemFlags,
)

def curve_type_to_model_value(display_text):
    try:
        return CURVE_TYPE_MAP[display_text]
    except KeyError as error:
        raise ValueError(f"지원하지 않는 커브 종류입니다: {display_text}") from error


def build_method_to_model_value(display_text):
    return BUILD_METHOD_MAP[display_text]


# Degree 설정 (토글)
def degree_to_model_value(display_text):
    return int(display_text)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = Path(__file__).resolve().with_name("test.ui")
        uic.loadUi(str(ui_path), self)

        self.curve_model = CurveModel()
        self.last_curve_result = None
        self.last_error_message = ""

        self.selected_curve_type = curve_type_to_model_value(
            self.comboBox.currentText()
        )
        self.selected_build_method = build_method_to_model_value(
            self.comboBox_2.currentText()
        )
        self.selected_degree = degree_to_model_value(
            self.comboBox_3.currentText()
        )

        self.tableWidget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.setup_graph_widget()
        self.initialize_curve_settings()
        self.update_knots_row_visibility()

        self.comboBox.currentTextChanged.connect(self.on_curve_type_changed)
        self.comboBox_2.currentTextChanged.connect(self.on_build_method_changed)
        self.comboBox_3.currentTextChanged.connect(self.on_degree_changed)
        self.pushButton_3.clicked.connect(self.add_point_row)
        self.pushButton_2.clicked.connect(self.remove_selected_point_rows)
        self.pushButton.clicked.connect(self.generate_curve)

    def on_curve_type_changed(self, display_text):
        self.selected_curve_type = curve_type_to_model_value(display_text)
        self.update_knots_row_visibility()
        self.update_point_coordinate_editability()

    def on_build_method_changed(self, display_text):
        self.selected_build_method = build_method_to_model_value(display_text)
        self.refresh_point_names()
        self.update_knots_row_visibility()
        self.update_point_coordinate_editability()

    def on_degree_changed(self, display_text):
        self.selected_degree = degree_to_model_value(display_text)

    # POC or CP 기입
    def point_name_prefix(self):
        if self.selected_build_method == "Interpolation":
            return "poc"
        return "cp"

    # +항목 추가
    def add_point_row(self):
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)

        name_item = QtWidgets.QTableWidgetItem(
            f"{self.point_name_prefix()}{row}"
        )
        name_item.setFlags(NAME_ITEM_FLAGS)
        self.tableWidget.setItem(row, 0, name_item)

        for column in range(1, 4):
            self.tableWidget.setItem(row, column, QtWidgets.QTableWidgetItem(""))

        self.update_point_coordinate_editability()

    # -항목 제거
    def remove_selected_point_rows(self):
        selected_rows = {
            index.row() for index in self.tableWidget.selectedIndexes()
        }

        for row in sorted(selected_rows, reverse=True):
            self.tableWidget.removeRow(row)

        self.refresh_point_names()

    def refresh_point_names(self):
        prefix = self.point_name_prefix()
        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 0)
            if name_item is None:
                name_item = QtWidgets.QTableWidgetItem()
                name_item.setFlags(NAME_ITEM_FLAGS)
                self.tableWidget.setItem(row, 0, name_item)
            name_item.setText(f"{prefix}{row}")

    def is_bspline_build_mode(self):
        return (
            self.selected_curve_type == "Bspline"
            and self.selected_build_method == "BuildCurve"
        )

    def update_point_coordinate_editability(self):
        y_only_mode = self.is_bspline_build_mode()

        for row in range(self.tableWidget.rowCount()):
            for column in range(1, 4):
                item = self.tableWidget.item(row, column)
                if item is None:
                    item = QtWidgets.QTableWidgetItem("")
                    self.tableWidget.setItem(row, column, item)

                if y_only_mode and column in (1, 3):
                    item.setText("0")
                    item.setFlags(COORDINATE_DISABLED_FLAGS)
                else:
                    item.setFlags(COORDINATE_EDITABLE_FLAGS)

    # knots와 parameter를 기입
    def initialize_curve_settings(self):
        if self.tableWidget_2.item(0, 0) is None:
            self.tableWidget_2.setItem(
                0,
                0,
                QtWidgets.QTableWidgetItem("100"),
            )
        if self.tableWidget_2.item(1, 0) is None:
            self.tableWidget_2.setItem(
                1,
                0,
                QtWidgets.QTableWidgetItem(""),
            )

    def update_knots_row_visibility(self):
        knots_required = (
            self.selected_curve_type == "Bspline"
            and self.selected_build_method == "BuildCurve"
        )
        self.tableWidget_2.setRowHidden(1, not knots_required)

    def setting_text(self, row):
        item = self.tableWidget_2.item(row, 0)
        return "" if item is None else item.text().strip()

    def collect_point_rows(self):
        point_rows = []
        for row in range(self.tableWidget.rowCount()):
            coordinates = []
            for column in range(1, 4):
                item = self.tableWidget.item(row, column)
                coordinates.append("" if item is None else item.text().strip())
            point_rows.append(tuple(coordinates))
        return point_rows


    # Curve 생성 시작 (버튼)
    def generate_curve(self):
        self.last_curve_result = None
        self.last_error_message = ""

        try:
            converter = InputDataConverter(
                curve_type=self.selected_curve_type,
                build_method=self.selected_build_method,
                degree=self.selected_degree,
                parameter=self.setting_text(0),
                point_rows=self.collect_point_rows(),
                knots=self.setting_text(1),
            )
            input_data = converter.to_dict()
            result = self.curve_model.calculate(input_data)
            self.draw_curve(result)
        except (
            IndexError,
            KeyError,
            OverflowError,
            TypeError,
            ValueError,
            ZeroDivisionError,
        ) as error:
            self.last_error_message = str(error)
            self.axes.clear()
            self.canvas.draw_idle()
            self.statusbar.showMessage("Curve 생성 실패")
            QtWidgets.QMessageBox.warning(
                self,
                "입력 오류",
                self.last_error_message,
            )
            return

        self.last_curve_result = result
        self.statusbar.showMessage("Curve 생성 완료")


    # Graph 시각화
    def setup_graph_widget(self):
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QtWidgets.QVBoxLayout(self.GraphWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def draw_curve(self, result):
        self.axes.clear()
        Visualize(
            result.control_points,
            result.curve_points,
            result.degree,
            kind_of_curve=result.curve_type,
            kind_of_struct_curve=result.build_method,
            axes=self.axes,
            show=False,
            **result.visualization_options,
        )
        self.canvas.draw_idle()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
