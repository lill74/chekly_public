function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function addList(text, element) {
  var list = '<li class="list-group-item">' + text + "</li>";
  $(element).append(list);
}

$(function () {
  if (!getCookie("csrf_access_token")) {
    alert("로그인을 먼저 해주세요!");
  }
  $.ajax({
    url: "/api/getuserinfo",
    type: "POST",
    dataType: "json",
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-CSRF-TOKEN", getCookie("csrf_access_token"));
    },
    success: function (response) {
      if (response["msg"] == "none data") {
        alert("정보를 등록해주세요!");
        window.setTimeout(function () {
          window.location.href = "/register";
        }, 500);
        return;
      }
      for (var i in response) {
        addList(i + ": " + response[i], "#userInformation");
      }
      addList("등록이 완료되었습니다!", "#transactionsList");
      addList("이곳에 자가진단 기록이 저장됩니다!", "#transactionsList");
      addList("이 화면을 다시 보시려면 로그인을 하시면 됩니다!", "#transactionsList");
    },
    error: function (error) {
      sendErrorMessage(error);
    },
  });

  $.ajax({
    url: "/api/gettransactions",
    type: "POST",
    dataType: "json",
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-CSRF-TOKEN", getCookie("csrf_access_token"));
    },
    success: function (response) {
      for (var i in response["msg"]) {
        addList(response["msg"][i], "#transactionsList");
      }
    },
    error: function (error) {
      sendErrorMessage(error);
    },
  });
});
