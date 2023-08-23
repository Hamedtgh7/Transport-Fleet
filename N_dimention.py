class Vectornd:

    def __init__(self, *elements):
        self.elements = elements

    def __add__(self, second):
        if len(self.elements) == len(second.elements):
            return Vectornd([x+y for x, y in zip(self.elements, second.elements)])
        else:
            raise ValueError('not match')

    def __mul__(self, second):
        return Vectornd([x*y for x, y in zip(self.elements, second.elements)])

    def __len__(self):
        return len(self.elements)

    def __matmul__(self, second):
        return sum([x*y for x, y in zip(self.elements, second.elements)])

    def __sub__(self, second):
        return Vectornd([x-y for x, y in zip(self.elements, second.elements)])

    def __truediv__(self, second):
        raise ValueError('not allowed')

    @property
    def length(self):
        return sum([x**2 for x in self.elements])**0.5


class Vector2d(Vectornd):
    def __init__(self, *elements):
        super().__init__(*elements)
