# mp6z
This software was written to use a Raspberry Pi Zero W to control a Monoprice (and clones) 6-zone Whole House Audio System.  It will work on any linux machine with a serial port connected to it, just make sure you change the serial port in the software appropriately.  

If you know of other products that use this same protocol, please let me know so I can start a list of everything this works with.

```
usage: mp6z.py mode [zone] [-h] [--verbose] [-v V] [-s S] [-b B] [-t T] [-m M] [-d D]
               [-p P] [-B B]
               

positional arguments:
  mode        <get|set>
  zone        <11-16,21-26,31-36>

optional arguments:
  -h, --help  show this help message and exit
  --verbose   Increase output verbosity
  -v V        Set Volume (0-38)
  -s S        Set Source (1-6)
  -b B        Set Bass (0-7)
  -t T        Set Treble (0-7)
  -m M        Set Mute (0=Off, 1=On)
  -d D        Set Do Not Disturb (0=Off, 1=On)
  -p P        Set Power (0=Off, 1=On)
  -B B        Set Balance (0-20, 10=Center)

Examples:
$ ./mp6z.py get   --  This will get the settings for all zones and output in JSON format
$ ./mp6z.py get 21 --  This will get the settings for the 1st zone on the second controller (if you have multiples chained)
$ ./mp6z.py set 21 -v 15 -s 6 --  This will set the 1st zone on the second controller to use source 6 and set volume to 15.
                                  Output will be the new settings in JSON format.
                                  
Known issues - Still working on set functionality
               Adding a name field for zones that can be configured in the script.
```
