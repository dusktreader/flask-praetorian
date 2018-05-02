function refresh() {
  makeRequest(
    'GET',
    'refresh',
    addTokenHeader(),
    null,
    function (response) {
      setToken(response.access_token);
      startTimer(ACCESS_LIFESPAN, "access");
    }
  );
};

function disableUser() {
  makeRequest(
    'POST',
    'disable_user',
    addTokenHeader(),
    {
      "username": document.getElementById("username").value,
      "password": document.getElementById("password").value
    }
  );
};
