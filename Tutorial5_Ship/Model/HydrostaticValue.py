import math

from Loadxlsx import Loadxlsx
from SimpsonRule import SimpsonRule

class Calculate:
    # offset_data        : Loadxlsx.interpolate()로 0~30m 1m 등간격이 된 오프셋 데이터
    # dimension          : Input/320K_VLCC.py의 Dimension
    # specific_dimension : Input/320K_VLCC.py의 Specific_Dimension
    # draft              : 계산할 흘수 [m]
    def __init__(self, offset_data, dimension, specific_dimension, draft):
        self.stations = offset_data["stations"]
        self.waterlines = offset_data["waterlines"]
        self.half_breadth = offset_data["half_breadth"]
        self.dimension = dimension
        self.draft = draft

        # station 간격 s = LBP / station 구간 개수 (station이 21개면 구간은 20개)
        self.station_spacing = dimension["LBP"] / (len(self.stations) - 1)
        # waterline 간격 w = Specific_Dimension["Step"]
        self.waterline_spacing = specific_dimension["Step"]

    # Volume
        # mld : 각 station마다 waterline 방향(반폭 -> 단면적)으로 적분한 뒤,
        #       그 단면적들을 station 방향으로 다시 적분해서 부피를 구한다.
    def Volume_mld(self):
        w = self.waterline_spacing
        n = math.floor(self.draft)
        remainder = self.draft - n

        areas = []

        for station in self.stations:
            ys = self.half_breadth[station]
            area = 0.0

            if n >= 2:
                if n % 2 == 0:
                    # 구간 개수가 짝수 -> 1법칙만으로 딱 떨어짐
                    area += SimpsonRule.CompositeFirstRule(ys[:n + 1], w)
                else:
                    # 구간 개수가 홀수 -> 짝수 부분만 1법칙, 마지막 1m는 사다리꼴
                    area += SimpsonRule.CompositeFirstRule(ys[:n], w)
                    area += SimpsonRule.Trapezoid(ys[n - 1], ys[n], w)
            elif n == 1:
                area += SimpsonRule.Trapezoid(ys[0], ys[1], w)

            # 소수 흘수의 마지막 자투리 구간 (예: 19.0 ~ 19.6)
            if remainder > 0:
                y_draft = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
                area += SimpsonRule.Trapezoid(ys[n], y_draft, remainder)

            # 오프셋이 반폭이라 2배
            areas.append(2 * area)

        # station 21개 = 20구간, 짝수라 1법칙만으로 계산됨
        return SimpsonRule.CompositeFirstRule(areas, self.station_spacing)
        # ext

    # Displacement
        # mld
        # ext

    # LCB
    # LCF
    # VCB(=KB)
    # BM
        # T
        # L
    # GM
        # T
        # L
    # MTC
    # TPC
    # WSA
    # CB
    # CWP
    # CM
    # CP
