import celery
import os
import subprocess
import requests

from gidgethub import sansio


app = celery.Celery('example')

app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])


CPYTHON_CREATE_PR_URL = "https://api.github.com/repos/Mariatta/cpython/pulls"

@app.task
def clone_cpython():
    print("cloning cpython")
    result = subprocess.check_output(
        "git clone https://github.com/mariatta-bot/cpython.git".split())
    print(result.decode('utf-8'))
    os.chdir('./cpython')
    result = subprocess.check_output(
        "git remote add upstream https://github.com/mariatta/cpython.git".split())
    print(result.decode('utf-8'))

    print("finished cloning")
    #
    # os.chdir('..')


@app.task
def backport_task(commit_hash, branch):
    """Backport a commit into a branch. Wait until cpython has been successfully cloned."""

    print(f"backporting {commit_hash} {branch}")
    branch_name = f"backport-{commit_hash[:7]}-{branch}"
    print(subprocess.check_output(f"git fetch upstream".split()).decode('utf-8'))

    # print(f"is merged {event.data['pull_request']['merged']}")
    # print(f"commit hash {event.data['pull_request']['merge_commit_sha']}")
    # commit_hash = event.data['pull_request']['merge_commit_sha']
    # issue = await gh.getitem(event.data['repository']['issues_url'],
    #                                      {'number': f"{event.data['pull_request']['number']}"})
    # print("ISSUES")
    # print(issue)
    # print("LABELS")
    # labels = await gh.getitem(issue['labels_url'])
    # branches = [label['name'].split()[-1] for label in labels if label['name'].startswith("needs backport to")]
    # print(branches)
    # print(subprocess.check_output(f"git fetch upstream".split()).decode('utf-8'))
    #
    # for b in branches:
    #     branch_name = f"backport-{commit_hash[:7]}-{b}"
    print(subprocess.check_output(f"git checkout -b {branch_name} upstream/{b}".split()).decode('utf-8'))
    print(subprocess.check_output(f"git cherry-pick -x {commit_hash}".split()).decode('utf-8'))
    print(subprocess.check_output(f"git push origin {branch_name}".split()).decode('utf-8'))
    print(subprocess.check_output(f"git branch -D {branch_name}".split()).decode('utf-8'))
    create_gh_pr(branch, branch_name, gh_auth=os.getenv("GH_AUTH"))

def create_gh_pr(base_branch, head_branch, *,
                 gh_auth):
    """
    Create PR in GitHub
    """
    request_headers = sansio.create_headers(
        "mariatta-bot", oauth_token=gh_auth)
    title, body = f"[{base_branch}] cherry-pick PR by a bot", "hello"

    data = {
        "title": title,
        "body": body,
        "head": f"Mariatta:{head_branch}",
        "base": base_branch,
        "maintainer_can_modify": True
    }
    response = requests.post(CPYTHON_CREATE_PR_URL,
                             headers=request_headers, json=data)
    if response.status_code == requests.codes.created:
        print(
            f"Backport PR created at {response.json()['html_url']}")
    else:
        print(response.status_code)
        print(response.text)
