# nginx反代示例

## ChatGPT

```nginx
  location / {
    proxy_ssl_server_name on;
    proxy_pass https://new.oaifree.com;
    proxy_set_header Host new.oaifree.com;
  }
  
  location /auth/login_auth0 {
    proxy_ssl_server_name on;
    proxy_pass https://new.oaifree.com;
    proxy_set_header Accept-Encoding "";  # 禁用压缩
    sub_filter_once on;
    sub_filter '</body>' '<script>
!function(){const e=document.querySelector("div.ulp-alternate-action");let t=!1;function o(t,o,n){const r=e.cloneNode(!0),a=r.querySelector("p"),l=a.querySelector("a").cloneNode(!0);a.textContent=t,l.textContent=o,l.onclick=n,l.href="#",a.appendChild(l),e.parentNode.insertBefore(r,e.nextSibling)}function n(e){fetch("/api/share/auth/openai/login_user_key?user_key="+e).then(e=>e.json()).then(e=>{e.success?window.location.href="/auth/login_oauth?token="+e.data:Swal.fire("Error",e.data,"error").then(()=>{window.location.reload()})}).catch(()=>{Swal.fire("Error","没有可用的帐户。请稍后再试。","error").then(()=>{window.location.reload()})})}o("No account? ","Use custom system account",e=>(e.preventDefault(),Swal.fire({customClass:{inputLabel:"bold-label"},input:"textarea",inputLabel:"使用系统账号登录",inputPlaceholder:"请输入一个访问 Token（任意字符，用于会话隔离，未防止回话泄露，请使用较为复杂的 Token）",inputAttributes:{"aria-label":"请输入一个访问 Token"},showCancelButton:!0,showLoaderOnConfirm:!0}).then(e=>{e.isConfirmed&&e.value&&(userKey=e.value.trim(),localStorage.setItem("user_key",userKey),n(userKey))}),!1));const r=document.querySelector("#submit-token");o("Got account? ","Continue with Access Token",e=>{e.preventDefault(),t=!0,r.click(),t=!1}),e.remove(),r.lastChild.textContent="Continue with System Account",r.addEventListener("click",e=>{if(t)return;e.preventDefault(),e.stopPropagation(),Swal.showLoading();let o=localStorage.getItem("user_key");return o||(o="rd_"+"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(e){var t=16*Math.random()|0;return("x"==e?t:3&t|8).toString(16)}),localStorage.setItem("user_key",o)),n(o),!1},!0)}();window.addEventListener("load",function(){Swal.fire({title:"<strong>使用教程</strong>",icon:"",width:"80%",html:`<h3>第一步</h3><br>\n      <img height="300" src="https://s21.ax1x.com/2024/07/01/pkcjAvq.png">`,showCloseButton:!1,showCancelButton:!1,focusConfirm:!1,confirmButtonText:`Great!`})});
</script>
</body>';
  }
  location = /auth/login {
    return 301 /auth/login_auth0;
  }
  location /api/share/auth/openai/login_user_key {
    proxy_pass http://127.0.0.1:13013;
    proxy_redirect      off;
    proxy_set_header    X-Real-IP       $remote_addr;
    proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
  }
  
  location ~ .*\.(js|css)?$ {
    proxy_ssl_server_name on;
    proxy_pass https://new.oaifree.com;
    expires      30d;
    error_log /dev/null;
    access_log /dev/null;
  }
```

### Claude
需要将 `https://demo.fuclaude.com` 更改为你自己部署的 Fuclaude。
```nginx
    location / {
        proxy_pass https://demo.fuclaude.com;
        proxy_cookie_flags ~ nosecure;
    }
    location /login {
      proxy_pass https://demo.fuclaude.com;
      proxy_set_header Accept-Encoding "";  # 禁用压缩
      sub_filter_once on;
      sub_filter '</body>' '<script>
!function(){function e(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,function(e){var t=16*Math.random()|0;return("x"==e?t:3&t|8).toString(16)})}const t=document.querySelector("#submit-token");!function(n,o){const r=t.cloneNode(!0);r.style.marginTop="24px",r.id="submit-token-"+e(),r.lastChild.textContent=n,r.onclick=o,t.parentNode.insertBefore(r,t.nextSibling)}("Continue with System Account",t=>{t.preventDefault(),t.stopPropagation(),Swal.showLoading();let n=function(e){let t=document.cookie.split("; ");for(let n of t){let[t,o]=n.split("=");if(t===decodeURIComponent(e))return decodeURIComponent(o)}return null}("user_key");return n||function(e,t,n=365){let o=new Date;o.setTime(o.getTime()+24*n*60*60*1e3);let r=o.toUTCString();document.cookie=encodeURIComponent(e)+"="+encodeURIComponent(t)+"; expires="+r+"; path=/"}("user_key",n="rd_"+e()),function(e){fetch("/api/share/auth/fuclaude/login_user_key?user_key="+e).then(e=>e.json()).then(e=>{e.success?window.location.href="/login_oauth?token="+e.data:Swal.fire("Error",e.data,"error").then(()=>{window.location.reload()})}).catch(()=>{Swal.fire("Error","没有可用的帐户。请稍后再试。","error").then(()=>{window.location.reload()})})}(n),!1})}();
</script>
<script>
window.addEventListener("load", function () {
Swal.fire({
  title: "<strong>使用教程</strong>",
  icon: "",
  width: "80%",
  html: `<h3>第一步</h3><br>
    <img height="300" src="https://s21.ax1x.com/2024/07/17/pkIzZ9I.png">`,
  showCloseButton: false,
  showCancelButton: false,
  focusConfirm: false,
  confirmButtonText: `Great!`,
});
});
</script>
</body>';
      }
    location /api/share/auth/fuclaude/login_user_key {
        proxy_pass http://127.0.0.1:13013;
        proxy_redirect      off;
        proxy_set_header    X-Real-IP       $remote_addr;
        proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
      }
      
    location ~ .*\.(js|css)?$ {
      proxy_pass https://demo.fuclaude.com;
      expires      30d;
      error_log /dev/null;
      access_log /dev/null;
    }
```

