import gidgethub.routing
import cherry_picker
import os

router = gidgethub.routing.Router()

@router.register("pull_request", action="opened")
async def backport_pr(event, gh, *args, **kwargs):
    print(os.listdir('.'))
    print(event)
    print(gh)
    pass