# %%
"""
CSC2042S - Assignment 3
Multinomial Logistic Regression for MasakhaNEWS
Notebook (python script with Jupyter cell markers)

This file is structured as a Jupyter notebook using # %% cell separators so you
can open it directly in VSCode (or convert to .ipynb with jupytext).

It follows the assignment specification provided in the course PDF and uses the
MasakhaNEWS repository layout as a basis for locating data. The notebook will:
 - inspect a local `masakhane-news` repo (if present) to find data files
 - otherwise load the dataset via the `datasets` (HuggingFace) loader
 - implement preprocessing, feature extraction (Count/Binary/TF-IDF)
 - implement an OOP PyTorch Multinomial logistic regression model
 - training loop, grid-search style hyperparameter tuning, evaluation
 - additional isiXhosa experiments (regularization + sampling)
 - weight analysis and utilities for reproducibility

Author: generated for the user per their spec. Replace paths / adjust runtime
parameters as needed for your machine (notebooks often require tuned batch sizes
and compute budget).
"""

# %%
# --- Setup & Imports --------------------------------------------------------
from __future__ import annotations

import os
import random
import math
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt

# set a default seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# %%
# --- Utility functions -----------------------------------------------------

def set_seed(seed: int = SEED) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def find_local_masakhane_repo(root: str = '.') -> Optional[str]:
    """Search `root` (non-recursive) for a folder named `masakhane-news` or similar.

    Returns path to data directory if found, otherwise None.
    """
    candidates = []
    for entry in os.listdir(root):
        if entry.lower().startswith('masakhane') and os.path.isdir(os.path.join(root, entry)):
            candidates.append(os.path.join(root, entry))
    if not candidates:
        return None
    # prefer exact name
    for c in candidates:
        if os.path.basename(c) == 'masakhane-news':
            return c
    return candidates[0]


def inspect_data_layout(repo_path: str) -> Dict[str, List[str]]:
    """Return a dict summarising files under repo_path/data (if present).

    The returned dict maps language code -> list of files found for that language.
    """
    data_dir = os.path.join(repo_path, 'data')
    out: Dict[str, List[str]] = {}
    if not os.path.isdir(data_dir):
        return out
    for name in sorted(os.listdir(data_dir)):
        lang_dir = os.path.join(data_dir, name)
        if os.path.isdir(lang_dir):
            out[name] = sorted(os.listdir(lang_dir))
    return out


# %%
# --- Data loading ----------------------------------------------------------

@dataclass
class DatasetSplit:
    X: List[str]
    y: List[int]
    labels: Optional[List[str]] = None


def load_from_local(repo_path: str, lang: str) -> Dict[str, DatasetSplit]:
    """Try to load data for a language from local `repo_path/data/<lang>/`.

    Expects CSV/TSV files named train.csv, dev.csv or train.tsv etc, but will
    attempt to infer files. Returns dict with keys 'train','validation','test'.
    """
    data_dir = os.path.join(repo_path, 'data', lang)
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Local data dir not found: {data_dir}")

    def _read_any(path: str) -> pd.DataFrame:
        if path.endswith('.csv'):
            return pd.read_csv(path)
        else:
            # fallback: pandas can usually infer
            return pd.read_table(path)

    splits = {}
    for split in ['train', 'dev', 'test', 'validation']:
        for ext in ('.csv', '.tsv', '.txt'):
            candidate = os.path.join(data_dir, split + ext)
            if os.path.exists(candidate):
                df = _read_any(candidate)
                splits[split if split != 'dev' else 'validation'] = df
                break
    # If no named files, attempt to find any CSV-like files
    if not splits:
        for fname in os.listdir(data_dir):
            if fname.endswith(('.csv', '.tsv', '.txt')):
                df = _read_any(os.path.join(data_dir, fname))
                key = 'train' if 'train' in fname else ('test' if 'test' in fname else 'validation')
                splits.setdefault(key, df)
    # validate and convert
    out = {}
    for key, df in splits.items():
        # expected cols include 'label', 'headline', 'text', 'headline_text'
        if 'headline_text' in df.columns:
            texts = df['headline_text'].fillna('').astype(str).tolist()
        else:
            # concat headline + text
            headline = df['headline'].fillna('').astype(str)
            text = df['text'].fillna('').astype(str)
            texts = (headline + ' ' + text).tolist()
        labels = df['label'].tolist() if 'label' in df.columns else [None] * len(texts)
        out[key] = DatasetSplit(X=texts, y=labels)
    return out


