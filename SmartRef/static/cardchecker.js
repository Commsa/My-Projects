window.onload = function () {

    const order = document.getElementById('order')

    order.addEventListener("click", () =>{
        let firstName = document.getElementById('firstName').value
        let lastName = document.getElementById('lastName').value
        let email = document.getElementById('email').value
        let address = document.getElementById('address').value
        let country = document.getElementById('country').value
        let voivodeship = document.getElementById('voivodeship').value
        let creditCard = String(document.getElementById('creditCardNumber').value)

        let ccArray = creditCard.split("").reverse().map(i => Number.parseInt(i));

        let ccLastNumber = ccArray.shift();

        let ccNumbersSum = ccArray.reduce((accum, num, i) => 
            i % 2 !== 0 ? accum + num : accum + ((num *= 2) > 9 ? num - 9 : num), 0);

        let total = ccLastNumber + ccNumbersSum;
        if(total % 10 === 0){
            fetch("http://127.0.0.1:5000/checkout", {
                method: "POST",
                body: JSON.stringify({
                  'firstName': firstName,
                  'lastName': lastName,
                  'email': email,
                  'address': address,
                  'country': country,
                  'voivodeship': voivodeship
                }),
                headers: {
                  "Content-type": "application/json; charset=utf-8",
                  "Accept": "application/json"
                }
              }).then((response) => {
                setTimeout(2000);
                window.location.href = "http://127.0.0.1:5000/thankyou";
              });
        } else {
            document.getElementById("creditCardNumber").style.borderColor = 'red';
            alert("You have provided wrong Credit Card Number");
        }
    });
};
