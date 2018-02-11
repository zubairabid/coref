import os
import sys
from collections import defaultdict
import operator

pos = defaultdict(int)
path = sys.argv[1] 
files = os.listdir(path)
for fil in files:
    with open(path+fil) as f:
        lines = f.readlines()
        for lin in lines:
            if 'cref' in lin:
                if len(lin.split('\t'))>3:
                    pos[lin.split('\t')[2]]+= 1

print sorted(pos.items(), key=operator.itemgetter(1), reverse=True)
