from InputData import Inputdata
from Bezier import BuildCurve as BezierBuildCurve, Interpolation as BezierInterpolation
from Bspline import BuildCurve as BsplineBuildCurve, Interpolation as BsplineInterpolation
from Visualize import Visualize

class playing:
    @staticmethod
    def run_curve(input_data):
        """
        input_data 하나만 넣으면 "커브 종류" / "커브 생성 방식" 값을 보고
        어떤 클래스를 쓸지, 어떤 순서로 메서드를 호출할지 자동으로 판단해서
        끝까지 계산한 뒤 (curve 객체, control_points, POC) 를 돌려준다.
        """
        data = Inputdata(input_data)
        visualize_kwargs = {}

        if data.kind_of_curve == "BezierCurve":
            if data.kind_of_struct_curve == "BuildCurve":
                curve = BezierBuildCurve(data.degree, data.parameter, data.control_points)
                curve.normalize()
                curve.DeCasteljau()
                curve.denormalize()

                control_points = curve.control_points

            else:  # Interpolation
                curve = BezierInterpolation(data.degree, data.parameter, data.poc)
                curve.Chordlength()
                curve.Normalize()
                curve.Calculate()
                curve.Denormalize()

                # 정규화 이전 값인 curve.control_points가 아니라
                # Denormalize()가 만들어낸 curve.denormalized_control_points가 실제 좌표임
                control_points = curve.denormalized_control_points

            poc = curve.curve

        elif data.kind_of_curve == "Bspline":
            if data.kind_of_struct_curve == "BuildCurve":
                curve = BsplineBuildCurve(
                    data.degree, data.parameter, data.knots,
                    data.control_point_count, data.control_points,
                    data.domain_start, data.domain_end,
                )
                curve.Compute_curve_points()

                control_points = curve.control_points
                poc = curve.POC

                # control point가 scalar(숫자)인 경우, Visualize가
                # Greville abscissae / domain 구간을 x축으로 쓸 수 있게 전달
                visualize_kwargs = {
                    "greville": curve.Greville(),
                    "domain_start": curve.domain_start,
                    "domain_end": curve.domain_end,
                    "parameter": curve.parameter,
                }

            else:  # Interpolation
                curve = BsplineInterpolation(data.degree, data.parameter, data.poc, data.poc_count)
                curve.Chordlength()
                curve.KnotVector()
                curve.Calculate()

                control_points = curve.control_points
                poc = curve.curve

        else:
            raise ValueError("알 수 없는 커브 종류: " + str(data.kind_of_curve))

        Visualize(
            control_points, poc, data.degree,
            kind_of_curve=data.kind_of_curve,
            kind_of_struct_curve=data.kind_of_struct_curve,
            **visualize_kwargs,
        )

        return curve, control_points, poc




