from Play import playing
from Vector import Vector

input_data = {
    "커브 종류" : "BezierCurve",
    "커브 생성 방식" : "Interpolation",
    "poc0": Vector.xyz(100, 100, 0),
    "poc1": Vector.xyz(200, 300, 0),
    "poc2": Vector.xyz(300, 350, 0),
    "poc3": Vector.xyz(500, 100, 0),
    "parameter": 100,
    "Degree": 3,
}

playing.run_curve(input_data)
