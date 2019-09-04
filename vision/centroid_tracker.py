from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


class CentroidTracker:
    def __init__(self, max_disappeared=150):
        self.next_object = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()

        self.max_disappeared = max_disappeared

    def register(self, centroid):
        self.objects[self.next_object] = centroid
        self.disappeared[self.next_object] = 0
        self.next_object += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def deregister_all(self):
        self.next_object = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()

    def update(self, centroids):
        if len(centroids) == 0:
            for object_id in self.disappeared.keys():
                self.disappeared[object_id] += 1

                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            return self.objects

        if len(self.objects) == 0:
            for i in range(0, len(centroids)):
                self.register(centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            D = dist.cdist(np.array(object_centroids), centroids)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_columns = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_columns:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_columns.add(col)

            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_columns = set(range(0, D.shape[1])).difference(used_columns)

            if D.shape[0] >= D.shape[1]:
                for row in unused_rows:
                    object_id = object_ids[row]
                    self.disappeared[object_id] += 1

                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                for col in unused_columns:
                    self.register(centroids[col])

        return self.objects
