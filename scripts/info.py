#!/usr/bin/env python

from pygit2 import Repository
from datetime import datetime

_repo = Repository('.')
_commit = _repo.revparse_single('HEAD')
_info = {
    'origin': [x.url for x in _repo.remotes][0],
    'commit': '{}'.format(_commit.id),
    'branch': _repo.head.name,
    'built': datetime.fromtimestamp(_commit.commit_time).isoformat()
}
print(_info)

from ons_ras_common import ons_env
print("ONS_ENV:", ons_env)


GIT_COMMIT=5b1bd4cdb669e502e1aa856a09626e3c43dc451d
GIT_BRANCH=origin/TBL063/health_check
JOB_BASE_NAME=RAS Test API Gateway
GIT_URL=https://github.com/ONSdigital/ras-api-gateway.git