import unittest

from model import CurveModel, InputDataConverter
from Vector import Vector


class CurveModelTests(unittest.TestCase):
    def setUp(self):
        self.model = CurveModel()

    def convert(self, curve_type, build_method, rows, knots=""):
        return InputDataConverter(
            curve_type=curve_type,
            build_method=build_method,
            degree="3",
            parameter="20",
            point_rows=rows,
            knots=knots,
        ).to_dict()

    def test_bezier_build_curve_returns_curve_result(self):
        input_data = self.convert(
            "BezierCurve",
            "BuildCurve",
            [("0", "0", "0"), ("1", "2", "0"), ("2", "2", "0"), ("3", "0", "0")],
        )

        result = self.model.calculate(input_data)

        self.assertEqual(len(result.control_points), 4)
        self.assertEqual(len(result.curve_points), 21)
        self.assertEqual(result.curve_points[0].components, [0.0, 0.0, 0.0])
        self.assertEqual(result.curve_points[-1].components, [3.0, 0.0, 0.0])

    def test_bezier_interpolation_returns_curve_result(self):
        input_data = self.convert(
            "BezierCurve",
            "Interpolation",
            [("0", "0", "0"), ("1", "2", "0"), ("2", "2", "0"), ("3", "0", "0")],
        )

        result = self.model.calculate(input_data)

        self.assertEqual(len(result.control_points), 4)
        self.assertEqual(len(result.curve_points), 21)
        self.assertEqual(result.curve_points[0].components, [0.0, 0.0, 0.0])
        self.assertEqual(result.curve_points[-1].components, [3.0, 0.0, 0.0])

    def test_bspline_build_curve_returns_visualization_metadata(self):
        input_data = self.convert(
            "Bspline",
            "BuildCurve",
            [
                ("0", "0", "0"),
                ("1", "2", "0"),
                ("2", "2", "0"),
                ("3", "1", "0"),
                ("4", "0", "0"),
            ],
            "0, 0, 0, 0.5, 1, 1, 1",
        )

        result = self.model.calculate(input_data)

        self.assertEqual(len(result.control_points), 5)
        self.assertEqual(len(result.curve_points), 21)
        self.assertEqual(len(result.visualization_options["greville"]), 5)
        self.assertEqual(result.visualization_options["parameter"], 20)

    def test_bspline_interpolation_returns_curve_result(self):
        input_data = self.convert(
            "Bspline",
            "Interpolation",
            [
                ("0", "0", "0"),
                ("1", "2", "0"),
                ("2", "2", "0"),
                ("3", "1", "0"),
                ("4", "0", "0"),
            ],
        )

        result = self.model.calculate(input_data)

        self.assertEqual(len(result.control_points), 5)
        self.assertEqual(len(result.curve_points), 21)
        self.assertEqual(result.curve_points[0].components, [0.0, 0.0, 0.0])
        self.assertEqual(result.curve_points[-1].components, [4.0, 0.0, 0.0])

    def test_non_finite_calculation_result_is_rejected(self):
        input_data = {
            "커브 종류": "BezierCurve",
            "커브 생성 방식": "BuildCurve",
            "Degree": 1,
            "parameter": 10,
            "cp0": Vector.xyz(-1e308, 0, 0),
            "cp1": Vector.xyz(1e308, 0, 0),
        }

        with self.assertRaisesRegex(ValueError, "계산 결과"):
            self.model.calculate(input_data)


if __name__ == "__main__":
    unittest.main()
