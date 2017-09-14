import gidgethub.routing
import cherry_picker
import os
import subprocess
import requests

from gidgethub import sansio
from . import tasks


router = gidgethub.routing.Router()

@router.register("state")
async def backport_pr(event, gh, *args, **kwargs):
    print(" state change ")
    print("event")
    print(event.data)


    # print(event.data)
    # print(subprocess.check_output("git branch".split()).decode('utf-8'))
    # print('checking out master')

    # subprocess.check_output('git checkout -b master upstream/master'.split())
    # subprocess.check_output('git status'.split())
    pass


@router.register("pull_request", action="opened")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr opened ")
    print("event")
    print(event)
    print("gh")
    print(gh)
    print("args")
    print(args)
    print("kwargs")
    print(kwargs)

    # print(event.data)
    # print(subprocess.check_output("git branch".split()).decode('utf-8'))
    # print('checking out master')

    # subprocess.check_output('git checkout -b master upstream/master'.split())
    # subprocess.check_output('git status'.split())
    pass

@router.register("pull_request", action="reopened")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr reopened ")
    print(" pr opened ")
    print("event")
    print(event)
    print("gh")
    print(gh)
    print("args")
    print(args)
    print("kwargs")
    print(kwargs)
    pass

@router.register("pull_request", action="closed")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr closed ")
    print(os.getcwd())
    # async_result = AsyncResult(task_id)
    print("event")
    print(dir(event))
    print("gh")
    print(dir(gh))

    print("args")
    print(args)
    print("kwargs")
    print(kwargs)
    if event.data["pull_request"]["merged"]:
        comment_on_pr(event, os.getenv('GH_AUTH'))
        commit_hash = event.data['pull_request']['merge_commit_sha']
        # print(f"is merged {event.data['pull_request']['merged']}")
        # print(f"commit hash {event.data['pull_request']['merge_commit_sha']}")
        # commit_hash = event.data['pull_request']['merge_commit_sha']
        issue = await gh.getitem(event.data['repository']['issues_url'],
                                             {'number': f"{event.data['pull_request']['number']}"})

        # print("ISSUES")
        # print(issue)
        # print("LABELS")
        labels = await gh.getitem(issue['labels_url'])
        branches = [label['name'].split()[-1] for label in labels if label['name'].startswith("needs backport to")]
        # print(branches)
        # print(subprocess.check_output(f"git fetch upstream".split()).decode('utf-8'))
        #
        for b in branches:
            tasks.backport_task.delay(commit_hash, b)


CPYTHON_CREATE_PR_URL = "https://api.github.com/repos/Mariatta/cpython/pulls"


def comment_on_pr(event, gh_auth):
    request_headers = sansio.create_headers(
        "mariatta-bot", oauth_token=gh_auth)
    issue_number = event.data['pull_request']['number']
    merged_by = event.data['pull_request']['merged_by']['login']
    created_by = event.data['pull_request']['user']['login']

    issue_comment_url = f"https://api.github.com/repos/Mariatta/cpython/issues/{issue_number}/comments"
    data = {
        "body": f"Thanks @{created_by} for the PR, and @{merged_by} for merging it.  I will now backport this PR.",
    }
    response = requests.post(issue_comment_url,
                             headers=request_headers,
                             json=data)
    if response.status_code == requests.codes.created:
        print(f"Commented at {response.json()['url']}")
    else:
        print(response.status_code)
        print(response.text)



def create_gh_pr(base_branch, head_branch, *,
                 gh_auth):
    """
    Create PR in GitHub
    """
    request_headers = sansio.create_headers(
        "mariatta-bot", oauth_token=gh_auth)
    title, body = "hi", "cherrypick pr by a bot"

    data = {
      "title": title,
      "body": body,
      "head": f"Mariatta:{head_branch}",
      "base": base_branch,
      "maintainer_can_modify": True
    }
    response = requests.post(CPYTHON_CREATE_PR_URL, headers=request_headers, json=data)
    if response.status_code == requests.codes.created:
        print(f"Backport PR created at {response.json()['_links']['html']}")
    else:
        print(response.status_code)
        print(response.text)
