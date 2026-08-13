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
