from Matrix import Matrix

m1 = Matrix([[1,3,5],[3,1,7]])
print("Matrix m1 =")
print(m1)

m2 = Matrix([[3,4,8],[7,3,5]])
print("Matrix m2 =")
print(m2)

# 덧셈
result = m1 + m2
print("result =")
print(result)

# 뺄셈
result1 = m1 - m2
print("result1 =")
print(result1)

## 에러가 나와야 정상
#result2 = m1 * m2
#print("result2 =")
#print(result2)

#곱셈
m3 = Matrix([[1,2],[5,3],[2,4]])
print("Matrix m3 =")
print(m3)
result3 = m1 *m3
print("result3 =")
print(result3)

#나눗셈
result4 = m1 / m2
print("result4 =")
print(result4)

#같은지 체크
Matrix.check_equal(m1,m2)

#Transpose
result5 = Matrix.transpose(m1)
print("result5 =")
print(result5)

#정방행렬
Matrix.is_square(m1)

# 단위 행렬 생성
id_Matrix = Matrix.identity(4)
print(id_Matrix)
Matrix.is_square(id_Matrix)

#가우스소거법
result6 = Matrix.gaussian_elimination(m1)
print("result6 =")
print(result6)

#LU 분해
m4 = Matrix([[6,5,9],[6,7,2],[1,8,9]])
Matrix.is_square(m4)
result7 = Matrix.lu_decomposition(m4)
lower, upper = result7
print("lower = ")
print(lower)
print("upper = ")
print(upper)

#복사 생성자
m5 = Matrix(m1)
print("Matrix m5 (m1을 복사) =")
print(m5)

Matrix.check_equal(m1, m5)

m5.components[0][0] = 999.0
print("m5 수정 후 =")
print(m5)
print("m1 =")
print(m1)
