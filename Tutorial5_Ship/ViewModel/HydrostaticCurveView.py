import math

from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class HydrostaticCurveView:
    # results의 키, 범례 이름
    CURVES = [
        ("volume", "Volume"),
        ("displacement", "Displacement"),
        ("lcb", "LCB"),
        ("lcf", "LCF"),
        ("kb", "VCB (KB)"),
        ("km_t", "KM_T"),
        ("km_l", "KM_L"),
        ("tpc", "TPC"),
        ("mtc", "MTC"),
        ("waterplane_area", "Waterplane Area"),
        ("wsa", "Wetted Surface Area"),
        ("cb", "CB"),
        ("cp", "CP"),
        ("cwp", "CWP"),
        ("cm", "CM"),
    ]

    def __init__(self, container_widget):
        """Qt Designer의 빈 QWidget 또는 QFrame에 그래프를 추가한다."""
        self.figure = Figure(figsize=(8, 5), constrained_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)

        layout = container_widget.layout()
        if layout is None:
            layout = QVBoxLayout(container_widget)
            layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.canvas)
        self.setup_axes()

    def setup_axes(self):
        self.axes.set_title("Hydrostatic Curves")
        self.axes.set_xlabel("Value / max(abs(Value)) per curve")
        self.axes.set_ylabel("Draft [m]")
        self.axes.grid(True, alpha=0.3)

    def update_curve(self, results):
        """
        Play.py의 흘수별 results를 그린다.

        각 곡선은 최대 절댓값으로 나누어 표시하며 원본 값은 유지한다.
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

        for index, (key, label) in enumerate(self.CURVES):
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

            scale = max(abs(value) for value in valid_values)
            if scale == 0:
                scale = 1.0

            self.axes.plot(
                [value / scale for value in values],
                drafts,
                label=label,
                color=colors[index % len(colors)],
                linestyle=line_styles[(index // len(colors)) % len(line_styles)],
                linewidth=1.4,
                marker=".",
                markersize=3,
            )
            plotted_count += 1

        if plotted_count:
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
