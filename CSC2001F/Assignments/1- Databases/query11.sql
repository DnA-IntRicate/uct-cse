SELECT orderdetails.orderNumber, orders.status, orderdetails.priceEach, orderdetails.quantityOrdered, products.productName
FROM orderdetails, orders, products
WHERE orderdetails.orderNumber = orders.orderNumber
AND orderdetails.productCode = products.productCode
AND products.productVendor = 'Exoto Designs';
