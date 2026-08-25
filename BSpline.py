import math
import matplotlib.pyplot as plt
from Matrix import Matrix
from Vector import Vector

class de_boor:
    def __init__(self,input_data:dict): #딕셔너리로 input_data받기
        if not isinstance(input_data, dict):
            raise TypeError("input_data는 dict")

        self.input_data = input_data
        self.degree = input_data["Degree"]
        self.parameter = input_data["parameter"]
        self.knots = list(input_data["knots"])

        # knots의 개수 확인
        # len(knots) = control point 개수 + Degree - 1 이므로 역산해서 cp 개수를 구함
        self.control_point_count = len(self.knots) - self.degree + 1

        # control points 동적 할당
        self.control_points = []
        for i in range(self.control_point_count):
            key = "cp" + str(i)
            self.control_points.append(input_data[key])

        # 곡선이 정의되는 구간 (양 끝 Degree개의 knot는 중복 구간이라 제외)
        self.domain_start = self.knots[self.degree - 1]
        self.domain_end = self.knots[len(self.knots) - self.degree]

    # ① Greville abscissae
    # knot를 Degree개씩 묶어서 평균낸 값이 Greville abscissae가 됨
    def greville(self):
        # ζ_i = (u_i + u_{i+1} + ... + u_{i+Degree-1}) / Degree
        self.greville_X = []

        for i in range(self.control_point_count):
            knot_group = self.knots[i:i + self.degree]

            total = 0
            for knot in knot_group:
                total += knot

            self.greville_X.append(total / self.degree)

        return self.greville_X

    # ② Knot insertion
    # knot 하나를 끼워 넣어도 곡선 모양은 그대로이고, control point만 하나 늘어남
    def insert_knot(self, new_knot):
        multiplicity = self.knots.count(new_knot)

        # new_knot이 들어갈 구간 찾기: u[span] <= new_knot < u[span+1]
        span = 0
        for j in range(len(self.knots) - 1):
            if self.knots[j] <= new_knot < self.knots[j + 1]:
                span = j

        new_control_points = []

        for i in range(self.control_point_count + 1):
            if i <= span + 1 - self.degree:
                # 앞쪽: 그대로 유지
                new_control_points.append(self.control_points[i])

            elif i <= span + 1 - multiplicity:
                # 가운데: alpha = (û - u_{i-1}) / (u_{i+Degree-1} - u_{i-1})
                lower_knot = self.knots[i - 1]
                upper_knot = self.knots[i + self.degree - 1]

                alpha = (new_knot - lower_knot) / (upper_knot - lower_knot)

                previous_point = self.control_points[i - 1]
                current_point = self.control_points[i]

                new_control_points.append((1 - alpha) * previous_point + alpha * current_point)

            else:
                # 뒤쪽: 인덱스만 하나 밀림
                new_control_points.append(self.control_points[i - 1])

        self.knots.insert(span + 1, new_knot)

        self.control_points = new_control_points
        self.control_point_count = self.control_point_count + 1

        self.domain_start = self.knots[self.degree - 1]
        self.domain_end = self.knots[len(self.knots) - self.degree]

        return self.control_points

    # ③ de Boor algorithm - Evaluation
    # u에서의 knot 중복도를 확인해서, Degree가 될 때까지만 insert_knot을 반복
    def evaluate(self, u):
        # 원본 knots/control_points를 건드리지 않도록 얕은 복제본에서 계산
        clone = de_boor.__new__(de_boor)
        clone.degree = self.degree
        clone.knots = list(self.knots)
        clone.control_points = list(self.control_points)
        clone.control_point_count = self.control_point_count

        multiplicity = clone.knots.count(u)

        for _ in range(self.degree - multiplicity):
            clone.insert_knot(u)

        index = clone.knots.index(u)

        return clone.control_points[index]

    # parameter 개수만큼 domain을 등분해서 각 u에 대해 evaluate()를 반복 -> POC(Point On Curve) 목록
    def compute_curve_points(self):
        self.POC = []

        step = (self.domain_end - self.domain_start) / self.parameter

        for k in range(self.parameter + 1):
            u = self.domain_start + k * step

            self.POC.append(self.evaluate(u))

        return self.POC

    # control polygon과 POC를 그래프로 표시
    def visualize(self):
        if not hasattr(self, "POC"):
            raise RuntimeError("compute_curve_points()를 먼저 호출해야 합니다.")

        abscissae = self.greville()

        if isinstance(self.control_points[0], Vector):
            cp_x = [cp.components[0] for cp in self.control_points]
            cp_y = [cp.components[1] for cp in self.control_points]

            poc_x = [point.components[0] for point in self.POC]
            poc_y = [point.components[1] for point in self.POC]
        else:
            # control point가 scalar일 때는 Greville abscissae를 가로축으로 사용
            cp_x = abscissae
            cp_y = self.control_points

            step = (self.domain_end - self.domain_start) / self.parameter
            poc_x = [self.domain_start + k * step for k in range(self.parameter + 1)]
            poc_y = self.POC

        plt.plot(
            cp_x, cp_y,
            linestyle='-', color='black',
            marker='o', markersize=8,
            markerfacecolor='white', markeredgecolor='black',
            label='Control Polygon',
        )
        plt.plot(
            poc_x, poc_y,
            linestyle='-', color='blue',
            marker='o', markersize=4,
            label='B-Spline Curve',
        )

        plt.title("B-Spline Curve (Degree " + str(self.degree) + ")")
        plt.legend()
        plt.show()

