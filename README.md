# RPi_Movidius_baby_sitter
This project is about a system for automatic monitoring of a newborn child: a face detector, activity, open eyes. For each event, you can configure the reaction - displaying an alert in a telegram channel or displaying an image / sequence of images. A more complete description of the system is available in Russian here - https://habr.com/ru/company/recognitor/blog/516232/


# SetUP

For setup (for Raspberry Pi):
1. Clone the project
2. Run `Get_models.py` script from Models folder
3. If autostart is needed - use this https://github.com/ZlodeiBaal/RPi_WiFi_autoconnect#work-on-the-startup (what to start you can read in "Start" paragraph)
3. Install `l_openvino_toolkit_runtime_raspbian_p_2020.1.023.tgz` as described - docs.openvinotoolkit.org/latest/openvino_docs_install_guides_installing_openvino_raspbian.html
4. Install reqirements (for desktop use requirement.txt, for RPi need to install also python-dev and portaudio19-dev via apt-get):
```
   pip3 install webrtcvad
   sudo apt-get install python-dev
   sudo apt-get install portaudio19-dev
   pip3 install pyaudio
   pip3 pyzbar
   pip3 python-telegram-bot
```

Also, this is usefull command for me:
1. Turn on SSH - https://www.raspberrypi.org/documentation/remote-access/ssh/
2. Remove message about default password - sudo apt purge libpam-chksshpwd
3. Turn off screen saver - www.raspberrypi.org/forums/viewtopic.php?t=260355
  

# Different SetUP

You can use this RPi image, which is already set up - https://yadi.sk/d/mkt8nhx1w03m3A

#Start

There are 2 script that you may need to start this repo:
1. `QRCode.py` - providing connection to WiFi and telegram, checking camera and movidius connection.
2. `face.py` - main script, better to read this article - https://habr.com/ru/company/recognitor/blog/516232/ 

#QRCode.py

1. If internet is not connected this script connecti to camera and start searching QRCode with information that discrabed here - https://github.com/ZlodeiBaal/RPi_WiFi_autoconnect
2. Checking file `tg_creedential.txt` with telegram credentials. If file not present - start searching QRCode with text:
```
token to access the HTTP API (could get from @BotFather throught "/newbot")
socks5://… — don't used at this time, but this string should present
login for socks5  —  don't used at this time, but this string should present
password socks5 —  don't used at this time, but this string should present
```
You could serialize this information throught www.the-qrcode-generator.com
