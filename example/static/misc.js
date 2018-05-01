function fetchToken() {
  return document.getElementById("token").value;
};

function setToken(token) {
  document.getElementById("token").value = token;
};

function copyToken() {
  var token = document.getElementById("token");
  token.select();
  document.execCommand("Copy");
  token.blur();
};

function clearToken() {
  document.getElementById("token").value = ''
};

function addTokenHeader(headers) {
  let token = fetchToken();
  if (token) {
    if (!headers) {
      headers = {};
    }
    headers["Authorization"] = "Bearer " + token;
  }
  return headers;
};
