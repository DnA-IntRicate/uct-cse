import jupytext

# read the .py file as a notebook object
nb = jupytext.read("csc_2042_s_a_3_multinomial_logistic_regression_masakha_news_notebook.py")

# write it out as .ipynb
jupytext.write(nb, "notebook-assignment3.ipynb", fmt = "ipynb")

input("Press Enter to continue...")
