# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

code = """import pandas as pd

# Load the data
iris = pd.read_csv('/tmp/iris.csv')

# Display the first few rows of the data
iris.head()
"""

from IPython import get_ipython


ipython = get_ipython()

exec(code)


output_result = ipython.last_execution_result.capture.output
print("\n".join(output_result))