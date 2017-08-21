import gidgethub.routing
import cherry_picker
import os
import subprocess
router = gidgethub.routing.Router()

@router.register("pull_request", action="opened")
async def backport_pr(event, gh, *args, **kwargs):
    os.chdir("cpython")
    subprocess.check_output("git status".split())
    subprocess.check_output("git remote --v".split())
    pass