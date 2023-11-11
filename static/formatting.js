 // wait until html is loaded
 document.addEventListener('DOMContentLoaded', function() {
    // find all elements with class 'millions'
    var numbers = document.getElementsByClassName('millions');

    // iterate through found elements
    for (var i = 0; i < numbers.length; i++) {
        // store element's value
        var value = numbers[i];
        // convert text from value into integer
        var number = parseInt(value.textContent);
        // format integer
        value.textContent = number.toLocaleString('en-US');
    }
});