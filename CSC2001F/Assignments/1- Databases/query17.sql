SELECT x.country, x.officeCode AS oneOffice, y.officeCode AS otherOffice
FROM offices x
JOIN offices y
ON x.country = y.country AND x.officeCode < y.officeCode;
