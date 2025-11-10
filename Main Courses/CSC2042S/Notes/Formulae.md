# Formulae

## Metrics

| Term   | Meaning                                                    |
| ------ | ---------------------------------------------------------- |
| **TP** | True Positives — correctly predicted positives             |
| **TN** | True Negatives — correctly predicted negatives             |
| **FP** | False Positives — predicted positive but actually negative |
| **FN** | False Negatives — predicted negative but actually positive |

### 1. Precision
``` math
Precision = \frac{TP}{TP + FP}
```
How many of the predicted positives were *actually* positive.

### 2. Recall (True Positive Rate)
``` math
Recall = \frac{TP}{TP + FN}
```
How many of the actual positives did you catch.

### 3. F1 Score
``` math
F1 = 2 \times \frac{Precision \times Recall}{Precision + Recall}
```
The harmonic mean of precision and recall.

### 4. Accuracy
``` math
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
```
The overall fraction of correct predictions.

---
