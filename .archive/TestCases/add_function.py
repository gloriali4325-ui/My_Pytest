import errno

def add(a,b):
    if a=="mark":
        raise ValueError("mark test in this case")
    elif( a=="errorn"):
        raise OSError(errno.EACCES,"errorn test in this case")
    else:
        return a+b