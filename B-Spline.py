import math
import matplotlib.pyplot as plt
from Matrix import Matrix
from Vector import Vector

class de_boor:
    def __init__(self,input_data:dict):
        if not isinstance(input_data, dict):
            raise TypeError("input_data는 dict")

        self.input_data = input_data
        self.degree = input_data["Degree"]
        self.parameter = input_data["parameter"]

        # control points 동적 할당
        self.control_points = []
        for i in range(self.degree + 1):
            key = "cp" + str(i)
            self.control_points.append(input_data[key])

        # knots의 개수 확인
