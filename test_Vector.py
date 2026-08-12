from Vector import Vector

# 벡터 정의
v1 = Vector(1,2,3)
v2 = Vector(4,5,2)
v3 = Vector(8,12,4)
v4 = Vector(2,4,1,5)
# 출력
print(v1)
print(v2)
print(v3)

# 더하기
result1 = v1 + v2
result2 = v1 + v2 + v3
#result12 = v1 + v2 + v4 <= 다른 차원일때 오류 발생
print(result1)
print(result2)
#print(result12)

# 빼기
result3 = v1 - v2
result4 = v1 - v2 - v3
print(result3)
print(result4)

# 복합
result5 = v1 + v2 - v3
print(result5)

# 곱하기
result6 = v1 * v2 * v3
print(result6)

# 나누기
result7 = v1 + v2 / v3 #기본적으로 파이썬 자체에서 +,-보다 *,/를 우선순위로 계산하는 규칙이 있음
print(result7)

# 내적
result8 = Vector.cdot(v1,v2)
print(result8)

# 외적
result9 = Vector.crossproduct(v2,v3)
print(result9)

# 동일 체크
result10 = Vector.check_equal(v1,v2)

# Normalization 전 열별 최댓값, 최솟값
result11 = Vector.normalization(v1,v2,v3)
print(result11)

result13 = Vector.magnitude(v1)
print(result13)
