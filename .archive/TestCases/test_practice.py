import pytest
import time
from functools import wraps

def divide(a,b):
    return a/b

@pytest.mark.parametrize("args,expected_exception",[
    ((1,0),ZeroDivisionError),
    ((10,0),ZeroDivisionError),
    ((-5,0),ZeroDivisionError),
])
def test_divide(args,expected_exception):
    with pytest.raises(expected_exception):
        divide(*args)
###Function: add
###args: (3,4)
###7
def logger(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        print("Function:",func.__name__)
        print("args:",args)
        func(*args,**kwargs)
    return wrapper

@logger
def add(a,b):
    print(a+b)

add(3,4)

def timer(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        start_time=time.time()
        result=func(*args,**kwargs)
        end_time=time.time()
        print(f"Function slow_add took {end_time-start_time:.4f} seconds")
        print(result)
        return result
    return wrapper

@timer
def slow_add(a,b):
    time.sleep(1)
    return a+b

slow_add(1,2)
import random as r


def retry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
                if i == 2:
                    raise
    return wrapper


@retry
def unstable():
    if r.random() < 0.5:
        raise ValueError("Unstable function failed")
    return "Success"


def  retrySpecificException(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except ValueError as e:
                    print(f"Attempt {i+1} failed: {e}")
                    if i == times-1:
                        raise
                except TypeError as e:
                    print(f"TypeError occurred: {e}")
                    raise
        return wrapper
    return decorator


@retrySpecificException(times=5)
def retryFunction():
    if r.random() < 0.5:
        raise ValueError("ValueError occurred")
    else:
        raise TypeError("TypeError occurred")


try:
    print("unstable result:", unstable())
except Exception as e:
    print("unstable final error:", e)

try:
    print("retryFunction result:", retryFunction())
except Exception as e:
    print("retryFunction final error:", e)

print(unstable.__name__)
print(retryFunction.__name__)