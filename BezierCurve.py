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
        """
        if not isinstance(input_data, dict):
            raise TypeError("input_data는 dict")

        self.input_data = input_data

    def normalize(self):
        cp0 = self.input_data["cp0"]
        cp1 = self.input_data["cp1"]
        cp2 = self.input_data["cp2"]
        cp3 = self.input_data["cp3"]

        normalized_vectors, self.max_vector, self.min_vector, self.variation = cp0.normalization(cp1, cp2, cp3)
        normalized_cp0, normalized_cp1, normalized_cp2, normalized_cp3 = normalized_vectors

        self.normalized_data = {
            "cp0": normalized_cp0,
            "cp1": normalized_cp1,
            "cp2": normalized_cp2,
            "cp3": normalized_cp3,
        }

        return self.normalized_data

    def calculate(self):
        parameter = self.input_data["parameter"]

        self.normalized_curve = []

        for k in range(parameter + 1):
            t = k / parameter

            # De Casteljau 삼각형 축소: 레벨마다 인접한 두 점을 t로 보간해 점 개수를 하나씩 줄여나감
            points = [
                self.normalized_data["cp0"],
                self.normalized_data["cp1"],
                self.normalized_data["cp2"],
                self.normalized_data["cp3"],
            ]

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
        cp_points = [
            self.input_data["cp0"],
            self.input_data["cp1"],
            self.input_data["cp2"],
            self.input_data["cp3"],
        ]

        cp_x = [cp.components[0] for cp in cp_points]
        cp_y = [cp.components[1] for cp in cp_points]

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

        plt.axis('equal')
        plt.legend()
        plt.show()