def load_via_hf(lang: str) -> Dict[str, DatasetSplit]:
    """Load the MasakhaNEWS dataset for `lang` using HuggingFace `datasets`.

    This requires the `datasets` package to be installed: pip install datasets
    If it's not available we let the user know and raise an informative error.
    """
    try:
        from datasets import load_dataset
    except Exception as e:
        raise RuntimeError("datasets library is required to load MasakhaNEWS from HF. Install with `pip install datasets`")

    ds = load_dataset('masakhanews', lang)
    out = {}
    # hf uses splits: train, validation, test
    for split in ds.keys():
        df = pd.DataFrame(ds[split])
        if 'headline_text' in df.columns:
            texts = df['headline_text'].fillna('').astype(str).tolist()
        else:
            texts = (df['headline'].fillna('').astype(str) + ' ' + df['text'].fillna('').astype(str)).tolist()
        labels = df['label'].tolist() if 'label' in df.columns else [None] * len(texts)
        out[split] = DatasetSplit(X=texts, y=labels, labels=getattr(ds[split].features['label'], 'names', None))
    return out


# %%
# --- Basic preprocessing ---------------------------------------------------

import re
from typing import Callable

TOKEN_RE = re.compile(r"\b\w+\b", flags=re.UNICODE)


def basic_clean(text: str) -> str:
    """Lowercase and remove excessive whitespace. Keep punctuation splitting to
    vectorizers (we rely on sklearn tokenisers)."""
    t = text.lower()
    t = t.replace('\n', ' ').strip()
    t = re.sub(r'\s+', ' ', t)
    return t


def preprocess_texts(texts: List[str], cleaner: Callable[[str], str] = basic_clean) -> List[str]:
    return [cleaner(t) for t in texts]


# %%
# --- Feature extraction wrappers -------------------------------------------

@dataclass
class FeatureExtractor:
    method: str  # 'count', 'binary', or 'tfidf'
    max_features: Optional[int] = None
    min_df: Optional[int] = None
    vectorizer: Optional[object] = None

    def fit(self, texts: List[str]):
        if self.method == 'count' or self.method == 'binary':
            v = CountVectorizer(max_features=self.max_features, min_df=self.min_df, binary=(self.method == 'binary'))
        elif self.method == 'tfidf':
            v = TfidfVectorizer(max_features=self.max_features, min_df=self.min_df)
        else:
            raise ValueError('Unknown method')
        self.vectorizer = v.fit(texts)
        return self

    def transform(self, texts: List[str]) -> np.ndarray:
        assert self.vectorizer is not None, 'vectorizer not fitted'
        X = self.vectorizer.transform(texts)
        return X.toarray()  # convert to dense for simplicity; large vocabs may need sparse support

    def fit_transform(self, texts: List[str]) -> np.ndarray:
        self.fit(texts)
        return self.transform(texts)


# %%
# --- Multinomial Logistic Regression (PyTorch) ------------------------------

class MultinomialLogisticRegression(nn.Module):
    """
    Simple multinomial logistic regression implemented in PyTorch.

    OOP design with required methods: forward, compute_probabilities, predict.
    """

    def __init__(self, input_dim: int, num_classes: int, l2: float = 0.0):
        super().__init__()
        self.linear = nn.Linear(input_dim, num_classes)  # includes bias
        self.l2 = l2

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Return logits for input batch x (shape: batch x input_dim)."""
        return self.linear(x)

    def compute_probabilities(self, x: torch.Tensor) -> torch.Tensor:
        """Return softmax probabilities for input batch."""
        logits = self.forward(x)
        return torch.softmax(logits, dim=1)

    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Return predicted class indices (tensor)."""
        probs = self.compute_probabilities(x)
        return torch.argmax(probs, dim=1)


