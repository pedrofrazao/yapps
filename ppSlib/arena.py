import uuid
import pickle
import base64
import random

from pos_object import positional_object

class ArenaObject:
    """Generic class to representing an object in the arena."""
    def __init__(self, name, volume=1, object=None):
        self.name = name
        self.x = None
        self.y = None
        self.id = uuid.uuid4()
        self.remove_on_move_out = True
        self.volume = volume
        self.object = object
        self.can_move = True
        self.msg = []
        self.max_msg = 5

    def serialize(self):
        """Serialize the ArenaObject to a dictionary."""
        return base64.b64encode(pickle.dumps(self)).decode('utf-8')
    
    @classmethod
    def deserialize(cls, data):
        """Deserialize a dictionary to an ArenaObject."""
        return pickle.loads(base64.b64decode(data))

    def setposition(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"ArenaObject(name={self.name})"
    
    def __str__(self):
        return ','.join( self.name, self.x, self.y )
    
    def add_msg(self, msg):
        self.msg.append(msg)
        self.msg = self.msg[-self.max_msg:]

class Arena:
    """A class representing the arena."""
    def __init__(self, rows, cols, arena_type='torus', max_volume_per_position=100):
        self.rows = rows
        self.cols = cols
        self.type = arena_type
        self.max_volume_per_position = max_volume_per_position
        self.grid = [[[] for _ in range(cols)] for _ in range(rows)]
        self.num_objects = 0

    def serialize(self):
        """Serialize the Arena to a dictionary."""
        data = {
            'rows': self.rows,
            'cols': self.cols,
            'type': self.type,
            'max_volume_per_position': self.max_volume_per_position,
            'objects': [obj.serialize() for row in self.grid for cell in row for obj in cell],
            'num_objects': self.num_objects
        }
        return data
    
    @classmethod
    def deserialize(cls, data):
        """Deserialize a dictionary to an Arena object."""
        arena = cls(data['rows'], data['cols'], data['type'], data['max_volume_per_position'])
        # arena.num_objects = data['num_objects'] -- Will be defined on the add_to_position method phase
        for obj_data in data['objects']:
            obj = ArenaObject.deserialize(obj_data)
            arena.add_to_position(obj.x,obj.y,obj)
        return arena

    # def json_serialize(self):
    #     return json.dumps(self.serialize())
    
    # @classmethod
    # def json_deserialize(cls, data):    
    #     return cls.deserialize(json.loads(data))

    def get_objects(self):
        return [obj for row in self.grid for cell in row for obj in cell]

    def get_pos_obj_list(self):
        # pos_obj_list = []
        # for row in range(self.rows):
        #     for col in range(self.cols):
        #         for obj in self.grid[row][col]:
        #             pos_obj_list.append(positional_object(row, col, None, obj.name))
        # return pos_obj_list
        return [positional_object(obj.x, obj.y, None, obj.name) for obj in self.get_objects()]

    def _move_objects_at_random(self):
        for o in self.get_objects():
            if o.can_move:
                self.move_object_position(o, random.choice(['up', 'down', 'left', 'right']))


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
        for obj in objects:
            obj.setposition(x,y)
        self.grid[x][y] = objects
        self.num_objects += len(objects)

    def add_to_position(self, x, y, obj):
        """Add an object to the list at position (x, y)."""
        if self.get_total_volume(x, y) + obj.volume > self.max_volume_per_position:
            return False
        self.grid[x][y].append(obj)
        self.num_objects += 1
        obj.setposition(x,y)
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

    def move_object_position(self, obj, direction, length=1):
        """Move an object from position (x, y) in the given direction.
        
        direction can be 'up', 'down', 'left', or 'right' OR
        123
        4 6
        789
        where 5 is the object and 1, 2, 3, 4, 6, 7, 8, 9 are the directions
        """ 
        x = obj.x
        y = obj.y
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
            # impossible move
            if obj.remove_on_move_out:
                # remove object from arena
                self.remove_from_position(obj.x, obj.y, obj)
                obj.add_msg(f"{obj.name} moved out ({obj.x},{obj.y}) -> {x},{y})")
                return True
            else:
                return False

        # apply the move
        ox,oy = obj.x, obj.y
        if self.add_to_position(x, y, obj) is True:
            self.remove_from_position(ox, oy, obj)
            obj.add_msg(f"{obj.name} moved ({ox,oy}) -> {x},{y})")
            return True
        else:
            return False


    def __str__(self):
        """Create a string representation of the arena with the number of objects at each position."""
        arena_str = ""
        for row in self.grid:
            row_str = " ".join(str(len(cell)) for cell in row)
            arena_str += row_str + "\n"
        return arena_str
    
class Surrounding:
    """A class representing the surrounding of an object in the arena."""
    def __init__(self, arena, x, y, direction=0, length=1):
        self.arena = arena
        self.x = x
        self.y = y
        self.direction = direction
        self.length = length
        self.objects = self.get_surrounding()

    def get_surrounding(self):
        """Get the surrounding objects of the current position."""
        surrounding = []
        for i in range( self.x - self.length, self.x + self.length +1 ):
            for j in range( self.y - self.length, self.y + self.length +1 ):
                pi,pj = self.arena.convert_position(i, j)
                if pi is None or pj is None:
                    continue
                else:
                    surrounding.extend(self.arena.get_position(pi, pj))
        return surrounding
