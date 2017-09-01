import gidgethub.routing
import cherry_picker
import os
import subprocess
from gidgethub import sansio
import requests


router = gidgethub.routing.Router()

@router.register("pull_request", action="opened")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr opened ")
    # print(event.data)
    pass

@router.register("pull_request", action="reopened")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr reopened ")
    # print(event.data)
    pass

@router.register("pull_request", action="closed")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr closed ")
    print(os.getcwd())
    if event.data["pull_request"]["merged"]:
        print(f"is merged {event.data['pull_request']['merged']}")
        print(f"commit hash {event.data['pull_request']['merge_commit_sha']}")
        commit_hash = event.data['pull_request']['merge_commit_sha']
        issue = await gh.getitem(event.data['repository']['issues_url'],
                                             {'number': f"{event.data['pull_request']['number']}"})
        print("ISSUES")
        print(issue)
        print("LABELS")
        labels = await gh.getitem(issue['labels_url'])
        branches = [label['name'].split()[-1] for label in labels if label['name'].startswith("needs backport to")]
        print(branches)
        for b in branches:
            branch_name = f"backport-{commit_hash[:7]}-{b}"
            print(subprocess.check_output(f"git fetch upstream".split()).decode('utf-8'))
            print(subprocess.check_output(f"git checkout -b {branch_name}-{b} upstream/{b}".split()).decode('utf-8'))
            print(subprocess.check_output(f"git cherry-pick -x {commit_hash}".split()).decode('utf-8'))
            print(subprocess.check_output(f"git push origin {branch_name}".split()).decode('utf-8'))
            print(subprocess.check_output(f"git branch -D {branch_name}".split()).decode('utf-8'))
            create_gh_pr(b, branch_name, gh_auth=os.getenv("GH_AUTH"))

CPYTHON_CREATE_PR_URL = "https://api.github.com/repos/Mariatta/cpython/pulls"

def create_gh_pr(base_branch, head_branch, *,
                 gh_auth):
    """
    Create PR in GitHub
    """
    request_headers = sansio.create_headers(
        "Mariatta", oauth_token=gh_auth)
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