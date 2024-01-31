A simple desktop app that displays points on a map using a handful of python libraries.

## installation

`pip install git+https://github.com/dorgeshuun/pygis`

## usage

Use a csv file as input file (a culverts.csv file is provided as example): 

`pygis culverts.csv`

The input file must have longitude and latitude as first fields and use semicolons as separators:

longitude;latitude;Road name;Culvert material<br>
-72.064055186;44.374348231;KEYSER HILL RD;Steel Corrugated<br>
-72.311560587;44.393511727;WHITTIER HILL RD;Plastic Corrugated<br>
-72.62324037;43.242357135;POPPLE DUNGEON RD;Steel Corrugated<br>

The program also reads from standard input:

`head culverts.csv | pygis`

![pygis_screenshot.png](https://github.com/dorgeshuun/pygis/blob/master/pygis_screenshot.png)
