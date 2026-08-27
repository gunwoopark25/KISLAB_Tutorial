import matplotlib.pyplot as plt

from Vector import Vector

class Visualize:
    def __init__(self, control_points, curve, degree,
        kind_of_curve="Bspline", kind_of_struct_curve="BuildCurve",
        greville=None, domain_start=0, domain_end=0, parameter=0):
        if greville is None:
            greville = []

        self.control_points = control_points
        self.curve = curve
        self.degree = degree
        self.kind_of_curve = kind_of_curve
        self.kind_of_struct_curve = kind_of_struct_curve

        curve_name = "Bezier" if self.kind_of_curve == "BezierCurve" else "B-Spline"
        method_name = "Interpolation" if self.kind_of_struct_curve == "Interpolation" else "Build Curve"

        if isinstance(self.control_points[0], Vector):
            cp_x = [cp.components[0] for cp in self.control_points]
            cp_y = [cp.components[1] for cp in self.control_points]

            middle_control_points = self.control_points[1:-1]

            middle_cp_x = [cp.components[0] for cp in middle_control_points]
            middle_cp_y = [cp.components[1] for cp in middle_control_points]

            poc_x = [point.components[0] for point in self.curve]
            poc_y = [point.components[1] for point in self.curve]
        else:
            # control point가 scalar(숫자)일 때는 Greville abscissae를 가로축으로 사용
            cp_x = greville
            cp_y = list(self.control_points)

            middle_cp_x = cp_x[1:-1]
            middle_cp_y = cp_y[1:-1]

            step = (domain_end - domain_start) / parameter
            poc_x = [domain_start + k * step for k in range(parameter + 1)]
            poc_y = list(self.curve)

        plt.plot(
            cp_x, cp_y,
            linestyle='-', color='black',
            label='Control Polygon',
        )
        plt.plot(
            middle_cp_x, middle_cp_y,
            linestyle='None',
            marker='o', markersize=8,
            markerfacecolor='white', markeredgecolor='black',
            label='Control Points',
        )
        plt.plot(
            poc_x, poc_y,
            linestyle='-', color='blue',
            marker='o', markersize=4,
            label=curve_name + ' Curve',
        )

        plt.title(curve_name + " " + method_name + " (Degree " + str(self.degree) + ")")
        plt.axis('equal')
        plt.legend()
        plt.show()
