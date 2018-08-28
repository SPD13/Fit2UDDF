Fit2UDDF
===============

Here's a Python script to convert ANT/Garmin `.FIT` files coming from Garmin Descent MK1 into UDDF (Universal Dive Data Format).
UDDF format (http://uddf.org/) is used by most Dive Log softwares while few of them are supporting `.FIT` file format

use Python 3

```
Fit2UDDF.py -i <fit_file> -o <uddf_file>
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