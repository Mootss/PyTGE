import sys
import os
import itertools
import json
import base64
import tempfile

OS = sys.platform
if OS == "win32":
    import winsound
else:
    pass
    # TODO: make everything unix compatible

class Screen():
    def __init__(self, colorMode, height, width, color=0):
        self.colorMode = colorMode
        # colorMode should be 8 or 256. thats the number of colors to be used
        # fyi, all 8 color arrays can be displaed in 256 but not vice versa
        self.height = height
        self.width = width
        self.color = color # if undefined, default = black

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Box():
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

class Layer():

    def __init__(self, pos, size, collision_box, children, frames, frame_id=0):
        self.pos = Point(*pos)
        self.size = Point(*size)
        if collision_box:
            self.collision_box = collision_box
        self.children = [] or children
        self.frames = frames
        self.frame_id = frame_id

    def get_frame(self, id=None):
        return self.frames[id or self.frame_id]

    def move(self, direction, i): # i = increment amount
        match direction.lower():
            case "up":
                self.pos.y -= i
            case "down":
                self.pos.y += i
            case "right":
                self.pos.x += i
            case "left":
                self.pos.x -= i
            case _:
                raise ValueError("ERROR: Invalid direction, accepted directions are: 'up', 'down', 'right', 'left'")

    # TODO: this will be handled by a layer manager or whatever and call on_collision for the collided objects
    # def checkCollision(self, otherSprite):
    #     # using AABB method
    #     if ((((self.posX + self.width) > otherSprite.posX) and (self.posX < (otherSprite.posX + otherSprite.width)))
    #                                                         and 
    #         (((self.posY + self.height) > otherSprite.posY) and (self.posY < (otherSprite.posY + otherSprite.height)))):

    #         return True # return true IF this sprite is colliding with another sprite