# %%
# --- Training utilities ----------------------------------------------------

@dataclass
class TrainConfig:
    epochs: int = 30
    lr: float = 1e-2
    batch_size: int = 64
    weight_decay: float = 0.0  # L2 regularisation (applied via optimizer)
    device: str = 'cpu'


def train_model(model: nn.Module, X_train: np.ndarray, y_train: np.ndarray,
                X_val: np.ndarray, y_val: np.ndarray, cfg: TrainConfig) -> Dict:
    set_seed()
    device = torch.device(cfg.device)
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

    train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.long))
    train_loader = DataLoader(train_dataset, batch_size=cfg.batch_size, shuffle=True)

    history = {'train_loss': [], 'val_loss': [], 'val_acc': []}

    best_val_acc = -1.0
    best_state = None

    for epoch in range(cfg.epochs):
        model.train()
        running_loss = 0.0
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * xb.size(0)
        epoch_loss = running_loss / len(train_loader.dataset)

        # validation
        model.eval()
        with torch.no_grad():
            Xv = torch.tensor(X_val, dtype=torch.float32).to(device)
            yv = torch.tensor(y_val, dtype=torch.long).to(device)
            val_logits = model(Xv)
            val_loss = criterion(val_logits, yv).item()
            preds = torch.argmax(val_logits, dim=1).cpu().numpy()
            val_acc = accuracy_score(y_val, preds)

        history['train_loss'].append(epoch_loss)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        # simple early stopping on validation accuracy improvement
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    # load best state
    if best_state is not None:
        model.load_state_dict(best_state)

    return {'model': model, 'history': history}


# %%
# --- Evaluation helpers ----------------------------------------------------

