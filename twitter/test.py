import shutil, os

path = os.getcwd() + '/stored/' + '7:3/'
files = os.listdir(path)

for f in files:
    shutil.move(path + f, os.getcwd() + '/stored/')