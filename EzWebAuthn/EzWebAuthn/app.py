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

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


@app.route("/")
def index():
    if session.get("authenticated"):
        # --- DEBUG PRINT ---
        auth_username = session.get("authentication_username")
        print(
            f"[*] app.py - index() - Authenticated user from session: {
                auth_username}",
            flush=True,
        )
        # --- END DEBUG ---
        user = Users.one({"username": session.get("authentication_username")})
        return render_template("index.html", user=user, flag=os.environ.get("FLAG"))
    return render_template("auth.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


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
        session["authentication_challenge"] = authentication_options.get(
            "challenge")
        # --- DEBUG PRINT ---
        print(
            f"[*] app.py - authenticate(GET) - Challenge set: {
                session['authentication_challenge']
            }",
            flush=True,
        )
        # --- END DEBUG ---
        return jsonify(dict(status="success", options=authentication_options))
    elif request.method == "POST":
        challenge = session.get("authentication_challenge")
        if not challenge:
            # --- DEBUG PRINT ---
            print(
                "[!] app.py - authenticate(POST) - Session missing challenge!",
                flush=True,
            )
            # --- END DEBUG ---
            return jsonify(dict(status="error", msg="Session missing!"))

        # --- DEBUG PRINT ---
        print(
            f"[*] app.py - authenticate(POST) - Raw request data: {
                request.data}",
            flush=True,
        )
        # --- END DEBUG ---
        try:
            authentication_credential = json.loads(request.data)
            # --- DEBUG PRINT ---
            print(
                f"[*] app.py - authenticate(POST) - Parsed credential: {
                    authentication_credential
                }",
                flush=True,
            )
            cred_id_from_req = authentication_credential.get("id")
            print(
                f"[*] app.py - authenticate(POST) - Credential ID from request: {
                    cred_id_from_req
                }",
                flush=True,
            )
            # --- END DEBUG ---

            # --- Get Public Key ---
            print(
                f"[*] app.py - authenticate(POST) - Getting public key for cred_id: {
                    cred_id_from_req
                }",
                flush=True,
            )
            expected_public_key_b64 = Credentials.scalar(
                {"credential_id": cred_id_from_req}, "public_key"
            )
            print(
                f"[*] app.py - authenticate(POST) - Found public key (b64): {
                    expected_public_key_b64
                }",
                flush=True,
            )
            if not expected_public_key_b64:
                raise Exception("Public key not found for credential ID")
            credential_public_key_bytes = base64url_to_bytes(
                expected_public_key_b64)

            # --- Get Sign Count ---
            print(
                f"[*] app.py - authenticate(POST) - Getting sign count for cred_id: {
                    cred_id_from_req
                }",
                flush=True,
            )
            credential_current_sign_count = Credentials.scalar(
                {"credential_id": cred_id_from_req}, "sign_count"
            )
            print(
                f"[*] app.py - authenticate(POST) - Found sign count: {
                    credential_current_sign_count
                }",
                flush=True,
            )
            if (
                credential_current_sign_count is None
            ):  # Sign count can be 0, check for None
                raise Exception("Sign count not found for credential ID")

            # --- DEBUG PRINT - verify_authentication_response Args ---
            print(
                "[*] app.py - authenticate(POST) - Calling verify_authentication_response with:",
                flush=True,
            )
            print(f"  - credential: {authentication_credential}", flush=True)
            print(
                f"  - expected_challenge: {base64url_to_bytes(challenge)} ({
                    challenge
                })",
                flush=True,
            )
            print(
                f"  - expected_rp_id: {request.host.split(':')[0]}", flush=True)
            print(
                f"  - expected_origin: {request.host_url.rstrip('/')}", flush=True)
            print(
                f"  - credential_public_key: {credential_public_key_bytes} (from {
                    expected_public_key_b64
                })",
                flush=True,
            )
            print(
                f"  - credential_current_sign_count: {
                    credential_current_sign_count}",
                flush=True,
            )
            # --- END DEBUG ---

            authentication_verification = verify_authentication_response(
                credential=authentication_credential,
                expected_challenge=base64url_to_bytes(challenge),
                expected_rp_id=request.host.split(":")[0],
                expected_origin=request.host_url.rstrip("/"),
                credential_public_key=credential_public_key_bytes,
                credential_current_sign_count=credential_current_sign_count,
            )
            # --- DEBUG PRINT ---
            print(
                "[*] app.py - authenticate(POST) - verify_authentication_response SUCCESSFUL!",
                flush=True,
            )
            print(
                f"[*] app.py - authenticate(POST) - New sign count: {
                    authentication_verification.new_sign_count
                }",
                flush=True,
            )
            # --- END DEBUG ---

            Credentials.update(
                # Use the ID from request again
                {"credential_id": cred_id_from_req},
                {"sign_count": authentication_verification.new_sign_count},
            )
            del session["authentication_challenge"]

            # --- Get User ID ---
            print(
                f"[*] app.py - authenticate(POST) - Getting user_id for cred_id: {
                    cred_id_from_req
                }",
                flush=True,
            )
            verified_user_id = Credentials.scalar(
                # Use the ID from request again
                {"credential_id": cred_id_from_req},
                "user_id",
            )
            print(
                f"[*] app.py - authenticate(POST) - Found user_id: {
                    verified_user_id}",
                flush=True,
            )
            if not verified_user_id:
                raise Exception(
                    "User ID not found for credential ID after verification"
                )

            # --- Get Username ---
            print(
                f"[*] app.py - authenticate(POST) - Getting username for user_id: {
                    verified_user_id
                }",
                flush=True,
            )
            verified_username = Users.scalar(
                {"id": verified_user_id},
                "username",
            )
            print(
                f"[*] app.py - authenticate(POST) - Found username: {
                    verified_username
                }",
                flush=True,
            )
            if not verified_username:
                raise Exception("Username not found for user ID")

            session["authenticated"] = True
            session["authentication_username"] = verified_username
            print(
                f"[*] app.py - authenticate(POST) - Session set: authenticated=True, authentication_username={
                    verified_username
                }",
                flush=True,
            )
            return jsonify(dict(status="success"))
        except Exception as e:
            # --- DEBUG PRINT ---
            import traceback

            print(
                f"[!] app.py - authenticate(POST) - EXCEPTION: {e}", flush=True)
            print(traceback.format_exc(), flush=True)  # Print full traceback
            # --- END DEBUG ---
            if "authentication_challenge" in session:
                del session["authentication_challenge"]
            return jsonify(dict(status="error", msg="登录失败！"))


