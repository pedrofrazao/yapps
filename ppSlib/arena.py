import uuid
import pickle
import base64
import random
import copy

from ppSlib.pos_object import positional_object

class ArenaObject:
    """
    Generic class to representing an object in the arena.
    with the following attributes:
    - name: the name of the object
    - volume: the volume of the object (default is 1)
    - can_move: a boolean indicating whether the object can move (default is True)
    - arena: the arena in which the object is located
    """
    def __init__(self, name, volume=1, can_move=True, arena=None):
        self.name = name
        self.x = None
        self.y = None
        self.id = uuid.uuid4()
        self.remove_on_move_out = True
        self.volume = volume
        self.can_move = can_move
        self.msg = []
        self.max_msg = 5
        self.arena = arena
        self.nickname = self.name[0] + self.name[-1]

    def __copy__(self):
        return ArenaObject(self.name, self.volume, self.object, self.can_move)

    def serialize(self):
        """Serialize the ArenaObject to a dictionary."""
        return base64.b64encode(pickle.dumps(self)).decode('utf-8')
    
    @classmethod
    def _deser_get_row_pos_from_data(cls,data):
        return data.get('row', data.get('x', None))

    @classmethod
    def _deser_get_col_pos_from_data(cls,data):
        return data.get('col', data.get('y', None))
    
    @classmethod
    def deserialize(cls, data):
        """Deserialize a dictionary to an ArenaObject."""
        result = None
        if isinstance(data, dict):
            result = cls(data['name'], data['volume'], None, data.get('can_move', True))
            if( data.get('positions', False) ):
                o = result
                result = []
                for x,y in data['positions']:
                    oo = copy.copy(o)
                    oo.setposition(x,y)
                    result.append( oo )
            else:
                result.setposition( cls._deser_get_row_pos_from_data(data),
                                    cls._deser_get_col_pos_from_data(data) )
            return result
        else:
            try:
                decoded_data = base64.b64decode(data)
                result = pickle.loads(decoded_data)
            except Exception:
                """fail to decode using base64"""
                result = None
            return result

    @classmethod
    def byclass(cls, data):
        """Deserialize a dictionary to an ArenaObject."""
        return cls(data['name'], data['volume'], None, data.get('can_move', True))

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

    def info(self):
        if( self.can_move is False ):
            return ""
        else:
            return f"""
{self.name} @ ({self.x}, {self.y})
""" + "\n".join(self.msg)


class Arena:
    """A class representing the arena."""
    def __init__(self, rows, cols, arena_type='torus', max_volume_per_position=100, **kwargs):
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
        if 'objects' in data:            
            for obj_data in data['objects']:
                obj = ArenaObject.deserialize(obj_data)
                if not isinstance(obj, list):
                    obj = [obj]
                for o in obj:
                    arena.add_to_position(o.x,o.y,o)

        elif 'class' in data:
            for class_data in data['class']:
                for _ in range(class_data.get('num', 1)):
                    obj = ArenaObject.byclass(class_data)
                    arena.add_to_random_position(obj)
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

    # not in use?!
    # def set_position(self, x, y, objects): 
    #     """Set the list of objects at position (x, y)."""
    #     for obj in objects:
    #         obj.setposition(x,y)
    #     self.grid[x][y] = objects
    #     self.num_objects += len(objects)

    def add_to_position(self, x, y, obj):
        return self._add_to_position(x, y, obj)

    def _add_to_position(self, x, y, obj):
        """Add an object to the list at position (x, y)."""
        if self.get_total_volume(x, y) + obj.volume > self.max_volume_per_position:
            return False
        self.grid[x][y].append(obj)
        self.num_objects += 1
        obj.setposition(x,y)
        return True
    
    def add_to_random_position(self, obj):
        """Add an object to a random position in the arena."""
        x = random.randint(0, self.rows-1)
        y = random.randint(0, self.cols-1)
        for i in range(0,10):
            if self.add_to_position(x, y, obj):
                return True
        return False

    def remove_from_position(self, x, y, obj):
        return self._remove_from_position(x, y, obj)
    
    def _remove_from_position(self, x, y, obj):
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
        if self._add_to_position(x, y, obj) is True:
            self._remove_from_position(ox, oy, obj)
            obj.add_msg(f"{obj.name} moved ({ox,oy}) -> {x},{y})")
            return True
        else:
            return False

    def get_pos_surrounding(self, x, y, direction=0, length=1):
        """Get the surrounding objects of the current position."""
        return Surrounding(self, x, y, direction, length)

    def __str__(self):
        """Create a string representation of the arena with the number of objects at each position."""
        arena_str = f"#{self.num_objects}\n"
        for row in self.grid:
            row_str = ""
            for cell in row:
                c = len(cell)
                if c == 0:
                    c = "__"
                else:
                    c = str(cell[0])
                # c = "_" if c == 0 else str(c)
                row_str = f"{row_str} {c}"
            arena_str += row_str + "\n"
        return arena_str
    
    def objects_info(self):
        msg = [obj.info() for obj in self.get_objects()]
        return "\n".join(msg)
    
