from Vector import Vector
from HermiteCurve import HermiteCurve

# ============================================================
# 데이터 입력
# ============================================================
input_data = {
    "P0": Vector.xyz(0, 200, 0),
    "P1": Vector.xyz(200, 300, 0),
    "T0": Vector.xyz(0, 150, 0),
    "T1": Vector.xyz(0, 150, 0),
    "parameter": 20,
}

hc = HermiteCurve(input_data)
print("hc.input_data =")
print(hc.input_data)

# ============================================================
# input_data를 가지고 Matrix 생성
# ============================================================
hc_matrix = hc.build_geometry_matrix()
print("hc_matrix =")
print(hc_matrix)

# ============================================================
# Matrix 연산 생성
# ============================================================
hc_POC = hc.compute_curve_points()
print("calculated_point =")
for point in hc_POC:
    print(point)

# ============================================================
# 그래프 출력
# ============================================================
hc.plot_curve()




