from pathlib import Path
import sys
import math
from dataclasses import dataclass, field

BASE_DIR = Path(__file__).resolve().parent / "Base"
sys.path.insert(0, str(BASE_DIR))

from InputData import InputDataConverter, Inputdata
from Bezier import BuildCurve as BezierBuildCurve, Interpolation as BezierInterpolation
from Bspline import BuildCurve as BsplineBuildCurve, Interpolation as BsplineInterpolation
from Visualize import Visualize


@dataclass
class CurveResult:
    curve_object: object
    control_points: list
    curve_points: list
    curve_type: str
    build_method: str
    degree: int
    visualization_options: dict = field(default_factory=dict)


class CurveModel:
    def calculate(self, input_data):
        data = Inputdata(input_data)
        visualization_options = {}

        if data.kind_of_curve == "BezierCurve":
            if data.kind_of_struct_curve == "BuildCurve":
                curve = BezierBuildCurve(
                    data.degree,
                    data.parameter,
                    data.control_points,
                )
                curve.normalize()
                curve.DeCasteljau()
                curve.denormalize()
                control_points = curve.control_points
            else:
                curve = BezierInterpolation(
                    data.degree,
                    data.parameter,
                    data.poc,
                )
                curve.Chordlength()
                curve.Normalize()
                curve.Calculate()
                curve.Denormalize()
                control_points = curve.denormalized_control_points

            curve_points = curve.curve

        elif data.kind_of_curve == "Bspline":
            if data.kind_of_struct_curve == "BuildCurve":
                curve = BsplineBuildCurve(
                    data.degree,
                    data.parameter,
                    data.knots,
                    data.control_point_count,
                    data.control_points,
                    data.domain_start,
                    data.domain_end,
                )
                curve.Compute_curve_points()
                control_points = curve.control_points
                curve_points = curve.POC
                visualization_options = {
                    "greville": curve.Greville(),
                    "domain_start": curve.domain_start,
                    "domain_end": curve.domain_end,
                    "parameter": curve.parameter,
                }
            else:
                curve = BsplineInterpolation(
                    data.degree,
                    data.parameter,
                    data.poc,
                    data.poc_count,
                )
                curve.Chordlength()
                curve.KnotVector()
                curve.Calculate()
                control_points = curve.control_points
                curve_points = curve.curve

        self._validate_finite_points(control_points, "Control Point")
        self._validate_finite_points(curve_points, "Curve Point")

        return CurveResult(
            curve_object=curve,
            control_points=control_points,
            curve_points=curve_points,
            curve_type=data.kind_of_curve,
            build_method=data.kind_of_struct_curve,
            degree=data.degree,
            visualization_options=visualization_options,
        )

    @staticmethod
    def _validate_finite_points(points, label):
        for index, point in enumerate(points):
            components = getattr(point, "components", (point,))
            if not all(math.isfinite(float(value)) for value in components):
                raise ValueError(
                    f"{label} {index}의 계산 결과가 유한한 숫자가 아닙니다."
                )
