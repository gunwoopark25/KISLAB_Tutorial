"""
s : 등간격 = Input에 Step
ys : WL값
i : station
"""

class SimpsonRule:

    # Simpson 1/3 공식 (2구간)
    @staticmethod
    def FirstRule(y0, y1, y2, s):
        return s / 3 * (y0 + 4 * y1 + y2)

    # Simpson 3/8 공식 (3구간)
    @staticmethod
    def SecondRule(y0, y1, y2, y3, s):
        return 3 * s / 8 * (y0 + 3 * y1 + 3 * y2 + y3)

    # 사다리꼴 공식 (1구간)
    @staticmethod
    def Trapezoid(y0, y1, s):
        return s / 2 * (y0 + y1)


# ==============================================================================
# 위의 SimpsonRule 사용해서 반복 계산
# ==============================================================================
    # FirstRule을 등간격 배열 전체에 반복 적용 (구간 개수가 짝수여야 함)
    @staticmethod
    def CompositeFirstRule(ys, s):
        interval_count = len(ys) - 1

        total = 0.0

        for i in range(0, interval_count, 2):
            total += SimpsonRule.FirstRule(ys[i], ys[i + 1], ys[i + 2], s)

        return total

    # SecondRule을 등간격 배열 전체에 반복 적용 (구간 개수가 3의 배수여야 함)
    @staticmethod
    def CompositeSecondRule(ys, s):
        interval_count = len(ys) - 1

        total = 0.0

        for i in range(0, interval_count, 3):
            total += SimpsonRule.SecondRule(ys[i], ys[i + 1], ys[i + 2], ys[i + 3], s)

        return total