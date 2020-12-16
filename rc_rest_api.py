import requests

from settings import *

BOTURL = "https://recurse.rctogether.com/api/bots/"
NOTEURL = "https://recurse.rctogether.com/api/notes/"
WALLURL = "https://recurse.rctogether.com/api/walls/"

# ==== REST API ================================================================

def post(id, j, url=BOTURL):
    return requests.post(url+str(id), json=j, auth=(app_id, app_secret))

def patch(id, j, url=BOTURL):
    return requests.patch(url+str(id), json=j, auth=(app_id, app_secret))

def delete(id, j=None, url=BOTURL):
    if j is None:
        return requests.delete(url+str(id), auth=(app_id, app_secret))
    else:
        return requests.delete(url+str(id), json=j, auth=(app_id, app_secret))
