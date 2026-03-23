### ERROR REPORT

## API end Point: `GET /api/v1/profile`
### Issue: if the user ID in the header  exist but missing, the server returns a 404 error instead of a 400 error.
 


## API end Point: `PUT /api/v1/profile`
### Issue: if the user puts phone number with 10 digits but with some non-digit characters, the server accepts it and updates the profile instead of returning a 400 error.

### Issue: if the user ID in the header exist but missing, the server returns a 404 error instead of a 400 error.

## API end Point: `GET /api/v1/products`
### Issue: the price field returned in the product listing does not match the price stored in the database for some products.

## API end Point: `GET /api/v1/products/{product_id}`
### Issue: looking up an inactive product by ID returns a 200 status with the product details instead of a 404 error.
### Issue: if the user ID in the header exist but missing, the server returns a 404 error instead of a 400 error.
### Issue: if the user ID in the header is non-existent, the server returns a 404 error instead of a 400 error.