let { startAuthentication, startRegistration } = SimpleWebAuthnBrowser;
const login = document.getElementById("login");
const loginInnerHTML = login.innerHTML;
const register = document.getElementById("register");
const registerInnerHTML = register.innerHTML;
const handleError = (button, buttonInnerHTML, error, msg = "出错啦！") => {
  alert(msg);
  button.innerHTML = buttonInnerHTML;
  button.disabled = false;
  throw error;
};
login.addEventListener("click", async () => {
  login.disabled = true;
  login.innerHTML = "等待身份验证器响应...";
  let r = await fetch("/webauthn/authenticate");
  if (r.status !== 200) {
    handleError(
      login,
      loginInnerHTML,
      new Error("Failed to fetch authentication options")
    );
    return;
  }
  r = await r.json();
  if (r.status !== "success" || !r.options) {
    handleError(
      login,
      loginInnerHTML,
      new Error("Failed to get authentication options"),
      r.msg
    );
    return;
  }
  let attestation;
  try {
    attestation = await startAuthentication(r.options);
  } catch (error) {
    handleError(login, loginInnerHTML, error);
    return;
  }
  r = await fetch("/webauthn/authenticate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(attestation),
  });
  if (r.status === 200) {
    r = await r.json();
    if (r.status === "success") {
      window.location = "/";
      return;
    }
  }
  handleError(
    login,
    loginInnerHTML,
    new Error("Failed to verify authentication response"),
    r.msg
  );
});

register.addEventListener("click", async () => {
  register.disabled = true;
  register.innerHTML = "等待身份验证器响应...";
  let r = await fetch(
    "/webauthn/register?" +
      new URLSearchParams({
        username: document.getElementById("username").value,
      })
  );
  if (r.status !== 200) {
    handleError(
      register,
      registerInnerHTML,
      new Error("Failed to fetch registration options")
    );
    return;
  }
  r = await r.json();
  if (r.status !== "success" || !r.options) {
    handleError(
      register,
      registerInnerHTML,
      new Error("Failed to get registration options"),
      r.msg
    );
    return;
  }
  let attestation;
  try {
    attestation = await startRegistration(r.options);
  } catch (error) {
    handleError(register, registerInnerHTML, error);
    return;
  }
  r = await fetch("/webauthn/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(attestation),
  });
  if (r.status === 200) {
    r = await r.json();
    if (r.status === "success") {
      alert("注册成功！");
      window.location.reload();
      return;
    }
  }
  handleError(
    register,
    registerInnerHTML,
    new Error("Failed to verify registration response"),
    r.msg
  );
});
