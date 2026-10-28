SELECT customers.salesRepEmployeeNumber, COUNT(customers.salesRepEmployeeNumber) AS numCustomers
FROM employees, customers
WHERE customers.salesRepEmployeeNumber = employees.employeeNumber
AND employees.jobTitle = 'Sales Rep'
AND employees.reportsTo = 1143
GROUP BY customers.salesRepEmployeeNumber
HAVING numCustomers >= 10;
