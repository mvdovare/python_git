from shapely.geometry import Point, LineString
from match_gps_to_road import match_point_to_road


def test_parallel_roads_case():
    """
    GPS point is closer to one road,
    but logically should match to another (e.g., by direction)
    """

    # GPS point (with noise)
    point = Point(0, 0)

    # Two parallel roads
    road_1 = LineString([(-1, 1), (1, 1)])   # correct
    road_2 = LineString([(-1, -1), (1, -1)]) # incorrect

    roads = [road_1, road_2]

    result = match_point_to_road(point, roads)

    # for now expect nearest (this will FAIL later)
    assert result in roads

def test_filters_far_roads():
    point = Point(0, 0)
    
    close_road = LineString([(-1, 0.5), (1, 0.5)])
    far_road = LineString([(-1, 10), (1, 10)])

    result = match_point_to_road(point, [close_road, far_road])

    assert result == close_road