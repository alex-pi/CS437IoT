from multiprocessing import Process, Queue
import time


class ProTest():
    def __init__(self):
        self.x = 0
        self.active = True

        self.q = Queue()
        self.p = Process(target=self.f, args=(self.q,))
        #p.start()
        #print(q.get())    # prints "[42, None, 'hello']"
        #p.join()

    def start(self):
        self.p.start()

    def stop(self):
        self.active = False
        #self.p.join()

    def f(self, q):
        flag = True
        while flag:
            self.x += 1
            if not q.empty():
                flag = q.get(False)
            print(self.x, self.active, flag)
            time.sleep(1)
            #q.put([42, None, 'hello'])

if __name__ == '__main__':
    p = ProTest()
    p.start()
    print("process started")
    time.sleep(5)
    p.stop()

    p.q.put(False)
    print("wait ended", p.active, p.x)
