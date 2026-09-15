import sys
from pathlib import Path
from typing import cast

from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtBoundSignal
from PyQt5.QtWidgets import (
    QApplication, QAbstractItemView, QGridLayout, QHeaderView,
    QMainWindow, QMessageBox, QTableWidgetItem, QVBoxLayout,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ViewModel.Play import Playing
from ViewModel.HydrostaticTableView import HydrostaticTableView
from ViewModel.HydrostaticCurveView import HydrostaticCurveView
from ViewModel.BodyPlan import BodyPlan


class CalculationWorker(QThread):
    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, drafts=None, parent=None):
        super().__init__(parent)
        self.drafts = drafts

    def run(self):
        # 계산만 작업 스레드에서 수행하고 위젯은 메인 스레드에서 갱신한다.
        try:
            data = Playing.run(drafts=self.drafts)
        except Exception as error:
            self.failed.emit(f"{type(error).__name__}: {error}")
        else:
            self.succeeded.emit(data)


class MainWindow(QMainWindow):
    # None: 1m~D까지 0.5m 간격 + Input의 Specific_Draft 목록 사용.
    # 더 촘촘한 곡선이 필요하면 예: [i / 2 for i in range(2, 51)]
    DRAFTS = None

    def __init__(self):
        super().__init__()
        uic.loadUi(str(Path(__file__).with_name("Interface.ui")), self)
        self.setWindowTitle("Ship Hydrostatics")
        # 세 개 패널과 선형도 축 제목이 겹치지 않도록 최소 크기를 확보한다.
        self.setMinimumSize(1400, 850)
        self.worker = None
        self.data = None
        self.setup_layout()
        self.setup_dimension_table()

        self.table_view = HydrostaticTableView(self.tableWidget)
        # QGraphicsView의 내부 표시 영역에 Matplotlib 캔버스를 배치한다.
        self.curve_view = HydrostaticCurveView(self.graphicsView_2.viewport())
        self.body_view = BodyPlan(self.graphicsView_4, self.comboBox_4)
        self.comboBox_4.setEnabled(False)
        self.pushButton.clicked.connect(self.start_calculation)
        self.statusbar.showMessage("Start를 눌러 입력 데이터를 계산하세요.")

        screen = QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            self.resize(int(available.width() * 0.9), int(available.height() * 0.85))

    def setup_layout(self):
        """Designer의 고정 좌표를 창 크기에 맞춰 늘어나는 배치로 연결한다."""
        layout = QGridLayout(self.centralwidget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        left, middle, right = QVBoxLayout(), QVBoxLayout(), QVBoxLayout()
        layout.addLayout(left, 0, 0)
        layout.addLayout(middle, 0, 1)
        layout.addLayout(right, 0, 2)
        for column, stretch in enumerate((2, 4, 4)):
            layout.setColumnStretch(column, stretch)

        for title in (self.textEdit, self.textEdit_2, self.textEdit_3):
            title.setReadOnly(True)
            title.setFixedHeight(56)
            title.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            title.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        left.addWidget(self.pushButton)
        left.addWidget(self.textEdit_3)
        left.addWidget(self.tableWidget_2, 1)
        middle.addWidget(self.textEdit)
        middle.addWidget(self.tableWidget, 1)
        right.addWidget(self.textEdit_2)
        right.addWidget(self.graphicsView_2, 1)
        right.addWidget(self.comboBox_4)
        right.addWidget(self.graphicsView_4, 1)

    def setup_dimension_table(self):
        table = self.tableWidget_2
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Dimension", "Value", "Unit"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def update_dimension_table(self, dimension):
        self.tableWidget_2.setRowCount(len(dimension))
        for row, (name, value) in enumerate(dimension.items()):
            unit = "ton/m³" if name == "Density of sea water" else "m"
            for column, text in enumerate((name, f"{value:g}", unit)):
                item = QTableWidgetItem(text)
                item.setTextAlignment(
                    (Qt.AlignmentFlag.AlignRight if column == 1 else Qt.AlignmentFlag.AlignLeft)
                    | Qt.AlignmentFlag.AlignVCenter
                )
                self.tableWidget_2.setItem(row, column, item)

    def start_calculation(self):
        if self.worker is not None:
            return
        self.pushButton.setEnabled(False)
        self.pushButton.setText("Calculating...")
        self.statusbar.showMessage("입력 읽기 및 hydrostatic 계산 중...")
        self.worker = CalculationWorker(self.DRAFTS, self)
        self.worker.succeeded.connect(self.show_results)
        self.worker.failed.connect(self.show_error)
        # PyQt5 5.15.4의 stub은 finished 시그널을 일반 메서드로 표기한다.
        cast(pyqtBoundSignal, self.worker.finished).connect(self.finish_calculation)
        self.worker.start()

    def show_results(self, data):
        try:
            self.update_dimension_table(data["dimension"])
            self.table_view.update_table(data["results"])
            self.curve_view.update_curve(data["results"])
            self.body_view.update_body(data["body_data"], data["dimension"])
        except Exception as error:
            self.show_error(f"화면 표시 오류: {error}")
            return
        self.data = data
        self.comboBox_4.setEnabled(True)
        self.statusbar.showMessage(
            f"완료: {len(data['results'])}개 흘수 계산 | "
            "Curve 배율은 범례 참고 | WSA는 선저를 포함한 둘레 적분 근삿값입니다."
        )

    def show_error(self, message):
        self.statusbar.showMessage("실패: 입력 데이터와 오류 내용을 확인하세요.")
        QMessageBox.critical(self, "Hydrostatic calculation", message)

    def finish_calculation(self):
        if self.worker is not None:
            self.worker.deleteLater()
        self.worker = None
        self.pushButton.setEnabled(True)
        self.pushButton.setText("Start")

    def closeEvent(self, a0):
        # 실행 중인 QThread가 창과 함께 파괴되는 것을 방지한다.
        if self.worker is not None:
            self.statusbar.showMessage("계산이 완료된 후 창을 닫아주세요.")
            if a0 is not None:
                a0.ignore()
        else:
            super().closeEvent(a0)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
