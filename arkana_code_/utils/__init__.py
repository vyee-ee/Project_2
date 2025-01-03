    def __init__(self, canvas, x1, y1, x2, y2, color):
        self.canvas = canvas
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=color)
