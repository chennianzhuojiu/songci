import itertools
import multiprocessing
import os


class MapReduceDriver:
    def __init__(self, map_func, reduce_func, workers=None):
        self.map_func = map_func
        self.reduce_func = reduce_func
        self._workers = os.cpu_count() or 1 if workers is None else workers

    @staticmethod
    def partition(map_result):
        partition_result = {}
        for k, v in map_result:
            try:
                partition_result[k].append(v)
            except KeyError:
                partition_result[k] = [v]
        return partition_result.items()

    @staticmethod
    def chunks(collection, chunk_len):
        return (collection[x:x + chunk_len]
                for x in range(0, len(collection), chunk_len))

    def __call__(self, items):
        if not isinstance(items, (list, tuple)):
            items = tuple(items)
        with multiprocessing.Pool(processes=self._workers) as pool:
            chunks = list(self.chunks(items, int(len(items) / self._workers)))
            map_result = pool.map(self.map_func, chunks)
            partition_result = self.partition(itertools.chain(*map_result))
            reduce_result = pool.map(self.reduce_func, partition_result)
            return reduce_result
