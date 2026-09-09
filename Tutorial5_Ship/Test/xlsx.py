import os
import sys

# Model 폴더를 path에 추가 (Model 내부 모듈들이 flat import를 사용하기 때문)
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Model")
sys.path.insert(0, MODEL_DIR)

from Loadxlsx import Loadxlsx

file = Loadxlsx.load()
print(file["stations"])
print(len(file["stations"]))