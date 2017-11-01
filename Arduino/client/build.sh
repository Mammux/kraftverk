git pull origin master
ino clean && ino build --cppflags="-ffunction-sections -fdata-sections -g -Os -w -DBUTTON_ARDUINO" && ino upload -p /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_85632313039351D0F020-if00
ino clean && ino build --cppflags="-ffunction-sections -fdata-sections -g -Os -w -DCONTROLS_ARDUINO" && ino upload -p /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5573730303035141F012-if00


