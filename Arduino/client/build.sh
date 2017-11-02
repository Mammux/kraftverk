git pull origin master
ino clean && ino build --cppflags="-ffunction-sections -fdata-sections -g -Os -w -DBUTTON_ARDUINO" -m uno && ino upload -p /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_85632313039351D0F020-if00 -m uno
ino clean && ino build --cppflags="-ffunction-sections -fdata-sections -g -Os -w -DCONTROLS_ARDUINO" -m uno && ino upload -p /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5573730303035141F012-if00 -m uno

