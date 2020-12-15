import requests

from settings import *

BOTURL = "https://recurse.rctogether.com/api/bots/"

# ==== REST API ================================================================

def post(id, j):
    return requests.post(BOTURL+str(id), json=j, auth=(app_id, app_secret))

def patch(id, j):
    return requests.patch(BOTURL+str(id), json=j, auth=(app_id, app_secret))

def delete(id, j=None):
    if j is None:
        return requests.delete(BOTURL+str(id), auth=(app_id, app_secret))
    else:
        return requests.delete(BOTURL+str(id), json=j, auth=(app_id, app_secret))