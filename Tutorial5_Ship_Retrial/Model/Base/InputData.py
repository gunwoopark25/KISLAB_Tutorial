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
import math

from Vector import Vector


class InputDataConverter:
    MAX_PARAMETER = 5000
    MAX_POINT_COUNT = 100
    MAX_ABS_VALUE = 1e100

    def __init__(
        self,
        curve_type,
        build_method,
        degree,
        parameter,
        point_rows,
        knots="",
    ):
        self.curve_type = curve_type
        self.build_method = build_method
        self.degree = degree
        self.parameter = parameter
        self.point_rows = point_rows
        self.knots = knots

    def to_dict(self):
        if self.curve_type not in ("BezierCurve", "Bspline"):
            raise ValueError("지원하지 않는 커브 종류입니다.")
        if self.build_method not in ("BuildCurve", "Interpolation"):
            raise ValueError("지원하지 않는 커브 생성 방식입니다.")

        degree = self._positive_integer(self.degree, "Degree")
        parameter = self._positive_integer(self.parameter, "Parameter")
        if parameter > self.MAX_PARAMETER:
            raise ValueError(
                f"Parameter는 {self.MAX_PARAMETER} 이하여야 합니다."
            )

        if not self.point_rows:
            raise ValueError("CP 또는 POC를 한 개 이상 입력해야 합니다.")
        if len(self.point_rows) > self.MAX_POINT_COUNT:
            raise ValueError(
                f"CP 또는 POC는 {self.MAX_POINT_COUNT}개 이하로 입력해야 합니다."
            )

        prefix = "cp" if self.build_method == "BuildCurve" else "poc"
        input_data = {
            "커브 종류": self.curve_type,
            "커브 생성 방식": self.build_method,
            "Degree": degree,
            "parameter": parameter,
        }

        y_only_bspline_build = (
            self.curve_type == "Bspline"
            and self.build_method == "BuildCurve"
        )

        for index, row in enumerate(self.point_rows):
            if len(row) != 3:
                raise ValueError("각 점에는 X, Y, Z 좌표가 필요합니다.")
            try:
                if y_only_bspline_build:
                    coordinate_values = (float(row[1].strip()),)
                    point = coordinate_values[0]
                else:
                    coordinate_values = tuple(
                        float(value.strip()) for value in row
                    )
                    point = Vector.xyz(*coordinate_values)
            except (AttributeError, TypeError, ValueError) as error:
                raise ValueError(
                    f"{prefix}{index}의 좌표를 숫자로 입력해야 합니다."
                ) from error
            if not all(math.isfinite(value) for value in coordinate_values):
                raise ValueError(
                    f"{prefix}{index}의 좌표는 유한한 숫자여야 합니다."
                )
            if any(
                abs(value) > self.MAX_ABS_VALUE
                for value in coordinate_values
            ):
                raise ValueError(
                    f"{prefix}{index}의 좌표가 허용 범위를 초과했습니다."
                )
            input_data[f"{prefix}{index}"] = point

        if self.curve_type == "BezierCurve":
            expected_count = degree + 1
            if len(self.point_rows) != expected_count:
                raise ValueError(
                    f"Bezier는 Degree {degree}일 때 점이 {expected_count}개 필요합니다."
                )

        elif self.build_method == "BuildCurve":
            knots = self._parse_knots(self.knots)
            expected_count = len(knots) - degree + 1
            if expected_count <= 0 or len(self.point_rows) != expected_count:
                raise ValueError(
                    "B-Spline의 CP 개수는 len(knots) - Degree + 1과 같아야 합니다."
                )
            if len(self.point_rows) <= degree:
                raise ValueError("B-Spline은 Degree보다 많은 CP가 필요합니다.")

            domain_start = knots[degree - 1]
            domain_end = knots[len(knots) - degree]
            if domain_start >= domain_end:
                raise ValueError(
                    "B-Spline knot domain의 시작값은 끝값보다 작아야 합니다."
                )

            if any(knots.count(knot) > degree for knot in set(knots)):
                raise ValueError(
                    "동일한 Knot의 중복 개수는 Degree를 초과할 수 없습니다."
                )
            input_data["knots"] = knots

        elif len(self.point_rows) <= degree:
            raise ValueError("B-Spline Interpolation은 Degree보다 많은 POC가 필요합니다.")

        return input_data

    @staticmethod
    def _positive_integer(value, label):
        try:
            converted = int(str(value).strip())
        except (TypeError, ValueError) as error:
            raise ValueError(f"{label}는 정수로 입력해야 합니다.") from error
        if converted <= 0:
            raise ValueError(f"{label}는 1 이상이어야 합니다.")
        return converted

    @staticmethod
    def _parse_knots(value):
        text = str(value).strip()
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        parts = text.replace(",", " ").split()
        if not parts:
            raise ValueError("B-Spline BuildCurve에는 Knots 입력이 필요합니다.")
        try:
            knots = [float(part) for part in parts]
        except ValueError as error:
            raise ValueError("Knots는 숫자 목록으로 입력해야 합니다.") from error
        if not all(math.isfinite(knot) for knot in knots):
            raise ValueError("Knots는 유한한 숫자여야 합니다.")
        if any(abs(knot) > InputDataConverter.MAX_ABS_VALUE for knot in knots):
            raise ValueError("Knots가 허용 범위를 초과했습니다.")
        if any(left > right for left, right in zip(knots, knots[1:])):
            raise ValueError("Knots는 오름차순으로 입력해야 합니다.")
        return knots


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
