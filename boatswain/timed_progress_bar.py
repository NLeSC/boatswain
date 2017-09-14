import threading
import time
import progressbar
from progressbar import Percentage, BouncingBar, SimpleProgress, Bar, Timer, Counter
from .dynamic_string_message import DynamicStringMessage


class TimedProgressBar(threading.Thread):
    def __init__(self, start, total, name):
        threading.Thread.__init__(self)
        self.done = False
        self.step = start + 1
        self.total = total + 1
        self.imagename = name
        self.progress_bar = None
        self.create_progress_bar()

    def run(self):
        while not self.done:
            if self.progress_bar:
                self.progress_bar.update(self.step, imagename=self.imagename)
            time.sleep(1)
        self.clean_up()

    def clean_up(self):
        if self.progress_bar is not None:
            self.progress_bar.finish()
            self.progress_bar = None

    def stop(self):
        self.done = True
        self.join()

    def update(self):
        self.progress_bar.update(self.step, imagename=self.imagename)

    def create_progress_bar(self):
        """
            Initialize the progress bar
        """
        if self.total is None:
            self.total = progressbar.UnknownLength
            widgets = [DynamicStringMessage('imagename'), ' ', Counter(), ' ',
                       BouncingBar(marker=u'\u2588', left=u'\u2502', right=u'\u2502'),
                       ' ', Timer()]
        else:
            widgets = [DynamicStringMessage('imagename'), ' ', Percentage(), ' (', SimpleProgress(), ')',
                       ' ', Bar(marker=u'\u2588', left=u'\u2502', right=u'\u2502'),
                       ' ', Timer()]

        self.progress_bar = progressbar.ProgressBar(
            max_value=self.total, redirect_stdout=True,
            redirect_stderr=True, widgets=widgets)
        self.progress_bar.start()
        self.progress_bar.update(self.step, imagename=self.imagename)
