"""Matplotlib의 Qt 캔버스를 한 곳에서만 import 하기 위한 모듈.

matplotlib 3.6부터 backend_qt5agg가 backend_qtagg로 통합되어
버전에 따라 모듈 이름이 달라지므로 여기서 한 번만 흡수한다.
"""
import matplotlib

# Figure를 만들기 전에 Qt 백엔드를 지정해야 한다.
matplotlib.use("QtAgg")

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
except ImportError:  # matplotlib 3.6 미만
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

__all__ = ["FigureCanvasQTAgg"]
