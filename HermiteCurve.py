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
        # Dictionary에 있는 input_data를 각 용소로 옮기기
        # 리스트 형태로 저장
        P0 = self.input_data["P0"]
        P1 = self.input_data["P1"]
        T0 = self.input_data["T0"]
        T1 = self.input_data["T1"]

        rows = []

        # 현재는 열의 개수가 정해져있기때문에 range = 3으로 표기 되었지만 수정되어야함
        for axis_index in range(3):
            rows.append([
                P0.components[axis_index],
                P1.components[axis_index],
                T0.components[axis_index],
                T1.components[axis_index],
            ])

        self.matrix = Matrix(rows)

        return self.matrix

