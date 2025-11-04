# ToC Notes

## Language Theory

### Turing-recognizable Languages (recursively enumerable)

A language L is **Turing-recognizable** if there exists a Turing Machine M such that:
- For every input $w$ in the language L, M accepts $w$
- For every input $w$ **not** in the language L, M either rejects or loops forever

> A Turing-recognizable language is one where a TM can recognize members of the language but may loop forever on inputs outside of the language.

The **halting problem** is **Turing-recognizable**.

### Turing-decidable Languages (recursive)

A language L is **Turing-decidable** if there exists a Turing Machine M such that:
- For every input $w$ in the language L, M accepts $w$
- For every input $w$ **not** in the language L, M rejects $w$
- M **always halts**

> A Turing-decidable language is one for which there is an algorithm that **always terminates** and correctly tells whether the input string is in the language or not.

The language of all strings over $\{0,1\}$ with an **even number of 1s** is **Turing-decidable** by some Turing Machine M.

> The set of all **Turing-decidable** languages is a subset of the **Turing-recognizable** languages. $L_{R} \; \subset \; L_{RE}$.

> **All decidable languages can be recognized, but some recognizable languages are undecidable**.

---
