import sys
import os
import itertools
import json
import base64
import tempfile
import ctypes

OS = sys.platform
if OS == "win32":
    import winsound
    import msvcrt
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
        if (size == None) and frames:
            if (not frames[0]) or (len(frames[0]) <= 0):
                raise ValueError("Sprite frames empty!")
            self.size = Point(len(frames[0][0]), len(frames[0]))
        elif (size == None) and (frames == None):
                raise ValueError("Size must be provided when no frames are given!")
        else:
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

    def __init__(self, pos, size=None, collision_box=None, children=[], frames=None, frame_id=0):
        super().__init__(pos, size, collision_box, children, frames, frame_id)

        self.uhb = "\u2580" # upper half block ▀
        self.flipX = False
        self.flipY = False

    def render_char(self, x, y): # draws 1 character (which is 2 px)
        frame = self.rendered_frame
        fg = frame[y*2][x]
        bg = frame[y*2+1][x]
        if self.screen.colorMode == 8:
            return f"\033[3{fg}m;[4{bg}m{self.uhb}"
        elif self.screen.colorMode == 256:
            return f"\033[38;5;{fg};48;5;{bg}m{self.uhb}"
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
        sys.stdout.write(f"\033[H{"\n".join([
            "".join(self.render_char(x, y) for x in range(len(self.rendered_frame[y])))
            for y in range(len(self.rendered_frame) // 2)
        ])}\033[0m")
        sys.stdout.flush()

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
        frame = frame[:self.size.y]
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
        for l in lines:
            sys.stdout.write(l[:self.size.x])
            sys.stdout.write(f"\033[1E\033[{self.pos.x-1}C")
        sys.stdout.flush()
        # print(f"\033[{(self.screen.height / 2)+2};1H\033[0J", end="")

class FillBox(PixelSprite):

    def __init__(self, pos, size, collision_box=None, children=[], color=0):
        super().__init__(pos, size, collision_box, children, None)
        self.set_color(color)

    def set_color(self, color):
        self.color = color
        self.frames = (tuple(tuple(color for x in range(self.size.x)) for y in range(self.size.y)),)

class TextToSprite(PixelSprite):
    #       caseSensitive\
    #       add more fonts
    def __init__(self, pos, text, font, color=0, wordSpace=5, charSpace=1):
        # wordSpace = space between words, charSpace = space between characters
        self.text = str(text)
        self.font = font
        self.color = color
        self.wordSpace = wordSpace
        self.charSpace = charSpace
        super().__init__(pos, frames=(self.renderText(),))

    def renderText(self):
        row = []
        final = []
        for i in range(len(self.font["a"])):
            for char in self.text:
                if char == " ":
                    row.extend([-1] * (self.wordSpace - self.charSpace))
                else:
                    row.extend([(self.color if pixel != -1 else -1) for pixel in self.font[char][i]] + ([-1] * self.charSpace))
            final.append(row)
            row = []
        return final

class Fonts():
    minecraft = {
        "caseSensitive": True,
        "A": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,0,0,0,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "B": [[0,0,0,0,-1],[0,-1,-1,-1,0],[0,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,0,0,0,-1]],
        "C": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "D": [[0,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,0,0,0,-1]],
        "E": [[0,0,0,0,0],[0,-1,-1,-1,-1],[0,0,0,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,0,0,0,0]],
        "F": [[0,0,0,0,0],[0,-1,-1,-1,-1],[0,0,0,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1]],
        "G": [[-1,0,0,0,0],[0,-1,-1,-1,-1],[0,-1,-1,0,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "H": [[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,0,0,0,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "I": [[0,0,0],[-1,0,-1],[-1,0,-1],[-1,0,-1],[-1,0,-1],[-1,0,-1],[0,0,0]],
        "J": [[-1,-1,-1,-1,0],[-1,-1,-1,-1,0],[-1,-1,-1,-1,0],[-1,-1,-1,-1,0],[-1,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "K": [[0,-1,-1,-1,0],[0,-1,-1,0,-1],[0,0,0,-1,-1],[0,-1,-1,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "L": [[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,0,0,0,0]],
        "M": [[0,-1,-1,-1,0],[0,0,-1,0,0],[0,-1,0,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "N": [[0,-1,-1,-1,0],[0,0,-1,-1,0],[0,-1,0,-1,0],[0,-1,-1,0,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "O": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "P": [[0,0,0,0,-1],[0,-1,-1,-1,0],[0,0,0,0,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1]],
        "Q": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,0,-1],[-1,0,0,-1,0]],
        "R": [[0,0,0,0,-1],[0,-1,-1,-1,0],[0,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "S": [[-1,0,0,0,0],[0,-1,-1,-1,-1],[-1,0,0,0,-1],[-1,-1,-1,-1,0],[-1,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "T": [[0,0,0,0,0],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1]],
        "U": [[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "V": [[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,-1,0,-1],[-1,0,-1,0,-1],[-1,-1,0,-1,-1]],
        "W": [[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,0,-1,0],[0,0,-1,0,0],[0,-1,-1,-1,0]],
        "X": [[0,-1,-1,-1,0],[-1,0,-1,0,-1],[-1,-1,0,-1,-1],[-1,0,-1,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "Y": [[0,-1,-1,-1,0],[-1,0,-1,0,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1]],
        "Z": [[0,0,0,0,0],[-1,-1,-1,-1,0],[-1,-1,-1,0,-1],[-1,-1,0,-1,-1],[-1,0,-1,-1,-1],[0,-1,-1,-1,-1],[0,0,0,0,0]],
        "a": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[-1,0,0,0,-1],[-1,-1,-1,-1,0],[-1,0,0,0,0],[0,-1,-1,-1,0],[-1,0,0,0,0]],
        "b": [[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,0,0,-1],[0,0,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,0,0,0,-1]],
        "c": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,-1],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "d": [[-1,-1,-1,-1,0],[-1,-1,-1,-1,0],[-1,0,0,-1,0],[0,-1,-1,0,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,0]],
        "e": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,0,0,0,0],[0,-1,-1,-1,-1],[-1,0,0,0,0]],
        "f": [[-1,-1,-1,0,0],[-1,-1,0,-1,-1],[-1,0,0,0,0],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1]],
        "g": [[-1,-1,-1,-1,-1],[-1,0,0,0,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,0],[-1,-1,-1,-1,0],[0,0,0,0,-1]],
        "h": [[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,0,0,-1],[0,0,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "i": [[0],[-1],[0],[0],[0],[0],[0]],
        "j": [[-1,-1,-1,-1,0],[-1,-1,-1,-1,-1],[-1,-1,-1,-1,0],[-1,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "k": [[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,0,-1],[0,-1,0,-1,-1],[0,0,-1,-1,-1],[0,-1,0,-1,-1],[0,-1,-1,0,-1]],
        "l": [[0,-1],[0,-1],[0,-1],[0,-1],[0,-1],[0,-1],[-1,0]],
        "m": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,0,-1,0,-1],[0,-1,0,-1,0],[0,-1,0,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "n": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0]],
        "o": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "p": [[-1,-1,-1,-1,-1],[0,-1,0,0,-1],[0,0,-1,-1,0],[0,-1,-1,-1,0],[0,0,0,0,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1]],
        "q": [[-1,-1,-1,-1,-1],[-1,0,0,-1,0],[0,-1,-1,0,0],[0,-1,-1,-1,0],[-1,0,0,0,0],[-1,-1,-1,-1,0],[-1,-1,-1,-1,0]],
        "r": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,-1,0,0,-1],[0,0,-1,-1,0],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1],[0,-1,-1,-1,-1]],
        "s": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[-1,0,0,0,0],[0,-1,-1,-1,-1],[-1,0,0,0,-1],[-1,-1,-1,-1,0],[0,0,0,0,-1]],
        "t": [[-1,0,-1],[0,0,0],[-1,0,-1],[-1,0,-1],[-1,0,-1],[-1,0,-1],[-1,-1,0]],
        "u": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,0]],
        "v": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,-1,0,-1],[-1,-1,0,-1,-1]],
        "w": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,0,-1,0],[0,-1,0,-1,0],[-1,0,0,0,0]],
        "x": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,-1,-1,-1,0],[-1,0,-1,0,-1],[-1,-1,0,-1,-1],[-1,0,-1,0,-1],[0,-1,-1,-1,0]],
        "y": [[-1,-1,-1,-1,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,0],[-1,-1,-1,-1,0],[0,0,0,0,-1]],
        "z": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,0,0,0,0],[-1,-1,-1,0,-1],[-1,-1,0,-1,-1],[-1,0,-1,-1,-1],[0,0,0,0,0]],
        "0": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,0,0],[0,-1,0,-1,0],[0,0,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "1": [[-1,-1,0,-1,-1],[-1,0,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[0,0,0,0,0]],
        "2": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[-1,-1,-1,-1,0],[-1,-1,0,0,-1],[-1,0,-1,-1,-1],[0,-1,-1,-1,-1],[0,0,0,0,0]],
        "3": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[-1,-1,-1,-1,0],[-1,-1,0,0,-1],[-1,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "4": [[-1,-1,-1,0,0],[-1,-1,0,-1,0],[-1,0,-1,-1,0],[0,-1,-1,-1,0],[0,0,0,0,0],[-1,-1,-1,-1,0],[-1,-1,-1,-1,0]],
        "5": [[0,0,0,0,0],[0,-1,-1,-1,-1],[0,0,0,0,-1],[-1,-1,-1,-1,0],[-1,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "6": [[-1,-1,0,0,-1],[-1,0,-1,-1,-1],[0,-1,-1,-1,-1],[0,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "7": [[0,0,0,0,0],[0,-1,-1,-1,0],[-1,-1,-1,-1,0],[-1,-1,-1,0,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1]],
        "8": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,-1]],
        "9": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,-1,-1,0],[-1,0,0,0,0],[-1,-1,-1,-1,0],[-1,-1,-1,0,-1],[-1,0,0,-1,-1]],
        ".": [[-1],[-1],[-1],[-1],[-1],[-1],[0]],
        ",": [[-1],[-1],[-1],[-1],[-1],[0],[0]],
        ":": [[-1],[-1],[0],[-1],[-1],[0],[-1]],
        ";": [[-1],[-1],[0],[-1],[-1],[0],[0]],
        "'": [[0],[0],[-1],[-1],[-1],[-1],[-1]],
        "!": [[0],[0],[0],[0],[0],[-1],[0]],
        '"': [[0,-1,0],[0,-1,0],[-1,-1,-1],[-1,-1,-1],[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]],
        "#": [[-1,0,-1,0,-1],[-1,0,-1,0,-1],[0,0,0,0,0],[-1,0,-1,0,-1],[0,0,0,0,0],[-1,0,-1,0,-1],[-1,0,-1,0,-1]],
        "$": [[-1,-1,0,-1,-1],[-1,0,0,0,0],[0,-1,0,-1,-1],[-1,0,0,0,-1],[-1,-1,0,-1,0],[0,0,0,0,-1],[-1,-1,0,-1,-1]],
        "/": [[-1,-1,-1,-1,0],[-1,-1,-1,0,-1],[-1,-1,-1,0,-1],[-1,-1,0,-1,-1],[-1,0,-1,-1,-1],[-1,0,-1,-1,-1],[0,-1,-1,-1,-1]],
        "%": [[0,-1,-1,-1,0],[0,-1,-1,0,-1],[-1,-1,-1,0,-1],[-1,-1,0,-1,-1],[-1,0,-1,-1,-1],[-1,0,-1,-1,0],[0,-1,-1,-1,0]],
        "?": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[-1,-1,-1,-1,0],[-1,-1,-1,0,-1],[-1,-1,0,-1,-1],[-1,-1,-1,-1,-1],[-1,-1,0,-1,-1]],
        "&": [[-1,-1,0,-1,-1],[-1,0,-1,0,-1],[-1,-1,0,-1,-1],[-1,0,0,-1,0],[0,-1,0,0,-1],[0,-1,-1,0,-1],[-1,0,0,-1,0]],
        "(": [[-1,-1,0,0],[-1,0,-1,-1],[0,-1,-1,-1],[0,-1,-1,-1],[0,-1,-1,-1],[-1,0,-1,-1],[-1,-1,0,0]],
        ")": [[0,0,-1,-1],[-1,-1,0,-1],[-1,-1,-1,0],[-1,-1,-1,0],[-1,-1,-1,0],[-1,-1,0,-1],[0,0,-1,-1]],
        "@": [[-1,0,0,0,-1],[0,-1,-1,-1,0],[0,-1,0,-1,0],[0,-1,0,-1,0],[0,-1,0,0,0],[0,-1,-1,-1,-1],[-1,0,0,0,0]],
        "+": [[-1,-1,-1,-1,-1],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[0,0,0,0,0],[-1,-1,0,-1,-1],[-1,-1,0,-1,-1],[-1,-1,-1,-1,-1]],
        "-": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,0,0,0,0],[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1]],
        "=": [[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1],[0,0,0,0,0],[-1,-1,-1,-1,-1],[0,0,0,0,0],[-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1]]
    }

