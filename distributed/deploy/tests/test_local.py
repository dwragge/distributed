from time import sleep, time
import unittest

from distributed.deploy import Local
from distributed import Executor, Worker, Nanny
from distributed.utils_test import inc

from distributed.deploy.utils_test import ClusterTest

def test_simple():
    with Local(4, scheduler_port=0, processes=False) as c:
        with Executor((c.scheduler.ip, c.scheduler.port)) as e:
            x = e.submit(inc, 1)
            x.result()
            assert x.key in c.scheduler.tasks
            assert any(w.data == {x.key: 2} for w in c.workers)


def test_procs():
    with Local(2, scheduler_port=0, processes=False, cores_per_worker=3) as c:
        assert len(c.workers) == 2
        assert all(isinstance(w, Worker) for w in c.workers)
        with Executor((c.scheduler.ip, c.scheduler.port)) as e:
            assert all(w.ncores == 3 for w in c.workers)
        repr(c)

    with Local(2, scheduler_port=0, processes=True, cores_per_worker=3) as c:
        assert len(c.workers) == 2
        assert all(isinstance(w, Nanny) for w in c.workers)
        with Executor((c.scheduler.ip, c.scheduler.port)) as e:
            assert all(v == 3 for v in e.ncores().values())

            c.start_worker(separate_process=False)
            assert isinstance(c.workers[-1], Worker)
        repr(c)


class LocalTest(ClusterTest, unittest.TestCase):
    Cluster = Local
