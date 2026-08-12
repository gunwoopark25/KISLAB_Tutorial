from Matrix import Matrix
from Vector import Vector

class HermiteCurve:
    def __init__(self, input_data:dict): #InputData는 Dictionary로 받음
        # input_data가 dictionary이여야 가능함
        if not isinstance(input_data, dict):
            raise TypeError("input_data는 dict")

        parameter = input_data["parameter"]

        # Parameter의 값이 1이나 2일 경우에 곡선이 형성 될 수 없음
        if not isinstance(parameter, int) or parameter < 3:
            raise ValueError("parameter는 3 이상의 정수여야 합니다.")
        
        self.input_data = input_data

    # Input Data를 가지고 Matrix 생성
    def build_geometry_matrix(self):
        P0 = self.input_data["P0"]
        P1 = self.input_data["P1"]
        T0 = self.input_data["T0"]
        T1 = self.input_data["T1"]

        rows = []

        for axis_index in range(3):
            rows.append([
                P0.components[axis_index],
                P1.components[axis_index],
                T0.components[axis_index],
                T1.components[axis_index],
            ])

        self.matrix = Matrix(rows)

        return self.matrix

    # Normalization
    def normalize_matrix(self):
        self.min_list = []
        self.max_list = []

        normalized_rows = []

        for row in self.matrix.components:
            row_min = min(row)
            row_max = max(row)
            variation = row_max - row_min

            self.min_list.append(row_min)
            self.max_list.append(row_max)

            normalized_row = []

            for value in row:
                if variation == 0:
                    normalized_row.append(0.0)
                else:
                    normalized_row.append((value - row_min) / variation)

            normalized_rows.append(normalized_row)

        self.normalized_matrix = Matrix(normalized_rows)

        return self.normalized_matrix