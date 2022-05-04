from work_with_github import save_and_load_lists_str
from work_with_github import save_and_load_lists_float


def save(path: str, arg, arg_name: str):
    if type(arg) == list:
        flag = True
        for i in arg:
            flag = flag and (type(i) == float)
        if flag:
            save_and_load_lists_float.save(path=path, ls=arg, ls_name=arg_name)
            return
        flag = True
        for i in arg:
            flag = flag and (type(i) == str)
        if flag:
            save_and_load_lists_str.save(path=path, ls=arg, ls_name=arg_name)
            return
    elif type(arg) == float:
        pass


def load(path: str, arg, arg_name: str):
    if type(arg) == list:
        flag = True
        for i in arg:
            flag = flag and (type(i) == float)
        if flag:
            arg = save_and_load_lists_float.load(path=path, ls_name=arg_name)
            return arg
        flag = True
        for i in arg:
            flag = flag and (type(i) == str)
        if flag:
            arg = save_and_load_lists_str.load(path=path, ls_name=arg_name)
            return arg
    elif type(arg) == float:
        pass

