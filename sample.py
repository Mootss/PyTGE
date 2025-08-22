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
    game.prevTime = time.time()
    game.FPS = 1
    game.move = "Use arrow keys to move!"

    class Mario(PixelSprite):

        def __init__(self):
            super().__init__((0,0), (len(mario[0]), len(mario)), None, [], (mario,))

    game.box = FillBox((0,0), (64,32), None, [
        FillBox((0,0), (10,10), None, [], color=1),
        FillBox((5,5), (10,10), None, [
            FillBox((2,0), (5,5), None, [], color=3),
        ], color=2),
        Mario()
    ], color=59)
    game.box.screen = screen
    game.textbox = TextBox((66, 7), (26, 5), None, [], text=["123","45678","90"]) 
    game.textbox.screen = screen

def process(game):
    mario = game.box.children[-1]
    # handle input
    key = getKey() # getKey returns a key u click
    if key:
        if key.lower() == "q":
            return True

        elif key in ["H", "A"]: # up
            mario.move("up", 1)
            game.move = "up"

        elif key in ["P", "B"]: # down
            mario.move("down", 1)
            game.move = "down"

        elif key in ["M", "C"]: # right
            mario.flipX = False
            mario.move("right", 1)
            game.move = "right"

        elif key in ["K", "D"]: # left
            
            mario.flipX = True
            mario.move("left", 1)
            game.move = "left"

        
    
    # draw to console
    game.textbox.draw()
    game.box.draw()
    # time.sleep(1/60)
    # print(f"\033[94;1H\033[0J", end="")
    # print(f"\033[1J", end="")
    
    # --------------- I RECOMMEND PUTTING ALL PRINT STATEMENTS AFTER OUTPUTING LAYERS ---------------------------

    # debugging stuff
    #time.sleep(0.05) # control framerate
    now = time.time()
    dt = now - game.prevTime
    game.prevTime = now
    if dt > 0:
        currentFPS = 1 / dt
        game.FPS = 0.9 * game.FPS + 0.1 * currentFPS

    game.textbox.text = [
        f"FPS: {game.FPS:.2f}",
        f"X: {mario.pos.x} Y: {mario.pos.y}",
        f"move: {game.move}",
        "click 'q' to quit",
    ]

game = Game(ready, process)
game.start()
