function getProtected() {
  makeRequest(
    'GET',
    'protected',
    addTokenHeader(),
  );
};
