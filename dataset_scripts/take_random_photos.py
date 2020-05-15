import os
import numpy as np

import os, shutil, threading, queue

import typer as typer


class FileCopy(threading.Thread):
    def __init__(self, queue_, files, dirs):
        threading.Thread.__init__(self)
        self.queue_ = queue_
        self.files = list(files)  # copy list
        self.dirs = list(dirs)  # copy list
        for f in files:
            if not os.path.exists(f):
                raise ValueError('%s does not exist' % f)
        for d in dirs:
            if not os.path.isdir(d):
                raise ValueError('%s is not a directory' % d)

    def run(self):
        # This puts one object into the queue for each file,
        # plus a None to indicate completion
        try:
            for f in self.files:
                try:
                    for d in self.dirs:
                        shutil.copy(f, d)
                except IOError as e:
                    self.queue_.put(e)
                else:
                    self.queue_.put(f)
        finally:
            self.queue_.put(None)  # signal completion


def get_random_file(root_dir, dataset_size):
    for root, dirs, files in os.walk(root_dir):
        random_list = np.random.choice(a=range(len(files)), size=dataset_size, replace=False)
        for i in random_list:
            yield os.sep.join([root_dir, files[i]])


def copy_photos_from_to(from_, to, size):
    files = []
    for file in get_random_file(from_, size):
        files.append(file)
    queue_ = queue.Queue()
    # files = ['a', 'b', 'c']
    dirs = [to]
    copythread = FileCopy(queue_, files, dirs)
    copythread.start()
    label_ = f"Copying {size} files from: {from_}, to: {to}"
    with typer.progressbar(length=100) as process:
        while True:
            process.update(100 / size)
            x = queue_.get()
            if x is None:
                break
            # print(x)
    copythread.join()


def main(from_: str, to: str, size: int):
    copy_photos_from_to(from_, to, size)


if __name__ == "__main__":
    typer.run(main)
