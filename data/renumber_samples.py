import os

os.chdir("positives-raw")
files = os.listdir()
num = 1
for fil in files:
    os.system("mv " + fil + " raw-sample-" + str(num) + ".wav")
    num += 1
