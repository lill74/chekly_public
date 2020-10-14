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

$(function () {
  $("#inputBirthDay").keyup(function () {
    $("#submit")
      .removeClass("btn-outline-secondary")
      .addClass("btn-outline-primary");
    $("#submit").attr("disabled", false);

    $("#delete")
      .removeClass("btn-outline-secondary")
      .addClass("btn-outline-danger");
    $("#delete").attr("disabled", false);
  });

  $("#submit").click(function () {
    if (
      !(
        $("#inputName").val() &&
        $("#inputBirthDay").val() &&
        $("#inputRegion").val() &&
        $("#inputSchoolName").val()
      )
    ) {
      alert("먼저 정보를 입력해주세요!");
      return;
    }
    if (getCookie("csrf_access_token")) {
      var data = {
        region: $("#inputRegion").val(),
        schoolName: $("#inputSchoolName").val(),
      };

      var data = {
        region: $("#inputRegion").val(),
        schoolCode: $("#inputSchoolName").val(),
        name: $("#inputName").val(),
        birthDay: $("#inputBirthDay").val(),
        time: $(
          "#timeSelection > div > label.btn.btn-outline-secondary.active > input"
        ).val(),
      };

      $.ajax({
        url: "/api/save",
        type: "POST",
        data: data,
        dataType: "json",
        beforeSend: function (xhr) {
          xhr.setRequestHeader("X-CSRF-TOKEN", getCookie("csrf_access_token"));
        },
        success: function (response) {
          if (response["msg"] == "created") {
            alert("정보가 저장되었습니다!");
            window.setTimeout(function () {
              window.location.href = "/dashboard";
            }, 500);
          } else if (response["msg"] == "updated") {
            alert("정보가 수정되었습니다!");
            window.setTimeout(function () {
              window.location.href = "/dashboard";
            }, 500);
          } else if (
            response["msg"] == 'Missing cookie "access_token_cookie"'
          ) {
            alert("로그인을 다시 해주세요!");
          } else {
            sendErrorMessage(response);
          }
        },
        error: function (error) {
          if (error.responseJSON["msg"] == "Token has expired") {
            alert("로그인을 다시 해주세요!");
          } else if (error.responseJSON["msg"] == "missing parameters") {
            alert("먼저 정보를 입력해주세요!");
          } else {
            //ERROR
            sendErrorMessage(error);
          }
        },
      });
    } else {
      alert("로그인을 먼저 해주세요!");
    }
  });

  $("#delete").click(function () {
    if (getCookie("csrf_access_token")) {
      var data = {
        region: $("#inputRegion").val(),
        schoolName: $("#inputSchoolName").val(),
      };

      $.ajax({
        url: "/api/remove",
        type: "POST",
        data: data,
        dataType: "json",
        beforeSend: function (xhr) {
          xhr.setRequestHeader("X-CSRF-TOKEN", getCookie("csrf_access_token"));
        },
        success: function (response) {
          if (response["msg"] == "updated") {
            alert("정보가 삭제되었습니다!");
            window.setTimeout(function () {
              window.location.href = "/";
            }, 500);
          } else if (response["msg"] == "none data") {
            alert("정보가 존재하지 않습니다.");
          } else {
            sendErrorMessage(response);
          }
        },
        error: function (error) {
          if (error.responseJSON["msg"] == "Token has expired") {
            alert("로그인을 다시 해주세요!");
          } else {
            sendErrorMessage(error);
          }
        },
      });
    } else {
      alert("로그인을 먼저 해주세요!");
    }
  });

  $("#inputRegion").on("change", function () {
    $("#inputSchoolName").attr("disabled", false);
  });

  $("#inputSchoolName").on("change", function () {
    $("#inputSchoolNameLabel").html("학교코드");
  });

  $("#inputSchoolName").autocomplete({
    source: function (request, response) {
      $.ajax({
        type: "GET",
        url: "/api/getSchoolName",
        data: {
          schoolName: $("#inputSchoolName").val(),
          region: $("#inputRegion option:selected").val(),
        },
        dataType: "json",
        success: function (data) {
          response(
            $.map(data, function (code, name) {
              return { label: name, value: code };
            })
          );
        },
      });
    },
    minLength: 1,
    delay: 150,
  });
});
