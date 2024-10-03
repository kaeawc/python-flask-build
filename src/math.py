from core.logging import logging

def add(a: int, b: int) -> int:
    result = a + b
    logging.info('%d + %d = %d')
    return result
