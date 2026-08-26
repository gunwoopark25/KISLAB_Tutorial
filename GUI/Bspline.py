class BuildCurve:
    def Greville(self):
        # ζ_i = (u_i + u_{i+1} + ... + u_{i+Degree-1}) / Degree
        self.greville_X = []
    
        for i in range(self.control_point_count):
            knot_group = self.knots[i:i + self.degree]
    
            total = 0
            for knot in knot_group:
                total += knot
    
            self.greville_X.append(total / self.degree)
    
        return self.greville_X
# Knot insertion
    # knot 하나를 끼워 넣어도 곡선 모양은 그대로이고, control point만 하나 늘어남
    def Insert_knot(self, new_knot):
        multiplicity = self.knots.count(new_knot)

        # new_knot이 들어갈 구간 찾기: u[span] <= new_knot < u[span+1]
        span = 0
        for j in range(len(self.knots) - 1):
            if self.knots[j] <= new_knot < self.knots[j + 1]:
                span = j

        new_control_points = []

        for i in range(self.control_point_count + 1):
            if i <= span + 1 - self.degree:
                # 앞쪽: 그대로 유지
                new_control_points.append(self.control_points[i])

            elif i <= span + 1 - multiplicity:
                # 가운데: alpha = (û - u_{i-1}) / (u_{i+Degree-1} - u_{i-1})
                lower_knot = self.knots[i - 1]
                upper_knot = self.knots[i + self.degree - 1]

                alpha = (new_knot - lower_knot) / (upper_knot - lower_knot)

                previous_point = self.control_points[i - 1]
                current_point = self.control_points[i]

                new_control_points.append((1 - alpha) * previous_point + alpha * current_point)

            else:
                # 뒤쪽: 인덱스만 하나 밀림
                new_control_points.append(self.control_points[i - 1])

        self.knots.insert(span + 1, new_knot)

        self.control_points = new_control_points
        self.control_point_count = self.control_point_count + 1

        self.domain_start = self.knots[self.degree - 1]
        self.domain_end = self.knots[len(self.knots) - self.degree]

        return self.control_points

    # de Boor algorithm - Evaluation
    # u에서의 knot 중복도를 확인해서, Degree가 될 때까지만 insert_knot을 반복
    def Evaluate(self, u):
        # 원본 knots/control_points를 건드리지 않도록 얕은 복제본에서 계산
        clone = de_boor.__new__(de_boor)
        clone.degree = self.degree
        clone.knots = list(self.knots)
        clone.control_points = list(self.control_points)
        clone.control_point_count = self.control_point_count

        multiplicity = clone.knots.count(u)

        for _ in range(self.degree - multiplicity):
            clone.insert_knot(u)

        index = clone.knots.index(u)

        return clone.control_points[index]

    # parameter 개수만큼 domain을 등분해서 각 u에 대해 evaluate()를 반복 -> POC(Point On Curve) 목록
    def Compute_curve_points(self):
        self.POC = []

        step = (self.domain_end - self.domain_start) / self.parameter

        for k in range(self.parameter + 1):
            u = self.domain_start + k * step

            self.POC.append(self.evaluate(u))

        return self.POC    

class Interpolation:
    # Chordlength
    def Chordlength(self):
        # l[i-1]
        self.l = []

        for i in range(1, self.poc_count):
            segment_length = (self.poc[i] - self.poc[i - 1]).magnitude()
            self.l.append(segment_length)

        # u[i] = u[i-1] + l[i-1]
        self.u = [0.0]

        for i in range(1, self.poc_count):
            self.u.append(self.u[i - 1] + self.l[i - 1])

        return self.u

    # Knot 생성
    def KnotVector(self):
        self.knots = []

        # 앞쪽: 시작값을 Degree개 중복 (곡선이 첫 POC에서 시작하도록)
        for _ in range(self.degree):
            self.knots.append(self.u[0])

        # 내부 knot: 연속한 u를 Degree개씩 평균 (de Boor averaging)
        for j in range(1, self.poc_count - self.degree):
            knot_group = self.u[j:j + self.degree]

            total = 0
            for value in knot_group:
                total += value

            self.knots.append(total / self.degree)

        # 뒤쪽: 끝값을 Degree개 중복 (곡선이 마지막 POC에서 끝나도록)
        for _ in range(self.degree):
            self.knots.append(self.u[-1])

        return self.knots

    # basis function
    def Basis_function(self, index, u):
        unit_input = {
            "Degree": self.degree,
            "parameter": self.parameter,
            "knots": list(self.knots),
        }

        for i in range(self.poc_count):
            if i == index:
                unit_input["cp" + str(i)] = 1.0
            else:
                unit_input["cp" + str(i)] = 0.0

        return de_boor(unit_input).evaluate(u)

    # Calculate
    def Calculate(self):
        # 4-1. BSplineMatrix: Matrix[i][j] = N_j(u_i)
        basis_components = []

        for i in range(self.poc_count):
            u_i = self.u[i]
            row = []

            for j in range(self.poc_count):
                row.append(self.basis_function(j, u_i)) # Basis Function

            basis_components.append(row)

        self.basis_matrix = Matrix(basis_components)

        # 4-2. GaussElimination: Basis 행렬의 역행렬 계산 (Matrix.inverse가 Gauss-Jordan으로 구현)
        self.inverse_matrix = self.basis_matrix.inverse()

        # 4-3. MatrixMul: CP = BasisMatrix^-1 * POC
        poc_components = [list(point.components) for point in self.poc]
        poc_matrix = Matrix(poc_components)

        cp_matrix = self.inverse_matrix * poc_matrix

        self.control_points = [Vector(*row) for row in cp_matrix.components]

        # 4-4. de Boor: 계산된 control point로 곡선 위의 점들 계산
        curve_input = {
            "Degree": self.degree,
            "parameter": self.parameter,
            "knots": list(self.knots),
        }

        for i in range(self.poc_count):
            curve_input["cp" + str(i)] = self.control_points[i]

        self.curve_solver = de_boor(curve_input)
        self.curve = self.curve_solver.compute_curve_points()

        return self.curve