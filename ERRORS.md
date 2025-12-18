(venv) PS C:\Users\Abhishek\Documents\GitHub\metrics-collector> python collectors/node/node_cpu_collector.py
>>
Traceback (most recent call last):
  File "C:\Users\Abhishek\Documents\GitHub\metrics-collector\collectors\node\node_cpu_collector.py", line 4, in <module>
    from config.settings import PROMETHEUS_URL
ModuleNotFoundError: No module named 'config'
(venv) PS C:\Users\Abhishek\Documents\GitHub\metrics-collector>

# SOLUTION :-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


