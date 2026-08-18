import math
import matplotlib.pyplot as plt
from Matrix import Matrix
from Vector import Vector

class DeCasteljau:
    def __init__(self,input_data:dict): #딕셔너리로 input_data받기
        """
        # 데이터 입력 방식
        input_data = {
            "cp0": Vector.xyz(0, 200, 0),
            "cp1": Vector.xyz(200, 300, 0),
            "cp2": Vector.xyz(0, 150, 0),
            "cp3": Vector.xyz(0, 150, 0),
            "parameter": 20,
            "Degree": 3,
        }
        # Degree가 n이면 컨트롤 포인트는 cp0 ~ cpn 으로 n+1개가 필요함
        """
        if not isinstance(input_data, dict):
            raise TypeError("input_data는 dict")

        self.input_data = input_data

        self.degree = input_data["Degree"]
        self.parameter = input_data["parameter"]

        # Degree에 맞춰 cp0 ~ cp{Degree} 를 순서대로 모으기
        self.control_points = []

        for i in range(self.degree + 1):
            key = "cp" + str(i)
            self.control_points.append(input_data[key])

    def normalize(self):
        cp0 = self.control_points[0]
        others = self.control_points[1:]

        normalized_points, self.max_vector, self.min_vector, self.variation = cp0.normalization(*others)

        self.normalized_points = normalized_points

        self.normalized_data = {}

        for i, normalized_point in enumerate(normalized_points):
            self.normalized_data["cp" + str(i)] = normalized_point

        return self.normalized_data

    def calculate(self):
        self.normalized_curve = []

        for k in range(self.parameter + 1):
            t = k / self.parameter

            # De Casteljau 삼각형 축소: 레벨마다 인접한 두 점을 t로 보간해 점 개수를 하나씩 줄여나감
            points = self.normalized_points

            while len(points) > 1:
                next_points = []

                for i in range(len(points) - 1):
                    p0 = points[i]
                    p1 = points[i + 1]

                    new_point = (1 - t) * p0 + t * p1

                    next_points.append(new_point)

                points = next_points

            self.normalized_curve.append(points[0])

        return self.normalized_curve

    def denormalize(self):
        self.curve = []

        for normalized_point in self.normalized_curve:
            denormalized_point = normalized_point * self.variation + self.min_vector
            self.curve.append(denormalized_point)

        return self.curve

    def visualize(self):
        cp_x = [cp.components[0] for cp in self.control_points]
        cp_y = [cp.components[1] for cp in self.control_points]

        poc_x = [point.components[0] for point in self.curve]
        poc_y = [point.components[1] for point in self.curve]

        plt.plot(
            cp_x, cp_y,
            linestyle='-', color='black',
            marker='o', markersize=8,
            markerfacecolor='white', markeredgecolor='black',
            label='Control Points',
        )
        plt.plot(
            poc_x, poc_y,
            linestyle='-', color='blue',
            marker='o', markersize=4,
            label='Bezier Curve',
        )

        plt.title("Bezier Curve (Degree " + str(self.degree) + ")")
        plt.axis('equal')
        plt.legend()
        plt.show()

class Interploation:
    def __init__(self,input_data:dict):
        if not isinstance(input_data, dict):
            raise TypeError("input_data는 dict")

        self.input_data = input_data
        self.degree = input_data["Degree"]
        self.parameter = input_data["parameter"]

        self.poc = []
        for i in range(self.degree + 1):
            key = "poc" + str(i)
            self.poc.append(input_data[key])

    def Chordlength(self):
        # l[i-1] = POC[i]와 POC[i-1] 사이의 직선 거리
        self.l = []

        for i in range(1, len(self.poc)):
            segment_length = (self.poc[i] - self.poc[i - 1]).magnitude()
            self.l.append(segment_length)

        # u[0] = 0, u[i] = u[i-1] + l[i-1] 누적합
        self.u = [0]

        for i in range(1, len(self.poc)):
            self.u.append(self.u[i - 1] + self.l[i - 1])

        return self.u

    def Normalize(self):
        # POC 좌표 정규화 (DeCasteljau.normalize()와 동일한 방식)
        poc0 = self.poc[0]
        others = self.poc[1:]

        self.normalized_poc, self.max_vector, self.min_vector, self.variation = poc0.normalization(*others)

        # u(chord length 누적값) 정규화: u[0]=0이 최솟값이라 u[-1](총 길이)로 나누는 것과 동일
        self.normalized_u = []

        u_min = self.u[0]
        u_max = self.u[-1]
        u_range = u_max - u_min

        for value in self.u:
            if u_range == 0:
                self.normalized_u.append(0)
            else:
                self.normalized_u.append((value - u_min) / u_range)

        return self.normalized_poc, self.normalized_u

    def Calculate(self):
        # 4-1. BernsteinMatrix: Matrix[i][j] = nCr(Degree,j) * (1-u_i)^(Degree-j) * (u_i)^j
        bernstein_components = []

        for i in range(self.degree + 1):
            u_i = self.normalized_u[i]
            row = []

            for j in range(self.degree + 1):
                n_c_r = math.comb(self.degree, j) #nCr 조합 연산
                basis = n_c_r * ((1 - u_i) ** (self.degree - j)) * (u_i ** j) # Basis Function
                row.append(basis)

            bernstein_components.append(row)

        self.bernstein_matrix = Matrix(bernstein_components)

        # 4-2. GaussElimination: Bernstein 행렬의 역행렬 계산 (Matrix.inverse가 Gauss-Jordan으로 구현)
        self.inverse_matrix = self.bernstein_matrix.inverse()

        # 4-3. MatrixMul: CP = BernsteinMatrix^-1 * POC
        poc_components = [list(point.components) for point in self.normalized_poc]
        poc_matrix = Matrix(poc_components)

        cp_matrix = self.inverse_matrix * poc_matrix

        self.control_points = [Vector(*row) for row in cp_matrix.components]

        # 4-4. DeCasteljau: 계산된 컨트롤 포인트로 곡선 위의 점들 계산
        self.normalized_curve = []

        for k in range(self.parameter + 1):
            t = k / self.parameter

            points = self.control_points

            while len(points) > 1:
                next_points = []

                for i in range(len(points) - 1):
                    p0 = points[i]
                    p1 = points[i + 1]

                    new_point = (1 - t) * p0 + t * p1

                    next_points.append(new_point)

                points = next_points

            self.normalized_curve.append(points[0])

        return self.normalized_curve

    def Denormalize(self):
        self.curve = []

        for normalized_point in self.normalized_curve:
            denormalized_point = normalized_point * self.variation + self.min_vector
            self.curve.append(denormalized_point)

        # Calculate()에서 구한 컨트롤 포인트도 정규화된 공간의 값이라 같이 되돌려야 함
        self.denormalized_control_points = []

        for normalized_cp in self.control_points:
            denormalized_cp = normalized_cp * self.variation + self.min_vector
            self.denormalized_control_points.append(denormalized_cp)

        return self.curve

    def Visualization(self):
        cp_x = [cp.components[0] for cp in self.denormalized_control_points]
        cp_y = [cp.components[1] for cp in self.denormalized_control_points]

        # 첫/마지막 CP는 POC 시작·끝점과 같은 위치라 곡선 마커와 겹치므로 흰 점 표시에서는 제외
        middle_control_points = self.denormalized_control_points[1:-1]

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
            label='Bezier Curve',
        )

        plt.title("Interpolation (Degree " + str(self.degree) + ")")
        plt.axis('equal')
        plt.legend()
        plt.show()
