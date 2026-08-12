class Matrix:
    # 행렬 정의
    def __init__(self, rows, columns=None):
        self.components = []

        # 복사 생성자
        if isinstance(rows, Matrix):
            for row in rows.components:
                self.components.append(row.copy())

        # 행과 열 개수로 영행렬 생성
        elif isinstance(rows, int) and isinstance(columns, int):
            if rows <= 0 or columns <= 0:
                raise ValueError("행과 열은 1 이상이어야 합니다.")

            for i in range(rows):
                new_row = []

                for j in range(columns):
                    new_row.append(0.0)

                self.components.append(new_row)

        # 리스트로 행렬 생성
        elif isinstance(rows, list) and columns is None:
            if len(rows) == 0 or len(rows[0]) == 0:
                raise ValueError("행렬에는 최소 하나의 값이 필요합니다.")

            column_count = len(rows[0])

            for row in rows:
                if len(row) != column_count:
                    raise ValueError("모든 행의 열 개수가 같아야 합니다.")

                new_row = []

                for value in row:
                    new_row.append(float(value))

                self.components.append(new_row)

        else:
            raise TypeError("행렬 데이터 또는 행과 열 개수를 입력해야 합니다.")

        self.rows = len(self.components)
        self.columns = len(self.components[0])

    # 출력 형식 정의
    def __repr__(self):
        result = ""

        for row in self.components:
            result += str(row) + "\n"

        return result.rstrip()

    # 기본 연산
    ## 덧셈
    def __add__(self, other):
        if self.rows != other.rows or self.columns != other.columns:
            raise ValueError("같은 크기의 Matrix끼리만 더할 수 있습니다.")

        result_components = []

        for i in range(self.rows):
            result_row = []

            for j in range(self.columns):
                value = (
                    self.components[i][j]
                    + other.components[i][j]
                )

                result_row.append(value)

            result_components.append(result_row)

        return Matrix(result_components)

    ## 뺄셈
    def __sub__(self, other):
        if self.rows != other.rows or self.columns != other.columns:
            raise ValueError("같은 크기의 Matrix끼리만 뺄 수 있습니다.")

        result_components = []

        for i in range(self.rows):
            result_row = []

            for j in range(self.columns):
                value = (
                    self.components[i][j]
                    - other.components[i][j]
                )

                result_row.append(value)

            result_components.append(result_row)

        return Matrix(result_components)

    ## 행렬 곱셈
    def __mul__(self, other):
        if self.columns != other.rows:
            raise ValueError(
                "첫 번째 Matrix의 열 개수와 두 번째 Matrix의 행 개수가 같아야 합니다."
            )

        result_components = []

        for i in range(self.rows):
            result_row = []

            for j in range(other.columns):
                value = 0

                for k in range(self.columns):
                    value += (
                        self.components[i][k]
                        * other.components[k][j]
                    )

                result_row.append(value)

            result_components.append(result_row)

        return Matrix(result_components)

    ## 나눗셈
    def __truediv__(self, other):
        if self.rows != other.rows or self.columns != other.columns:
            raise ValueError("같은 크기의 Matrix끼리만 나눌 수 있습니다.")

        result_components = []

        for i in range(self.rows):
            result_row = []

            for j in range(self.columns):
                if other.components[i][j] == 0:
                    raise ZeroDivisionError("0으로 나눌 수 없습니다.")

                value = (
                    self.components[i][j]
                    / other.components[i][j]
                )

                result_row.append(value)

            result_components.append(result_row)

        return Matrix(result_components)

    # 같은지 체크
    def check_equal(self, other):
        if self.rows != other.rows or self.columns != other.columns:
            return False

        for i in range(self.rows):
            for j in range(self.columns):
                if self.components[i][j] != other.components[i][j]:
                    return print("불일치")

        return print("일치")

    # 함수
    ## Transpose
    def transpose(self):
        result_components = []

        for j in range(self.columns):
            result_row = []

            for i in range(self.rows):
                result_row.append(self.components[i][j])

            result_components.append(result_row)

        return Matrix(result_components)

    ## 정방행렬인지 체크
    def is_square(self):
        if self.rows == self.columns:
            return print("정방행렬입니다.")
        else:
            return print("정방행렬이 아닙니다")

    ## 단위 행렬 생성
    @classmethod
    def identity(cls, size):
        if size <= 0:
            raise ValueError("단위 행렬의 크기는 1 이상이어야 합니다.")

        result_components = []

        for i in range(size):
            result_row = []

            for j in range(size):
                if i == j:
                    result_row.append(1.0)
                else:
                    result_row.append(0.0)

            result_components.append(result_row)

        return cls(result_components)

    ## Gaussian Elimination
    def gaussian_elimination(self):
        result = Matrix(self)  # 원본은 보존하고 복사본에서 계산
        pivot_row = 0

        for pivot_col in range(result.columns):
            if pivot_row >= result.rows:
                break

            # 부분 피벗팅
            max_row = pivot_row

            for i in range(pivot_row + 1, result.rows):
                if abs(result.components[i][pivot_col]) > abs(result.components[max_row][pivot_col]):
                    max_row = i

            if abs(result.components[max_row][pivot_col]) < 1e-10:
                continue

            result.components[pivot_row], result.components[max_row] = (
                result.components[max_row],
                result.components[pivot_row],
            )

            pivot_value = result.components[pivot_row][pivot_col]

            for i in range(pivot_row + 1, result.rows):
                factor = result.components[i][pivot_col] / pivot_value

                for j in range(pivot_col, result.columns):
                    result.components[i][j] -= factor * result.components[pivot_row][j]

            pivot_row += 1

        return result

    ## rank
    def rank(self):
        echelon = self.gaussian_elimination()
        count = 0

        for row in echelon.components:
            if any(abs(value) > 1e-10 for value in row):
                count += 1

        return count

    ## LU 분해
    def lu_decomposition(self):
        if self.rows != self.columns:
            raise ValueError("정방행렬만 LU 분해가 가능합니다.")

        n = self.rows
        lower = Matrix(n, n)
        upper = Matrix(n, n)

        for i in range(n):
            lower.components[i][i] = 1.0

            for j in range(i, n):
                value = self.components[i][j]

                for k in range(i):
                    value -= lower.components[i][k] * upper.components[k][j]

                upper.components[i][j] = value

            if abs(upper.components[i][i]) < 1e-10:
                raise ValueError("피벗이 0이라 피벗팅 없이는 LU 분해가 불가능합니다.")

            for j in range(i + 1, n):
                value = self.components[j][i]

                for k in range(i):
                    value -= lower.components[j][k] * upper.components[k][i]

                lower.components[j][i] = value / upper.components[i][i]

        return lower, upper