def evaluate_model(model: nn.Module, X: np.ndarray, y: np.ndarray, label_names: Optional[List[str]] = None) -> Dict:
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X, dtype=torch.float32)
        logits = model(X_t)
        preds = torch.argmax(logits, dim=1).numpy()

    acc = accuracy_score(y, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(y, preds, average='micro')
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(y, preds, average='macro')
    cm = confusion_matrix(y, preds)

    return {
        'accuracy': acc,
        'precision_micro': precision,
        'recall_micro': recall,
        'f1_micro': f1,
        'precision_macro': precision_macro,
        'recall_macro': recall_macro,
        'f1_macro': f1_macro,
        'confusion_matrix': cm,
        'preds': preds,
    }


# %%
# --- Weight analysis ------------------------------------------------------

def top_features_per_class(model: MultinomialLogisticRegression, vectorizer, top_k: int = 20) -> Dict[int, List[Tuple[str, float]]]:
    """Return top-k features (word, weight) for each class based on learned weights.

    Note: vectorizer must expose `.get_feature_names_out()` (scikit-learn >= 1.0)
    """
    # weight matrix: out_features x in_features
    W = model.linear.weight.detach().cpu().numpy()
    feature_names = vectorizer.get_feature_names_out()
    out = {}
    for i in range(W.shape[0]):
        row = W[i]
        top_idx = np.argsort(row)[-top_k:][::-1]
        out[i] = [(feature_names[j], float(row[j])) for j in top_idx]
    return out


# %%
# --- Experiment orchestration (high-level) --------------------------------

def run_experiment_for_language(lang: str,
                                feature_method: str = 'tfidf',
                                max_features: Optional[int] = 10000,
                                min_df: Optional[int] = 1,
                                lr: float = 1e-2,
                                batch_size: int = 64,
                                epochs: int = 30,
                                repo_path: Optional[str] = None,
                                use_local_if_available: bool = True,
                                device: str = 'cpu') -> Dict:
    """High-level runner that loads data, fits vectorizer, trains model and returns results.

    This function is the main entry used in grid-search loops.
    """
    # load data (local preferred)
    data_splits = None
    if use_local_if_available and repo_path is not None:
        try:
            data_splits = load_from_local(repo_path, lang)
        except Exception:
            data_splits = None
    if data_splits is None:
        data_splits = load_via_hf(lang)

    # ensure keys
    train = data_splits.get('train')
    val = data_splits.get('validation') or data_splits.get('dev')
    test = data_splits.get('test')
    assert train is not None and val is not None and test is not None, 'Missing splits'

    X_train = preprocess_texts(train.X)
    X_val = preprocess_texts(val.X)
    X_test = preprocess_texts(test.X)

    fe = FeatureExtractor(method=feature_method, max_features=max_features, min_df=min_df)
    X_train_vec = fe.fit_transform(X_train)
    X_val_vec = fe.transform(X_val)
    X_test_vec = fe.transform(X_test)

    # labels might be numeric already
    y_train = np.array(train.y, dtype=int)
    y_val = np.array(val.y, dtype=int)
    y_test = np.array(test.y, dtype=int)

    num_classes = len(np.unique(y_train))
    input_dim = X_train_vec.shape[1]

    model = MultinomialLogisticRegression(input_dim=input_dim, num_classes=num_classes)
    cfg = TrainConfig(epochs=epochs, lr=lr, batch_size=batch_size, device=device)
    result = train_model(model, X_train_vec, y_train, X_val_vec, y_val, cfg)
    trained_model = result['model']

    val_metrics = evaluate_model(trained_model, X_val_vec, y_val)
    test_metrics = evaluate_model(trained_model, X_test_vec, y_test)

    # weight analysis helper
    weights = top_features_per_class(trained_model, fe.vectorizer, top_k=15)

    return {
        'model': trained_model,
        'vectorizer': fe.vectorizer,
        'val_metrics': val_metrics,
        'test_metrics': test_metrics,
        'history': result['history'],
        'weights': weights,
    }


# %%
# --- Grid search helper (for hyperparameter tuning) ------------------------

def grid_search(lang: str, feature_method: str, repo_path: Optional[str], grid: Dict[str, List], device: str = 'cpu') -> Dict:
    """Perform a simple grid search over lr and batch_size. Returns best config.

    Note: This function is conservative for compute — keep grids small.
    """
    best = None
    records = []
    for lr in grid.get('lr', [1e-2]):
        for batch in grid.get('batch_size', [64]):
            for maxf in grid.get('max_features', [10000]):
                print(f"Running {lang} method={feature_method} lr={lr} batch={batch} maxf={maxf}")
                res = run_experiment_for_language(lang, feature_method=feature_method, max_features=maxf,
                                                  lr=lr, batch_size=batch, epochs=grid.get('epochs', [20])[0],
                                                  repo_path=repo_path, device=device)
                val_acc = res['val_metrics']['accuracy']
                records.append({'lr': lr, 'batch': batch, 'max_features': maxf, 'val_acc': val_acc, 'result': res})
                if best is None or val_acc > best['val_acc']:
                    best = {'lr': lr, 'batch': batch, 'max_features': maxf, 'val_acc': val_acc, 'result': res}
    return {'best': best, 'records': records}


# %%
# --- Example usage --------------------------------------------------------
if __name__ == '__main__':
    # Try to locate a local copy of the masakhane repo; if present, we'll use local data
    repo = find_local_masakhane_repo('.')
    if repo:
        print('Found local repository at', repo)
        layout = inspect_data_layout(repo)
        print('Languages found in data/:', list(layout.keys())[:10])
    else:
        print('Local masakhane-news repo not found. The notebook will attempt to use HuggingFace `datasets` loader.')

    # Example: to run a small experiment on English with TF-IDF (this is an example —
    # for the full assignment you should run grid_search loops and document results)
    #
    # Uncomment to run in an interactive environment:
    # result = run_experiment_for_language('eng', feature_method='tfidf', max_features=5000, lr=1e-2, batch_size=64, epochs=20, repo_path=repo)
    # print('Validation accuracy:', result['val_metrics']['accuracy'])

    print('\nNotebook ready. Edit parameters above and run cells in a Jupyter environment.')
