"""
Execute the Incidents_EDA notebook and save the output
"""
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import sys

print("Loading notebook...")
with open('Incidents_EDA.ipynb', 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

print("Executing notebook cells...")
print("This may take a few minutes...")

ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

try:
    ep.preprocess(nb, {'metadata': {'path': './'}})
    print("\n✅ Notebook executed successfully!")
    
    # Save executed notebook
    with open('Incidents_EDA_Executed.ipynb', 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    
    print("✅ Executed notebook saved as: Incidents_EDA_Executed.ipynb")
    
except Exception as e:
    print(f"\n❌ Error during execution: {str(e)}")
    sys.exit(1)
