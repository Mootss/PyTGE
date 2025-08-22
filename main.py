import sys
import os
import itertools

class Screen():
    #bit3 = "\033"
    #bit8 = "\033[38;5;0m"

    def __init__(self, colorMode, height, width, color=0):
        self.colorMode = colorMode
        # colorMode should be 8 or 256. thats the number of colors to be used
        # fyi, all 8 color arrays can be displaed in 256 but not vice versa
        self.height = height
        self.width = width
        self.color = color # if undefined, default = black
        # self.array = createShape(self.color, self.width, self.height)
        # self.displayArray = [row[:] for row in self.array]
        # sprite eh draw kuran v ma do it by modifying display array instead of og array, so og array can be re-used when a sprite is moved
        # im sure theres a more efficient way to do ts but my sikundi too smol

    # def reset(self):
    #     #self.displayArray = [[e for e in row] for row in self.array]
    #     self.displayArray = [row[:] for row in self.array]

    # def drawSprite(self, sprite):
    #     for row in range(len(sprite.array)):
    #         for e in range(len(sprite.array[row])):
    #             if sprite.array[row][e] != -1:
    #                 self.displayArray[sprite.posY + row][sprite.posX + e] = sprite.array[row][e]

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
        self.pos = pos
        self.size = size
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

    def render_char(self, x, y, frame): # draws 1 character (which is 2 px)
        # frame = self.render_pixels()
        fg = frame[max(0, y*2)][x]
        bg = frame[max(0, y*2+1)][x]
        if self.screen.colorMode == 8:
            return f"\033[3{fg}m\033[4{bg}m{self.uhb}\033[0m" # \033[0m actually only needs to be written at the end of each line but wtver
        elif self.screen.colorMode == 256:
            return f"\033[38;5;{fg}m\033[48;5;{bg}m{self.uhb}\033[0m"
        else:
            raise ValueError("ERROR: Invalid color mode, colorMode should be either 8 or 256")

    def render_pixels(self): # convert array to ansi & print it
        frame = [list(line) for line in self.get_frame()]
        for child in self.children:
            if child.frames:
                child_frame = child.render_pixels()
                # print(child_frame)
                for x, y in itertools.product(range(child.size.x), range(child.size.y)):
                    x1 = x + child.pos.x
                    y1 = y + child.pos.y
                    if 0 <= y1 < self.size.y \
                    and 0 <= x1 < self.size.x:
                        frame[y1][x1] = child_frame[y][x]
                # for relative_y, absolute_y in enumerate(range(child.pos.y, child.pos.y+child.size.y)):
                #     if absolute_y <= (len(frame) - 1):
                #         for relative_x, absolute_x in enumerate(range(child.pos.x, child.pos.x+child.size.x)):
                #             if absolute_x <= (len(frame[absolute_y]) - 1):
                #                 # print(x, y)
                #                 # print(len(frame[y]))
                #                 frame[absolute_y][absolute_x] = child_frame[relative_y][relative_x]
        if self.flipX:
            frame.reverse()
        if self.flipY:
            for line in frame:
                line.reverse()
        return frame

    def draw(self): # convert array to ansi & print it
        frame = self.render_pixels()
        lines = []

        for y in range(len(frame) // 2):
            chars = ""
            for x in range(len(frame[y])):
                # print(x, y)
                chars += self.render_char(x, y, frame)
            lines.append(chars)
        # sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        sys.stdout.write(f"\033[{self.pos.y};{self.pos.x}H")
        width = len(lines[0])
        for i, l in enumerate(lines):
            sys.stdout.write(l)
            sys.stdout.write(f"\033[1E\033[{self.pos.x-1}C")
            # sys.stdout.write(f"\033[{self.pos.y + i};{self.pos.x}H")
        # sys.stdout.write("\033[10;10H")
        sys.stdout.flush()
        # print(f"\033[{(self.screen.height / 2)+2};1H\033[0J", end="")

class TextSprite(Layer):

    def __init__(self, pos, size, collision_box, children, frames, frame_id=0):
        super().__init__(pos, size, collision_box, children)

    def draw(self, parent):
        pass

class TextBox(Layer):

    def __init__(self, pos, size, collision_box, children, text):
        super().__init__(pos, size, collision_box, children)
        self.text = text

    def draw(self, parent):
        pass

class FillBox(PixelSprite):

    def __init__(self, pos, size, collision_box, children, color):
        frames = (tuple(tuple(color for x in range(size.x)) for y in range(size.y)),)
        super().__init__(pos, size, collision_box, children, frames)
        self.color = color

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



# square1 = [[1, 1, 3, 1, 1],
#            [1,-1,-1,-1, 1],
#            [3,-1,-1,-1, 3],
#            [1,-1,-1,-1, 1],
#            [1, 1, 3, 1, 1]]

# square2 = [[4, 4, 6, 4, 4],
#            [4,-1,-1,-1, 4],
#            [6,-1,-1,-1, 6],
#            [4,-1,-1,-1, 4],
#            [4, 4, 6, 4, 4]]



# input handling, stole this from stackoverflow heh
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
 
