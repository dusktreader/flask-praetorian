function getProtected() {
  makeRequest(
    'GET',
    'protected',
    addTokenHeader(),
  );
};

function getProtectedAdminRequired() {
  makeRequest(
    'GET',
    'protected_admin_required',
    addTokenHeader(),
  );
};

function getProtectedOperatorAccepted() {
  makeRequest(
    'GET',
    'protected_operator_accepted',
    addTokenHeader(),
  );
};
