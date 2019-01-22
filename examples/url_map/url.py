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