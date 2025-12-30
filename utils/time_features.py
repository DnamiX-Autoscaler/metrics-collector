import math
from datetime import datetime


def compute_time_features(ts: datetime):
    seconds_in_day = 24 * 60 * 60
    t = ts.hour * 3600 + ts.minute * 60 + ts.second

    return {
        "time_sin_1": math.sin(2 * math.pi * t / seconds_in_day),
        "time_cos_1": math.cos(2 * math.pi * t / seconds_in_day),
        "time_sin_2": math.sin(4 * math.pi * t / seconds_in_day),
        "time_cos_2": math.cos(4 * math.pi * t / seconds_in_day),
    }
