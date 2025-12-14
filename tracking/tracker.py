import math
import time


class CentroidTracker:
    def __init__(self, max_distance=150, max_lost=2.0):
        self.next_id = 0
        self.objects = {}
        self.max_distance = max_distance
        self.max_lost = max_lost  # seconds

    def _distance(self, c1, c2): #euclidean distance
        return math.hypot(c1[0] - c2[0], c1[1] - c2[1])

    def update(self, detections):
        now = time.time()
        updated_objects = {}

        used_ids = set()

        for det in detections:
            cx, cy = det["center"]
            best_id = None
            best_dist = self.max_distance

            for obj_id, obj in self.objects.items():
                if obj_id in used_ids:
                    continue

                px = obj["center"][0] + obj.get("velocity", (0, 0))[0]
                py = obj["center"][1] + obj.get("velocity", (0, 0))[1]

                dist = self._distance((cx, cy), (px, py))

                if dist < best_dist:
                    best_dist = dist
                    best_id = obj_id

            if best_id is not None:
                prev_center = self.objects[best_id]["center"]

                vx = cx - prev_center[0]
                vy = cy - prev_center[1]

                updated_objects[best_id] = {
                    "center": (cx, cy),
                    "velocity": (vx, vy),
                    "last_seen": now
                }

                used_ids.add(best_id)
                det["id"] = best_id
            else:
                obj_id = self.next_id
                self.next_id += 1

                updated_objects[obj_id] = {
                    "center": (cx, cy),
                    "velocity": (0, 0),
                    "last_seen": now
                }

                det["id"] = obj_id

        for obj_id, obj in self.objects.items():
            if obj_id not in updated_objects:
                if now - obj["last_seen"] > self.max_lost:
                    continue


        self.objects = updated_objects
        return detections
