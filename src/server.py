"""Webhook server for Capacium GitHub App."""
import hashlib
import hmac
import json
import os

from src.config import get_config
from src.handlers import handle_push, handle_release, handle_installation


def verify_signature(payload_body, signature_header, secret):
    if not secret:
        return True
    expected = "sha256=" + hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def app(environ, start_response):
    config = get_config()
    path = environ.get("PATH_INFO", "")

    if environ["REQUEST_METHOD"] != "POST" or path != "/webhook":
        start_response("404 Not Found", [("Content-Type", "application/json")])
        return [b'{"error": "not found"}']

    content_length = int(environ.get("CONTENT_LENGTH", 0))
    body = environ["wsgi.input"].read(content_length)

    sig = environ.get("HTTP_X_HUB_SIGNATURE_256", "")
    if not verify_signature(body, sig, config["webhook_secret"]):
        start_response("401 Unauthorized", [("Content-Type", "application/json")])
        return [b'{"error": "invalid signature"}']

    event = environ.get("HTTP_X_GITHUB_EVENT", "")
    delivery = environ.get("HTTP_X_GITHUB_DELIVERY", "")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        start_response("400 Bad Request", [("Content-Type", "application/json")])
        return [b'{"error": "invalid JSON"}']

    if event == "push":
        result = handle_push(payload)
    elif event == "release":
        result = handle_release(payload)
    elif event in ("installation", "installation_repositories"):
        result = handle_installation(payload, event)
    else:
        result = {"status": "ignored", "event": event}

    result["delivery"] = delivery
    response_body = json.dumps(result).encode()

    start_response("200 OK", [("Content-Type", "application/json")])
    return [response_body]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    config = get_config()
    httpd = make_server(config["host"], config["port"], app)
    print(f"Capacium GitHub App listening on {config['host']}:{config['port']}")
    httpd.serve_forever()
