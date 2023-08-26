class Vector2d:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __add__(self, second):
        if isinstance(second, Vector2d):
            return Vector2d(self.x+second.x, self.y+second.y)
        else:
            raise ValueError('not match')

    def __mul__(self, second):
        return Vector2d(self.x*second.x, self.y*second.y)

    def __len__(self):
        return 2

    def __matmul__(self, second):
        return self.x*second.x+self.y*second.y

    def __sub__(self, second):
        return Vector2d(self.x-second.x, self.y-second.y)

    def __truediv__(self, second):
        raise ValueError('not allowed')

    @property
    def length(self):
        return int((self.x**2+self.y**2)**0.5)


def filter_less_two(vectors: list[Vector2d]):
    return filter(lambda vector: vector.length < 2, vectors)
