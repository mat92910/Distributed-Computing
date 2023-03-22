from __future__ import print_function
import time
import dill
from multiprocessing.managers import SyncManager
import queue
import pprint

from NQueens import geneticAlgorithm

#Server Connection Settings
IP = 'localhost'
PORTNUM = 55444
AUTHKEY = b'crowdsourcing'

#Calls the function that need to be run by the crowd
def call_function(n):
    return geneticAlgorithm(5000, 0.75, 0.05, n)

#stores the results into a file
def store_results(resultdict):
    print("Storing results")
    with open("Results", 'w') as f:
        for key, value in resultdict.items():
            f.write('%s:%s\n' % (key, value))

#creates the job manager, job queue, and result queue
def make_server_manager(port, authkey):
    job_q = queue.Queue()
    result_q = queue.Queue()

    class JobQueueManager(SyncManager):
        pass

    JobQueueManager.register('get_job_q', callable=lambda: job_q)
    JobQueueManager.register('get_result_q', callable=lambda: result_q)

    manager = JobQueueManager(address=('', port), authkey=authkey)
    manager.start()
    print('Server started at port %s' % port)
    return manager

#create the job server for clients to connect to and recieve jobs
def runserver():
    manager = make_server_manager(PORTNUM, AUTHKEY)
    shared_job_q = manager.get_job_q()
    shared_result_q = manager.get_result_q()

    try:
        while True:
            N = int(input("Number of jobs to do: "))

            #add the jobs into the job queue
            for i in range(0, N):
                code_string = dill.dumps(call_function, recurse=True)
                shared_job_q.put((code_string, i))
                print("Job: " + str(i))

            #add results into the results dictionary
            numresults = 0
            resultdict = {}
            while numresults <= (N - 1):
                outdict = shared_result_q.get()
                print(outdict)
                resultdict.update(outdict)
                numresults += len(outdict)
                print("num results " + str(numresults))
    #when the program is closed print and store the results into a file
    except KeyboardInterrupt:
        print(len(resultdict))
        pprint.pprint(resultdict)
        store_results(resultdict)
        print('--- DONE ---')
        time.sleep(2)
        manager.shutdown()

if __name__ == "__main__":
    runserver()
