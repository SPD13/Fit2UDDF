Fit2UDDF
===============

Here's a Python script to convert ANT/Garmin `.FIT` files coming from Garmin Descent MK1 into UDDF (Universal Dive Data Format).
UDDF format (http://uddf.org/) is used by most Dive Log softwares while few of them are supporting `.FIT` file format

use Python 3

```
python Fit2UDDF.py -i <fit_file> -o <uddf_file>
```
* <fit_file>: Your Fit full file path
* <uddf_file>: The output UDDF file path

Dependencies
-----------------------------------
This script is using FitParse Python library to parse `.FIT` files
but, it needs the modified version by xplwowi to take into account the Garmin Descent MK1 Specific fields.
You can find it there:
https://github.com/xplwowi/python-fitparse

Install
-----------------------------------
* Install python 3
* Download FitParse modified version from https://github.com/xplwowi/python-fitparse
* Install FitParse modified lib:
```
python setup.py install
```

Fresh install on Mac-OS
-----------------------------------
* Follow the tutorial here to install Python 3: https://docs.python-guide.org/starting/install3/osx/
* Create a workspace dir
```
mkdir python-workspace
```
* clone FitParse
```
git clone https://github.com/xplwowi/python-fitparse
```
* Install FitParse
```
cd python-fitparse
sudo python3 setup.py install
```
* Go back to your workspace dir
```
cd ..
```
* clone  Fit2UDDF
```
git clone https://github.com/SPD13/Fit2UDDF.git
```
* run the script
```
cd Fit2UDDF
python3 Fit2UDDF.py -i <fit_file> -o <uddf_file>
```

Features
-----------------------------------
* Automatic Timezone conversion. Use the UTC Offset to convert dive time to local time
* Unit Conversion (C to Kelvin) for temperature

Supported fields
-----------------------------------
The following fields will be populated from the `.FIT` file
* gasdefinitions
* divesite Lat and Long
* greatestdepth
* divenumber
* density
* ndl_time
* lowesttemperature
* dive datetime
* diveduration
* samples: depth, temperature, time