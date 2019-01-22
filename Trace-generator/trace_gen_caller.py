import random
import os
import math

import time


flow=os.popen("./trace_generator 564 "+ str(time.time())).read()
# size,start=flow.split(' ')[0].split('\n')[0].split(':')
print(flow.split(' ')[0].split('\n')[0].split(':'))