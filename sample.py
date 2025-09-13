from main import *
import time

# set up the screen here
screen = Screen(
    colorMode=256,
    height=32,
    width=64,
    color=1 
)

mario = [
    [ -1, -1, -1,203,203,203,203,203,203, -1, -1, -1,],
    [ -1, -1,203,203,203,203,203,203,203,203,203,203,],
    [ -1, -1, 94, 94, 94,223,223,223,  0,223, -1, -1,],
    [ -1, 94,223, 94,223,223,223,223,  0,223,223, -1,],
    [ -1, 94,223, 94, 94,223,223,223,223,  0,223,223,],
    [ -1, 94, 94,223,223,223,223,223,  0,  0,  0,  0,],
    [ -1, -1, -1,223,223,223,223,223,223,223,223, -1,],
    [ -1, -1,203,203, 31,203,203,203,203, -1, -1, -1,],
    [ -1,203,203,203, 31,203,203, 31,203,203,203, -1,],
    [203,203,203,203, 31, 31, 31, 31,203,203,203,203,],
    [223,223,203, 31, 11, 31, 31, 11, 31,203,223,223,],
    [223,223,223, 31, 31, 31, 31, 31, 31,223,223,223,],
    [223,223, 31, 31, 31, 31, 31, 31, 31, 31,223,223,],
    [ -1, -1, 31, 31, 31, 31, 31, 31, 31, 31, -1, -1,],
    [ -1, 94, 94, 94, -1, -1, -1, -1, 94, 94, 94, -1,],
    [ 94, 94, 94, 94, -1, -1, -1, -1, 94, 94, 94, 94,],
]

# shave the white px out of MARIO
# for x, y in enumerate(pictureOfMarioInArrayFormatBruh):
#     for z, w in enumerate(y):
#         if w == 255:
#             pictureOfMarioInArrayFormatBruh[x][z] = -1

def ready(game):
    print("\033[2J\33[?25l") # clear screen + hide cursor
    
    game.FPS = 1
    game.move = "Use arrow keys to move!"
    game.input = InputHandler("esc", "q", "upArrow", "downArrow", "rightArrow", "leftArrow") # add keys to track

    class Mario(PixelSprite):
        def __init__(self, hp=3):
            super().__init__((0,0), frames=(mario,))
            self.speed = 64

        def move(self, direction, deltaTime):
            i = round(self.speed * deltaTime)
            super().move(direction, i)
    
    redSquare = FillBox((0,0), (10,10), color=1)
    yellowSquare = FillBox((2,0), (5,5), color=3)
    greenSquare = FillBox((5,5), (10,10), color=2)
    game.mario = Mario()
    camera = FillBox((0,0), (92,64), color=59)

    greenSquare.children = [
        yellowSquare
    ]

    camera.children = [
        redSquare,
        greenSquare,
        game.mario
    ]

    game.box = camera
    game.box.screen = screen
    game.textbox = TextBox((94, 7), (26, 5), None, [], text=["123","45678","90"]) 
    game.textbox.screen = screen
    game.prevTime = time.time()

def process(game):
    time.sleep(0.01) # control framerate
    now = time.time()
    deltaTime = now - game.prevTime
    game.prevTime = now
    if deltaTime > 0:
        currentFPS = 1 / deltaTime
        game.FPS = 0.9 * game.FPS + 0.1 * currentFPS

    mario = game.mario

    # handle input
    game.input.updateKeyStates()
    keyDown = game.input.keyDown
    if keyDown("q", "esc"): # check multiple
        return True

    if keyDown("upArrow"): # check one
        mario.move("up", deltaTime)
        game.move = "up"

    if keyDown("downArrow"):
        mario.move("down", deltaTime)
        game.move = "down"

    if keyDown("rightArrow"): 
        mario.flipX = False
        mario.move("right", deltaTime)
        game.move = "right"

    if keyDown("leftArrow"): 
        
        mario.flipX = True
        mario.move("left", deltaTime)
        game.move = "left"
    
    # draw to console
    game.textbox.draw()
    game.box.draw()
    # time.sleep(1/60)
    # print(f"\033[94;1H\033[0J", end="")
    # print(f"\033[1J", end="")
    
    # --------------- I RECOMMEND PUTTING ALL PRINT STATEMENTS AFTER OUTPUTING LAYERS ---------------------------

    # debugging stuff
    game.textbox.text = [
        f"FPS: {game.FPS:.2f}",
        f"X: {mario.pos.x} Y: {mario.pos.y}",
        f"deltaTime: {deltaTime}",
        "click 'q' to quit",
    ]

game = Game(ready, process)
game.start()
