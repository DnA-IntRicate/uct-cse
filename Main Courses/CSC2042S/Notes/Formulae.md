# Formulae

## Metrics

| Term   | Meaning                                                    |
| ------ | ---------------------------------------------------------- |
| **TP** | True Positives — correctly predicted positives             |
| **TN** | True Negatives — correctly predicted negatives             |
| **FP** | False Positives — predicted positive but actually negative |
| **FN** | False Negatives — predicted negative but actually positive |

### Precision
``` math
Precision = \frac{TP}{TP + FP}
```
How many of the predicted positives were *actually* positive.

### Recall (True Positive Rate)
``` math
Recall = \frac{TP}{TP + FN}
```
How many of the actual positives did you catch.

### F1 Score
``` math
F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}
```
The harmonic mean of precision and recall.

### Accuracy
``` math
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
```
The overall fraction of correct predictions.

---

## Perceptron

### Learning Rule
``` math
w_1 \leftarrow w_1 + \alpha (y - g(in))x_1 \\
\\
w_2 \leftarrow w_2 + \alpha (y - g(in))x_2 \\
\\
b \leftarrow b + \alpha (y - g(in))
```

---

## Covariance

### Population Covariance
``` math
\Sigma_{pop} = \frac{1}{n}X^{T}X
```

## Cross-Entropy

### Binary Cross-Entropy Loss
``` math
L(y, \hat{y}) = -[y \log(\hat{y}) + (1 - y)\log(1 - \hat{y})]
```

### Cross-Entropy Loss
``` math
L = -\sum_{i=1}^{C} y_i \log(\hat{y}_i)
```

---
