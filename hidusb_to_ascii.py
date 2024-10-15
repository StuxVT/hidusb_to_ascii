#!/usr/bin/env python3

"""
Try and translate a pcap of USB HID to ascii text.
The data is in "USB Leftover section" - either use wireshark or tshark directly to extact the data.

tshark -r ./my.pcapng -T fields -e usb.capdata -Y usb.capdata 2>/dev/null

The output should look like:
0000000000000000
0000040000000000
0000000000000000
00000b0000000000

The first byte is used for modifiers, we only use 0x02 here. (shift)
The third byte is the keycode for the key.
The fourth byte is errorbit - here used for long keypresses

If all is 00, this is a key release

"""
import string

def usb_to_ascii(num, mod=0):
    # map keys
    lower = '????' + string.ascii_lowercase + "1234567890" + "\n??\t -=[]\\?;'`,./?"
    upper = '????' + string.ascii_uppercase + "!@#$%^&*()" + "\n??\t _|{}|?:\"~<>??"

    # Default to lower
    chars = lower
    
    if mod == 2:  # Changed from 32 to 2
        chars = upper
    if num == 42:
        # Hack in backspace
        return '\x08'
    if 0 <= num < len(chars):
        # print(num, chars[num])
        return chars[num]

text = ""
with open('./keyboard.txt', 'r') as file:
    for line in file:
        # Parse the line as a single 16-character hexadecimal string
        data = line.strip()
        if len(data) != 16:
            continue  # Skip invalid lines
        
        # Extract relevant bytes
        mod = int(data[0:2], 16)
        val = int(data[4:6], 16)
        err = int(data[6:8], 16)
        
        if err == 0:  # Only append if error bit isn't set (This will exclude long keypresses)
            if val:  # Only continue if this is not a keyrelease
                char = usb_to_ascii(val, mod=mod)
                if char is not None:
                    text += char

print(text)
