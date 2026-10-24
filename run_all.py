import subprocess,sys
from pathlib import Path
files=['arraysum.py','factorial.py','bubblesort.py','fibonacci.py','matmul.py','maxmin.py','oddeven.py','prime.py','transpose.py']
all_output=''
for file in files:
	print(f"Running {file}...");result=subprocess.run([sys.executable,file],capture_output=True,text=True);all_output+=f"Output of {file}:\n{result.stdout}\n"
	if result.stderr:all_output+=f"Errors in {file}:\n{result.stderr}\n"
print('All outputs:')
print(all_output)
Path('all_outputs.txt').write_text(all_output)
print('done')