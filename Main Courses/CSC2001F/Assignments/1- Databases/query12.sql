SELECT orders.orderNumber, orders.comments, customers.customerName
FROM orders, customers
WHERE orders.customerNumber = customers.customerNumber
AND orders.status = 'Disputed';
