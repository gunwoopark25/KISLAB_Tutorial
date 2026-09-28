import math
from typing import cast

from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ViewModel.QtCanvas import FigureCanvasQTAgg


class HydrostaticCurveView:
    # key, 항목/단위, divisor, shift: 표시 X = 실제 값 / divisor + shift
    # 선택한 흘수 범위에 따라 변하지 않는 고정 배율이다.
    CURVES = [
        ("volume", "Volume [m³]", 1000, 0),
        ("displacement", "Displ. [t]", 1000, 5),
        ("lcb", "LCB [m]", 0.1, 200),
        ("lcf", "LCF [m]", 0.5, 100),
        ("kb", "VCB [m]", 0.1, 0),
        ("km_t", "KM_T [m]", 1, 10),
        ("km_l", "KM_L [m]", 50, 35),
        ("tpc", "TPC [t/cm]", 1, 20),
        ("mtc", "MTC [t m/cm]", 20, 90),
        ("waterplane_area", "AWP [m²]", 100, 10),
        ("wsa", "WSA approx. [m²]", 100, 0),
        ("cb", "CB", 0.005, -5),
        ("cp", "CP", 0.005, 35),
        ("cwp", "CWP", 0.01, 0),
        ("cm", "CM", 0.01, 0),
    ]

    def __init__(self, container_widget):
        """Qt Designer의 빈 QWidget 또는 QFrame에 그래프를 추가한다."""
        self.figure = Figure(figsize=(8, 5), constrained_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = cast(Axes, self.figure.add_subplot(111))

        layout = container_widget.layout()
        if layout is None:
            layout = QVBoxLayout(container_widget)
            layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.canvas)
        self.setup_axes()

    def setup_axes(self):
        self.axes.set_title("Hydrostatic Curves")
        self.axes.set_xlabel("X = value / divisor + shift (see legend)")
        self.axes.set_ylabel("Draft [m]")
        self.axes.grid(True, alpha=0.3)

    def update_curve(self, results):
        """
        Play.py의 흘수별 results를 그린다.

        고정 배율과 이동값을 적용하며 원본 값은 유지한다.
        누락값은 곡선을 끊어 표시한다.
        """
        results = sorted(results, key=lambda result: result["draft"])

        self.axes.clear()
        self.setup_axes()

        colors = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
            "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
            "#bcbd22", "#17becf",
        ]
        line_styles = ["-", "--", "-."]
        plotted_count = 0

        for index, (key, label, divisor, shift) in enumerate(self.CURVES):
            drafts = []
            values = []

            for result in results:
                draft = float(result["draft"])
                value = result.get(key)

                if not math.isfinite(draft):
                    continue

                value = float(value) if value is not None else math.nan
                drafts.append(draft)
                values.append(value if math.isfinite(value) else math.nan)

            valid_values = [value for value in values if math.isfinite(value)]
            if not valid_values:
                continue

            self.axes.plot(
                [value / divisor + shift for value in values],
                drafts,
                label=f"{label}: /{divisor:g} {shift:+g}",
                color=colors[index % len(colors)],
                linestyle=line_styles[(index // len(colors)) % len(line_styles)],
                linewidth=1.4,
                marker="." if len(valid_values) <= 3 else None,
                markersize=3,
            )
            plotted_count += 1

        if plotted_count:
            self.axes.set_ylim(bottom=0)
            self.axes.legend(
                loc="upper left",
                bbox_to_anchor=(1.02, 1.0),
                fontsize=8,
            )
        else:
            self.axes.text(
                0.5, 0.5, "No hydrostatic data",
                transform=self.axes.transAxes,
                ha="center", va="center",
            )

        self.canvas.draw_idle()
