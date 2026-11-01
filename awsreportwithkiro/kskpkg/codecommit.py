####################################################################################################
#
# Purpose   : get CodeCommit repositories (REGIONAL)
# Source    : codecommit.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / codecommit.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_repositories(ctx) -> list[dict]:
    results = []
    try:
        cc = ctx.get_client("codecommit")
        for repo in paginate(cc, "list_repositories", "repositories"):
            results.append({
                "RepositoryName": repo.get("repositoryName", " "),
                "RepositoryId": repo.get("repositoryId", " "),
            })
        if not results:
            results.append({"RepositoryName": " ", "RepositoryId": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("codecommit.list_repositories(),region[%s],%s", ctx.region, err)
        results = [{"RepositoryName": "ERROR CHECK", "RepositoryId": "ERROR CHECK"}]
    return results
