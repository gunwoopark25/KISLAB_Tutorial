import unittest

from model import InputDataConverter


class InputDataConverterTests(unittest.TestCase):
    def test_bezier_build_strings_are_converted_to_typed_dictionary(self):
        converter = InputDataConverter(
            curve_type="BezierCurve",
            build_method="BuildCurve",
            degree="3",
            parameter="20",
            point_rows=[
                ("0", "0", "0"),
                ("1", "2", "0"),
                ("2", "2", "0"),
                ("3", "0", "0"),
            ],
        )

        input_data = converter.to_dict()

        self.assertEqual(input_data["커브 종류"], "BezierCurve")
        self.assertEqual(input_data["커브 생성 방식"], "BuildCurve")
        self.assertEqual(input_data["Degree"], 3)
        self.assertEqual(input_data["parameter"], 20)
        self.assertEqual(input_data["cp0"].components, [0.0, 0.0, 0.0])
        self.assertEqual(input_data["cp3"].components, [3.0, 0.0, 0.0])

    def test_interpolation_rows_use_poc_keys(self):
        converter = InputDataConverter(
            curve_type="BezierCurve",
            build_method="Interpolation",
            degree="1",
            parameter="10",
            point_rows=[("0", "0", "0"), ("1", "1", "0")],
        )

        input_data = converter.to_dict()

        self.assertIn("poc0", input_data)
        self.assertIn("poc1", input_data)
        self.assertNotIn("cp0", input_data)

    def test_bspline_build_knots_accept_brackets_and_commas(self):
        converter = InputDataConverter(
            curve_type="Bspline",
            build_method="BuildCurve",
            degree="3",
            parameter="20",
            point_rows=[
                ("0", "0", "0"),
                ("1", "2", "0"),
                ("2", "2", "0"),
                ("3", "1", "0"),
                ("4", "0", "0"),
            ],
            knots="[0, 0, 0, 0.5, 1, 1, 1]",
        )

        input_data = converter.to_dict()

        self.assertEqual(input_data["knots"], [0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0])

    def test_bspline_build_uses_only_y_as_scalar_control_points(self):
        converter = InputDataConverter(
            curve_type="Bspline",
            build_method="BuildCurve",
            degree="3",
            parameter="20",
            point_rows=[
                ("ignored", "10", "ignored"),
                ("ignored", "20", "ignored"),
                ("ignored", "30", "ignored"),
                ("ignored", "40", "ignored"),
                ("ignored", "50", "ignored"),
            ],
            knots="0,0,0,0.5,1,1,1",
        )

        input_data = converter.to_dict()

        self.assertEqual(input_data["cp0"], 10.0)
        self.assertEqual(input_data["cp4"], 50.0)

    def test_non_numeric_coordinate_is_rejected(self):
        converter = InputDataConverter(
            curve_type="BezierCurve",
            build_method="BuildCurve",
            degree="1",
            parameter="10",
            point_rows=[("x", "0", "0"), ("1", "1", "0")],
        )

        with self.assertRaisesRegex(ValueError, "좌표"):
            converter.to_dict()

    def test_non_finite_coordinate_is_rejected(self):
        converter = InputDataConverter(
            curve_type="BezierCurve",
            build_method="BuildCurve",
            degree="1",
            parameter="10",
            point_rows=[("nan", "0", "0"), ("1", "1", "0")],
        )

        with self.assertRaisesRegex(ValueError, "유한"):
            converter.to_dict()

    def test_extreme_coordinate_magnitude_is_rejected(self):
        converter = InputDataConverter(
            curve_type="BezierCurve",
            build_method="BuildCurve",
            degree="1",
            parameter="10",
            point_rows=[("1e200", "0", "0"), ("1", "1", "0")],
        )

        with self.assertRaisesRegex(ValueError, "범위"):
            converter.to_dict()

    def test_non_finite_knot_is_rejected(self):
        converter = InputDataConverter(
            curve_type="Bspline",
            build_method="BuildCurve",
            degree="3",
            parameter="10",
            point_rows=[
                ("0", "0", "0"),
                ("1", "1", "0"),
                ("2", "1", "0"),
                ("3", "1", "0"),
                ("4", "0", "0"),
            ],
            knots="0, 0, 0, 1, inf, inf, inf",
        )

        with self.assertRaisesRegex(ValueError, "유한"):
            converter.to_dict()

    def test_bspline_requires_more_control_points_than_degree(self):
        converter = InputDataConverter(
            curve_type="Bspline",
            build_method="BuildCurve",
            degree="3",
            parameter="10",
            point_rows=[("0", "0", "0"), ("1", "1", "0")],
            knots="0, 0, 1, 1",
        )

        with self.assertRaisesRegex(ValueError, "Degree보다 많은 CP"):
            converter.to_dict()

    def test_bspline_requires_nonzero_parameter_domain(self):
        converter = InputDataConverter(
            curve_type="Bspline",
            build_method="BuildCurve",
            degree="3",
            parameter="10",
            point_rows=[
                ("0", "0", "0"),
                ("1", "1", "0"),
                ("2", "1", "0"),
                ("3", "0", "0"),
            ],
            knots="0, 0, 1, 1, 1, 1",
        )

        with self.assertRaisesRegex(ValueError, "domain"):
            converter.to_dict()

    def test_parameter_above_gui_limit_is_rejected(self):
        converter = InputDataConverter(
            curve_type="BezierCurve",
            build_method="BuildCurve",
            degree="1",
            parameter="5001",
            point_rows=[("0", "0", "0"), ("1", "1", "0")],
        )

        with self.assertRaisesRegex(ValueError, "5000"):
            converter.to_dict()

    def test_point_count_above_gui_limit_is_rejected(self):
        converter = InputDataConverter(
            curve_type="Bspline",
            build_method="Interpolation",
            degree="1",
            parameter="10",
            point_rows=[("0", "0", "0")] * 101,
        )

        with self.assertRaisesRegex(ValueError, "100"):
            converter.to_dict()

    def test_knot_multiplicity_above_degree_is_rejected(self):
        converter = InputDataConverter(
            curve_type="Bspline",
            build_method="BuildCurve",
            degree="3",
            parameter="10",
            point_rows=[
                ("0", "0", "0"),
                ("1", "1", "0"),
                ("2", "1", "0"),
                ("3", "1", "0"),
                ("4", "0", "0"),
            ],
            knots="0, 0, 0, 0, 1, 1, 1",
        )

        with self.assertRaisesRegex(ValueError, "중복"):
            converter.to_dict()


if __name__ == "__main__":
    unittest.main()
