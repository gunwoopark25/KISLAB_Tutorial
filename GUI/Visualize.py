class Visualize:
    def __init__(self):
        cp_x = [cp.components[0] for cp in self.control_points]
        cp_y = [cp.components[1] for cp in self.control_points]

        middle_control_points = self.control_points[1:-1]

        middle_cp_x = [cp.components[0] for cp in middle_control_points]
        middle_cp_y = [cp.components[1] for cp in middle_control_points]

        poc_x = [point.components[0] for point in self.curve]
        poc_y = [point.components[1] for point in self.curve]

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
            label='B-Spline Curve',
        )

        plt.title("B-Spline Interpolation (Degree " + str(self.degree) + ")")
        plt.axis('equal')
        plt.legend()
        plt.show()
