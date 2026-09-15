import math
from typing import cast

import numpy as np

from PyQt5.QtWidgets import QGraphicsView, QVBoxLayout
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ViewModel.QtCanvas import FigureCanvasQTAgg


class BodyPlan:
    """오프셋을 측면도, 반폭 수선도, 횡단면도로 표시한다.

    입력 오프셋의 station 0=AP, 20=FP 기준을 사용한다.
    음수 station을 추가해도 AP와 midship 좌표는 변하지 않는다.
    """

    def __init__(self, container_widget, combo_box=None):
        self.figure = Figure(figsize=(10, 5), constrained_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        grid = self.figure.add_gridspec(2, 2, width_ratios=[3, 1])
        # 구버전 Matplotlib의 동적 subplot 클래스에도 Axes 인터페이스가 있다.
        self.profile_axes = cast(Axes, self.figure.add_subplot(grid[0, 0]))
        self.waterline_axes = cast(Axes, self.figure.add_subplot(grid[1, 0]))
        self.section_axes = cast(Axes, self.figure.add_subplot(grid[0, 1]))
        self.dimension_axes = cast(Axes, self.figure.add_subplot(grid[1, 1]))

        # Interface.ui의 QGraphicsView와 일반 QWidget 모두 지원한다.
        host = (
            container_widget.viewport()
            if isinstance(container_widget, QGraphicsView)
            else container_widget
        )
        if host is None:
            raise ValueError("그래프를 표시할 위젯이 없습니다.")
        layout = host.layout()
        if layout is None:
            layout = QVBoxLayout(host)
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.offset_data = None
        self.dimension = None
        self.body = "Fore Body"
        self.combo_box = combo_box

        if combo_box is not None:
            # 현재 UI의 항목을 Fore/Aft 표기로 통일한다.
            was_blocked = combo_box.blockSignals(True)
            combo_box.clear()
            combo_box.addItems(["Fore Body", "Aft Body"])
            combo_box.blockSignals(was_blocked)
            combo_box.currentTextChanged.connect(self.set_body)

        self.draw()

    def update_body(self, offset_data, dimension):
        """Playing.run()의 offset_data와 dimension을 전달받는다."""
        stations = np.array(sorted(offset_data["stations"]), dtype=float)
        waterlines = np.array(offset_data["waterlines"], dtype=float)
        breadths = np.array([
            offset_data["half_breadth"][station] for station in stations
        ], dtype=float)

        if stations.size < 3 or waterlines.size < 2:
            raise ValueError("station은 3개 이상, waterline은 2개 이상 필요합니다.")
        if breadths.shape != (stations.size, waterlines.size):
            raise ValueError("각 station의 반폭 개수는 waterline 개수와 같아야 합니다.")
        if not all(math.isfinite(value)
                   for values in (stations, waterlines, breadths)
                   for value in values.flat):
            raise ValueError("오프셋 좌표는 유한한 숫자여야 합니다.")
        if any(left >= right for values in (stations, waterlines)
               for left, right in zip(values[:-1], values[1:])):
            raise ValueError("station과 waterline은 중복 없이 증가해야 합니다.")
        if np.any(breadths < 0):
            raise ValueError("반폭은 0 이상이어야 합니다.")
        lbp = float(dimension["LBP"])
        if not math.isfinite(lbp) or lbp <= 0:
            raise ValueError("LBP는 양의 유한한 값이어야 합니다.")

        # 입력을 복사해 화면 변경이 원본 계산 데이터에 영향을 주지 않게 한다.
        self.offset_data = (stations.copy(), waterlines.copy(), breadths.copy())
        self.dimension = dict(dimension)
        self.draw()

    def set_body(self, body):
        if body not in ("Fore Body", "Aft Body"):
            raise ValueError("Fore Body 또는 Aft Body를 선택해야 합니다.")
        self.body = body
        if self.combo_box is not None and self.combo_box.currentText() != body:
            was_blocked = self.combo_box.blockSignals(True)
            self.combo_box.setCurrentText(body)
            self.combo_box.blockSignals(was_blocked)
        self.draw()

    def draw(self):
        for axes in (self.profile_axes, self.waterline_axes,
                     self.section_axes, self.dimension_axes):
            axes.clear()
        self.dimension_axes.set_axis_off()
        self.figure.suptitle(self.body)

        if self.offset_data is None or self.dimension is None:
            self.profile_axes.text(
                0.5, 0.5, "No offset data", transform=self.profile_axes.transAxes,
                ha="center", va="center",
            )
            self.canvas.draw_idle()
            return

        stations, z, breadths = self.offset_data
        lbp = float(self.dimension["LBP"])
        x = stations * lbp / 20
        midship = lbp / 2

        # midship station이 없으면 각 수선에서 선형보간하여 양쪽에 포함한다.
        if not np.any(x == midship):
            middle_breadths = np.array([
                np.interp(midship, x, breadths[:, i]) for i in range(len(z))
            ])
            position = np.searchsorted(x, midship)
            x = np.insert(x, position, midship)
            breadths = np.insert(breadths, position, middle_breadths, axis=0)

        mask = x >= midship if self.body == "Fore Body" else x <= midship
        body_x, body_y = x[mask], breadths[mask]

        # 측면도: 일정한 반폭에서의 등고선이 buttock line이다.
        low, high = float(body_y.min()), float(body_y.max())
        if high > low:
            levels = np.linspace(low, high, 12)[1:-1]
            contours = self.profile_axes.contour(
                body_x, z, body_y.T, levels=levels,
                colors="#555555", linewidths=0.6,
            )
            self.profile_axes.clabel(contours, fontsize=6, fmt="%.1f")

        # 반폭 수선도: 각 높이 z에서 station 방향의 반폭을 연결한다.
        for i in range(len(z)):
            self.waterline_axes.plot(body_x, body_y[:, i], color="#555555", lw=0.6)

        # 횡단면도: 각 station의 반폭과 높이를 연결한다.
        for section in body_y:
            # 중심선~Bottom 반폭을 추가해 평평한 선저를 표시한다.
            self.section_axes.plot(
                np.insert(section, 0, 0.0), np.insert(z, 0, z[0]),
                color="#555555", lw=0.6,
            )

        self.profile_axes.set(title="Profile (buttocks)", xlabel="X from AP [m]", ylabel="Z [m]")
        self.waterline_axes.set(title="Half-breadth (waterlines)", xlabel="X from AP [m]", ylabel="Half-breadth [m]")
        self.section_axes.set(title="Body sections", xlabel="Half-breadth [m]", ylabel="Z [m]")

        left, right = (midship, float(x[-1])) if self.body == "Fore Body" else (float(x[0]), midship)
        max_breadth = max(float(breadths.max()), 1.0)
        self.profile_axes.set(xlim=(left, right), ylim=(z[0], z[-1]))
        self.waterline_axes.set(xlim=(left, right), ylim=(0, max_breadth))
        self.section_axes.set(xlim=(0, max_breadth), ylim=(z[0], z[-1]))
        self.section_axes.set_aspect("equal", adjustable="box")
        for axes in (self.profile_axes, self.waterline_axes, self.section_axes):
            axes.grid(True, alpha=0.3)
            axes.tick_params(labelsize=7)

        rows = [[key, f"{float(self.dimension[key]):.2f}"]
                for key in ("LOA", "LBP", "B", "D", "T_d") if key in self.dimension]
        table = self.dimension_axes.table(
            cellText=rows, colLabels=["Dimension", "m"],
            cellLoc="center", loc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        self.canvas.draw_idle()
