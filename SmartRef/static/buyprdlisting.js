window.onload = function () {
  let buy = Array.from(document.getElementsByClassName("btn btn-primary productlisting"));
  let productId = document.getElementsByName("productid");
  let productName = document.getElementsByName("productname");
  let productPrice = document.getElementsByName("productprice");
  
  let btnval = 0;
  buy.forEach(element => {
    element.addEventListener('click', (e) => {
      btnval = e.target.value;
      productId = e.target.parentNode.childNodes[1].innerHTML;
      productName = e.target.parentNode.childNodes[5].innerHTML;
      productPrice = e.target.parentNode.childNodes[9].innerHTML;
      fetch("http://127.0.0.1:5000/add_to_cart/"+productId, {
        method: "POST",
        body: JSON.stringify({
          'productId': productId,
          'productName': productName,
          'productPrice': productPrice,
          'productStock': "1",
        }),
        headers: {
          "Content-type": "application/json; charset=utf-8"
        }
      });
    });
  }); 
};
