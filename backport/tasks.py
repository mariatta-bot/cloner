import celery
import os
import subprocess

app = celery.Celery('example')

app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

@app.task
def clone_cpython():
    print("cloning cpython")
    result = subprocess.check_output(
        "git clone https://github.com/mariatta-bot/cpython.git".split())
    print(result.decode('utf-8'))

    result = subprocess.check_output(
        "git remote add upstream https://github.com/mariatta/cpython.git".split())
    print(result.decode('utf-8'))

    print("finished cloning")

