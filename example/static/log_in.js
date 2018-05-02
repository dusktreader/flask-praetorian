function logIn() {
  clearToken();

  makeRequest(
    'POST',
    'login',
    {},
    {
      "username": document.getElementById("username").value,
      "password": document.getElementById("password").value
    },
    function (response) {
      setToken(response.access_token);
      startTimer(ACCESS_LIFESPAN, "access");
      startTimer(REFRESH_LIFESPAN, "refresh");
    },
    function (response) {
      clearToken;
    },
  );
};

function passwordMap() {
  return {
    'TheDude': 'abides',
    'Walter': 'calmerthanyouare',
    'Donnie': 'iamthewalrus',
    'Maude': 'andthorough'
  };
};

function cheatPassword() {
  let username = document.getElementById('username').value;
  console.log(username);
  let map = passwordMap()

  if (username in map) {
    document.getElementById('password').value = map[username];
  }
};
