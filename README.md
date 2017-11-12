# mp6z

mp6z.py -- Python CLI script to control the Audio controller over serial
webapi.py -- Python/Flask web app that calls mp6z.py for control

This software was written to use a Raspberry Pi Zero W to control a Monoprice (and clones) 6-zone Whole House Audio System.  It will work on any linux machine with a serial port connected to it, just make sure you change the serial port in the software appropriately.  It will probably work on windows as well assuming you know what to change the serial port to.  The serial cable should be a straight through cable, and you can just plug the usb dongle directly into the back of unit.  If you have multiple units, it needs to be plugged into the first unit.

The script outputs JSON, with the intent that it will be run from a web app running locally to provide connectivity to phone apps and home automation systems.  If someone wants to write an Android app or a Vera plugin that can talk to the API, contact me via github and I'll assist where I can.

If you know of other products that use this same protocol, please let me know so I can start a list of everything this works with.

NOTE:  The webapi.py is pretty quick and dirty.  I've never written one before.  It does literally zero error checking, it has no authentication, it's almost certain to have huge security holes especially since it's calling things from the CLI and sanitizing nothing. DO NOT expose this to the internet!!!

Installation for CLI script

- Copy the script to a directory.
- chmod +x mp6z.py
- Make sure you have pyserial installed (apt-get install python-serial)
- Edit the top of the script for your source and zone names if you want, and make sure you set the serial port from /dev/ttyUSB0 to something else if your's is different.
- Run the script, usage info below.  Use the --verbose option so you can see what the script is sending and receiving over serial.

If you have a single controller, Zone 1 needs to be specified as "11" when using the script, Zone 2 is 12, etc.  This is because if you chain multiple controllers together, the first digit is the controller number, and the second digit is the zone number.  

```
usage: mp6z.py mode [zone] [-h] [--verbose] [-v V] [-s S] [-b B] [-t T] [-m M] [-d D]
               [-p P] [--bl bl]
               

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
  --bl BL        Set Balance (0-20, 10=Center)

Examples:
$ ./mp6z.py get   --  This will get the settings for all zones and output in JSON format
$ ./mp6z.py get 21 --  This will get the settings for the 1st zone on the second controller (if you have multiples chained)
$ ./mp6z.py set 21 -v 15 -s 6 --  This will set the 1st zone on the second controller to use source 6 and set volume to 15.
                                  Output will be the new settings in JSON format.
 
 
pi@pizerow:~/mp6z $ ./mp6z.py set 21 -v 5 -s 6
{
  "21": {
    "balance": "10", 
    "bass": "14", 
    "dnd": "00", 
    "keypad": "01", 
    "mute": "00", 
    "name": "Office", 
    "pa": "00", 
    "power": "01", 
    "source": "06", 
    "sourcename": "Sonos", 
    "treble": "13", 
    "volume": "05"
  }
}
pi@pizerow:~/mp6z $ ./mp6z.py get 11
{
  "11": {
    "balance": "10", 
    "bass": "13", 
    "dnd": "00", 
    "keypad": "01", 
    "mute": "00", 
    "name": "Dining Room", 
    "pa": "00", 
    "power": "01", 
    "source": "05", 
    "sourcename": "Empty", 
    "treble": "14", 
    "volume": "11"
  }
}
 
```

Usage for webapi.py flask app:

- Install flask and get it working with nginx (plenty of tutorials on this)
- Install shelljob (pip install shelljob)
- Default path for mp6z.py is /home/pi/mp6z/mp6z.py.  You'll need to change this in several places in the webapi.py script
- Start webserver

Examples of URLs:
http://127.0.0.1:5000/api/v1/zones  --- Method: GET - Gets settings for all zones
http://127.0.0.1/5000/api/v1/zones/11  --- Method: GET - Gets settings for Zone 1 on Controller 1
http://127.0.0.1/5000/api/v1/zones/11  --- Method: PUT - Updates settings for Zone 1 on Controller 1 and returns new settings. Example below:

```
pi@pizerow:~ $ curl -i -H "Content-Type: application/json" -X PUT -d '{"volume":"10", "source":"2", "bass":"14", "treble":"13"}' http://localhost:5000/api/v1/zones/21
HTTP/1.0 200 OK
Content-Type: text/plain; charset=utf-8
Connection: close
Server: Werkzeug/0.12.2 Python/2.7.9
Date: Sun, 12 Nov 2017 21:27:46 GMT

{
  "21": {
    "balance": "10", 
    "bass": "14", 
    "dnd": "00", 
    "keypad": "01", 
    "mute": "00", 
    "name": "Office", 
    "pa": "00", 
    "power": "01", 
    "source": "02", 
    "sourcename": "Chromecast", 
    "treble": "13", 
    "volume": "10"
  }
}
```
