def _register(f):
    print(f.__name__)
    print(f)
    def wrapper(self, *args, **kargs):
        print(f.__name__)
        self.dict[f.__name__] = f
        return f(self, *args, **kargs)

    return wrapper


class A():
    def __init__(self):
        self.dict = {}
        pass

    @_register
    def a(self):
        print('haha')


obj = A()
print(obj.dict)
#
# print(dir(obj))
# print(obj.__dict__)
# obj['a']
# obj['a']




