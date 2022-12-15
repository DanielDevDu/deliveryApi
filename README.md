# deliveryApi

## ROUTES TO IMPLEMENT

| METHOD   | ROUTE                              | FUNCTIONALITY               | ACCESS      |
| -------- | ---------------------------------- | --------------------------- | ----------- |
| _POST_   | `/auth/signup/`                    | _Register new user_         | _All users_ |
| _POST_   | `/auth/login/`                     | _Login user_                | _All users_ |
| _GET_    | `/auth/all/`                       | _List all users_            | _Superuser_ |
| _POST_   | `/orders/order/`                   | _Place an order_            | _All users_ |
| _PUT_    | `/orders/order/update/{order_id}/` | _Update an order_           | _All users_ |
| _PUT_    | `/orders/order/status/{order_id}/` | _Update order status_       | _Superuser_ |
| _DELETE_ | `/orders/order/delete/{order_id}/` | _Delete/Remove an order_    | _All users_ |
| _GET_    | `/orders/user/orders/`             | _Get user's orders_         | _All users_ |
| _GET_    | `/orders/all/`                     | _List all orders made_      | _Superuser_ |
| _GET_    | `/orders/orders/{order_id}/`       | _Retrieve an order_         | _Superuser_ |
| _GET_    | `/orders/user/order/{order_id}/`   | _Get user's specific order_ |
| _GET_    | `/docs/`                           | _View API documentation_    | _All users_ |
