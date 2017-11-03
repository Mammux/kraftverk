git pull origin master

# Buttons
ino clean && ino build --cppflags="-ffunction-sections -fdata-sections -g -Os -w -DBUTTON_ARDUINO" -m uno && ino upload -p /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_85632313039351D0F020-if00 -m uno

# Controls
ino clean && ino build --cppflags="-ffunction-sections -fdata-sections -g -Os -w -DCONTROLS_ARDUINO" -m uno && ino upload -p /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5573730303035141F012-if00 -m uno

# VFD, Lights, DC Volt, DC Amp
ino clean && ino build --cppflags="-ffunction-sections -fdata-sections -g -Os -w -DVFD_ARDUINO -DLIGHT_ARDUINO -DDC_VOLT_ARDUINO -DDC_AMP_ARDUINO" -m uno && ino upload -p /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_55737303030351D052F0-if00 -m uno


