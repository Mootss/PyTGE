# 18/8/25
# to do:
# implement transparent pixels (impotrant)
# add option to modify screen border behaviour, aka when sprite hit end of array
# add option load a background image into bg array
# handle odd arays for bg array
# fix displaying text
# add sprite collision detection
# make minecraft?

#from random import choice
import time
import sys
import os

def createShape(color, width, height): # 2d array
    return [[color for x in range(width)] for y in range(height)]

class Screen():
    uhb = "\u2580" # upper half block ▀
    #bit3 = "\u001b"
    #bit8 = "\033[38;5;0m"

    def __init__(self, colorMode, height, width, color=0):
        self.colorMode = colorMode
        # colorMode should be 8 or 256. thats the number of colors to be used
        # fyi, all 8 color arrays can be displaed in 256 but not vice versa
        self.height = height
        self.width = width
        self.color = color # if undefined, default = black
        self.array = createShape(self.color, self.width, self.height)
        self.displayArray = [row[:] for row in self.array]
        # sprite eh draw kuran v ma do it by modifying display array instead of og array, so og array can be re-used when a sprite is moved
        # im sure theres a more efficient way to do ts but my sikundi too smol

    def draw(self, fg, bg): # draws 1 character (which is 2 px)
        if self.colorMode == 8:
            return f"\u001b[3{fg}m\u001b[4{bg}m{self.uhb}\u001b[0m" # \u001b[0m actually only needs to be written at the end of each line but wtver
        elif self.colorMode == 256:
            return f"\033[38;5;{fg}m\033[48;5;{bg}m{self.uhb}\u001b[0m"
        else:
            raise ValueError("ERROR: Invalid color mode, colorMode should be either 8 or 256")
    
    def render(self): # convert array to ansi & print it
        # todo: add a way to render transparent pixels aka no color pixels
        print("\033[2;1H", end="")
        lines = []
        pixels = []
        for y in range(0, len(self.displayArray), 2):
            for fg, bg in zip(self.displayArray[y], self.displayArray[y+1]):
                pixels.append(self.draw(fg, bg))
                #print(draw(fg, bg))
            lines.append("".join(pixels))
            pixels = []
            #print(lines)
        window = "\n".join(lines)
        print(window)
        print(f"\033[{(self.height / 2)+2};1H\033[0J", end="")
        self.reset()

    def reset(self):
        #self.displayArray = [[e for e in row] for row in self.array]
        self.displayArray = [row[:] for row in self.array]

    def drawSprite(self, sprite):
        # todo: add a check to see if there is enough space to insert the sprite
        for row in range(len(sprite.array)):
            for e in range(len(sprite.array[row])):
                if sprite.array[row][e] != -1:
                    self.displayArray[sprite.posY + row][sprite.posX + e] = sprite.array[row][e]
        

class Sprite():
    def __init__(self, array, posX, posY):
        self.array = array
        self.posX = posX
        self.posY = posY

    def move(self, direction, i): # i = increment amount
        direction = direction.lower()

        if direction == "up":
            self.posY -= i
        
        elif direction == "down":
            self.posY += i

        elif direction == "right":
            self.posX += i

        elif direction == "left":
            self.posX -= i
        else:
            raise ValueError("ERROR: Invalid direction, accepted directions are: 'up', 'down', 'right', 'left'")
        
    def flip():
        pass
    
    def rotate():
        pass

class InputHandler():
    #not sure how to write ts
    pass


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
 