import gidgethub.routing
import cherry_picker


router = gidgethub.routing.Router()

@router.register("pull_request", action="opened")
async def backport_pr(event, gh, *args, **kwargs):
    print(event)
    print(gh)
    pass