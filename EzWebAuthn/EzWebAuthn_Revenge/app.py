import json
import os
from base64 import urlsafe_b64encode

from flask import Flask, jsonify, redirect, render_template, request, session
from webauthn import (
    base64url_to_bytes,
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)
from werkzeug.middleware.proxy_fix import ProxyFix

from db import Credentials, Users, create_user

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


@app.route("/")
def index():
    if session.get("authenticated"):
        user = Users.one({"id": session.get("authentication_user_id")})
        return render_template("index.html", user=user, flag=os.environ.get("FLAG"))
    return render_template("auth.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


def check_credential_id(credential_id):
    if type(credential_id) is not str:
        return False
    for c in credential_id:
        if c not in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_":
            return False
    return True


@app.route("/webauthn/authenticate", methods=["GET", "POST"])
def authenticate():
    if session.get("authenticated"):
        return jsonify(dict(status="error", msg="已经登录！"))
    if request.method == "GET":
        authentication_options = json.loads(
            options_to_json(
                generate_authentication_options(
                    rp_id=request.host.split(":")[0],
                )
            )
        )
        session["authentication_challenge"] = authentication_options.get("challenge")
        return jsonify(dict(status="success", options=authentication_options))
    elif request.method == "POST":
        challenge = session.get("authentication_challenge")
        if not challenge:
            return jsonify(dict(status="error", msg="Session missing!"))
        try:
            authentication_credential = json.loads(request.data)
            if not check_credential_id(authentication_credential.get("id")):
                raise Exception("Invalid credential ID")
            authentication_verification = verify_authentication_response(
                credential=authentication_credential,
                expected_challenge=base64url_to_bytes(challenge),
                expected_rp_id=request.host.split(":")[0],
                expected_origin=request.host_url.rstrip("/"),
                credential_public_key=base64url_to_bytes(
                    Credentials.scalar(
                        {"credential_id": authentication_credential.get("id")},
                        "public_key",
                    )
                ),
                credential_current_sign_count=Credentials.scalar(
                    {"credential_id": authentication_credential.get("id")},
                    "sign_count",
                ),
            )
            Credentials.update(
                {"credential_id": authentication_credential.get("id")},
                {"sign_count": authentication_verification.new_sign_count},
            )
            del session["authentication_challenge"]
            session["authenticated"] = True
            session["authentication_user_id"] = Credentials.scalar(
                {"credential_id": authentication_credential.get("id")},
                "user_id",
            )
            return jsonify(dict(status="success"))
        except Exception:
            del session["authentication_challenge"]
            return jsonify(dict(status="error", msg="登录失败！"))


@app.route("/webauthn/register", methods=["GET", "POST"])
def register():
    if session.get("authenticated"):
        return jsonify(dict(status="error", msg="已经登录！"))
    if request.method == "GET":
        username = request.args.get("username")
        if not username or Users.one({"username": username}):
            return jsonify(dict(status="error", msg="用户名已存在或无效！"))
        authenticator_selection = AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        registration_options = json.loads(
            options_to_json(
                generate_registration_options(
                    rp_id=request.host.split(":")[0].split(":")[0],
                    rp_name="EzWebAuthn",
                    user_id=username.encode("utf-8"),
                    user_name=username,
                    authenticator_selection=authenticator_selection,
                )
            )
        )
        session["registration_username"] = username
        session["registration_challenge"] = registration_options.get("challenge")
        return jsonify(dict(status="success", options=registration_options))
    elif request.method == "POST":
        username = session.get("registration_username")
        challenge = session.get("registration_challenge")
        if not username or not challenge:
            return jsonify(dict(status="error", msg="Session missing!"))
        try:
            registration_credential = json.loads(request.data)
            verified_registration = verify_registration_response(
                credential=registration_credential,
                expected_challenge=base64url_to_bytes(challenge),
                expected_origin=request.host_url.rstrip("/"),
                expected_rp_id=request.host.split(":")[0],
            )
            create_user(
                username=username,
                role="user",
                credential_id=urlsafe_b64encode(verified_registration.credential_id)
                .decode("utf-8")
                .rstrip("="),
                public_key=urlsafe_b64encode(
                    verified_registration.credential_public_key
                )
                .decode("utf-8")
                .rstrip("="),
            )
            del session["registration_challenge"]
            return jsonify(dict(status="success"))
        except Exception:
            del session["registration_challenge"]
            return jsonify(dict(status="error", msg="注册失败！"))
