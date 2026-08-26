"""
# 데이터 입력 방식
input_data = {
    "커브 종류" : "BezierCurve",
    "커브 생성 방식" : "BuildCurve",
    "cp0": Vector.xyz(0, 200, 0),
    "cp1": Vector.xyz(200, 300, 0),
    "cp2": Vector.xyz(0, 150, 0),
    "cp3": Vector.xyz(0, 150, 0),
    "parameter": 20,
    "Degree": 3,
    }

input_data = {
    "커브 종류" : "Bspline",
    "커브 생성 방식" : "BuildCurve",
    "cp0": 50,
    "cp1": 175,
    "cp2": 200,
    "cp3": 150,
    "cp4": 25,
    "parameter": 200,
    "Degree": 3,
    "knots" : [50,50,50,200,350,350,350],
}
"""
class Inputdata:
    def __init__(self, input_data:dict):
        if not isinstance(input_data,dict):
            raise TypeError("Input Data가 Dictionary 형태가 아닙니다.")

        self.kind_of_curve = input_data["커브 종류"]
        self.kind_of_struct_curve = input_data["커브 생성 방식"]
        self.input_data = input_data
        self.degree = input_data["Degree"]
        self.parameter = input_data["parameter"]

        # 커브 생성 방식이 BuildCurve인 경우와 Interpolation인 경우를 나눠서 데이터 처리
        if self.kind_of_struct_curve == "BuildCurve": # CP를 가지고 Curve 생성
            # 커브 종류가 Bspline인 경우: knots를 직접 입력받아 control point 개수를 역산
            # (Interpolation은 knots를 입력받지 않고 알고리즘 내부에서 직접 만들어내므로 여기서 요구하지 않음)
            if self.kind_of_curve == "Bspline":
                self.knots = list(input_data["knots"])
                self.control_point_count = len(self.knots) - self.degree + 1
                self.domain_start = self.knots[self.degree - 1]
                self.domain_end = self.knots[len(self.knots) - self.degree]
            else:
                # Bezier는 knots가 없어서 control point 개수가 Degree + 1로 고정됨
                self.control_point_count = self.degree + 1

            self.control_points = []
            for i in range(self.control_point_count):
                        key = "cp" + str(i)
                        self.control_points.append(input_data[key])
        else: # Interpolation
            self.poc = []
            i = 0
            while ("poc" + str(i)) in input_data:
                self.poc.append(input_data["poc" + str(i)])
                i += 1
            self.poc_count = len(self.poc)