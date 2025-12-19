import time
import math


class RiskEngine:
    def __init__(
        self,
        time_thresh=1.8,
        contact_thresh=35,
        severity_multiplier=4,
        min_intrusive_risk=0.4,
        min_hand_speed=30.0
    ):
        """
        time_thresh          : seconds to reach 100% risk
        contact_thresh       : pixel distance for hand-to-body contact
        severity_multiplier  : escalation speed for intrusive contact
        min_intrusive_risk   : minimum initial risk for intrusive contact
        min_hand_speed       : px/sec threshold to consider hand as 'reaching'
        """

        self.time_thresh = time_thresh
        self.contact_thresh = contact_thresh
        self.severity_multiplier = severity_multiplier
        self.min_intrusive_risk = min_intrusive_risk
        self.min_hand_speed = min_hand_speed

        # pair_key -> accumulated time
        self.pair_timers = {}

        # (person_id, hand_idx) -> last (x, y)
        self.prev_hand_positions = {}

        self.last_update = time.time()

    # Geometry helpers

    def _dist(self, x1, y1, x2, y2):
        return math.hypot(x1 - x2, y1 - y2)

    # Hand motion (INTENT FILTER)

    def _hand_is_moving(self, person_id, hand_idx, x, y, dt):
        key = (person_id, hand_idx)

        if key not in self.prev_hand_positions:
            self.prev_hand_positions[key] = (x, y)
            return False

        px, py = self.prev_hand_positions[key]
        self.prev_hand_positions[key] = (x, y)

        speed = self._dist(x, y, px, py) / max(dt, 1e-6)
        return speed > self.min_hand_speed

    # One-way intrusive contact (src → tgt)

    def _hand_to_body(self, src_id, src_kpts, tgt_kpts, dt):
        """
        Detects ACTIVE hand → face/chest/hip contact (one direction)
        """

        HANDS = [9, 10]               # wrists
        FACE = [0, 1, 2]              # nose, eyes
        CHEST = [5, 6]                # shoulders (chest proxy)
        HIPS = [11, 12]               # hips

        for h in HANDS:
            xh, yh, ch = src_kpts[h]
            if ch < 0.5:
                continue

            moving = self._hand_is_moving(src_id, h, xh, yh, dt)

            # --- hand → face (strong, no motion required)
            for f in FACE:
                xf, yf, cf = tgt_kpts[f]
                if cf < 0.5:
                    continue

                if self._dist(xh, yh, xf, yf) < self.contact_thresh:
                    return True

            # --- hand → chest (strong, no motion required)
            for c in CHEST:
                xc, yc, cc = tgt_kpts[c]
                if cc < 0.5:
                    continue

                if self._dist(xh, yh, xc, yc) < self.contact_thresh:
                    return True

            # --- hand → hip (WEAK unless hand is moving)
            for hip in HIPS:
                xhip, yhip, chip = tgt_kpts[hip]
                if chip < 0.5:
                    continue

                if (
                    self._dist(xh, yh, xhip, yhip) < self.contact_thresh
                    and moving
                ):
                    return True

        return False

    # Symmetric + asymmetric logic

    def _intrusive_contact(self, d1, d2, dt):
        """
        Returns True only for ASYMMETRIC or active interaction
        """

        c12 = self._hand_to_body(
            d1["id"], d1["keypoints"], d2["keypoints"], dt
        )
        c21 = self._hand_to_body(
            d2["id"], d2["keypoints"], d1["keypoints"], dt
        )

        # Reject symmetric passive overlap (your false positive case)
        if c12 and c21:
            return False

        return c12 or c21

    # Main update loop

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
                pair_time = self.pair_timers.get(pair_key, 0.0)

                contact = self._intrusive_contact(d1, d2, dt)

                if contact:
                    # fast escalation
                    pair_time += dt * self.severity_multiplier

                    # severity floor
                    pair_time = max(
                        pair_time,
                        self.time_thresh * self.min_intrusive_risk
                    )

                    self.pair_timers[pair_key] = pair_time
                    active_pairs.add(pair_key)

        # decay inactive pairs
        for pair in list(self.pair_timers.keys()):
            if pair not in active_pairs:
                self.pair_timers[pair] *= 0.9
                if self.pair_timers[pair] < 0.1:
                    del self.pair_timers[pair]

        return self.compute_risk()

    # Scene risk = max pair risk

    def compute_risk(self):
        max_time = 0.0
        for t in self.pair_timers.values():
            max_time = max(max_time, t)

        return min(max_time / self.time_thresh, 1.0)
