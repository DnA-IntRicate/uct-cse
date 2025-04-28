SELECT offices.officeCode, COUNT(employees.officeCode) AS numReps
FROM offices, employees
WHERE offices.officeCode = employees.officeCode
AND employees.jobTitle = 'Sales Rep'
GROUP BY employees.officeCode;
