"""구버전(GUI 환경)과 최신 Matplotlib의 Qt 캔버스 경로를 지원한다."""

from importlib import import_module


# Matplotlib 3.3은 qt5agg, 최신 버전은 qtagg에 클래스를 정의한다.
# 버전마다 없는 모듈을 정적으로 import하지 않고 설치된 모듈을 선택한다.
try:
    backend = import_module("matplotlib.backends.backend_qtagg")
except ModuleNotFoundError as error:
    if error.name != "matplotlib.backends.backend_qtagg":
        raise
    backend = import_module("matplotlib.backends.backend_qt5agg")

FigureCanvasQTAgg = backend.FigureCanvasQTAgg
