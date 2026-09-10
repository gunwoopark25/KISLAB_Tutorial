import os
import sys
import importlib

# Model, Input 폴더를 path에 추가 (Model 내부 모듈들이 flat import를 사용하기 때문)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT_DIR, "Model")
INPUT_DIR = os.path.join(ROOT_DIR, "Input")
sys.path.insert(0, MODEL_DIR)
sys.path.insert(0, INPUT_DIR)

from Loadxlsx import Loadxlsx
from HydrostaticValue import Calculate

# 320K_VLCC.py는 파일명이 숫자로 시작해서 "import 320K_VLCC" 문법을 못 쓰기 때문에
# importlib로 불러온다
vlcc = importlib.import_module("320K_VLCC")

# ============================================================
# 데이터 입력
# ============================================================
raw_data = Loadxlsx.load()
offset_data = Loadxlsx.interpolate(raw_data)

draft = vlcc.Dimension["T_d"]

calculate = Calculate(offset_data, vlcc.Dimension, vlcc.Specific_Dimension, draft)

# ============================================================
# 전처리 값 확인
# ============================================================
print("stations count =", len(calculate.stations) - 1)
print("waterlines count =", len(calculate.waterlines) - 1)
print("draft =", calculate.draft, "m")
print("station_spacing =", calculate.station_spacing, "m")
print("waterline_spacing =", calculate.waterline_spacing,"m")

# ============================================================
# Volume_mld 계산
# ============================================================
volume_ext = calculate.Volume_mld()
print("Volume_mld =", volume_ext, "m^3")

WSA = calculate.WSA()
print("WSA = ", WSA, "m^3")