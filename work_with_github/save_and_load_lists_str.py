import time

from work_with_github import get_token
from github import Github
from work_with_github import convert_list_to_str
from copy import deepcopy


def save(path: str, ls: list, ls_name: str):
    g = Github(get_token.get_token())
    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents(path)
    s = contents.decoded_content.decode()
    str_save = f'{ls_name}: {convert_list_to_str.convert(ls=ls)}'
    mass = s.split('\n')
    new_mass = list()

    flag_is_save = False

    for line in mass:
        line_name = line.split(':')[0]
        if line.find(':') == -1:
            continue
        if line_name == ls_name:
            new_mass.append(str_save)
            flag_is_save = True
        else:
            new_mass.append(line)

    if not flag_is_save:
        new_mass.append(str_save)

    s = ''
    for ind, i in enumerate(new_mass):
        s += i
        if ind != len(new_mass) - 1:
            s += '\n'

    repo.update_file(contents.path, f"save {ls_name}", s, contents.sha, branch='main')

    time.sleep(0.1)


def load(path: str, ls_name: str):
    g = Github(get_token.get_token())
    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents(path)
    s = contents.decoded_content.decode()
    mass = s.split('\n')

    list_to_return = list()

    for line in mass:
        line_name = line.split(':')[0]
        if line_name == ls_name:
            list_to_return = line.split(':')[1].split(' ')

    while list_to_return.count('') > 0:
        list_to_return.remove('')

    time.sleep(0.1)

    return list(map(str, list_to_return))


def remove(path: str, ls_name: str):
    g = Github(get_token.get_token())
    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents(path)
    s = contents.decoded_content.decode()
    mass = s.split('\n')
    new_mass = list()

    for line in mass:
        line_name = line.split(':')[0]
        if line.find(':') == -1:
            continue
        if not line_name == ls_name:
            new_mass.append(line)

    s = ''

    for ind, i in enumerate(new_mass):
        s += i
        if ind != len(new_mass) - 1:
            s += '\n'

    repo.update_file(contents.path, f"remove {ls_name}", s, contents.sha, branch='main')

    time.sleep(0.1)


class PoolLists:
    def __init__(self, dc: dict = {}):
        self.pool = list()
        for i in dc:
            if type(dc[i]) == list:
                self.pool.append((deepcopy(i), deepcopy(dc[i])))

    def __deepcopy__(self, mem):
        my_copy = type(self)()
        for i, j in self.pool:
            dc = dict()
            dc[i] = j
            my_copy.set_to_pool(deepcopy(dc))
        return my_copy

    def set_to_pool(self, dc):
        for i in dc:
            if type(dc[i]) == list:
                self.pool.append((i, dc[i]))

    def get_from_pool(self, name: str):
        for i, j in self.pool:
            if i == name:
                return j

    def set_value_to_pool(self, name: str, value: list):
        for ind, i, j in enumerate(self.pool):
            if i == name:
                self.pool[ind] = (i, deepcopy(value))
