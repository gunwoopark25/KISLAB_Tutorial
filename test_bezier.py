from BezierCurve import DeCasteljau
from Vector import Vector
# ============================================================
# 알고리즘
# ============================================================
"""
## Bezier Curve Algorithm
1. InputData
2. Normalize
3. Calculate
4. Denormalize
5. Visualization

## Interpolation
1. InputData
2. ChordLength
3. Normalize
4. Calculate
    4-1. BernsteinMatrix
    4-2. GaussElimination
    4-3. MatrixMul
    4-4. DeCasteljau
5. Denormalize
6. Visualization
"""
# ============================================================
# 데이터 입력
# ============================================================
input_data = {
    "cp0": Vector.xyz(100, 100, 0),
    "cp1": Vector.xyz(150, 250, 0),
    "cp2": Vector.xyz(200, 300, 0),
    "cp3": Vector.xyz(250, 400, 0),
    "parameter": 5,
    "Degree": 3,
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
