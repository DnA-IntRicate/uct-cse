SELECT 'YES' AS anyProblems
WHERE EXISTS ((SELECT 1 FROM orderdetails WHERE priceEach = 0.0) UNION (SELECT 1 FROM products WHERE buyPrice = 0.0));
