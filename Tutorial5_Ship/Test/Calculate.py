import os
import sys
import importlib

# 파일을 직접 실행할 때도 프로젝트 패키지를 찾도록 루트를 추가한다.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from Model.Loadxlsx import Loadxlsx
from Model.HydrostaticValue import Calculate

# 320K_VLCC.py는 파일명이 숫자로 시작해서 "import 320K_VLCC" 문법을 못 쓰기 때문에
# importlib로 불러온다
vlcc = importlib.import_module("Input.320K_VLCC")

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
