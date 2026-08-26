from InputData import Inputdata
from Bezier import BuildCurve as BezierBuildCurve, Interpolation as BezierInterpolation
from Bspline import BuildCurve as BsplineBuildCurve, Interpolation as BsplineInterpolation
from Visualize import Visualize
from Vector import Vector


def test_bezier_build_curve():
    input_data = {
        "커브 종류": "BezierCurve",
        "커브 생성 방식": "BuildCurve",
        "cp0": Vector.xyz(100, 100, 0),
        "cp1": Vector.xyz(150, 250, 0),
        "cp2": Vector.xyz(200, 300, 0),
        "cp3": Vector.xyz(250, 400, 0),
        "parameter": 5,
        "Degree": 3,
    }

    data = Inputdata(input_data)
    curve = BezierBuildCurve(data.degree, data.parameter, data.control_points)

    curve.normalize()
    curve.DeCasteljau()
    curve.denormalize()

    print("[Bezier BuildCurve] control_points =", curve.control_points)
    print("[Bezier BuildCurve] curve =", curve.curve)

    Visualize(curve.control_points, curve.curve, curve.degree)


def test_bezier_interpolation():
    input_data = {
        "커브 종류": "BezierCurve",
        "커브 생성 방식": "Interpolation",
        "poc0": Vector.xyz(100, 100, 0),
        "poc1": Vector.xyz(200, 300, 0),
        "poc2": Vector.xyz(300, 350, 0),
        "poc3": Vector.xyz(500, 100, 0),
        "parameter": 100,
        "Degree": 3,
    }

    data = Inputdata(input_data)
    curve = BezierInterpolation(data.degree, data.parameter, data.poc)

    curve.Chordlength()
    curve.Normalize()
    curve.Calculate()
    curve.Denormalize()

    print("[Bezier Interpolation] control_points =", curve.denormalized_control_points)
    print("[Bezier Interpolation] curve =", curve.curve)

    # 정규화 이전 상태인 curve.control_points가 아니라
    # Denormalize()가 만들어낸 curve.denormalized_control_points를 넘겨야 함
    Visualize(curve.denormalized_control_points, curve.curve, curve.degree)


def test_bspline_build_curve():
    input_data = {
        "커브 종류": "Bspline",
        "커브 생성 방식": "BuildCurve",
        "cp0": 50,
        "cp1": 175,
        "cp2": 200,
        "cp3": 150,
        "cp4": 25,
        "parameter": 200,
        "Degree": 3,
        "knots": [50, 50, 50, 200, 350, 350, 350],
    }

    data = Inputdata(input_data)
    curve = BsplineBuildCurve(
        data.degree, data.parameter, data.knots,
        data.control_point_count, data.control_points,
        data.domain_start, data.domain_end,
    )

    curve.Compute_curve_points()

    print("[BSpline BuildCurve] control_points =", curve.control_points)
    print("[BSpline BuildCurve] POC =", curve.POC)

    # 이 시나리오는 control point가 스칼라(숫자)라서 Visualize(components 접근)와는
    # 맞지 않음 -> 원본 de_boor.visualize()도 이 경우를 따로 분기해서 처리했음.
    # Visualize.py는 아직 그 분기가 없으므로 여기서는 호출하지 않음.


def test_bspline_interpolation():
    input_data = {
        "커브 종류": "Bspline",
        "커브 생성 방식": "Interpolation",
        "poc0": Vector.xyz(200, 300, 0),
        "poc1": Vector.xyz(300, 400, 0),
        "poc2": Vector.xyz(400, 200, 0),
        "poc3": Vector.xyz(500, 300, 0),
        "parameter": 100,
        "Degree": 3,
    }

    data = Inputdata(input_data)
    curve = BsplineInterpolation(data.degree, data.parameter, data.poc, data.poc_count)

    curve.Chordlength()
    curve.KnotVector()
    curve.Calculate()

    print("[BSpline Interpolation] control_points =", curve.control_points)
    print("[BSpline Interpolation] curve =", curve.curve)

    Visualize(curve.control_points, curve.curve, curve.degree)


if __name__ == "__main__":
    test_bezier_build_curve()
    test_bezier_interpolation()
    test_bspline_build_curve()
    test_bspline_interpolation()
