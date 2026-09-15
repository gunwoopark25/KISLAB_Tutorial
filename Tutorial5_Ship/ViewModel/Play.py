import importlib
import math
import sys
from pathlib import Path


# 프로젝트 폴더 경로
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from Model.Loadxlsx import Loadxlsx
from Model.HydrostaticValue import Calculate


class Playing:
    @staticmethod
    def run(drafts=None):
        """
        drafts:
            계산할 흘수 목록.
            생략하면 1m~D까지 0.5m 간격과 Input의 지정 흘수를 사용한다.

        반환값:
            dimension   : Dimension 표에 표시할 입력값
            offset_data : Fore/Aft Body를 그릴 오프셋
            results     : Hydrostatic Table과 Curve의 공통 계산 결과
        """

        # 1. 선박 제원 읽기
        # 파일명이 숫자로 시작하므로 importlib 사용
        ship = importlib.import_module("Input.320K_VLCC")

        dimension = dict(ship.Dimension)
        specific_dimension = dict(ship.Specific_Dimension)

        # 2. Offset 읽기 및 전처리
        body_data = Loadxlsx.load(include_overhang=True)
        raw_data = {
            "stations": [s for s in body_data["stations"] if 0 <= s <= 20],
            "waterlines": body_data["waterlines"],
            "half_breadth": {
                s: ys for s, ys in body_data["half_breadth"].items() if 0 <= s <= 20
            },
        }
        offset_data = Loadxlsx.interpolate(raw_data)

        # 현재 계산 코드는 0m부터 1m 간격인 데이터를 전제로 한다.
        if specific_dimension["Step"] != 1:
            raise ValueError("현재 계산에서는 Step을 1로 설정해야 합니다.")

        # 3. 계산할 흘수 목록 구성
        if drafts is None:
            drafts = [
                value
                for key, value in specific_dimension.items()
                if key.startswith("Specific_Draft_")
            ]
            upper = min(float(dimension["D"]), offset_data["waterlines"][-1])
            drafts.extend(i / 2 for i in range(2, math.floor(upper * 2) + 1))
            drafts.append(upper)

        drafts = sorted(set(float(draft) for draft in drafts))

        if not drafts:
            raise ValueError("계산할 흘수를 한 개 이상 지정해야 합니다.")

        max_draft = offset_data["waterlines"][-1]

        for draft in drafts:
            # 0m에서는 부피 등으로 나누는 계산을 할 수 없다.
            if not 0 < draft <= max_draft:
                raise ValueError(
                    f"흘수는 0보다 크고 {max_draft}m 이하여야 합니다: "
                    f"{draft}"
                )

        # 4. 흘수별 계산
        results = []

        for draft in drafts:
            calculate = Calculate(
                offset_data,
                dimension,
                specific_dimension,
                draft,
            )

            result = Playing.calculate_one_draft(calculate)
            results.append(result)

        # 5. 화면에서 사용할 데이터 반환
        return {
            "dimension": dimension,
            "offset_data": offset_data,
            "body_data": body_data,
            "results": results,
        }

    @staticmethod
    def calculate_one_draft(calculate):
        """한 흘수의 계산 결과를 딕셔너리로 취합한다."""

        volume = calculate.Volume_mld()
        displacement = calculate.Displacement_mld()

        lcb = calculate.LCB()
        lcf = calculate.LCF()

        kb = calculate.KB()
        bm_t = calculate.BM_T()
        bm_l = calculate.BM_L()

        tpc = calculate.TPC()
        mtc = calculate.MTC()
        wsa = calculate.WSA()

        cb = calculate.CB()
        cm = calculate.CM()
        cwp = calculate.CWP()

        rho = calculate.dimension["Density of sea water"]

        return {
            "draft": calculate.draft,
            "volume": volume,
            "displacement": displacement,
            "lcb": lcb,
            "lcf": lcf,
            "kb": kb,
            "bm_t": bm_t,
            "bm_l": bm_l,
            "km_t": kb + bm_t,
            "km_l": kb + bm_l,
            "i_t": bm_t * volume,
            "i_l": bm_l * volume,
            "waterplane_area": tpc * 100 / rho,
            "tpc": tpc,
            "mtc": mtc,
            "wsa": wsa,
            "cb": cb,
            "cp": cb / cm,
            "cwp": cwp,
            "cm": cm,
        }


if __name__ == "__main__":
    # 기본 흘수 범위 및 Input의 지정 흘수 계산
    data = Playing.run()

    # 여러 흘수를 지정하려면:
    # data = Playing.run(drafts=range(1, 26))

    for result in data["results"]:
        print(
            f'Draft: {result["draft"]:.3f} m | '
            f'Volume: {result["volume"]:,.1f} m³ | '
            f'Displacement: {result["displacement"]:,.1f} ton'
        )
