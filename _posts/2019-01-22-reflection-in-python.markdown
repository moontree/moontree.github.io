---
layout: post
title:  "Reflection in python"
date:   2019-01-22
categories: python
author: moontree
---

反射机制

核心问题：利用字符串驱动不同的事件
- 是否存在某个变量或字符串
- 如何通过字符串调用名字相同的函数呢

其实，在python中，这个问题很容易让我们想到`dict`这个结构，实现了`key-value`的映射，而且value可以是任何类型。

那么，当我们想以字符串形式访问某个类的函数，或者访问某个文件中的函数时，该怎么办呢？这个dict在哪里呢？

```python
# func.py
def hello():
    print('hello world')

def say_hi(name):
    print('hi', name)
```

```python
# main.py
import func
func.hello()
```
正常来说，我们可以通过`func.hello()`来调用函数；然而，如果我们想通过字符串'hello'来调用这个函数呢？
貌似，可以利用上一篇的装饰器，在`func.py`中加一个包含了内部所有函数的字典。
如下所示：
```python
# func.py
_funcs = {}

def _register(f):
    _funcs[f.__name__] = f
    return f

@_register
def hello():
    print('hello world')

@_register
def say_hi(name):
    print('hi', name)
```
``` python
# main.py
import func
func._funcs['hello']()
```

这样做，就解决了上述的问题，可以通过字符串来访问函数了。
可是，这样要再每个函数前面加一个注册器函数，
还要用一个字典来保存名称到函数的映射，似乎不够优雅。
有没有更好的方式呢？
这时候，python的内置函数就起到作用了,让我们来看一下`getattr`

```
import func
getattr(func, 'hello')()
```

与`getattr`相似的，还有其他3个函数：`hasattr`, `delattr`, `setattr`
``` python

def hasattr(*args, **kwargs): # real signature unknown
    """
    Return whether the object has an attribute with the given name.

    This is done by calling getattr(obj, name) and catching AttributeError.
    """

def getattr(object, name, default=None): # known special case of getattr
    """
    getattr(object, name[, default]) -> value

    Get a named attribute from an object; getattr(x, 'y') is equivalent to x.y.
    When a default argument is given, it is returned when the attribute doesn't
    exist; without it, an exception is raised in that case.
    """
    pass

def setattr(x, y, v): # real signature unknown; restored from __doc__
    """
    Sets the named attribute on the given object to the specified value.

    setattr(x, 'y', v) is equivalent to ``x.y = v''
    """
    pass

def delattr(x, y): # real signature unknown; restored from __doc__
    """
    Deletes the named attribute from the given object.

    delattr(x, 'y') is equivalent to ``del x.y''
    """
    pass
```


函数可以通过字符串调用，那是不是也可通过字符串来import module呢？答案是可以的：
python提供了两种方式，一种是`__import__`，一种是利用`importlib`来动态加载模块。
```
getattr(__import__('func'), 'hello')()
getattr(importlib.import_module('func'), 'hello')()
```
如果`func.py`在子文件夹中，可以使用以下方式：
```
getattr(importlib.import_module('folder.func'), 'hello')()
getattr(__import__('folder.func', fromlist=True), 'hello')()
getattr(__import__('func', fromlist='folder'), 'hello')()
```

### `__import__`
```
def __import__(name, globals=None, locals=None, fromlist=(), level=0): # real signature unknown; restored from __doc__
    """
    __import__(name, globals=None, locals=None, fromlist=(), level=0) -> module

    Import a module. Because this function is meant for use by the Python
    interpreter and not for general use, it is better to use
    importlib.import_module() to programmatically import a module.

    The globals argument is only used to determine the context;
    they are not modified.  The locals argument is unused.  The fromlist
    should be a list of names to emulate ``from name import ...'', or an
    empty list to emulate ``import name''.
    When importing a module from a package, note that __import__('A.B', ...)
    returns package A when fromlist is empty, but its submodule B when
    fromlist is not empty.  The level argument is used to determine whether to
    perform absolute or relative imports: 0 is absolute, while a positive number
    is the number of parent directories to search relative to the current module.
    """
    pass
```



### 对路由的模拟
最简单的方式，是通过路径来解析，
url包含为module的路径，调用的函数。
具体示例参照[示例代码](examples/url_map/url.py)。
部分代码如下：
```
import importlib


def run():
    while True:
        content = input("请输入您想访问页面的url：  ").strip()
        if content == 'q':
            break
        data = content.split("/")
        if len(data) > 1:
            modules = '.'.join(data[:-1])
            func = data[-1]
            try:
                obj = importlib.import_module('routes.%s' % modules)
                if hasattr(obj, func):
                    func = getattr(obj, func)
                    func()
                else:
                    print("404")
            except:
                print('module not find')

        else:
            print('url not valid!')


if __name__ == '__main__':
    run()
```


然而，这样做会有一个问题，如果路径很长，就要一层层地嵌套，导致目录结构很复杂。
这时候，就可以加一个映射，将某些路径，映射到同一个模块的不同类中，具体可以参照django的做法。