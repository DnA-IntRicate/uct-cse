SELECT customers.customerNumber
FROM customers, payments
WHERE payments.amount = (SELECT MAX(payments.amount) FROM payments)
AND payments.customerNumber = customers.customerNumber;
