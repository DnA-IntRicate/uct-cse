SELECT productCode FROM products WHERE productCode NOT IN (SELECT productCode FROM orderdetails);
