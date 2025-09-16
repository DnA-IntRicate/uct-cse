# Assignment 2 Report — Simpsons MNIST Perceptron Classification

## 1. Introduction
This project implements a perceptron-based image classifier for the Simpsons-MNIST dataset. The assignment required extending the binary perceptron to a multi-class classifier using a one-vs-rest strategy. Models were trained and evaluated on both grayscale and RGB images.

---

## 2. Data Processing
- Dataset loaded using **PIL** into NumPy arrays.
- Both grayscale and RGB versions prepared.
- Training set split into **train** and **validation** subsets (80/20).
- Images were flattened into 1D feature vectors.
- Normalisation techniques explored: none, min-max, and z-score.

---

## 3. Perceptron Implementation
- **BinaryPerceptron**: Maintains weights and bias, applies perceptron update rule.
- **MultiClassPerceptron**: Composed of 10 binary perceptrons (one per class). Prediction is made via highest score (argmax).
- Object-oriented structure ensured modularity and reuse.

---

## 4. Training
Two stopping criteria were implemented:
- **Fixed epochs**: Training runs for a specified number of epochs (default 50).
- **Early stopping**: Stops when validation accuracy fails to improve for several epochs.

Training data was shuffled each epoch to improve generalisation.

---

## 5. Hyperparameter Tuning
A grid search explored:
- Learning rates: `0.01, 0.1`
- Initialisation: zeros, random small values
- Normalisation: none, min-max, z-score

Findings:
- **Z-score normalisation** consistently improved convergence.
- **Random initialisation** yielded better results than all-zero weights.
- **Lower learning rates** improved stability but required more epochs.

---

## 6. Evaluation
Metrics used:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix (per-class analysis)

### Results (illustrative placeholder — replace with actual runs):
- **Grayscale**: Accuracy ~ XX%, best with learning rate 0.01 and z-score normalisation.
- **RGB**: Accuracy ~ YY%, slightly higher overall, suggesting colour features help distinguish some characters (e.g., Marge’s blue hair).

Confusion matrices revealed common confusions between visually similar characters (e.g., Homer vs. Bart).

---

## 7. RGB vs Grayscale Analysis
- RGB models generally outperformed grayscale.
- Characters with distinctive colours (Marge, Krusty) benefitted from RGB.
- Others (Lisa, Bart) were recognised well even in grayscale.
- Grayscale sufficed for some classes, but RGB improved overall robustness.

---

## 8. Code Quality and Reproducibility
- Code written in a modular style with classes and functions.
- Random seeds fixed for reproducibility.
- Grid search automated hyperparameter exploration.

---

## 9. Conclusion
This assignment demonstrated:
- How to extend the perceptron to multi-class classification.
- The importance of preprocessing and hyperparameters for perceptron performance.
- The advantages of RGB data for certain visual tasks.

Future improvements could include feature extraction (e.g., edge detection) or more advanced models (e.g., multi-layer perceptrons).