if os.name == 'nt':  # Windows
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
                try: # temporary solution
                    if not loop:
                        winsound.PlaySound(self.soundPaths[sound], winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NOSTOP)
                    else:
                        winsound.PlaySound(self.soundPaths[sound], winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NOSTOP | winsound.SND_LOOP)
                except RuntimeError:
                    pass
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
else:  # Unix (Linux, macOS)
    # dummy class
    class Audio():
        def __init__(self, sounds):
            pass
        def play(self, sound, loop=False):
            pass
        def stop(self):
            pass
        def cleanup(self): # should run this when exiting to delete all temp files created during runtime
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

    virtualKeyCodeMap = {
        "leftmousebutton": 0x01,
        "rightmousebutton": 0x02,
        "backspace": 0x08,
        "tab": 0x09,
        "enter": 0x0D,
        "shift": 0x10,
        "ctrl": 0x11,
        "alt": 0x12,
        "capslock": 0x14,
        "esc": 0x1B,
        "spacebar": 0x20,
        "uparrow": 0x26,
        "downarrow": 0x28,
        "rightarrow": 0x27,
        "leftarrow": 0x25,
        "0": 0x30,
        "1": 0x31,
        "2": 0x32,
        "3": 0x33,
        "4": 0x34,
        "5": 0x35,
        "6": 0x36,
        "7": 0x37,
        "8": 0x38,
        "9": 0x39,
        "a": 0x41,  
        "b": 0x42,  
        "c": 0x43,  
        "d": 0x44,  
        "e": 0x45,  
        "f": 0x46,    
        "g": 0x47,  
        "h": 0x48,  
        "i": 0x49,  
        "j": 0x4A,
        "k": 0x4B,
        "l": 0x4C,
        "m": 0x4D,
        "n": 0x4E,
        "o": 0x4F,
        "p": 0x50,
        "q": 0x51,
        "r": 0x52,
        "s": 0x53,
        "t": 0x54,
        "u": 0x55,
        "v": 0x56,
        "w": 0x57,
        "x": 0x58,
        "y": 0x59,
        "z": 0x5A,
        "+": 0x68,
        "-": 0x6D
    }

    def __init__(self, inputKeys):

        for key in inputKeys:
            if key.lower() not in self.virtualKeyCodeMap:
                raise ValueError(f"Key '{key}' was not found, pleaes check spelling and / or if given keys exists in virtualKeyCodeMap")
        self.keyStates = {str(key).lower(): False for key in inputKeys}
        self.getAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState

    def updateKeyStates(self):
        if msvcrt.kbhit(): 
            msvcrt.getch()
        for k in self.keyStates:
            if self.getAsyncKeyState(self.virtualKeyCodeMap[k]) > 0:
                self.keyStates[k] = True
            else: self.keyStates[k] = False 

    def keyDown(self, keys):
        if isinstance(keys, str):   
            keys = [keys]
        if not keys:
            raise ValueError("keyDown keys list is empty")
        keys = [k.lower() for k in keys]
        for k in keys:
            if k not in self.keyStates:
                raise ValueError(f"Given key '{k}' is not registered as an inputKey in the InputHandler")
            if self.keyStates[k]:
                return True
        