class Surrounding:
    """A class representing the surrounding of an object in the arena."""
    def __init__(self, arena, x, y, direction=0, length=1):
        self.arena = arena
        self.x = x
        self.y = y
        self.direction = direction
        self.length = length
        self.objects_meta = []
        self.objects = self.get_surrounding()

    def get_surrounding(self):
        """Get the surrounding objects of the current position."""
        surrounding = []
        meta = []
        for x in range( self.x - self.length, self.x + self.length +1 ):
            for y in range( self.y - self.length, self.y + self.length +1 ):

                px,py = self.arena.convert_position(x, y)
                if px is None or py is None:
                    # outbound position
                    continue

                objs = self.arena.get_position(px, py)
                for o in objs:
                    distance = self.distance_xy(x,y)
                    direction = self.direction_xy(x,y)
                    if( distance <= self.length ):
                        surrounding.append(o)
                        meta.append( (o, distance, direction) )

        self.objects_meta = meta
        return surrounding

    # need to be redefined to support torus shape
    # def distance_o(self, obj):
    #     return self.distance_xy( obj.x,obj.y)
    
    @classmethod
    def _distance_xykz(cls,x,y, k,z):
        # Chebyshev distance
        return max(abs(x - k), abs(y - z))

    def distance_xy(self, x,y):
        return Surrounding._distance_xykz(self.x, self.y, x,y)

    def direction_xy(self, x,y):
        return 0

    def __str__(self):
        """Create a string representation of the surrounding objects."""
        return str(self.objects_meta)

class SurroundingManhattan(Surrounding):
    """A class representing the surrounding of an object with a Manhattan distance."""  
    def distance_xy( self, x,y):
        return abs(self.x - x) + abs(self.y - y)
    
    def direction_xy(self, x, y, distance=None):
        """
        direction_xy
        return:  2 
                456
                 8
        """
        diff_y = self.y - y
        diff_x = self.x - x
        
        if diff_x == 0:
            if diff_y == 0:
                return 5
            else:
                return 4 if diff_y > 0 else 6
        elif diff_x > 0:
            if diff_y == 0:
                return 2
            else:
                return random.choice((2,4)) if diff_y > 0 else random.choice((2,6))
        elif diff_x < 0:
            if diff_y == 0:
                return 8
            else:
                return random.choice((4,8)) if diff_y > 0 else random.choice((6,8))
        raise ValueError(f"fail to calculate distance_xy: {diff_x},{diff_y}")

class SurroundingEuclidean(Surrounding):
    """A class representing the surrounding of an object with a Euclidean distance."""
    def distance_xy( self, x,y):
        return ((self.x - x)**2 + (self.y - y)**2)**0.5
    
class SurroundingChebyshev(Surrounding):
    """A class representing the surrounding of an object with a Chebyshev distance."""
    def distance_xy( self, x,y):
        return max(abs(self.x - x), abs(self.y - y))

    def direction_xy(self, x, y, distance=None):
        """
        direction_xy
        return: 123
                456
                789
        """
        diff_y = self.y - y
        diff_x = self.x - x
        
        if diff_x == 0:
            if diff_y == 0:
                return 5
            else:
                return 4 if diff_y > 0 else 6
        elif diff_x > 0:
            if diff_y == 0:
                return 2
            else:
                return 1 if diff_y > 0 else 3
        elif diff_x < 0:
            if diff_y == 0:
                return 8
            else:
                return 7 if diff_y > 0 else 9
        raise ValueError(f"fail to calculate distance_xy: {diff_x},{diff_y}")


def main():
    """Main function."""
    arena = Arena(5, 5)
    obj1 = ArenaObject("obj1", 1)
    obj2 = ArenaObject("obj2", 1)
    arena.add_to_position(0, 0, obj1)
    arena.add_to_position(0, 1, obj2)

    print(arena)

if __name__ == "__main__":
    main()