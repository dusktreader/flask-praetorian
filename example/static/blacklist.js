function blacklistToken() {
  makeRequest(
    'POST',
    'blacklist_token',
    addTokenHeader(),
    {
      "token": document.getElementById("token").value
    }
  );
};
