class positional_object:
    """object to store a position in 2D space"""
    def __init__(self, x,y, color=None, text=None):
        self.x = x
        self.y = y
        self.color = color
        self.text = text

    def get(self):
        return (self.x, self.y, self.color, self.text)