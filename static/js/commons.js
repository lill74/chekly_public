function alert(message) {
  document.getElementById("alert-msg").innerHTML = message; // set message text
  if (document.getElementById("alert").classList.contains("d-none"))
    document.getElementById("alert").classList.remove("d-none"); // Display alert-box
}

function closeAlert() {
  document.getElementById("alert").classList.add("d-none"); // hide alert-box
  document.getElementById("alert-msg").innerHTML = ""; // reset message
}

function sendErrorMessage(message) {
  alert("에러발생");
  data = {
    error: message,
  };

  $.ajax({
    url: "/api/errorreport",
    type: "POST",
    data: { data: JSON.stringify(data) },
    success: function (response) {
      alert("에러로그가 전송되었습니다." + response.text);
    },
    error: function (error) {
      alert("에러가 발생했습니다. alus20x@gmail.com으로 연락해주세요.");
      console.log(error);
    },
  });
}

$(function () {
  $.ajax({
    url: "/api/getnotification",
    type: "GET",
    dataType: "json",
    success: function (response) {
      document.querySelector("#notify").textContent = response["msg"];
    },
    error: function (error) {
      sendErrorMessage(error);
    },
  });
});
