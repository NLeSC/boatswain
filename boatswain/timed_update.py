import threading
import time


class TimedUpdate(threading.Thread):
    def __init__(self, progress_bar, imagename='Total'):
        threading.Thread.__init__(self)
        self.progress_bar = progress_bar
        self.done = False
        self.step = 0
        self.imagename = imagename

    def run(self):
        while not self.done:
            if self.progress_bar:
                self.progress_bar.update(self.step, imagename=self.imagename)
            time.sleep(1)
