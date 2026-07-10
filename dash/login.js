(() => {
  const params = new URLSearchParams(window.location.search);
  const requestedNext = params.get("next") || "/";
  const next = requestedNext.startsWith("/") && !requestedNext.startsWith("//") ? requestedNext : "/";
  const error = params.get("error");
  const messages = {
    invalid: "用户名或密码不正确，请重新输入。",
    rate: "尝试次数过多，请稍后再试。",
    service: "登录服务暂时不可用，请稍后再试。",
  };

  const nextInput = document.querySelector("#auth-next");
  const message = document.querySelector("#auth-message");
  const form = document.querySelector("#auth-form");
  const password = document.querySelector("#auth-password");
  const toggle = document.querySelector("#auth-password-toggle");
  const submit = document.querySelector("#auth-submit");

  if (nextInput) {
    nextInput.value = next;
  }

  if (message && error && messages[error]) {
    message.textContent = messages[error];
    message.hidden = false;
  }

  toggle?.addEventListener("click", () => {
    const show = password.type === "password";
    password.type = show ? "text" : "password";
    toggle.textContent = show ? "隐藏" : "显示";
    toggle.setAttribute("aria-label", show ? "隐藏密码" : "显示密码");
    password.focus();
  });

  form?.addEventListener("submit", () => {
    submit.disabled = true;
    submit.querySelector("span").textContent = "正在进入…";
  });

  fetch("/auth/check", { credentials: "same-origin", cache: "no-store" })
    .then((response) => {
      if (response.status === 204) {
        window.location.replace(next);
      }
    })
    .catch(() => {});
})();
