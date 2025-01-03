import random
from tkinter import *
import time
import pygame

# Initialize pygame mixer for sound playback
pygame.mixer.init()

try:
    background_music = pygame.mixer.Sound("C418_-_Subwoofer_Lullaby_30921632.mp3")
    block_break_sound = pygame.mixer.Sound("clash-royale-laugh.mp3")
except pygame.error as e:
    print(f"Sound loading error: {e}")

class Ball:
    def __init__(self, canvas, platform, blocks, color, x_velocity=None, y_velocity=None):
        self.canvas = canvas
        self.platform = platform
        self.blocks = blocks
        self.oval = canvas.create_oval(200, 200, 215, 215, fill=color)
        self.dir = [-3, -2, -1, 1, 2, 3]
        self.x = x_velocity if x_velocity else random.choice(self.dir)
        self.y = y_velocity if y_velocity else -1
        self.touch_bottom = False

    def touch_platform(self, ball_pos):
        platform_pos = self.canvas.coords(self.platform.rect)
        if ball_pos[2] >= platform_pos[0] and ball_pos[0] <= platform_pos[2]:
            if ball_pos[3] >= platform_pos[1] and ball_pos[3] <= platform_pos[3]:
                return True
        return False

    def draw(self):
        self.canvas.move(self.oval, self.x, self.y)
        pos = self.canvas.coords(self.oval)
        if pos[1] <= 0:
            self.y = 3
        if pos[3] >= 400:
            self.touch_bottom = True
        if self.touch_platform(pos):
            self.y = -3
        if self.touch_block(pos):
            self.y *= -1
        if pos[0] <= 0:
            self.x = 3
        if pos[2] >= 500:
            self.x = -3

    def touch_block(self, ball_pos):
        blocks_to_remove = []
        line_y_coords = set()

        for block in self.blocks:
            block_pos = self.canvas.coords(block.rect)
            if ball_pos[2] >= block_pos[0] and ball_pos[0] <= block_pos[2]:
                if ball_pos[1] <= block_pos[3] and ball_pos[3] >= block_pos[1]:
                    blocks_to_remove.append(block)
                    line_y_coords.add(block_pos[1])

                    block_color = self.canvas.itemcget(block.rect, "fill")
                    if block_color == "red":
                        self.x *= 2
                        self.y *= 2
                    elif block_color == "blue":
                        self.x *= 0.5
                        self.y *= 0.5
                    elif block_color == "green":
                        self.split_ball()

        if blocks_to_remove:
            for block in blocks_to_remove:
                self.canvas.delete(block.rect)
                self.blocks.remove(block)

            for line_y in line_y_coords:
                if not self.canvas.find_enclosed(0, line_y, 500, line_y + 20):
                    add_new_block_line(self.blocks, self.canvas)

            if block_break_sound:
                block_break_sound.play()

            return True
        return False

    def split_ball(self):
        new_ball = Ball(self.canvas, self.platform, self.blocks, 'red', self.x, -self.y)
        balls.append(new_ball)

class Platform:
    def __init__(self, canvas, color):
        self.canvas = canvas
        self.rect = canvas.create_rectangle(230, 300, 330, 310, fill=color)
        self.x = 0
        self.canvas.bind_all('<KeyPress-Left>', self.left)
        self.canvas.bind_all('<KeyRelease-Left>', self.stop)
        self.canvas.bind_all('<KeyPress-Right>', self.right)
        self.canvas.bind_all('<KeyRelease-Right>', self.stop)

    def left(self, event):
        self.x = -4

    def right(self, event):
        self.x = 4

    def stop(self, event):
        self.x = 0

    def draw(self):
        self.canvas.move(self.rect, self.x, 0)
        pos = self.canvas.coords(self.rect)
        if pos[0] <= 0:
            self.x = 0
        if pos[2] >= 500:
            self.x = 0

class Block:
    def __init__(self, canvas, x1, y1, x2, y2, color):
        self.canvas = canvas
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=color)

def create_blocks(canvas):
    blocks = []
    y_offset = 50
    colors = ['red', 'blue', 'green', 'grey']
    block_distribution = [5, 5, 3, 32]  # Number of each type of blocks

    for i in range(5):
        row_colors = random.choices(colors, weights=block_distribution, k=10)
        for j, color in enumerate(row_colors):
            blocks.append(Block(canvas, j * 50, y_offset, j * 50 + 45, y_offset + 20, color))
        y_offset += 25
    return blocks

def add_new_block_line(blocks, canvas):
    new_block_y = 25
    for j in range(10):
        blocks.append(Block(canvas, j * 50, new_block_y, j * 50 + 45, new_block_y + 20, 'grey'))

def play_music():
    try:
        background_music.play(-1)
    except pygame.error as e:
        print(f"Error playing music: {e}")

def restart_game():
    global blocks, platform, balls, restart_button
    # Clear canvas
    canvas.delete("all")

    # Recreate blocks, platform, and ball
    blocks = create_blocks(canvas)
    platform = Platform(canvas, 'green')
    balls = [Ball(canvas, platform, blocks, 'red')]

    # Hide the restart button
    restart_button.place_forget()

    # Start playing music again
    play_music()

def show_restart_button():
    restart_button.place(relx=0.5, rely=0.5, anchor=CENTER)

# Initialize the main window
window = Tk()
window.title("Arkanoid")
window.resizable(0, 0)
window.wm_attributes("-topmost", 1)

canvas = Canvas(window, width=500, height=400)
canvas.pack()

# Create Restart button but don't display it yet
restart_button = Button(window, text="Restart", command=restart_game)

# Begin the game
restart_game()

while True:
    if not blocks or not balls:  # Game ends if all blocks are broken or all balls are lost
        show_restart_button()
    else:
        for ball in balls[:]:  # Iterate over a copy of the list to allow modifications
            if not ball.touch_bottom:
                ball.draw()
            else:
                balls.remove(ball)

        platform.draw()

    window.update()
    time.sleep(0.01)

window.mainloop()

pygame.mixer.music.stop()  # Stop music when the game ends
