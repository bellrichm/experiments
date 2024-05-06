''' Test rolling own thread pool. '''
import queue
import threading
import time

class MyThread(threading.Thread):
    ''' A simple worker thread. '''
    def __init__(self, data_queue):
        threading.Thread.__init__(self)
        self.data_queue = data_queue

    def run(self):
        print(f"starting: {threading.current_thread().native_id}")
        while True:
            data = self.data_queue.get()
            if data:
                print(f". processing: {threading.current_thread().native_id} {data}")
                time.sleep(.5)
            else:
                break
        print(f"ending: {threading.current_thread().native_id}")

if __name__ == "__main__":
    def main():
        ''' The main. '''
        print("Start")
        data_queue = queue.Queue()
        max_threads = 3
        threads = []
        for i in range(max_threads):
            thread = MyThread(data_queue)
            thread.start()
            threads.append(thread)

        for i in range(1, 11):
            data_queue.put(i)

        time.sleep(2)
        data_queue.put(None)

        for i in range(11, 21):
            data_queue.put(i)

        for i in range(max_threads):
            data_queue.put(None)

        for i in range(max_threads):
            threads[i].join()

        print("The end.")

    main()
