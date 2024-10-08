window.onload = function () {
    let productqty = document.getElementsByName("productqty");
    let productId = document.getElementsByName("productid");
    let productName = document.getElementsByName("productname");
    let productPrice = document.getElementsByName("productprice");
    let clearcart = document.getElementById("clearcart");
    let checkout = document.getElementById("checkout");

    checkout.addEventListener("click", () =>{
      location.href = "/checkout";
  });

    clearcart.addEventListener("click", () =>{
      fetch("http://127.0.0.1:5000/cart", {
        method: "DELETE",
        headers: {
          "Content-type": "application/json; charset=utf-8"
        }
      }).then((response) => {
        return response.text();
      }).then((html) => {
        document.body.innerHTML = html
      })
  });

    let prdqty = 0;
    productqty.forEach(element => {
        element.addEventListener('change', (e) => {
            prdqty = e.target.value;
            productId = e.target.parentNode.childNodes[3].innerHTML;
            fetch("http://127.0.0.1:5000/cart", {
                method: "POST",
                body: JSON.stringify({
                  'productId': productId,
                  'productQuantity': prdqty,
                }),
                headers: {
                  "Content-type": "application/json; charset=utf-8"
                }
              })
        });
    });
};

