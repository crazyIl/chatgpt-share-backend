!function () {
  function guid() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0,
        v = c == "x" ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  function loginUserKey(userKey) {
    fetch("/api/share/auth/fuclaude/login_user_key?user_key=" + userKey)
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          window.location.href = "/login_oauth?token=" + data.data;
        } else {
          Swal.fire("Error", data.data, "error").then(() => {
            window.location.reload();
          });
        }
      })
      .catch(() => {
        Swal.fire("Error", "没有可用的帐户。请稍后再试。", "error").then(() => {
          window.location.reload();
        });
      });
  }

  function getCookie(name) {
    let cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
      let [cookieName, cookieValue] = cookie.split("=");
      if (cookieName === decodeURIComponent(name)) {
        return decodeURIComponent(cookieValue);
      }
    }
    return null;
  }

  function setCookie(name, value, days = 365) {
    let date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    let expires = date.toUTCString();
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + "; expires=" + expires + "; path=/";
  }


  const originalButton = document.querySelector("#submit-token");
  function createAlternateActionButton(textContent, clickEvent) {
    const clonedButton = originalButton.cloneNode(true);
    clonedButton.style.marginTop = "24px";
    clonedButton.id = "submit-token-" + guid();
    clonedButton.lastChild.textContent = textContent;
    clonedButton.onclick = clickEvent;
    originalButton.parentNode.insertBefore(clonedButton, originalButton.nextSibling);
  }

  createAlternateActionButton("Continue with System Account", (event) => {
    event.preventDefault();
    event.stopPropagation();
    Swal.showLoading();
    // 随机生成一个 Token
    let userKey = getCookie("user_key");
    if (!userKey) {
      userKey = "rd_" + guid();
      setCookie("user_key", userKey);
    }
    loginUserKey(userKey);
    return false;
  });

}();
