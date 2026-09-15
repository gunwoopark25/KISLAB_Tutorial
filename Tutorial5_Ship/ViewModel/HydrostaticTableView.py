from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidgetItem,
)


class HydrostaticTableView:
    # 표시 이름, results의 키, 소수점 자릿수
    ROWS = [
        ("Draft Moulded [m]", "draft", 3),
        ("Volume Moulded [m³]", "volume", 1),
        ("Displacement S.W. [ton]", "displacement", 1),
        ("LCF from Midship [m]", "lcf", 3),
        ("LCB from Midship [m]", "lcb", 3),
        ("VCB above B.L. [m]", "kb", 3),
        ("TPC [ton/cm]", "tpc", 2),
        ("MTC [ton·m/cm]", "mtc", 2),
        ("KM_T [m]", "km_t", 3),
        ("KM_L [m]", "km_l", 3),
        ("I_T [m⁴]", "i_t", 1),
        ("I_L [m⁴]", "i_l", 1),
        ("Waterplane Area [m²]", "waterplane_area", 1),
        ("Wetted Surface Area [m²]", "wsa", 1),
        ("Block Coeff. (CB)", "cb", 4),
        ("Prismatic Coeff. (CP)", "cp", 4),
        ("Waterplane Coeff. (CWP)", "cwp", 4),
        ("Midship Coeff. (CM)", "cm", 4),
    ]

    def __init__(self, table_widget):
        # Qt Designer에서 만든 QTableWidget을 전달받는다.
        self.table = table_widget
        self.setup_table()

    def setup_table(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.ROWS))
        self.table.setColumnCount(0)

        # 왼쪽 행 제목: 계산 항목
        self.table.setVerticalHeaderLabels(
            [label for label, _, _ in self.ROWS]
        )

        # 결과 표이므로 직접 편집하지 못하게 설정
        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.table.setAlternatingRowColors(True)

        # 열이 많으면 가로 스크롤로 확인
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

    def update_table(self, results):
        """
        results:
            흘수별 계산 결과 딕셔너리의 리스트

            [
                {"draft": 15.0, "volume": ..., "kb": ..., ...},
                {"draft": 16.0, "volume": ..., "kb": ..., ...},
            ]

        전달되지 않은 항목은 '-'로 표시한다.
        """
        # 흘수 오름차순으로 표시
        results = sorted(
            results,
            key=lambda result: result["draft"],
        )

        self.table.setUpdatesEnabled(False)

        try:
            # 기존 결과 제거. 행 제목은 유지한다.
            self.table.clearContents()
            self.table.setColumnCount(len(results))

            self.table.setHorizontalHeaderLabels([
                f'{result["draft"]:.3f} m'
                for result in results
            ])

            for column, result in enumerate(results):
                for row, (_, key, decimals) in enumerate(self.ROWS):
                    value = result.get(key)

                    text = (
                        "-"
                        if value is None
                        else f"{value:,.{decimals}f}"
                    )

                    item = QTableWidgetItem(text)
                    item.setTextAlignment(
                        Qt.AlignRight | Qt.AlignVCenter
                    )

                    # 흘수 행 강조
                    if key == "draft":
                        item.setBackground(QColor("#FFF2CC"))
                        item.setForeground(QColor("#202020"))

                    self.table.setItem(row, column, item)

        finally:
            self.table.setUpdatesEnabled(True)