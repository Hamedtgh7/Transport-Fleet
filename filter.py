from vector_2d import Vector2d


def filter_less_two(vectors: list[Vector2d]):
    return filter(lambda vector: vector.length < 2, vectors)
