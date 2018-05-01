function makeRequest(method, endpoint, headers, payload, on_success, on_failure) {
  let request = new XMLHttpRequest();
  let url = 'http://localhost:' + API_PORT + '/' + endpoint;
  request.open(method, url, true);
  request.onerror = function() {
    alert("No connection to API. Is the example app running?");
  };

  request.onreadystatechange = function() {
    if (request.readyState == XMLHttpRequest.DONE) {
      let response = JSON.parse(this.responseText);
      document.getElementById("response").value = JSON.stringify(response, null, 2);
      console.log(this.status);
      if (this.status == 200 && on_success) {
        on_success(response);
      } else if(on_failure) {
        on_failure(response);
      }
    }
  };
  for (var header in headers) {
    request.setRequestHeader(header, headers[header]);
  }
  document.getElementById("request").value = JSON.stringify({
    "method": method,
    "url": url,
    "payload": payload,
    "headers": headers
  }, null, 2);
  if (payload) {
    request.send(JSON.stringify(payload));
  } else {
    request.send();
  }
};
