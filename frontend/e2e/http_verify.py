#!/usr/bin/env python3
"""HTTP-level Retail ERP verification harness (no browser required).

Exercises the real backend APIs the Vue SPA depends on through an
authenticated session, using only the Python standard library. This is a
fallback for environments where Playwright/Chromium cannot be installed
(see docs/ui/SMJ_VISUAL_REGRESSION.md) — it proves the data layer behind
the UI works (real records, correct empty/error states, working auth) but
does NOT verify rendering, layout, or console output. Prefer
e2e/wholesale.spec.js (Playwright) once real browser automation is
available; this script is not a replacement for it.

Usage:
    python3 e2e/http_verify.py

Environment variables:
    BASE_URL   default http://127.0.0.1:8000
    ERP_USER   default Administrator
    ERP_PW     required — no default, this script refuses to guess one
"""

import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
USER = os.environ.get("ERP_USER", "Administrator")
PW = os.environ.get("ERP_PW")

if not PW:
    print("ERP_PW environment variable is required (no default password is baked in).", file=sys.stderr)
    sys.exit(2)

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def call(method, params=None, http_method="GET"):
    params = params or {}
    url = f"{BASE}/api/method/{method}"
    if http_method == "GET":
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url)
    else:
        req = urllib.request.Request(
            url,
            data=json.dumps(params).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
    try:
        with opener.open(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}


def route(path):
    req = urllib.request.Request(f"{BASE}{path}")
    try:
        with opener.open(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    failures = 0

    # Login needs form encoding, not JSON, so it bypasses call().
    req = urllib.request.Request(
        f"{BASE}/api/method/login",
        data=urllib.parse.urlencode({"usr": USER, "pwd": PW}).encode(),
        method="POST",
    )
    with opener.open(req) as resp:
        login_body = json.loads(resp.read())
    if not check("login succeeds", login_body.get("message") == "Logged In"):
        failures += 1
        sys.exit(1)

    status, body = call("my_store_ui.standalone.get_session_bootstrap")
    msg = body.get("message", {})
    if not check("session bootstrap returns authenticated user", status == 200 and msg.get("authenticated")):
        failures += 1
    if not check("navigation payload is non-empty", len(msg.get("navigation", [])) > 0):
        failures += 1

    for path in ["/retail-erp/home", "/retail-erp/smart-sales", "/retail-erp/reports"]:
        if not check(f"SPA shell serves {path}", route(path) == 200):
            failures += 1

    status, body = call("my_store_ui.search.global_search", {"text": "a", "limit": 5})
    if not check("global search responds 200", status == 200):
        failures += 1

    status, body = call("my_store_ui.priority_pages.get_module_dashboard", {"module": "home"})
    if not check("home dashboard responds 200 with metrics", status == 200 and body.get("message", {}).get("metrics")):
        failures += 1

    print(f"\n{failures} failure(s).")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
