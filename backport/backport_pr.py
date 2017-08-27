import gidgethub.routing
import cherry_picker
import os

router = gidgethub.routing.Router()

@router.register("pull_request", action="opened")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr opened ")
    print(event.data)
    pass

@router.register("pull_request", action="reopened")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr reopened ")
    print(event.data)
    pass

@router.register("pull_request", action="closed")
async def backport_pr(event, gh, *args, **kwargs):
    print(" pr closed ")
    if event.data["pull_request"]["merged"]:
        print(f"is merged {event.data['pull_request']['merged']}")
        print(f"commit hash {event.data['pull_request']['merge_commit_sha']}")
        issue = await gh.getitem(event.data['repository']['issues_url'],
                                             {'number': f"{event.data['pull_request']['number']}"})
        print("ISSUES")
        print(issue)
        print("LABELS")
        labels = await gh.getitem(issue['labels_url'])
        branches = [label['name'].split()[-1] for label in labels if label['name'].startswith("needs backport to")]
        print(branches)

