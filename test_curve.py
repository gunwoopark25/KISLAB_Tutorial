from Vector import Vector
from HermiteCurve import HermiteCurve

# ============================================================
# 데이터 입력
# ============================================================
input_data = {
    "P0": Vector.xyz(100, 200, 0),
    "P1": Vector.xyz(200, 300, 0),
    "T0": Vector.xyz(10, 20, 0),
    "T1": Vector.xyz(20, 30, 0),
    "parameter": 4,
}

hc = HermiteCurve(input_data)

# ============================================================
# input_data 확인 출력
# ============================================================
print("hc.input_data =")
print(hc.input_data)

# ============================================================
# input_data를 가지고 Matrix 생성
# ============================================================
hc_matrix = hc.build_geometry_matrix()
print("hc_matrix =")
print(hc_matrix)

# ============================================================
# Normalization
# ============================================================
hc_normalized_matrix = hc.normalize_matrix()
print("hc_normalized_matrix =")
print(hc_normalized_matrix)
print("min_list =", hc.min_list)
print("max_list =", hc.max_list)