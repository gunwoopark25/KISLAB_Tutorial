import math
from numbers import Number

class Vector:
    # 벡터 정의
    def __init__(self, *components):
        self.components = [] # 리스트로 생성

        # 복사 생성자
        if len(components) == 1 and isinstance(components[0], Vector):
            self.components = components[0].components.copy()
        else:
            for c in components:
                converted_value = float(c)
                self.components.append(converted_value)

        if len(self.components) == 0:
            raise ValueError("Vector에는 최소 1개의 성분이 있어야 합니다.")
        
    # 출력 형식 정의
    def __repr__(self): 
        return str(self.components)
    
    @classmethod # 객체가 아닌 클래스 자체를 기준으로 동작
    def xyz(cls,x, y, z):
        return cls(x, y, z)

    # 기본 연산
    # 기본 형태
    #def __add__(self, other): <= 매서드 종류
    #        if len(self.components) != len(other.components):
    #            raise ValueError("같은 차원의 Vector끼리만 연산 가능")
    #
    #        result_components = [] # 벡터를 리스트로 정의
    #
    #        for a,b in zip(self.components, other.components): <= 두 리스트에서 같은 위치의 값으로 묶어줌
    #            result_components.append(a+b)
    #
    #        return Vector(*result_components)
    

    ## 더하기
    def __add__(self, other):
        if len(self.components) != len(other.components):
            raise ValueError("같은 차원의 Vector끼리만 연산 가능")

        result_components = [] # 벡터를 리스트로 정의

        for a,b in zip(self.components, other.components):
            result_components.append(a+b)

        return Vector(*result_components)

    ## 빼기
    def __sub__(self, other):
        if len(self.components) != len(other.components):
            raise ValueError("같은 차원의 Vector끼리만 연산 가능")

        result_components = []

        for a,b in zip(self.components, other.components):
            result_components.append(a-b)
        
        return Vector(*result_components)
    ## 곱하기
    def __mul__(self, other):
        if isinstance(other, Number):
            result_components = [c * other for c in self.components]
            return Vector(*result_components)

        if len(self.components) != len(other.components):
            raise ValueError("같은 차원의 Vector끼리만 연산 가능")

        result_components = []

        for a,b in zip(self.components, other.components):
            result_components.append(a*b)

        return Vector(*result_components)

    ## 스칼라 * 벡터 (예: t * vector)
    def __rmul__(self, other):
        return self.__mul__(other)
    ## 나누기
    def __truediv__(self, other):
        if len(self.components) != len(other.components):
            raise ValueError("같은 차원의 Vector끼리만 연산 가능")
    
        result_components = []
    
        for a,b in zip(self.components, other.components):
            result_components.append(a/b)
            
        return Vector(*result_components)

    # 내적
    def cdot(self, other):
        if len(self.components) != len(other.components):
            raise ValueError("같은 차원의 Vector끼리만 연산 가능")

        for (a,b) in zip(self.components, other.components):
            result =+ a*b

        return result
    
    # 외적 (외적은 3차원 벡터만 가능)
    def crossproduct(self, other):
        if len(self.components) != 3:
            raise ValueError("외적은 3차원 벡터만 연산 가능")
        if len(other.components) != 3:
            raise ValueError("외적은 3차원 벡터만 연산 가능")

        x1, y1, z1 = self.components
        x2, y2, z2 = other.components

        x = y1*z2 - z1*y2
        y = z1*x2 - x1*z2
        z = x1*y2 - y1*x2

        result_components = [x, y, z]

        return Vector(*result_components)

    # ==
    # !=
    def check_equal(self, other):
        x1, y1, z1 = self.components
        x2, y2, z2 = other.components

        if x1 == x2 and y1 == y2 and z1 == z2:
            return print("일치")
        else:
            return print("불일치")

    # Nomalization
    def normalization(self, *others):

        vectors = (self, *others)
        dimension = len(self.components)

        if any(len(vector.components) != dimension for vector in vectors):
            raise ValueError("같은 차원의 Vector끼리만 연산 가능")

        max_list = []
        min_list = []
        variation = []

        # 최댓값, 최솟값 찾기
        for column in zip(*(vector.components for vector in vectors)):
            max_list.append(max(column))
            min_list.append(min(column))
        # 변화량 계산
        for a,b in zip(max_list, min_list):
            variation.append(a-b)
        # 정규화 계산
        normalized_vectors = []

        for vector in vectors:
            normalized_components = []
            for value, min_val, dv in zip(vector.components, min_list, variation):
                if dv == 0:
                    normalized_components.append(0)
                else:
                    normalized_components.append((value - min_val) / dv)
            normalized_vectors.append(Vector(*normalized_components))

        return normalized_vectors, Vector(*max_list), Vector(*min_list), Vector(*variation)
    
    # Magnitude
    def magnitude(self):
        if len(self.components) == 0:
            raise ValueError("0차원의 벡터는 연산 불가")

        result = 0

        for component in self.components:
            result += component **2
        result = math.sqrt(result)

        return result

## 사용하지 않은 기능 (위의 기능으로 대체 가능)
    # +=    
    # -=
    # *=
