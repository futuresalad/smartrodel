const xhttp = new XMLHttpRequest();
const rangeSlider = document.getElementById('range-slider');
const timeText = document.getElementById('text-field-time');

rangeSlider.addEventListener('input', function() {
  const rangeSliderValue = rangeSlider.value;

  timeText.value = rangeSliderValue;

  xhttp.open('POST', '/get_time', true);
  xhttp.setRequestHeader('Content-Type', 'application/json');

  xhttp.onload = function() {
    console.log(this.responseText);
  };

  xhttp.send(JSON.stringify({ rangeSliderValue }));

});

function action(command)
{
    xhttp.open("POST", command);
    xhttp.send();
}