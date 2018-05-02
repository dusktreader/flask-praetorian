// Borrowed heavily from https://stackoverflow.com/a/20618517

var currentInterval = {
};

function startTimer(duration, elementId) {
  var timer = duration, minutes, seconds;
  if (currentInterval[elementId]) {
    clearInterval(currentInterval[elementId]);
  }
  currentInterval[elementId] = setInterval(function () {
    days = parseInt(timer / (24 * 60 * 60), 10)
    hours = parseInt((timer / (60 * 60) % 24), 10)
    minutes = parseInt((timer / 60) % 60, 10)
    seconds = parseInt(timer % 60, 10);

    hours = hours < 10 ? "0" + hours : hours;
    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;

    document.getElementById(elementId).value = days + ":" + hours + ":" + minutes + ":" + seconds;

    if (--timer < 0) {
      clearInterval(currentInterval[elementId]);
    }
  }, 1000);
};
