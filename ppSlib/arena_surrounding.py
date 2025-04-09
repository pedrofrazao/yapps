import random

class Surrounding:
    """A class representing the surrounding of an object in the arena."""
    def __init__(self, arena, x, y, direction=0, length=1, exclude_obj=None ):
        self.arena = arena
        self.x = x
        self.y = y
        self.direction = direction
        self.length = length
        self.exclude = exclude_obj
        self.objects_meta = []
        self.empty_pos = []
        self.objects = self._get_surrounding() # list of objects
        

    def sorted(self):
        return sorted(self,key=lambda x: x[1])

    def get_objects(self,only_class=None):
        """
        return: list of object: [obj1, obj2, ...]
        """ 
        if only_class is not None and isinstance(only_class, list):
            return [o for o in self.objects if any(isinstance(o, cls) for cls in only_class)]
        elif only_class is not None:
            # only one class
            return [o for o in self.objects if isinstance(o, only_class)]
        else:
            return self.objects
        
    def get_objects_plus_meta(self, only_class=None):
        """
        return: list of object: [(obj1, distance, direction), (obj2, distance, direction), ...]
        """
        checkclass = lambda o,c: True if o.__class__.__name__ == c else False
        if only_class is not None and isinstance(only_class, list):
            return [(o,ds,dr) for o,ds,dr in self.objects_meta if any(checkclass(o, cls) for cls in only_class)]
        elif only_class is not None:
            return [(o,ds,dr) for o,ds,dr in self.objects_meta if checkclass(o, only_class)]
        else:
            return self.objects_meta

    def _get_surrounding(self):
        """Get the surrounding objects of the current position."""
        empty_pos = set()
        meta = set()
        if self.length > self.arena.rows and self.length > self.arena.cols:
            # too lengthy
            self.length = max(self.arena.rows, self.arena.cols)

        for x in range( self.x - self.length, self.x + self.length +1 ):
            for y in range( self.y - self.length, self.y + self.length +1 ):

                px,py = self.arena.convert_position(x, y)
                if px is None or py is None:
                    # outbound position
                    continue

                objs = self.arena.get_position(px, py)
                if( len(objs) == 0 ):
                    # empty position
                    empty_pos.add((px, py))
                    continue

                for o in objs:
                    if o == self.exclude:
                        continue
                    distance = self.distance_xy(x,y)
                    direction = self.direction_xy(x,y)
                    if( distance <= self.length ):
                        meta.add( (o, distance, direction) )

        self.empty_pos = list(empty_pos)
        self.objects_meta = sorted(list(meta), key=lambda x: x[1])
        surrounding = [ o for o, _, _ in self.objects_meta ]
        return surrounding

    def _all_positions_at_distance(self):
        """Get all positions at a certain distance from a point."""
        distance = self.length
        positions = []
        for x in range( self.x - distance, self.x + distance +1 ):
            for y in range( self.y - distance, self.y + distance +1 ):
                px,py = self.arena.convert_position(x, y)
                if px is None or py is None:
                    # outbound position
                    continue
                positions.append( (px,py) )
        return positions

    def find_empty_position(self):
        """Find an empty position in the surrounding."""
        return self.empty_pos

    def get_direction_to(self, obj):
        """Get the direction of an object in the surrounding."""
        for o, distance, direction in self.objects_meta:
            if o == obj:
                return direction
        return None

    def __iter__(self):
        """Iterate over all objects in the surrounding."""
        self._index = 0
        return self

    def __next__(self):
        """Return the next object in the surrounding."""
        if self._index < len(self.objects_meta):
            o, dis, dir = self.objects_meta[self._index]
            self._index += 1
            return o, dis, dir
        else:
            raise StopIteration
    
    def __lt__(self, other):
        """Compare objects based on their distance."""
        return self.distance_xy(self.x, self.y) < other.distance_xy(other.x, other.y)

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
