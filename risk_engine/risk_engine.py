import time
import math


class RiskEngine:
    def __init__(self, distance_thresh=100, time_thresh=3.0):
        self.distance_thresh = distance_thresh
        self.time_thresh = time_thresh
        self.min_intrusive_risk = 0.4   # 40%


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

                close = self._keypoint_distance(
                    d1["keypoints"],
                    d2["keypoints"],
                    self.distance_thresh
                )

                if close:
                    pair_time = self.pair_timers.get(pair_key, 0.0)

                    severity = self._interaction_severity(
                        d1["keypoints"],
                        d2["keypoints"]
                    )

                    if severity == 1:
                        pair_time += dt

                    elif severity == 2:
                        pair_time += dt * 4
                        pair_time = max(pair_time, self.time_thresh * self.min_intrusive_risk)
                        # intrusive contact grows faster

                    self.pair_timers[pair_key] = pair_time
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

    def _keypoint_distance(self, kpts1, kpts2, thresh):
        
        critical_indices = [5, 6, 11, 12]  # shoulders + hips

        for i in critical_indices:
            x1, y1, c1 = kpts1[i]
            if c1 < 0.5:
                continue

            for j in critical_indices:
                x2, y2, c2 = kpts2[j]
                if c2 < 0.5:
                    continue

                dist = math.hypot(x1 - x2, y1 - y2)
                if dist < thresh:
                    return True

        return False
    
    def _interaction_severity(self, kpts1, kpts2):
        # Symmetric check: A→B OR B→A
        return max(
            self._one_way_severity(kpts1, kpts2),
            self._one_way_severity(kpts2, kpts1)
        )


    def _one_way_severity(self, src, tgt):
        # Keypoint indices
        TORSO = [5, 6, 11, 12]   # shoulders + hips
        HANDS = [9, 10]         # wrists
        FACE = [0, 1, 2]        # nose + eyes

        TORSO_THRESH = 45
        HAND_FACE_THRESH = 35

        # 🔴 Intrusive: hands → face or torso
        for h in HANDS:
            xh, yh, ch = src[h]
            if ch < 0.5:
                continue

            for t in FACE + TORSO:
                xt, yt, ct = tgt[t]
                if ct < 0.5:
                    continue

                if ((xh - xt) ** 2 + (yh - yt) ** 2) ** 0.5 < HAND_FACE_THRESH:
                    return 2

        # 🟡 Passive: torso proximity
        for i in TORSO:
            xi, yi, ci = src[i]
            if ci < 0.5:
                continue

            for j in TORSO:
                xj, yj, cj = tgt[j]
                if cj < 0.5:
                    continue

                if ((xi - xj) ** 2 + (yi - yj) ** 2) ** 0.5 < TORSO_THRESH:
                    return 1

        return 0

