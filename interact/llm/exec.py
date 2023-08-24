import os
import subprocess
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

def start_jupyter_notebook():
    try:
        subprocess.run(['jupyter', 'notebook'], check=True)
    except subprocess.CalledProcessError as e:
        print("Error starting Jupyter Notebook:", e)


def run_ipython_code(code):
    try:
        result = subprocess.run(['ipython', '-c', code], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running IPython code:", e)


if __name__ == "__main__":
    # Start Jupyter Notebook server
    # start_jupyter_notebook()

    # Run IPython code
    ipython_code = """
    import pandas as pd

    # Load the data
    iris = pd.read_csv('/tmp/iris.csv')

    # Display the first few rows of the data
    iris.head()
    """
    run_ipython_code(ipython_code)
