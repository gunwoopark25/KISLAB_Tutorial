import math

from Loadxlsx import Loadxlsx
from SimpsonRule import SimpsonRule

class Calculate:
    def __init__(self, offset_data, dimension, specific_dimension, draft):
        # offset_data        : Loadxlsx.interpolate()로 0~30m 1m 등간격이 된 오프셋 데이터
        self.stations = offset_data["stations"]
        self.waterlines = offset_data["waterlines"]
        self.half_breadth = offset_data["half_breadth"]
        # dimension : Input/320K_VLCC.py의 Dimension
        self.dimension = dimension
        # draft : 계산할 흘수 [m]
        self.draft = draft

        # station 간격 s = LBP / station 구간 개수 (station이 21개면 구간은 20개)
        self.station_spacing = dimension["LBP"] / (len(self.stations) - 1)
        # waterline 간격 w = Specific_Dimension["Step"]
        self.waterline_spacing = specific_dimension["Step"]

    # Volume
    ## mld : 각 station마다 waterline 방향(반폭 -> 단면적)으로 적분한 뒤,    
    def Volume_mld(self):
        w = self.waterline_spacing
        n = math.floor(self.draft)
        remainder = self.draft - n

        areas = []

        for station in self.stations:
            # station마다 단면적 구하기
            ys = self.half_breadth[station]
            area = 0.0

            # 정수부분
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
        result = SimpsonRule.CompositeFirstRule(areas, self.station_spacing)
        return result
        # ext : mld 부피에 외판(shell plating) 부피만큼을 더한다.
        #       외판 부피 ≈ 침수 표면적(WSA) × 평균 외판 두께(Mean plate thickness)
    
    ## ext : 그 단면적들을 station 방향으로 다시 적분해서 부피를 구한다.
    def Volume_ext(self):
        t = self.dimension["Mean plate thickness"]

        result = self.Volume_mld() + self.WSA() * t

        return result

    # Displacement
    def Displacement_mld(self):
        rho = self.dimension["Density of sea water"]

        result = self.Volume_mld() * rho
        return result

    def Displacement_ext(self):
        rho = self.dimension["Density of sea water"]

        result = self.Volume_ext() * rho
        return result

    # LCB : station마다 단면적을 구하고, 그 단면적에 midship으로부터의 거리(x, 선수쪽이 +)를 곱해 모멘트를 만든 뒤
    #       station 방향으로 적분(모멘트 총합)해서 mld 부피로 나눈다.
    def LCB(self):
        w = self.waterline_spacing
        n = math.floor(self.draft)
        remainder = self.draft - n

        moments = []

        for station in self.stations:
            # station마다 단면적 구하기 (Volume_mld와 동일)
            ys = self.half_breadth[station]
            area = 0.0

            if n >= 2:
                if n % 2 == 0:
                    area += SimpsonRule.CompositeFirstRule(ys[:n + 1], w)
                else:
                    area += SimpsonRule.CompositeFirstRule(ys[:n], w)
                    area += SimpsonRule.Trapezoid(ys[n - 1], ys[n], w)
            elif n == 1:
                area += SimpsonRule.Trapezoid(ys[0], ys[1], w)

            if remainder > 0:
                y_draft = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
                area += SimpsonRule.Trapezoid(ys[n], y_draft, remainder)

            area *= 2

            # station의 midship 기준 x좌표 (station 10이 midship, 선수(F.P) 방향이 +)
            x = station * self.station_spacing - self.dimension["LBP"] / 2
            moments.append(area * x)

        # station 방향 적분 (station 21개 = 20구간, 짝수라 1법칙만으로 계산됨)
        moment = SimpsonRule.CompositeFirstRule(moments, self.station_spacing)
        result = moment / self.Volume_mld()

        return result

    # LCF : 흘수의 수선면(waterplane)에서 각 station의 폭(breadth)을 구하고,
    #       station 방향으로 적분해서 수선면적을 구한 뒤, 그 폭에 x를 곱한 모멘트를 같은 방식으로 적분해서 나눈다.
    def LCF(self):
        n = math.floor(self.draft)
        remainder = self.draft - n

        breadths = []
        moments = []

        for station in self.stations:
            ys = self.half_breadth[station]

            # 흘수선에서의 반폭 (소수 흘수면 보간)
            if remainder > 0:
                y = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
            else:
                y = ys[n]

            # 오프셋이 반폭이라 2배
            b = 2 * y
            breadths.append(b)

            # station의 midship 기준 x좌표 (station 10이 midship, 선수(F.P) 방향이 +)
            x = station * self.station_spacing - self.dimension["LBP"] / 2
            moments.append(b * x)

        # station 방향 적분 (station 21개 = 20구간, 짝수라 1법칙만으로 계산됨)
        waterplane_area = SimpsonRule.CompositeFirstRule(breadths, self.station_spacing)
        moment = SimpsonRule.CompositeFirstRule(moments, self.station_spacing)
        result = moment / waterplane_area

        return result

    # VCB(=KB) : Volume_mld와 같은 방식으로 station마다 적분하되, y(z) 대신 y(z)*z를 적분해서
    #            baseline(z=0) 기준 부피 모멘트를 구한 뒤 mld 부피로 나눈다.
    def KB(self):
        w = self.waterline_spacing
        n = math.floor(self.draft)
        remainder = self.draft - n

        moments = []

        for station in self.stations:
            ys = self.half_breadth[station]
            # y(z)*z 값 리스트 (z : waterline 높이)
            zys = [y * z for y, z in zip(ys, self.waterlines)]
            moment = 0.0

            if n >= 2:
                if n % 2 == 0:
                    moment += SimpsonRule.CompositeFirstRule(zys[:n + 1], w)
                else:
                    moment += SimpsonRule.CompositeFirstRule(zys[:n], w)
                    moment += SimpsonRule.Trapezoid(zys[n - 1], zys[n], w)
            elif n == 1:
                moment += SimpsonRule.Trapezoid(zys[0], zys[1], w)

            if remainder > 0:
                y_draft = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
                moment += SimpsonRule.Trapezoid(zys[n], y_draft * self.draft, remainder)

            # 오프셋이 반폭이라 2배
            moments.append(2 * moment)

        # station 방향 적분 (station 21개 = 20구간, 짝수라 1법칙만으로 계산됨)
        result_moment = SimpsonRule.CompositeFirstRule(moments, self.station_spacing)
        result = result_moment / self.Volume_mld()

        return result

    # BM
    ## T : 수선면의 폭(b=2y)을 세제곱해서 centerline 기준 단면 2차 모멘트(2/3 * y^3)를 만들고,
    ##     station 방향으로 적분해서 횡 관성모멘트(I_T)를 구한 뒤 mld 부피로 나눈다.
    def BM_T(self):
        n = math.floor(self.draft)
        remainder = self.draft - n

        moments_of_inertia = []

        for station in self.stations:
            ys = self.half_breadth[station]

            # 흘수선에서의 반폭 (소수 흘수면 보간)
            if remainder > 0:
                y = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
            else:
                y = ys[n]

            # centerline 기준 단면 2차 모멘트 (반폭이라 2/3 * y^3)
            moments_of_inertia.append((2 / 3) * y ** 3)

        i_t = SimpsonRule.CompositeFirstRule(moments_of_inertia, self.station_spacing)
        result = i_t / self.Volume_mld()

        return result

    ## L : 수선면의 폭(b=2y)에 LCF로부터의 거리 제곱을 곱해서 종 관성모멘트(I_L)를 구한 뒤 mld 부피로 나눈다.
    def BM_L(self):
        n = math.floor(self.draft)
        remainder = self.draft - n
        x_f = self.LCF()

        moments_of_inertia = []

        for station in self.stations:
            ys = self.half_breadth[station]

            # 흘수선에서의 반폭 (소수 흘수면 보간)
            if remainder > 0:
                y = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
            else:
                y = ys[n]

            # 오프셋이 반폭이라 2배
            b = 2 * y
            # station의 midship 기준 x좌표 (station 10이 midship, 선수(F.P) 방향이 +)
            x = station * self.station_spacing - self.dimension["LBP"] / 2

            # LCF(부심 아닌 부양심)로부터의 거리 제곱을 곱한 단면 2차 모멘트
            moments_of_inertia.append(b * (x - x_f) ** 2)

        i_l = SimpsonRule.CompositeFirstRule(moments_of_inertia, self.station_spacing)
        result = i_l / self.Volume_mld()

        return result

    # GM
    ## T : KB + BM_T - KG
    def GM_T(self):
        result = self.KB() + self.BM_T() - self.dimension["KG"]
        return result

    ## L : KB + BM_L - KG
    def GM_L(self):
        result = self.KB() + self.BM_L() - self.dimension["KG"]
        return result

    # MTC : (배수량 * GM_L) / (100 * LBP)
    def MTC(self):
        L = self.dimension["LBP"]

        result = self.Displacement_mld() * self.GM_L() / (100 * L)
        return result

    # TPC : (수선면적 * 해수 밀도) / 100
    def TPC(self):
        rho = self.dimension["Density of sea water"]
        n = math.floor(self.draft)
        remainder = self.draft - n

        breadths = []

        for station in self.stations:
            ys = self.half_breadth[station]

            # 흘수선에서의 반폭 (소수 흘수면 보간)
            if remainder > 0:
                y = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
            else:
                y = ys[n]

            # 오프셋이 반폭이라 2배
            breadths.append(2 * y)

        waterplane_area = SimpsonRule.CompositeFirstRule(breadths, self.station_spacing)
        result = waterplane_area * rho / 100

        return result

    # WSA : 각 station의 girth(침수 둘레)를 구한 뒤, station 방향으로 적분해서 침수 표면적을 구한다.
    def WSA(self):
        # 정수부분 소수 부분 나누기
        n = math.floor(self.draft)
        remainder = self.draft - n
        # g(x)
        girths = []

        for station in self.stations:
            # station마다 girth(침수 둘레) 구하기
            ys = self.half_breadth[station]
            girth = 0.0

            # 정수부분 : 인접한 waterline 두 점 사이를 직선으로 보고 그 길이를 더한다
            for i in range(n):
                dy = ys[i + 1] - ys[i]
                girth += math.hypot(dy, self.waterline_spacing)

            # 소수 흘수의 마지막 자투리 구간 (예: 19.0 ~ 19.6)
            if remainder > 0:
                y_draft = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
                dy = y_draft - ys[n]
                girth += math.hypot(dy, remainder)

            # 오프셋이 반폭이라 2배
            girths.append(2 * girth)

        # station 방향 적분 (station 21개 = 20구간, 짝수라 1법칙만으로 계산됨)
        result = SimpsonRule.CompositeFirstRule(girths, self.station_spacing)
        return result

    # CB : mld 부피 / (LBP * B * draft)
    def CB(self):
        B = self.dimension["B"]

        result = self.Volume_mld() / (self.dimension["LBP"] * B * self.draft)
        return result

    # CWP : 수선면적 / (LBP * B)
    def CWP(self):
        B = self.dimension["B"]
        n = math.floor(self.draft)
        remainder = self.draft - n

        breadths = []

        for station in self.stations:
            ys = self.half_breadth[station]

            # 흘수선에서의 반폭 (소수 흘수면 보간)
            if remainder > 0:
                y = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
            else:
                y = ys[n]

            # 오프셋이 반폭이라 2배
            breadths.append(2 * y)

        waterplane_area = SimpsonRule.CompositeFirstRule(breadths, self.station_spacing)
        result = waterplane_area / (self.dimension["LBP"] * B)

        return result

    # CM : midship(가운데 station) 단면적 / (B * draft)
    def CM(self):
        B = self.dimension["B"]
        w = self.waterline_spacing
        n = math.floor(self.draft)
        remainder = self.draft - n

        # 가운데 station (station 0~20이면 station 10)
        midship_station = self.stations[len(self.stations) // 2]
        ys = self.half_breadth[midship_station]
        area = 0.0

        if n >= 2:
            if n % 2 == 0:
                area += SimpsonRule.CompositeFirstRule(ys[:n + 1], w)
            else:
                area += SimpsonRule.CompositeFirstRule(ys[:n], w)
                area += SimpsonRule.Trapezoid(ys[n - 1], ys[n], w)
        elif n == 1:
            area += SimpsonRule.Trapezoid(ys[0], ys[1], w)

        if remainder > 0:
            y_draft = Loadxlsx.linear_interpolation(self.waterlines, ys, self.draft)
            area += SimpsonRule.Trapezoid(ys[n], y_draft, remainder)

        # 오프셋이 반폭이라 2배
        area *= 2

        result = area / (B * self.draft)
        return result

    # CP : mld 부피 / (midship 단면적 * LBP)  (= CB / CM)
    def CP(self):
        midship_area = self.CM() * self.dimension["B"] * self.draft
        result = self.Volume_mld() / (midship_area * self.dimension["LBP"])

        return result
