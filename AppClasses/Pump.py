class Point:
    rpm: float
    torque: float
    pressure: float
    flw: float


class Pump:
    def __init__(self):
        self.__points = []
        self.__type = {}

    def addPoint(self, point_data: dict):
        point = self.__processPointData(point_data)
        self.addPoint(point)
        pass

    def addPoint(self, point: Point):
        self.__points.append(point)

    def __processPointData(point_data: dict):
        point = Point()
        point.rpm = point_data['flw']
        point.torque = point_data['torque']
        point.pressure = abs(point_data['psi_out'] - point_data['psi_in'])
        point.flw = point_data['flw']
        return point
