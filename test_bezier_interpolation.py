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
    "parameter": 5,
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