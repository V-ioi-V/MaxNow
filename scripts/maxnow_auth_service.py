#!/usr/bin/env python3

import argparse
import base64
import binascii
import hashlib
import hmac
import os
import subprocess
import tempfile
import time
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_CREDENTIAL_FILE = "/etc/nginx/.htpasswd-maxnow"
DEFAULT_SECRET_FILE = "/etc/maxnow-auth/session.key"
SESSION_COOKIE = "maxnow_session"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60
MAX_FORM_BYTES = 8192


def encode_urlsafe(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def decode_urlsafe(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_session(username, secret, now=None):
    expires_at = int((time.time() if now is None else now) + SESSION_TTL_SECONDS)
    payload = f"{username}\n{expires_at}".encode("utf-8")
    encoded = encode_urlsafe(payload)
    signature = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded}.{encode_urlsafe(signature)}"


def validate_session(token, secret, now=None):
    try:
        encoded, supplied_signature = token.split(".", 1)
        expected_signature = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(decode_urlsafe(supplied_signature), expected_signature):
            return None
        username, raw_expiry = decode_urlsafe(encoded).decode("utf-8").split("\n", 1)
        if int(raw_expiry) < int(time.time() if now is None else now):
            return None
        return username
    except (ValueError, UnicodeDecodeError, binascii.Error):
        return None


def safe_next(value):
    if not value or not value.startswith("/") or value.startswith("//"):
        return "/"
    if "\r" in value or "\n" in value:
        return "/"
    return value


def load_secret(path):
    secret = Path(path).read_bytes()
    if len(secret) < 32:
        raise ValueError("session secret must contain at least 32 bytes")
    return secret


def load_password_hash(path, username):
    with Path(path).open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            stored_username, separator, stored_hash = raw_line.rstrip("\n").partition(":")
            if separator and hmac.compare_digest(stored_username, username):
                return stored_hash
    return None


def verify_password(username, password, credential_file):
    stored_hash = load_password_hash(credential_file, username)
    if not stored_hash or not stored_hash.startswith("$6$"):
        return False
    parts = stored_hash.split("$")
    if len(parts) != 4 or not parts[2]:
        return False
    result = subprocess.run(
        ["openssl", "passwd", "-6", "-salt", parts[2], "-stdin"],
        input=password.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=5,
    )
    candidate = result.stdout.decode("utf-8", errors="replace").strip()
    return result.returncode == 0 and hmac.compare_digest(candidate, stored_hash)


def read_session_cookie(header_value):
    jar = cookies.SimpleCookie()
    try:
        jar.load(header_value or "")
    except cookies.CookieError:
        return ""
    morsel = jar.get(SESSION_COOKIE)
    return morsel.value if morsel else ""


class AuthHandler(BaseHTTPRequestHandler):
    server_version = "MaxNowAuth"
    sys_version = ""

    def send_status(self, status):
        self.send_response(status)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def redirect(self, location, cookie_value=None):
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        if cookie_value is not None:
            self.send_header("Set-Cookie", cookie_value)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def session_username(self):
        token = read_session_cookie(self.headers.get("Cookie"))
        return validate_session(token, self.server.session_secret) if token else None

    def do_GET(self):
        if self.path == "/health":
            self.send_status(204)
            return
        if self.path == "/check":
            username = self.session_username()
            if username:
                self.send_response(204)
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Auth-User", username)
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                self.send_status(401)
            return
        self.send_status(404)

    def do_POST(self):
        if self.path == "/login":
            self.handle_login()
            return
        if self.path == "/logout":
            expired_cookie = (
                f"{SESSION_COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0"
            )
            self.redirect("/login", expired_cookie)
            return
        self.send_status(404)

    def handle_login(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_status(400)
            return
        if length <= 0 or length > MAX_FORM_BYTES:
            self.send_status(400)
            return

        payload = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"), keep_blank_values=True)
        username = payload.get("username", [""])[0]
        password = payload.get("password", [""])[0]
        next_path = safe_next(payload.get("next", ["/"])[0])

        try:
            valid = verify_password(username, password, self.server.credential_file)
        except (OSError, subprocess.SubprocessError):
            self.redirect("/login?" + urlencode({"error": "service", "next": next_path}))
            return
        finally:
            password = ""

        if not valid:
            self.redirect("/login?" + urlencode({"error": "invalid", "next": next_path}))
            return

        token = create_session(username, self.server.session_secret)
        cookie_value = (
            f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; Secure; SameSite=Strict; "
            f"Max-Age={SESSION_TTL_SECONDS}"
        )
        self.redirect(next_path, cookie_value)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}", flush=True)


class AuthServer(ThreadingHTTPServer):
    def __init__(self, address, handler, credential_file, secret_file):
        super().__init__(address, handler)
        self.credential_file = credential_file
        self.session_secret = load_secret(secret_file)


def run_self_test():
    secret = b"s" * 32
    token = create_session("maxnow", secret, now=100)
    assert validate_session(token, secret, now=101) == "maxnow"
    assert validate_session(token + "x", secret, now=101) is None
    assert validate_session(token, secret, now=100 + SESSION_TTL_SECONDS + 1) is None
    assert safe_next("/tokens") == "/tokens"
    assert safe_next("//example.com") == "/"

    with tempfile.TemporaryDirectory() as temp_dir:
        credential_file = Path(temp_dir) / "credentials"
        result = subprocess.run(
            ["openssl", "passwd", "-6", "-salt", "maxnowtest", "-stdin"],
            input=b"correct-password",
            stdout=subprocess.PIPE,
            check=True,
            timeout=5,
        )
        credential_file.write_text(f"maxnow:{result.stdout.decode().strip()}\n", encoding="utf-8")
        assert verify_password("maxnow", "correct-password", credential_file)
        assert not verify_password("maxnow", "wrong-password", credential_file)
        assert not verify_password("other", "correct-password", credential_file)
    print("[ok] maxnow auth service self-test")


def main():
    parser = argparse.ArgumentParser(description="MaxNow cookie authentication service")
    parser.add_argument("--host", default=os.environ.get("MAXNOW_AUTH_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MAXNOW_AUTH_PORT", DEFAULT_PORT)))
    parser.add_argument(
        "--credential-file",
        default=os.environ.get("MAXNOW_AUTH_CREDENTIAL_FILE", DEFAULT_CREDENTIAL_FILE),
    )
    parser.add_argument(
        "--secret-file",
        default=os.environ.get("MAXNOW_AUTH_SECRET_FILE", DEFAULT_SECRET_FILE),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    server = AuthServer((args.host, args.port), AuthHandler, args.credential_file, args.secret_file)
    print(f"MaxNow auth service listening on {args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