# ... (rest of app.py remains the same) ...


@app.route("/webauthn/register", methods=["GET", "POST"])
def register():
    if session.get("authenticated"):
        return jsonify(dict(status="error", msg="已经登录！"))
    if request.method == "GET":
        username = request.args.get("username")
        # --- DEBUG PRINT ---
        print(
            f"[*] app.py - register(GET) - Attempting registration for username: {
                username
            }",
            flush=True,
        )
        # --- END DEBUG ---
        if not username or Users.one({"username": username}):
            # --- DEBUG PRINT ---
            print(
                f"[!] app.py - register(GET) - Username invalid or exists: {
                    username}",
                flush=True,
            )
            # --- END DEBUG ---
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
        session["registration_challenge"] = registration_options.get(
            "challenge")
        # --- DEBUG PRINT ---
        print(
            f"[*] app.py - register(GET) - Registration options generated for {
                username
            }, challenge: {session['registration_challenge']}",
            flush=True,
        )
        # --- END DEBUG ---
        return jsonify(dict(status="success", options=registration_options))
    elif request.method == "POST":
        username = session.get("registration_username")
        challenge = session.get("registration_challenge")
        if not username or not challenge:
            # --- DEBUG PRINT ---
            print(
                f"[!] app.py - register(POST) - Session missing username or challenge! Username: {
                    username
                }, Challenge: {challenge}",
                flush=True,
            )
            # --- END DEBUG ---
            return jsonify(dict(status="error", msg="Session missing!"))
        # --- DEBUG PRINT ---
        print(
            f"[*] app.py - register(POST) - Raw request data: {request.data}",
            flush=True,
        )
        # --- END DEBUG ---
        try:
            registration_credential = json.loads(request.data)
            # --- DEBUG PRINT ---
            print(
                f"[*] app.py - register(POST) - Parsed registration credential: {
                    registration_credential
                }",
                flush=True,
            )
            print(
                f"[*] app.py - register(POST) - Calling verify_registration_response for user {
                    username
                }, challenge {challenge}",
                flush=True,
            )
            # --- END DEBUG ---
            verified_registration = verify_registration_response(
                credential=registration_credential,
                expected_challenge=base64url_to_bytes(challenge),
                expected_origin=request.host_url.rstrip("/"),
                expected_rp_id=request.host.split(":")[0],
            )
            # --- DEBUG PRINT ---
            print(
                f"[*] app.py - register(POST) - Registration verification successful!",
                flush=True,
            )
            new_cred_id = (
                urlsafe_b64encode(verified_registration.credential_id)
                .decode("utf-8")
                .rstrip("=")
            )
            new_pub_key = (
                urlsafe_b64encode(verified_registration.credential_public_key)
                .decode("utf-8")
                .rstrip("=")
            )
            print(
                f"[*] app.py - register(POST) - Creating user '{
                    username
                }' with cred_id '{new_cred_id}' and pub_key '{new_pub_key}'",
                flush=True,
            )
            # --- END DEBUG ---
            create_user(
                username=username,
                role="user",
                credential_id=new_cred_id,
                public_key=new_pub_key,
            )
            del session["registration_challenge"]
            # --- DEBUG PRINT ---
            print(
                f"[*] app.py - register(POST) - Registration complete for {
                    username}",
                flush=True,
            )
            # --- END DEBUG ---
            return jsonify(dict(status="success"))
        except Exception as e:
            # --- DEBUG PRINT ---
            import traceback

            print(f"[!] app.py - register(POST) - EXCEPTION: {e}", flush=True)
            print(traceback.format_exc(), flush=True)  # Print full traceback
            # --- END DEBUG ---
            if "registration_challenge" in session:
                del session["registration_challenge"]
            return jsonify(dict(status="error", msg="注册失败！"))
