# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""
Test heartbeat functionality

./test_health_all.py --env <dev,stage,prod>
"""
import argparse, logging, json
import urllib3

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("test-health-all").setLevel(logging.INFO)

timeout = 2.0

services_to_test = {
    "dev": {
        "auth": "https://example.com/healthz",
        "api": "https://example.com/healthz",
        "auth-version": "https://example.com/versionz",
        "api-version": "https://example.com/versionz",
        "proxy": "https://example.com/healthz",
    },
    "dev-non-json": {
        "admin": "https://admin.example.com",
        "ui": "https://example.com",
    },
    "stage": {
        "auth": "https://example.com/healthz",
        "api": "https://api.example.com/healthz",
        "auth-version": "https://example.com/versionz",
        "api-version": "https://api.example.com/versionz",
        "proxy": "https://example.com/healthz",
    },
    "stage-non-json": {
        "admin": "https://admin.example.com",
        "ui": "https://example.com",
    },
    "prod": {
        "auth": "https://auth.example.com/versionz",
        "api": "https://api.example.com/versionz",
        "auth-version": "https://auth.example.com/versionz",
        "api-version": "https://api.example.com/versionz",
        "proxy": "https://tools.example.com/healthz",
    },
    "prod-non-json": {
        "admin": "https://admin.example.com",
        "ui": "https://example.com",
    },
}

logging.info(f"urllib3: {urllib3.__version__}")


def test_endpoints(env):
    http = urllib3.PoolManager(timeout=timeout)
    for svc, url in services_to_test[env].items():
        logging.info(f"{svc} -> {url}")
        r = http.request("GET", url)
        assert r.status == 200, f"{svc} response: Should be 200"
        parsed = json.loads(r.data.decode("utf-8"))
        logging.info(json.dumps(parsed, indent=2))

    for svc, url in services_to_test[f"{env}-non-json"].items():
        logging.info(f"{svc} -> {url}")
        r = http.request("GET", url)
        assert r.status == 200, f"{svc} response: Should be 200"

    logging.info("RESULT::OK")


if __name__ == "__main__":
    logging.info("Validate STATUS for all services")
    parser = argparse.ArgumentParser(description="Test Services heartbeat")

    parser.add_argument(
        "-e",
        "--env",
        required=True,
        help="Environment",
        choices=["dev", "stage", "prod"],
    )
    args = parser.parse_args()
    test_endpoints(env=args.env)
