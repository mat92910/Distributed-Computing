from __future__ import print_function
import sys
import dill
import multiprocessing
from multiprocessing.managers import SyncManager
import time
import queue

#Server Connection Settings
IP = ''
PORTNUM = 55444
AUTHKEY = b'crowdsourcing'

#create the worker to complete jobs on the queue
def worker(job_q, result_q):
    myname = multiprocessing.current_process().name
    while True:
        try:
            job = job_q.get_nowait()
            print('%s got %s jobs...' % (myname, len(job)//2))
            outdict = {job[1]: dill.loads(job[0])(job[1])}
            print(outdict)
            result_q.put(outdict)
            print('  %s done' % myname)
        except queue.Empty:
            time.sleep(1)
            continue
        except EOFError:
            print("Lost connection to job server")
            return

#creates worker manager that handles multiple workers
def worker_manager(shared_job_q, shared_result_q, nprocs):
    procs = []
    for i in range(nprocs):
        p = multiprocessing.Process(
                target=worker,
                args=(shared_job_q, shared_result_q))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()

#create client manager to connect to the server and recieve job and result queue.
def make_client_manager(ip, port, authkey):
    class ServerQueueManager(SyncManager):
        pass

    ServerQueueManager.register('get_job_q')
    ServerQueueManager.register('get_result_q')

    manager = ServerQueueManager(address=(ip, port), authkey=authkey)
    manager.connect()

    print('Client connected to %s:%s' % (ip, port))
    return manager

if __name__ == '__main__':
    PY3 = sys.version_info[0] == 3
    if PY3:
        print("Running Python 3")
    else:
        assert False, "Not Running Python 3"

    while True:
        try:
            manager = make_client_manager(IP, PORTNUM, AUTHKEY)
            job_q = manager.get_job_q()
            result_q = manager.get_result_q()
            
            worker_manager(job_q, result_q, (multiprocessing.cpu_count()//2))
        except ConnectionError:
            time.sleep(1)
            continue
        except EOFError:
            time.sleep(1)
            continue
