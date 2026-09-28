"""
기본적인 단위 : [m]
믿도의 단위 : [ton/m^3]
"""
from Model.Loadxlsx import Loadxlsx

Dimension = {
    "LOA" : 332.0,
    "LBP" : 318,
    "B" : 60.0,
    "D" : 29.0,
    "T_d" : 20.8,
    "Mean plate thickness" : 0.022,
    "Density of sea water" : 1.025,
    "KG" : 14.2,
}

Specific_Dimension = {
    "Step" : 1,
    "Specific_Draft_1" : 19.6,
    "Specific_Draft_2" : 20.8,
    "Specific_Draft_3" : 21.3,
}

class OffsetData:
    """320K offset.xlsx의 반폭 데이터를 한 번만 읽어서 캐싱해두고,
    Model/ViewModel에서는 매번 엑셀을 다시 읽지 않고 여기서 불러 쓴다."""

    _body_data = None
    _offset_data = None

    # AP~FP + 선미 돌출부까지 포함한 원본 오프셋 (선형도 등 그리기용)
    @classmethod
    def body_data(cls):
        if cls._body_data is None:
            cls._body_data = Loadxlsx.load(include_overhang=True)
        return cls._body_data

    # AP~FP(station 0~20)만 남기고 waterline을 1m 등간격으로 보간한 오프셋 (계산용)
    @classmethod
    def offset_data(cls):
        if cls._offset_data is None:
            body_data = cls.body_data()
            raw_data = {
                "stations": [s for s in body_data["stations"] if 0 <= s <= 20],
                "waterlines": body_data["waterlines"],
                "half_breadth": {
                    s: ys for s, ys in body_data["half_breadth"].items() if 0 <= s <= 20
                },
            }
            cls._offset_data = Loadxlsx.interpolate(raw_data)
        return cls._offset_data
