from BSpline import Interpolation
from Vector import Vector
# ============================================================
# 알고리즘
# ============================================================
"""
## B-Spline Interpolation
1. InputData
2. Chordlength
3. KnotVector
4. Calculate
    4-1. BSplineMatrix
    4-2. GaussElimination
    4-3. MatrixMul
    4-4. de Boor
5. Visualization
"""
# ============================================================
# 데이터 입력
# ============================================================
# knots는 입력하지 않음 -> POC의 chord length로부터 직접 만들어냄
# POC는 Degree + 1개 이상이면 몇 개든 가능
input_data = {
    "poc0": Vector.xyz(200, 300, 0),
    "poc1": Vector.xyz(300, 400, 0),
    "poc2": Vector.xyz(400, 200, 0),
    "poc3": Vector.xyz(500, 300, 0),
    "parameter": 100,
    "Degree": 3,
}

bsplineinterpolation = Interpolation(input_data)
print("poc =")
for poc in bsplineinterpolation.poc:
    print(poc)

# ============================================================
# Chord Length
# ============================================================
chordlength = bsplineinterpolation.Chordlength()
print("chordlength =")
print(chordlength)

# ============================================================
# Knot Vector
# ============================================================
knots = bsplineinterpolation.KnotVector()
print("knots =")
print(knots)

# ============================================================
# Calculate
# ============================================================
POC = bsplineinterpolation.Calculate()
print("basis_matrix =")
print(bsplineinterpolation.basis_matrix)
print("control_points =")
for cp in bsplineinterpolation.control_points:
    print(cp)
print("POC =")
for point in POC:
    print(point)

# ============================================================
# Visualization
# ============================================================
bsplineinterpolation.Visualization()