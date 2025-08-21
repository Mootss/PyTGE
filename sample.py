from main import *
import time

# set up the screen here
screen = Screen(
    colorMode=8,
    height=32,
    width=64,
    # heigth and width must be an even number
    color=1 #59
    # in 8 colorMode to set red u will write color=1, bec 1 is red, bec 41 and 31 is red. in 8 colormode only use the last digit 
)

pictureOfMarioInArrayFormatBruh = [[255,255,255,203,203,203,203,203,203,255,255,255],[255,255,203,203,203,203,203,203,203,203,203,203],[255,255,94,94,94,223,223,223,0,223,255,255],[255,94,223,94,223,223,223,223,0,223,223,255],[255,94,223,94,94,223,223,223,223,0,223,223],[255,94,94,223,223,223,223,223,0,0,0,0],[255,255,255,223,223,223,223,223,223,223,223,255],[255,255,203,203,31,203,203,203,203,255,255,255],[255,203,203,203,31,203,203,31,203,203,203,255],[203,203,203,203,31,31,31,31,203,203,203,203],[223,223,203,31,11,31,31,11,31,203,223,223],[223,223,223,31,31,31,31,31,31,223,223,223],[223,223,31,31,31,31,31,31,31,31,223,223],[255,255,31,31,31,31,31,31,31,31,255,255],[255,94,94,94,255,255,255,255,94,94,94,255],[94,94,94,94,255,255,255,255,94,94,94,94]]

# shave the white px out of MARIO
# for x, y in enumerate(pictureOfMarioInArrayFormatBruh):
#     for z, w in enumerate(y):
#         if w == 255:
#             pictureOfMarioInArrayFormatBruh[x][z] = -1

# create the MARIO!
# mario = Sprite(
#     array= pictureOfMarioInArrayFormatBruh,
#     posX=5,
#     posY=5
# )

def ready(game):
    print("\033[2J\33[?25l") # clear screen + hide cursor
    game.prevTime = time.time()
    game.FPS = 1
    game.move = "You haven't moved yet! use arrow keys to move!"

def process(game):
    # handle input
    key = getKey() # getKey returns a key u click
    if key:
        if key.lower() == "q":
            running = False

        elif key in ["H", "A"]: # up
            mario.move("up", 1)
            move = "up"

        elif key in ["P", "B"]: # down
            mario.move("down", 1)
            move = "down"

        elif key in ["M", "C"]: # right
            mario.move("right", 1)
            move = "right"

        elif key in ["K", "D"]: # left
            mario.move("left", 1)
            move = "left"

        # H P M K is for windows, A B C D is for unix
    
    # draw the shits
    screen.drawSprite(mario) # this inserts the sprite into the screen array but doesnt actually print to terminal
    screen.render() # this prints the "pixel screen"
    
    # --------------- I RECOMMEND PUTTING ALL PRINT STATEMENTS AFTER screen.render() ---------------------------

    # debugging stuff
    #time.sleep(0.05) # control framerate
    now = time.time()
    dt = now - prevTime
    prevTime = now
    if dt > 0:
        currentFPS = 1 / dt
        FPS = 0.9 * FPS + 0.1 * currentFPS  

    print(f"FPS: {FPS:.2f}")
    print(f"X: {mario.posX} Y: {mario.posY}")
    print(f"move: {move}")
    print("click 'q' to quit")
    FPS+=1

box = FillBox((0,0), (4,4), None, None, color=1)
box.screen = screen
box.render()
