class Vector2d:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __add__(self, second):
        if not isinstance(second, Vector2d):
            raise ValueError('not match')
        return Vector2d(self.x+second.x, self.y+second.y)

    def __mul__(self, second):
        if not isinstance(second, Vector2d):
            raise ValueError('not match')
        return Vector2d(self.x*second.x, self.y*second.y)

    def __len__(self):
        return 2

    def __matmul__(self, second):
        if not isinstance(second, Vector2d):
            raise ValueError('not match')
        return self.x*second.x+self.y*second.y

    def __sub__(self, second):
        if not isinstance(second, Vector2d):
            raise ValueError('not match')
        return Vector2d(self.x-second.x, self.y-second.y)

    def __truediv__(self, second):
        raise ValueError('not allowed')

    @property
    def length(self):
        return int((self.x**2+self.y**2)**0.5)
