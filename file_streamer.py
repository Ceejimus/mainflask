"""Manages file streaming."""
import sys
import uuid
import time
import os
from threading import Thread, Lock
from queue import Queue
from datetime import datetime

def eprint(*args, **kwargs):
    now = datetime.now()
    args = (now.ctime(),) + args
    print(*args, file=sys.stderr, **kwargs)


class FileStreamer(Thread):
    def __init__(self, tmp_dir):
        eprint(self.__class__.__name__, 'Initializing')
        Thread.__init__(self)
        self.tmp_dir = tmp_dir
        self.thread_id = 1
        self.name = str(uuid.uuid4())
        self.lock = Lock()
        self.delay = 2
        self.slaves = {}
        self.active_dirs = {}

    def run(self):
        with self.lock:
            self.running = True

        while(True):
            with self.lock:
                if not self.running:
                    break
            time.sleep(self.delay)

    def stop(self):
        with self.lock:
            print('[DEBUG] a', self.active_dirs)
            dir_ids = list(self.active_dirs.keys());
            for dir_id in dir_ids:
                active_dir = self.active_dirs.pop(dir_id)
                file_ids = list(active_dir['writers'].keys())
                for file_id in file_ids:
                    writer = active_dir['writers'].pop(file_id)
                    writer['writer'].stop(force=True)
            print('[DEBUG] b', self.active_dirs)
            self.running = False

    def __del__(self):
        eprint(self.__class__.__name__, 'Destructing')
        self.stop()

    def init_dir_upload(self, dir):
        dir_id = str(uuid.uuid4())
        self.active_dirs[dir_id] = {
            "path": dir,
            "writers": {}
        }
        os.makedirs(os.path.join(self.tmp_dir, dir_id))
        eprint("init_dir_upload", self.active_dirs)
        return dir_id


    def init_file_upload(self, dir_id, path, size):
        file_id = str(uuid.uuid4())
        fileWriter = FileWriter(os.path.join(self.tmp_dir, dir_id, str(file_id)))
        fileWriter.start()
        self.active_dirs[dir_id]['writers'][file_id] = {
            'path': path,
            'writer': fileWriter,
            'uploaded': 0,
            'size': size
        }
        eprint('init_file_upload', self.active_dirs)
        return file_id

    def write_chunk(self, dir_id, file_id, chunk):
        writer = self.active_dirs[dir_id]['writers'][file_id]
        fileWriter = writer['writer']
        fileWriter.append_chunk(chunk)
        writer['uploaded'] += len(chunk)
        eprint('appended chunk', writer['uploaded'], writer['size'], writer['uploaded'] / writer['size'])
        if writer['uploaded'] >= writer['size']:
            eprint('DONE STOPPING')
            fileWriter.stop()
            eprint('STOPPED')


class FileWriter(Thread):
    def __init__(self, path):
        Thread.__init__(self)
        eprint('FileWriter initializing')
        self.f = open(path, 'ab+')
        self.path = path
        self.lock = Lock()
        self.delay = 0.1
        self.queue = Queue()

    def run(self):
        with self.lock:
            self.stop_when_done = False
            self.running = True

        while(True):
            with self.lock:
                if not self.running:
                    break

            # time.sleep(self.delay)

            if not self.queue.empty():
                eprint('queue not empty')
                try:
                    eprint('got chunk')
                    chunk = self.queue.get_nowait()
                    self._write_chunk(chunk)
                except Empty:
                    eprint('empty exception')
                    self.stop(force=True)
            elif self.stop_when_done:
                eprint('queue empty stopping')
                self.stop(force=True)

    def __del__(self):
        eprint(self.__class__.__name__, 'Destructing')
        self.stop()

    def _write_chunk(self, chunk):
        with self.lock:
            eprint('writing chunk to file', len(chunk))
            self.f.write(chunk)

    def stop(self, force=False):
        if force:
            eprint('forced stop')
            with self.lock:
                self.running = False
                self.f.close()
        else:
            eprint('stop when done')
            with self.lock:
                self.stop_when_done = True

    def append_chunk(self, chunk):
        self.queue.put(chunk)
