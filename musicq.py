import misc

class QueueItem:
    def __init__(self, sound, file_to_rm):
        self.sound = sound
        self.file_to_rm = file_to_rm
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
        return item
    def peek(self):
        if self.is_empty():
            return None
        return self.q[0]

queue = Queue()

def clear():
    while queue.length() > 1:
        queue.dequeue()
    if not queue.is_empty():
        if not queue.peek().playing:
            queue.dequeue()

def add(sound, file_to_rm, vc = None):
    item = QueueItem(sound, file_to_rm)
    queue.enqueue(item)
    if not queue.peek().playing:
        play_next(vc)

def play_next(vc):
    if vc == None or len(queue.q) == 0:
        return
    item = queue.peek()
    item.playing = True
    def after(x):
        is_playing = False
        if item.file_to_rm != None:
            misc.rm(item.file_to_rm)
        queue.dequeue()
        if(len(queue.q) != 0):
            play_next(vc)
    vc.play(item.sound, after = after)
