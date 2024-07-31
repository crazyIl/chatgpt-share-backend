!function () {
  const originalDiv = document.querySelector("div.ulp-alternate-action");
  function createAlternateActionDiv(textContent, aTextContent, clickEvent) {
    const clonedDiv = originalDiv.cloneNode(true);
    const pElement = clonedDiv.querySelector("p");
    const newLink = pElement.querySelector("a").cloneNode(true);
    pElement.textContent = textContent;
    newLink.textContent = aTextContent;
    newLink.onclick = clickEvent;
    newLink.href = "#";
    pElement.appendChild(newLink);
    originalDiv.parentNode.insertBefore(clonedDiv, originalDiv.nextSibling);
  }
  function guid() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0,
        v = c == "x" ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  function loginUserKey(userKey) {
    fetch("/api/share/auth/openai/login_user_key?user_key=" + userKey)
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          window.location.href = "/auth/login_oauth?token=" + data.data;
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

  createAlternateActionDiv("No account? ", "Use custom system account", (event) => {
    event.preventDefault();
    Swal.fire({
      customClass: {
        inputLabel: "bold-label"
      },
      input: "textarea",
      inputLabel: "使用系统账号登录",
      inputPlaceholder: "请输入一个访问 Token（任意字符，用于会话隔离，未防止回话泄露，请使用较为复杂的 Token）",
      inputAttributes: {
        "aria-label": "请输入一个访问 Token"
      },
      showCancelButton: true,
      showLoaderOnConfirm: true,
    }).then((result) => {
      if (!result.isConfirmed || !result.value) {
        return
      }
      userKey = result.value.trim();
      localStorage.setItem("user_key", userKey);
      loginUserKey(userKey);
    });
    return false;

  });
  // 修改按钮点击事件
  const loginButton = document.querySelector("#submit-token");


  let callOriginalMethod = false;
  createAlternateActionDiv("Got account? ", "Continue with Access Token", (event) => {
    // 打断原始点击事件
    event.preventDefault();
    callOriginalMethod = true;
    loginButton.click();
    callOriginalMethod = false;
  });


  // 删除 originalDiv
  originalDiv.remove();
  // 替换原始元素
  loginButton.lastChild.textContent = "Continue with System Account";
  // 添加新的点击事件
  loginButton.addEventListener("click", (event) => {
    if (callOriginalMethod) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    Swal.showLoading();
    // 随机生成一个 Token
    let userKey = localStorage.getItem("user_key");
    if (!userKey) {
      userKey = "rd_" + guid();
      localStorage.setItem("user_key", userKey);
    }
    loginUserKey(userKey);
    return false;
  }, true);

}();


window.addEventListener("load", function () {
  Swal.fire({
    title: "<strong>使用教程</strong>",
    icon: "",
    width: "80%",
    html: `<h3>第一步</h3><br>
      <img height="300" src="https://s21.ax1x.com/2024/07/01/pkcjAvq.png">`,
    showCloseButton: false,
    showCancelButton: false,
    focusConfirm: false,
    confirmButtonText: `Great!`,
  });
});

// html
// <br>
//       <strong>第二步</strong><br>
//       <img height="409" src="https://s21.ax1x.com/2024/07/01/pkcjk2n.png"></img>
