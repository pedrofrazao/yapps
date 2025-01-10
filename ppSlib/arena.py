import uuid

class ArenaObject:
    """A class representing an object in the arena."""
    def __init__(self, name, volume=1, object=None):
        self.name = name
        self.id = uuid.uuid4()
        self.volume = volume
        self.object = object

    def __repr__(self):
        return f"ArenaObject(name={self.name})"

class Arena:
    """A class representing the arena."""
    def __init__(self, rows, cols, arena_type='plan', max_volume_per_position=100):
        self.rows = rows
        self.cols = cols
        self.type = arena_type
        self.max_volume_per_position = max_volume_per_position
        self.grid = [[[] for _ in range(cols)] for _ in range(rows)]
        self.num_objects = 0

    def get_position(self, x, y):
        """Get the list of objects at position (x, y)."""
        return self.grid[x][y]

    def get_num_objects(self, x, y):
        """Get the number of objects at position (x, y)."""
        return len(self.grid[x][y])

    def get_total_volume(self, x, y):
        """Get the total volume of objects at position (x, y)."""
        return sum(obj.volume for obj in self.grid[x][y])

    def del_position(self, x, y):
        """Delete all objects at position (x, y) and return them."""
        objects = self.grid[x][y]
        self.grid[x][y] = []
        self.num_objects -= len(objects)
        return objects

    def set_position(self, x, y, objects):
        """Set the list of objects at position (x, y)."""
        self.grid[x][y] = objects
        self.num_objects += len(objects)

    def add_to_position(self, x, y, obj):
        """Add an object to the list at position (x, y)."""
        if self.get_total_volume(x, y) + obj.volume > self.max_volume_per_position:
            return False
        self.grid[x][y].append(obj)
        self.num_objects += 1
        return True

    def remove_from_position(self, x, y, obj):
        """Remove an object from the list at position (x, y) and return it."""
        self.grid[x][y].remove(obj)
        self.num_objects -= 1
        return obj

    def convert_position(self, x, y):
        if self.type == 'torus':
            x = x % self.rows
            y = y % self.cols
            return (x, y)
        elif 0 <= x < self.rows and 0 <= y < self.cols:
            return (x, y)
        else:
            return (None, None)

    def move_object_position(self, x, y, obj, direction, length=1):
        """Move an object from position (x, y) in the given direction.
        
        direction can be 'up', 'down', 'left', or 'right' OR
        123
        4 6
        789
        where 5 is the object and 1, 2, 3, 4, 6, 7, 8, 9 are the directions
        """
        self.remove_from_position(x, y, obj)
        ox, oy = x, y
        if direction == 'up' or direction == 2:
            x -= length
        elif direction == 'down' or direction == 8:
            x += length
        elif direction == 'left' or direction == 4:
            y -= length
        elif direction == 'right' or direction == 6:
            y += length
        elif direction == 1:
            x -= length
            y -= length
        elif direction == 3:
            x -= length
            y += length
        elif direction == 7:
            x += length
            y -= length
        elif direction == 9:
            x += length
            y += length
        x, y = self.convert_position(x, y)
        if x is None or y is None:
            return False
        if self.add_to_position(x, y, obj) is False:
            self.add_to_position(ox, oy, obj)
            return False
        return True
    
    def __str__(self):
        """Create a string representation of the arena with the number of objects at each position."""
        arena_str = ""
        for row in self.grid:
            row_str = " ".join(str(len(cell)) for cell in row)
            arena_str += row_str + "\n"
        return arena_str