import os
import urllib.request as req

if os.environ.get("app_url",None) is not None:
    req.urlopen(os.environ.get("app_url"))
