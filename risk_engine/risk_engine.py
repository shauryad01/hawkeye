import time
import math


class RiskEngine:
    def __init__(self, distance_thresh=100, time_thresh=3.0):
        self.distance_thresh = distance_thresh
        self.time_thresh = time_thresh

        # key: frozenset({id1, id2})
        # value: accumulated close time
        self.pair_timers = {}

        self.last_update = time.time()

    def _distance(self, c1, c2):
        return math.hypot(c1[0] - c2[0], c1[1] - c2[1])

    def update(self, detections):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        active_pairs = set()

        for i in range(len(detections)):
            for j in range(i + 1, len(detections)):
                d1 = detections[i]
                d2 = detections[j]

                id1 = d1.get("id")
                id2 = d2.get("id")

                if id1 is None or id2 is None:
                    continue

                pair_key = frozenset({id1, id2})

                dist = self._distance(d1["center"], d2["center"])

                if dist < self.distance_thresh:
                    self.pair_timers[pair_key] = self.pair_timers.get(pair_key, 0.0) + dt
                    active_pairs.add(pair_key)

        # decay timers for inactive pairs
        for pair in list(self.pair_timers.keys()):
            if pair not in active_pairs:
                self.pair_timers[pair] *= 0.9
                if self.pair_timers[pair] < 0.1:
                    del self.pair_timers[pair]

        return self.compute_risk()

    def compute_risk(self):
        max_time = 0.0
        for t in self.pair_timers.values():
            max_time = max(max_time, t)

        risk = min(max_time / self.time_thresh, 1.0)
        return risk
