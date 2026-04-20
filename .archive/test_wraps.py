import time
from functools import wraps

def logger(func):
    # 这里自己补
    @wraps(func)
    def wrapper(*args,**kwargs):
       result = func(*args,**kwargs)
       return result
    return wrapper
    pass

@logger
def multiply(a, b):
    """multiply two numbers"""
    return a * b

print(multiply.__name__)   # multiply
print(multiply.__doc__)    # multiply two numbers
print(multiply(2, 3))      # 6




def timer(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        start = time.time()

        result= func(*args, **kwargs)

        end = time.time()

        print(
            f"{func.__name__} took "
            f"{end-start:.4f} seconds"
        )

        return result

    return wrapper


@timer
def slow_add(a, b):
    """slow add"""
    time.sleep(1)
    return a + b

print(slow_add.__name__)   # slow_add
print(slow_add.__doc__)    # slow add
print(slow_add(1, 2))      # 3
