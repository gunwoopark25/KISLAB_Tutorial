from BSpline import de_boor
from Vector import Vector

# ============================================================
# 데이터 입력
# ============================================================
input_data = {
    "cp0": 50,
    "cp1": 175,
    "cp2": 200,
    "cp3": 150,
    "cp4": 25,
    "parameter": 5,
    "Degree": 3,
    "knots" : [50,50,50,200,350,350,350],
}

bsplinecurve = de_boor(input_data)
print("control_points =")
for control_point in bsplinecurve.control_points:
    print(control_point)

# ============================================================
# Greville abscissae
# ============================================================
abscissae = bsplinecurve.greville()
print(abscissae)