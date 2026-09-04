import unittest

from matplotlib.figure import Figure

from model import CurveModel, InputDataConverter, Visualize


class VisualizeTests(unittest.TestCase):
    def test_curve_is_drawn_on_provided_axes_without_standalone_window(self):
        input_data = InputDataConverter(
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
        ).to_dict()
        result = CurveModel().calculate(input_data)
        figure = Figure()
        axes = figure.add_subplot(111)

        Visualize(
            result.control_points,
            result.curve_points,
            result.degree,
            kind_of_curve=result.curve_type,
            kind_of_struct_curve=result.build_method,
            axes=axes,
            show=False,
        )

        self.assertEqual(len(axes.lines), 3)
        self.assertEqual(axes.get_title(), "Bezier Build Curve (Degree 3)")
        self.assertIsNotNone(axes.get_legend())

    def test_bspline_build_uses_knot_domain_for_plot_x_values(self):
        input_data = InputDataConverter(
            curve_type="Bspline",
            build_method="BuildCurve",
            degree="3",
            parameter="100",
            point_rows=[
                ("ignored", "50", "ignored"),
                ("ignored", "175", "ignored"),
                ("ignored", "200", "ignored"),
                ("ignored", "150", "ignored"),
                ("ignored", "25", "ignored"),
            ],
            knots="50,50,50,200,350,350,350",
        ).to_dict()
        result = CurveModel().calculate(input_data)
        figure = Figure()
        axes = figure.add_subplot(111)

        Visualize(
            result.control_points,
            result.curve_points,
            result.degree,
            kind_of_curve=result.curve_type,
            kind_of_struct_curve=result.build_method,
            axes=axes,
            show=False,
            **result.visualization_options,
        )

        self.assertEqual(
            list(axes.lines[0].get_xdata()),
            [50.0, 100.0, 200.0, 300.0, 350.0],
        )
        curve_x = list(axes.lines[2].get_xdata())
        self.assertEqual((min(curve_x), max(curve_x)), (50.0, 350.0))


if __name__ == "__main__":
    unittest.main()
