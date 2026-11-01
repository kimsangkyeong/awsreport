####################################################################################################
#
# Purpose   : get SES identities (REGIONAL)
# Source    : ses.py
# Usage     : python awsreportwithkiro.py
# Developer : k.s.k & kiro
# --------  -----------   -------------------------------------------------
# Version :     date    :  reason
#  1.0      2026.11.01     first create (based on awsreport.py / ses.py, ctx-based)
#
# Ref     : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html
####################################################################################################
from __future__ import annotations

from .config import awsglobal
from .utils import paginate

klogger = awsglobal.klogger


def list_identities(ctx) -> list[dict]:
    results = []
    try:
        ses = ctx.get_client("ses")
        identities = list(paginate(ses, "list_identities", "Identities"))
        verify = {}
        if identities:
            try:
                verify = ses.get_identity_verification_attributes(
                    Identities=identities).get("VerificationAttributes", {})
            except Exception:  # noqa: BLE001
                verify = {}
        for ident in identities:
            attr = verify.get(ident, {})
            results.append({
                "Identity": ident,
                "VerificationStatus": attr.get("VerificationStatus", " "),
                "IdentityType": "Domain" if "@" not in ident else "EmailAddress",
            })
        if not results:
            results.append({"Identity": " ", "VerificationStatus": " ", "IdentityType": " "})
    except Exception as err:  # noqa: BLE001
        klogger.error("ses.list_identities(),region[%s],%s", ctx.region, err)
        results = [{"Identity": "ERROR CHECK", "VerificationStatus": "ERROR CHECK", "IdentityType": "ERROR CHECK"}]
    return results
