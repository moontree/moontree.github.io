---
layout: post
title:  "reflection in python"
date:   2019-01-20
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
class A():
    def __init__(self):
        pass

    def a(self):
        print('haha')

obj = A()
```
正常来说，我们可以通过`obj.a()'来调用函数；然而，如果我们想通过字符串'a'来调用这个函数呢？
貌似，可以利用上一篇的装饰器，来加一个字典

python内置的反射函数：

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


python中对反射机制的应用：

### 动态载入模块之`__import__`
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
