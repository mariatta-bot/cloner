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
    print(" pr merged ")
    print(event.data)
    pass