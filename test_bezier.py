import matplotlib.pyplot as plt

from BezierCurve import DeCasteljau
from Matrix import Matrix
from Vector import Vector
# ============================================================
# 데이터 입력
# ============================================================
# Degree가 n이면 cp0 ~ cpn 까지 n+1개의 컨트롤 포인트를 넣어주면 됨
input_data = {
    "cp0": Vector.xyz(100, 100, 0),
    "cp1": Vector.xyz(150, 250, 0),
    "cp2": Vector.xyz(200, 300, 0),
    "cp3": Vector.xyz(250, 400, 0),
    "cp4": Vector.xyz(300, 300, 0),
    "cp5": Vector.xyz(350, 250, 0),
    "cp6": Vector.xyz(400, 100, 0),
    "parameter": 5,
    "Degree": 6,
}

beziercurve = DeCasteljau(input_data)
print("control_points =")
for control_point in beziercurve.control_points:
    print(control_point)

# ============================================================
# Normalize
# ============================================================
normalization = beziercurve.normalize()
print("normalization =")
for key, normalized_point in normalization.items():
    print(key, normalized_point)

# ============================================================
# Calculate
# ============================================================
calculated_point = beziercurve.calculate()
print("calculated_point =")
for point in calculated_point:
    print(point)

# ============================================================
# denormalize
# ============================================================
POC = beziercurve.denormalize()
print("POC =")
for point in POC:
    print(point)

# ============================================================
# visualization
# ============================================================
beziercurve.visualize()
