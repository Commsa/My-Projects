# SmartRef
#### Description: Ecommerce store for used phones.
The project includes full shopping experience from, creating account to submitting an order.
Users that are not logged in, are not able to make a purchase. Still, they are able to view products.
The project consists of modules/features:
- login, logout an registration
- panel with order history
- product page
- cart
- checkout

#### Login, Logout and Registration
Quite standard build, utilizing werkzeug to have a possiblity to login or create an account. The login function includes verification if such user data indeed exists in the user table along with the password check.  Similarly, the register function checks if the user already exists or not. The logout is built in a way that clears the cart when the user have logged out. The user session is being created with each login, still the app is configured so that the user activity is being measuered. If the user haven't performed any action for 30 minutes, it'll be logged out. It's done utilizing the config option and timedelta from datetime:
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=30) 

#### Panel with order history
Built in a way that use the table to display already created orders, which are stored in orders table. The most interesting part here is the database query which is built in a way to aggregate the products data. Doing that made it easier to display the data as I've designed it to be displayed, so that each product will be displayed in one column, result under result.

#### Product page

Simple product listing page, where products are split in to four columns. The two most interesting parts are the buyprdlisting.js where the code is sending POST request utilizing fetch. The other interesting part is the code in the app.py itself.
The view is built based on async functions, executing in chain so that one will run after another. What the code does is that it updates the cart table with each click, without reloading the page.

#### Cart

The updatecart.js is used here to send two types of request, POST and DELETE. Delete is being sent when the "Clear Cart" button is used by the logged in user. The POST on the other hand allows to send the information about current selected product quantity.
Using the POST this way along with async functions in the app allow to update the cart stock levels dynamically, without reloading the page.

#### Checkout

Finally checkout, here we use the cardchecker.js to implement the Luhn algorithm to verify if the card number used is viable. Other than that the information from the form and cart table is being inserted in to orders table based on POST request. Once it'd been done, the DELETE request is being executed on cart table, to clear the user cart. Lastly, the user is being transferred to the "Thank you" page. Once the order is done, it's visible in the order history, in the panel.

