
_sink = None


def set_sink(function):
    global _sink
    _sink = function


def has_sink():
    return _sink is not None


def out(text=""):
    if _sink is not None:
        _sink(str(text))
    else:
        print(text)