class PixelSprite(Layer):

    def __init__(self, pos, size, collision_box, children, frames, frame_id=0):
        super().__init__(pos, size, collision_box, children, frames, frame_id)

        self.uhb = "\u2580" # upper half block ▀
        self.flipX = False
        self.flipY = False

    def render_char(self, x, y): # draws 1 character (which is 2 px)
        frame = self.rendered_frame
        fg = frame[y*2][x]
        bg = frame[y*2+1][x]
        if self.screen.colorMode == 8:
            return f"\033[3{fg}m\033[4{bg}m{self.uhb}\033[0m"
        elif self.screen.colorMode == 256:
            return f"\033[38;5;{fg}m\033[48;5;{bg}m{self.uhb}\033[0m"
        else:
            raise ValueError("ERROR: Invalid color mode, colorMode should be either 8 or 256")

    def render_frame(self): # convert array to ansi & print it
        frame = [list(line) for line in self.get_frame()]
        for child in self.children:
            if child.frames:
                child_frame = child.render_frame()
                # print(child_frame)
                for x, y in itertools.product(range(child.size.x), range(child.size.y)):
                    x1 = x + child.pos.x
                    y1 = y + child.pos.y
                    pixel = child_frame[y][x]
                    if 0 <= y1 < self.size.y \
                    and 0 <= x1 < self.size.x \
                    and pixel != -1:
                        frame[y1][x1] = pixel
        if self.flipY:
            frame.reverse()
        if self.flipX:
            for line in frame:
                line.reverse()
        return frame

    def draw(self): # convert array to ansi & print it
        self.rendered_frame = self.render_frame()
        lines = []

        ## pixels
        for y in range(len(self.rendered_frame) // 2):
            chars = ""
            for x in range(len(self.rendered_frame[y])):
                # print(x, y)
                chars += self.render_char(x, y)
            lines.append(chars)
        # sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        sys.stdout.write(f"\033[{self.pos.y};{self.pos.x}H")
        width = len(lines[0])
        for i, l in enumerate(lines):
            sys.stdout.write(l)
            sys.stdout.write(f"\033[1E\033[{self.pos.x-1}C")
        sys.stdout.flush()
        # print(f"\033[{(self.screen.height / 2)+2};1H\033[0J", end="")

class TextSprite(Layer):

    def __init__(self, pos, size, collision_box, children, frames, frame_id=0):
        super().__init__(pos, size, collision_box, children)

    def draw(self):
        pass

class TextBox(Layer):

    def __init__(self, pos, size, collision_box, children, text):
        super().__init__(pos, size, collision_box, children, None)
        self.text = text

    def render_text(self):
        frame = self.text[:]
        for _ in range(len(frame), self.size.y):
            frame.append(" " * self.size.x)
        for i, line in enumerate(frame):
            if len(line) < self.size.x:
                frame[i] += " " * (self.size.x - len(line))
        for child in self.children:
            if child.text:
                child_text = child.render_text()
                for x, y in itertools.product(range(child.size.x), range(child.size.y)):
                    x1 = x + child.pos.x
                    y1 = y + child.pos.y
                    char = child_text[y][x]
                    if 0 <= y1 < self.size.y \
                    and 0 <= x1 < self.size.x:
                        frame[y1][x1] = char
        return frame

    def draw(self):
        self.rendered_text = self.render_text()
        lines = self.rendered_text

        ## pixels
        # for y in range(len(self.rendered_text) // 2):
        #     chars = ""
        #     for x in range(len(self.rendered_text[y])):
        #         # print(x, y)
        #         chars += self.render_char(x, y)
        #     lines.append(chars)
        # sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        sys.stdout.write(f"\033[{self.pos.y};{self.pos.x}H")
        width = len(lines[0])
        for i, l in enumerate(lines):
            sys.stdout.write(l)
            sys.stdout.write(f"\033[1E\033[{self.pos.x-1}C")
        sys.stdout.flush()
        # print(f"\033[{(self.screen.height / 2)+2};1H\033[0J", end="")

class FillBox(PixelSprite):

    def __init__(self, pos, size, collision_box, children, color):
        super().__init__(pos, size, collision_box, children, None)
        self.set_color(color)

    def set_color(self, color):
        self.color = color
        self.frames = (tuple(tuple(color for x in range(self.size.x)) for y in range(self.size.y)),)

# add a os check
class Audio():
    def __init__(self, sounds):
        # 'sounds' takes a dict containing all the audio in base64 format
        self.soundPaths = {}
        for k, v in sounds.items():
            if v:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                    temp.write(base64.b64decode(v))
                    self.soundPaths[k] = temp.name

    def play(self, sound, loop=False):
        if sound in self.soundPaths:
            if not loop:
                winsound.PlaySound(self.soundPaths[sound], winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                winsound.PlaySound(self.soundPaths[sound], winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        else:
            raise ValueError(f"Provided sound '{sound}' does not exist")
        
    def stop(self):
        winsound.PlaySound(None, winsound.SND_PURGE)
        
    def cleanup(self): # should run this when exiting to delete all temp files created during runtime
        self.stop()
        for path in self.soundPaths:
            try:
                os.remove(self.soundPaths[path])
            except FileNotFoundError:
                pass  


class Game():

    def __init__(self, ready, process):
        self._ready = ready
        self._process = process

    def start(self):
        self._ready(self)
        while not self._process(self): # return True to quit
            pass

class InputHandler():
    #not sure how to write ts
    pass

# input handling, stole this from stackoverflow heh
# arrow keys = H P M K (windows), A B C D (unix)
if os.name == 'nt':  # Windows
    import msvcrt

    def getKey():
        if msvcrt.kbhit():  # Only read if a key was pressed
            first = msvcrt.getch()
            if first in {b'\x00', b'\xe0'}:  # Special key (arrows, etc.)
                second = msvcrt.getch()
                return second.decode('utf-8', errors='ignore')
            else:
                return first.decode('utf-8', errors='ignore')
        return None  # No key pressed

else:  # Unix (Linux, macOS)
    import tty
    import termios
    import select

    def getKey():
        dr, _, _ = select.select([sys.stdin], [], [], 0)  # 0 = no wait
        if dr:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch1 = sys.stdin.read(1)
                if ch1 == '\x1b':  # Arrow keys
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1)
                    if ch2 == '[':
                        return ch3  # 'A'=up, 'B'=down, 'C'=right, 'D'=left
                return ch1
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None  # No key pressed
 
