from core.logging import logging

def add(a: int, b: int) -> int:
    result = a + b
    logging.debug('%d + %d = %d', a, b, result)
    return result
