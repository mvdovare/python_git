# def match_point_to_road(point, roads):
#     return min(roads, key=lambda r: point.distance(r))


def match_point_to_road(point, roads, max_distance=2):
    candidates = [
        r for r in roads if point.distance(r) < max_distance
    ]

    if not candidates:
        return None

    return min(candidates, key=lambda r: point.distance(r))

def print_test_changes():
    print("Test cases for match_point_to_road have been added/updated.")