class Interpolation:
    def __init__(self,input_data:dict): #딕셔너리로 input_data받기

        if not isinstance(input_data, dict):
            raise TypeError("input_data는 dict")

        self.input_data = input_data
        self.degree = input_data["Degree"]
        self.parameter = input_data["parameter"]

        # poc 동적할당
        self.poc = []
        i = 0
        while ("poc" + str(i)) in input_data:
            self.poc.append(input_data["poc" + str(i)])
            i += 1

        self.poc_count = len(self.poc)

    # Chordlength
    def Chordlength(self):
        # l[i-1]
        self.l = []

        for i in range(1, self.poc_count):
            segment_length = (self.poc[i] - self.poc[i - 1]).magnitude()
            self.l.append(segment_length)

        # u[i] = u[i-1] + l[i-1]
        self.u = [0.0]

        for i in range(1, self.poc_count):
            self.u.append(self.u[i - 1] + self.l[i - 1])

        return self.u

    # Knot 생성
    def KnotVector(self):
        self.knots = []

        # 앞쪽: 시작값을 Degree개 중복 (곡선이 첫 POC에서 시작하도록)
        for _ in range(self.degree):
            self.knots.append(self.u[0])

        # 내부 knot: 연속한 u를 Degree개씩 평균 (de Boor averaging)
        for j in range(1, self.poc_count - self.degree):
            knot_group = self.u[j:j + self.degree]

            total = 0
            for value in knot_group:
                total += value

            self.knots.append(total / self.degree)

        # 뒤쪽: 끝값을 Degree개 중복 (곡선이 마지막 POC에서 끝나도록)
        for _ in range(self.degree):
            self.knots.append(self.u[-1])

        return self.knots

    # basis function
    def basis_function(self, index, u):
        unit_input = {
            "Degree": self.degree,
            "parameter": self.parameter,
            "knots": list(self.knots),
        }

        for i in range(self.poc_count):
            if i == index:
                unit_input["cp" + str(i)] = 1.0
            else:
                unit_input["cp" + str(i)] = 0.0

        return de_boor(unit_input).evaluate(u)

    # Calculate
    def Calculate(self):
        # 4-1. BSplineMatrix: Matrix[i][j] = N_j(u_i)
        basis_components = []

        for i in range(self.poc_count):
            u_i = self.u[i]
            row = []

            for j in range(self.poc_count):
                row.append(self.basis_function(j, u_i)) # Basis Function

            basis_components.append(row)

        self.basis_matrix = Matrix(basis_components)

        # 4-2. GaussElimination: Basis 행렬의 역행렬 계산 (Matrix.inverse가 Gauss-Jordan으로 구현)
        self.inverse_matrix = self.basis_matrix.inverse()

        # 4-3. MatrixMul: CP = BasisMatrix^-1 * POC
        poc_components = [list(point.components) for point in self.poc]
        poc_matrix = Matrix(poc_components)

        cp_matrix = self.inverse_matrix * poc_matrix

        self.control_points = [Vector(*row) for row in cp_matrix.components]

        # 4-4. de Boor: 계산된 control point로 곡선 위의 점들 계산
        curve_input = {
            "Degree": self.degree,
            "parameter": self.parameter,
            "knots": list(self.knots),
        }

        for i in range(self.poc_count):
            curve_input["cp" + str(i)] = self.control_points[i]

        self.curve_solver = de_boor(curve_input)
        self.curve = self.curve_solver.compute_curve_points()

        return self.curve

    # ⑤ Visualization
    def Visualization(self):
        cp_x = [cp.components[0] for cp in self.control_points]
        cp_y = [cp.components[1] for cp in self.control_points]

        # 첫/마지막 CP는 POC 시작·끝점과 같은 위치라 곡선 마커와 겹치므로 흰 점 표시에서는 제외
        middle_control_points = self.control_points[1:-1]

        middle_cp_x = [cp.components[0] for cp in middle_control_points]
        middle_cp_y = [cp.components[1] for cp in middle_control_points]

        poc_x = [point.components[0] for point in self.curve]
        poc_y = [point.components[1] for point in self.curve]

        plt.plot(
            cp_x, cp_y,
            linestyle='-', color='black',
            label='Control Polygon',
        )
        plt.plot(
            middle_cp_x, middle_cp_y,
            linestyle='None',
            marker='o', markersize=8,
            markerfacecolor='white', markeredgecolor='black',
            label='Control Points',
        )
        plt.plot(
            poc_x, poc_y,
            linestyle='-', color='blue',
            marker='o', markersize=4,
            label='B-Spline Curve',
        )

        plt.title("B-Spline Interpolation (Degree " + str(self.degree) + ")")
        plt.axis('equal')
        plt.legend()
        plt.show()
