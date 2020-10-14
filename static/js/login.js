function countdown(elementName, minutes, seconds) {
  var element, endTime, hours, mins, msLeft, time;

  function twoDigits(n) {
    return n <= 9 ? "0" + n : n;
  }

  function updateTimer() {
    msLeft = endTime - +new Date();
    if (msLeft < 1000) {
      element.innerHTML = "";
      $("#verifyPhone").attr("disabled", false);
    } else {
      time = new Date(msLeft);
      hours = time.getUTCHours();
      mins = time.getUTCMinutes();
      element.innerHTML =
        (hours ? hours + ":" + twoDigits(mins) : mins) +
        ":" +
        twoDigits(time.getUTCSeconds() + " 남음");
      setTimeout(updateTimer, time.getUTCMilliseconds() + 500);
    }
  }

  element = document.getElementById(elementName);
  endTime = +new Date() + 1000 * (60 * minutes + seconds) + 500;
  updateTimer();
}

$(function () {
  $("#inputPhoneNumber").keyup(function () {
    $("#verifyPhone")
      .removeClass("btn-outline-secondary")
      .addClass("btn-outline-primary");
    $("#verifyPhone").attr("disabled", false);
  });

  $("#phoneNumber").val("");
  $("#verifyPhone").click(function () {
    if (!$("#inputPhoneNumber").val()) {
      alert("전화번호를 입력해주세요!");
    } else {
      if ($("#phoneNumber").val()) {
        var data = {
          phone: $("#phoneNumber").val(),
          code: $("#inputPhoneNumber").val(),
        };
        $.ajax({
          url: "/api/login",
          type: "POST",
          data: data,
          dataType: "json",
          success: function (response) {
            if (response["login"]) {
              window.location.href = "/dashboard";
            } else {
              sendErrorMessage(response);
            }
          },
          error: function (error) {
            if (error.responseJSON["msg"] == "wrong code") {
              alert("잘못된 인증번호 입니다!");
            } else {
              sendErrorMessage(error);
            }
          },
        });
      } else {
        $("#verifyPhone")
          .removeClass("btn-outline-primary")
          .addClass("btn-outline-secondary");
        $("#verifyPhone").attr("disabled", true);

        var data = { phone: $("#inputPhoneNumber").val() };
        $.ajax({
          url: "/api/sendVerifyCode",
          type: "POST",
          data: data,
          dataType: "json",
          success: function (response) {
            if (response["msg"]["status"] == "verify cooltime") {
              //cool time for verification
              alert("인증번호는 3분에 1개씩 보낼수 있습니다!");
              countdown("countdown", 0, response["msg"]["timeout"]);
            } else if (response["msg"] == "sent") {
              alert(
                "인증번호를 " +
                  $("#inputPhoneNumber").val() +
                  " 로 발송했습니다!"
              );
              $("#verifyPhone")
                .removeClass("btn-outline-secondary")
                .addClass("btn-outline-primary");
              $("#verifyPhone").attr("disabled", false);
              $("#phoneNumber").val($("#inputPhoneNumber").val());
              $("#inputPhoneNumber").val("");
              $("#inputPhoneNumber").attr("placeholder", "인증번호");
              $("#verifyPhone").html("인증하기");
            } else {
              sendErrorMessage;
              response;
            }
          },
          error: function (error) {
            sendErrorMessage(error);
          },
        });
      }
    }
  });
});
