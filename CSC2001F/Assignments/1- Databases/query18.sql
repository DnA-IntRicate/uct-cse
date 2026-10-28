SELECT ROUND(((SELECT COUNT(*) FROM offices WHERE country = 'USA') * 100.0) / (SELECT COUNT(*) FROM offices), 4) AS percentUSA;
