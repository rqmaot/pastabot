import os
from .mixer import Mixer

class QueueItem:
    def __init__(self, path, dir_to_rm):
        self.path = path
        self.dir_to_rm = dir_to_rm
    def __str__(self):
        return f"{self.path}"
    def __repr__(self):
        return str(self)

class Queue:
    def __init__(self):
        self.qs = {}
        self.mixer = None
        self.active = set()
    def is_empty(self, track=0):
        return track not in self.qs or len(self.qs[track]) == 0
    def all_empty(self):
        return all(map(lambda k: len(self.qs[k]) == 0, self.qs))
    def length(self, track=0):
        if track in self.qs: return len(self.qs[track])
        return 0
    def is_playing(self, track=0):
        return track in self.active
    def set_playing_to(self, active, track=0):
        if active: self.active.add(track)
        else: self.active.discard(track)
    def set_playing(self, track=0):
        self.set_playing_to(True, track)
    def set_not_playing(self, track=0):
        self.set_playing_to(False, track)
    def enqueue(self, path, track=0):
        if track not in self.qs: self.qs[track] = []
        self.qs[track].append(path)
    def dequeue(self, track=0):
        if self.is_empty(track): return None
        item = self.qs[track][0]
        self.qs[track] = self.qs[track][1:]
        if item.dir_to_rm:
            to_rm = item.dir_to_rm.replace('"', '\\"')
            os.system(f"rm -r \"{to_rm}\"")
        return item
    def peek(self, track=0):
        if self.is_empty(track): return None
        return self.qs[track][0]
    def clear(self, track=0):
        while self.length(track) > 1: self.dequeue(track)
    def add(self, path, dir_to_rm=None, vc=None, track=0):
        print(f"Adding {path}")
        item = QueueItem(path, dir_to_rm)
        self.enqueue(item, track)
        # if not self.peek(track).playing:
        #     print("Playing it...")
        #     self.play_next(vc, track)
        # else: print("A sound is already playing on this track")
        if self.mixer is None or not self.is_playing(track) or not vc.is_playing():
            print("Playing it...")
            self.play_next(vc, track)
        else: 
            print("Added it to the queue...")
            print(self.qs[track])
    def _after_impl(self, track, vc):
        self.dequeue(track)
        if self.all_empty(): 
            if vc.is_playing: vc.stop()
            self.active.clear()
            self.mixer = None
        if self.is_empty(track): self.set_not_playing(track)
        else: self.play_next(vc, track)
    def play_next(self, vc, track=0):
        if vc == None or self.is_empty(track): 
            self.set_not_playing(track)
            return
        item = self.peek(track)
        def after():
            vc.loop.call_soon_threadsafe(self._after_impl, track, vc)
        self.set_playing(track)
        if self.mixer is None or not vc.is_playing():
            self.mixer = Mixer(item.path, after)
            vc.play(self.mixer)
        else:
            self.mixer.mix_in(item.path, after)
