---
layout: post
title:  "@ : decorator in python"
date:   2019-01-19
categories: python
author: moontree
---

## 装饰器(decorator)
装饰器本质上是一个函数，接受一个函数，并返回一个修改后的函数进行替换。
或者说，将函数的内容传入装饰器进行运行。

主要的应用场景是针对多个函数提供在其之前，之后或周围进行调用的通用代码。

一般情况下，通过函数定义上一行的`@`表示。

## 常见的装饰器
#### 本体函数(identify function),除了返回自身什么都不做。
```python
def identify(f):
    return f

@identify
def foo():
    return 'bar'
```
上述代码和下面的过程类似：
```python
def identify(f):
    return f

def foo():
    return 'bar'

foo = identify(foo)
```

#### 注册装饰器
将函数名注册在词典中，除此之外什么都不做
```python
_functions = {}

def register(f):
    _functions[f.__name__] = f
    return f

@register
def foo():
    return 'bar'
```

## 带参数的装饰器
上面两个例子中，几乎是对函数进行了替换或者什么都没做，如果需要针对函数的参数进行检查或者其他操作，该怎么使用呢？
这就要求我们能够在装饰器中获得函数的参数。
牢记这一点，装饰器返回的也是一个函数，替换了传入的函数。
所以，我们可以定义一个函数，使用args和kwargs来接受参数。
前面的本体函数也可以写成下面的形式：
```python
def check_time(f):
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper
```
值得注意的是，Python中函数的参数，`*args`表示必须指定的列表，`**kwargs`表示可选参数的字典。
其中，`*args`必须在`**kwargs`前面。
```python
def f(*args, **kwargs):
    print args
    print kwargs

print f(1, 2, 3, a = 4, b = 5)
f()

## output
## (1, 2, 3)
## {'a': 4, 'b': 5}
```
#### 使用装饰器进行参数检查
在商店中，我们希望只有管理员有权限进行某些操作，
这时候就要对输入的参数进行检查。
装饰器可以优雅地完成这一点。
```python
def check_username(f):
    def wrapper(*args, **kwargs):
        # if kwargs.get('username') != 'admin':
        if args[0] != 'admin':
            raise Exception("User is not accessed")
        return f(*args, **kwargs)
    return wrapper

@check_username
def get_food(username, food):
    """
    get food
    :param username:
    :param food:
    :return:
    """
    return "%s get %s" % (username, food)
```

按照前面所学，上述代码可以实现该功能，只有用户是'admin'的时候，才可以从商店里拿出食物。

然而，如果使用`args`来通过列表进行参数检查的话，一方面可读性很差，一方面限制了接口的第一个参数必须是用户，不利于扩展。
能不能改成dict的形式呢？
幸运的是，`inspect`库为我们提供了这个功能，它可以将函数参数统一转变为字典的形式，只需要加入一句话：
```
function_args = inspect.getcallargs(f, *args, **kwargs)
```
这样，上面的装饰器代码就可以变得更加易读，扩展性也变得更好：
```python
import inspect
def check_username(f):
    def wrapper(*args, **kwargs):
        function_args = inspect.getcallargs(f, *args, **kwargs)
        print function_args
        if function_args.get('username') != 'admin':
            raise Exception("User is not accessed")
        return f(*args, **kwargs)
    return wrapper
```

## 装饰器隐藏了一些东西
从上面的内容来看，装饰器似乎是一个很好用的东西。但是呢，它也偷偷地隐藏了一些东西，比如函数名称、函数文档。
如果不使用装饰器，我们来看一下函数自身的属性：
```python
def get_food(username, food):
    """
    get food
    """
    return "%s get %s" % (username, food)
get_food.__name__ # get_food
get_food.__doc__ # get food
```
加上装饰器之后呢，输出就变成了
```python
# wrapper
# None
```
丢失了原有的函数信息。Python内置的functools模块通过其update_wrapper函数解决了这个问题，它会复制这些属性给这个包装器本身。
可以通过如下方式使用：
```python
import inspect
import functools
def check_username(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        function_args = inspect.getcallargs(f, *args, **kwargs)
        print function_args
        if function_args.get('username') != 'admin':
            raise Exception("User is not accessed")
        return f(*args, **kwargs)
    return wrapper
```
这样，我们就得到了一个足够优雅的装饰器。

## 最终示例
```python
import time
import functools
import inspect


def check_username(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        function_args = inspect.getcallargs(f, *args, **kwargs)
        print function_args
        if function_args.get('username') != 'admin':
            raise Exception("User is not accessed")
        return f(*args, **kwargs)
    return wrapper


def check_time(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        val = f(*args, **kwargs)
        end = time.time()
        print 'run time of', f.__name__, 'is', end - start
        return val
    return wrapper


@check_time
@check_username
def get_food(username, food):
    """
    get food
    :param username:
    :param food:
    :return:
    """
    return "%s get %s" % (username, food)


print get_food.__doc__
print get_food.__name__
get_food('a', 'b')
```
