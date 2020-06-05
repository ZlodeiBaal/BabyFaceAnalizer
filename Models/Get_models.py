import urllib.request
import os

try:
    if os.uname()[4][:3] == 'arm':
        print('RPi found')
        file1 = open('models_rpi.txt', 'r')
    else:
        print('CPU found, unix')
        file1 = open('models_cpu.txt', 'r')
except:
    print('CPU found, win')
    file1 = open('models_cpu.txt', 'r')

models_list = file1.readlines()


for file_adress in models_list:
    file_name = file_adress.strip().split('/')[-1]
    print('Downloading '+file_name)
    filedata = urllib.request.urlopen(file_adress.strip())
    datatowrite = filedata.read()

    with open(file_name, 'wb') as f:
        f.write(datatowrite)