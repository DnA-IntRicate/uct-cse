SELECT offices.officeCode, COUNT(employees.officeCode) AS numEmps
FROM offices, employees
WHERE offices.officeCode = employees.officeCode
GROUP BY employees.officeCode;
