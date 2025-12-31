import os

class QueueItem:
    def __init__(self, sound, dir_to_rm):
        self.sound = sound
        self.dir_to_rm = dir_to_rm
        self.playing = False

class Queue:
    def __init__(self):
        self.q = []
    def is_empty(self):
        return len(self.q) == 0
    def length(self):
        return len(self.q)
    def enqueue(self, item):
        self.q.append(item)
    def dequeue(self):
        if self.is_empty():
            return None
        item = self.q[0]
        self.q = self.q[1:]
        if item.dir_to_rm:
            to_rm = item.dir_to_rm.replace('"', '\\"')
            os.system(f"rm -r \"{to_rm}\"")
        return item
    def peek(self):
        if self.is_empty():
            return None
        return self.q[0]
    def clear(self):
        while self.length() > 1:
            self.dequeue()
        if not queue.is_empty():
            if not self.peek().playing:
                self.dequeue()
    def add(self, sound, dir_to_rm, vc=None):
        print(f"Adding {dir_to_rm}/{sound}")
        item = QueueItem(sound, dir_to_rm)
        self.enqueue(item)
        if not self.peek().playing:
            print("Playing it...")
            self.play_next(vc)
        else: print("A sound is already playing")
    def play_next(self, vc):
        if vc == None or len(self.q) == 0:
            return
        item = self.peek()
        item.playing = True
        def after(x):
            self.dequeue()
            if len(self.q) != 0:
                self.play_next(vc)
        vc.play(item.sound, after=after)
