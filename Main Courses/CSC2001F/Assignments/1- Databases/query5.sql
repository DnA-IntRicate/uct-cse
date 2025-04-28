SELECT productVendor, productCode, quantityInStock * 2 AS newStock FROM products WHERE productVendor LIKE 'Ex%to%';
