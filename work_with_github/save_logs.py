from github import Github
from work_with_github import get_token


def save(path: str, str_save: str):
    g = Github(get_token.get_token())
    repo = g.get_user().get_repo("stock-bot")
    contents = repo.get_contents(path)
    s = contents.decoded_content.decode()
    s = str_save + s
    mass = s.split('\n')
    mass = mass[:200]
    s = ''
    for ind, i in enumerate(mass):
        s += i
        if ind != len(mass) - 1:
            s += '\n'
    repo.update_file(contents.path, "save logs", s, contents.sha, branch='main')
