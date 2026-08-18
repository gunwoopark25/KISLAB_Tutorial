from BezierCurve import Interploation
from Vector import Vector
# ============================================================
# 데이터 입력
# ============================================================
input_data = {
    "poc0": Vector.xyz(100, 100, 0),
    "poc1": Vector.xyz(200, 300, 0),
    "poc2": Vector.xyz(300, 350, 0),
    "poc3": Vector.xyz(500, 100, 0),
    "parameter": 100,
    "Degree": 3,
}

beziercurve = Interploation(input_data)
print("poc =")
for poc in beziercurve.poc:
    print(poc)

# ============================================================
# Chord Length
# ============================================================
chordlength = beziercurve.Chordlength()
print("chordlength =")
print(chordlength)

# ============================================================
# Nrmaization
# ============================================================
normalized_poc, normalized_u = beziercurve.Normalize()
print("normalized_poc =")
for poc in normalized_poc:
    print(poc)
print("normalized_u =")
print(normalized_u)

# ============================================================
# Calculate
# ============================================================
calculated_point = beziercurve.Calculate()
print("control_points =")
for cp in beziercurve.control_points:
    print(cp)
print("calculated_point =")
for point in calculated_point:
    print(point)

# ============================================================
# Denormalize
# ============================================================
POC = beziercurve.Denormalize()
print("POC =")
for point in POC:
    print(point)

# ============================================================
# Visualization
# ============================================================
beziercurve.Visualization()
