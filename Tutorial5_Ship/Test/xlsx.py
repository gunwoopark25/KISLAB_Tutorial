import os
import sys

# 파일을 직접 실행할 때도 프로젝트 패키지를 찾도록 루트를 추가한다.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from Model.Loadxlsx import Loadxlsx

file = Loadxlsx.load()
print(file["stations"])
print(len(file["stations"]))
