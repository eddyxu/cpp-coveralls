from git import Repo


def gitrepo(root):
    repo = Repo(root)
    return {
        "head": {
            "id": repo.head.commit.hexsha,
            "author_name": repo.head.commit.author.name,
            "author_email": repo.head.commit.author.email,
            "committer_name": repo.head.commit.committer.name,
            "committer_email": repo.head.commit.committer.email,
            "message": repo.head.commit.message.strip()
        },
        "branch": repo.head.commit.name_rev.split()[1],
        "remotes": [{'name': remote.name, 'url': remote.url}
                    for remote in repo.remotes],
    }
