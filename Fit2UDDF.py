# Fit2UDDF by SPD13
import sys
import xml.etree.cElementTree as ET
import datetime
import argparse
import os.path
from fitparse import FitFile

def dump_record_to_text(record):
    print(record);

def celsius_to_kelvin(C):
    return (C + 273.15)

class RecordDecoder:
    def __init__(self):
        self._fields_dic = {}

    @property
    def fields(self):
        return self._fields_dic

    @staticmethod
    def units_conv(item):
        if item.value is None:
            return None

        if item.units == 's':  # [s] to min
            strval = "%d" % item.value
            #rd = round(float(item.value))
            #strval = "%d:%02d min" % (rd / 60, rd % 60)
        elif item.units == 'm':
            strval = "%.1f" % round(float(item.value), 1)
        elif item.units == 'C':
            strval = "%.0f" % round(float(celsius_to_kelvin(item.value)), 1)
        elif item.units == 'percent':
            strval = "%d%%" % int(item.value)
        elif item.units == 'OTUs':
            strval = "%d OTUs" % int(item.value)
        elif item.units == 'kg/m^3':
            strval = "%.1f" % float(item.value)
        else:
            strval = str(item.value)

        return strval

    def load_rec(self, record):
        self._fields_dic = {}
        for item in record:
            self._fields_dic.update({item.name: self.units_conv(item)})

def main(argv):
    help_string = 'Fit2UDDF.py -i <fit_file> -o <uddf_file>'

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()
    fit_file = None
    uddf_file = None
    if ("input" in args):
        fit_file = args.input
    if ("output" in args):
        uddf_file = args.output

    if (os.path.isfile(fit_file) is False):
        print("ERROR: Impossible to read FIT file")
        sys.exit(2)
    #test
    #fit_file = '/Users/sebastien.bock/Desktop/2963427918.fit'
    #uddf_file = "test.uddf"

    if (fit_file == None or uddf_file == None):
        print("ERROR: Missing Parameters")
        print(help_string)
        sys.exit(2)

    decoder = RecordDecoder()
    fitparser = FitFile(fit_file)
    messages = fitparser.get_messages()

    #main UDDF doc
    uddf_doc = ET.Element("uddf", version="3.2.0")

    #Generator section
    uddf_generator = ET.Element("generator")
    ET.SubElement(uddf_generator, "name").text = "Fit2UDDF"
    ET.SubElement(uddf_generator, "manufacturer").text = "SPD13"
    ET.SubElement(uddf_generator, "version").text = "1.0"
    ET.SubElement(uddf_generator, "datetime").text = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    ET.SubElement(uddf_generator, "type").text = "converter"
    uddf_profiledata = ET.Element("profiledata")

    #Divesite section
    uddf_divesite = ET.Element("divesite")
    uddf_site = ET.Element("site")

    #Gas definition
    uddf_gasdefinitions = ET.Element("gasdefinitions")

    #Repetition group
    uddf_repetitiongroup = ET.Element("repetitiongroup")
    uddf_dive = ET.Element("dive")
    uddf_informationbeforedive = ET.Element("informationbeforedive")
    uddf_informationafterdive = ET.Element("informationafterdive")

    #Samples
    uddf_samples = ET.Element("samples")
    ET.SubElement(uddf_samples, "switchmix").text = "1"


    #General Parameters
    utc_offset_hours = 0
    lowesttemperature = 1000
    dive_duration = 0
    first_sample_date = None
    dive_date = None

    #First pass
    for record in messages:
        # print(record.name)
        # device_settings => 'time_offset': '540:00 min'
        if record.name == 'device_settings':
            decoder.load_rec(record)
            utc_offset_hours = int(decoder.fields["time_offset"].replace(":00 min", "")) / 60 / 60
        if record.name == 'session':  # Lat/Long
            decoder.load_rec(record)
            uddf_geography = ET.Element("geography")
            ET.SubElement(uddf_geography, "latitude").text = decoder.fields["start_position_lat"]
            ET.SubElement(uddf_geography, "longitude").text = decoder.fields["start_position_long"]
            uddf_site.append(uddf_geography)
        if record.name == 'dive_gas':  # Dive Gas
            decoder.load_rec(record)
            if (decoder.fields["status"] == "enabled"):
                uddf_gasmix = ET.Element("mix", id=decoder.fields["message_index"])
                ET.SubElement(uddf_gasmix, "o2").text = "{:.3f}".format(
                    float(decoder.fields["oxygen_content"].replace("%", "")) / 100.0)
                ET.SubElement(uddf_gasmix, "he").text = "{:.3f}".format(
                    float(decoder.fields["helium_content"].replace("%", "")) / 100.0)
                uddf_gasdefinitions.append(uddf_gasmix)
        if record.name == 'dive_summary':
            decoder.load_rec(record)
            if (decoder.fields["reference_mesg"]=="session"):
                dive_date = datetime.datetime.strptime(decoder.fields["timestamp"], "%Y-%m-%d %H:%M:%S")
                ET.SubElement(uddf_informationafterdive, "greatestdepth").text = decoder.fields["max_depth"]
                if (decoder.fields["dive_number"] != "None"):
                    ET.SubElement(uddf_informationbeforedive, "divenumber").text = decoder.fields["dive_number"]
        if record.name == 'dive_settings':
            decoder.load_rec(record)
            ET.SubElement(uddf_dive, "density").text = decoder.fields["water_density"]
        if record.name == 'record':
            decoder.load_rec(record)
            uddf_waypoint = ET.Element("waypoint")
            if (float(decoder.fields["temperature"])<lowesttemperature):
                lowesttemperature = float(decoder.fields["temperature"])
            ET.SubElement(uddf_waypoint, "temperature").text = decoder.fields["temperature"]
            ET.SubElement(uddf_waypoint, "depth").text = decoder.fields["depth"]
            sample_date = datetime.datetime.strptime(decoder.fields["timestamp"],"%Y-%m-%d %H:%M:%S")
            if (first_sample_date == None):
                first_sample_date = sample_date
            sample_sec = (sample_date - first_sample_date).total_seconds()
            if (dive_duration<sample_sec):
                dive_duration = sample_sec
            ET.SubElement(uddf_waypoint, "divetime").text = "{:.0f}".format(sample_sec)
            if ("ndl_time" in decoder.fields):
                ET.SubElement(uddf_waypoint, "nodecotime").text = decoder.fields["ndl_time"]
            uddf_samples.append(uddf_waypoint)

    #Latest values calculation
    if (lowesttemperature<100):
        ET.SubElement(uddf_informationafterdive, "lowesttemperature").text = "{:.2f}".format(lowesttemperature)
    if (dive_date!=None):
        dive_hour = int((dive_date.hour + utc_offset_hours) % 24)
        ET.SubElement(uddf_informationbeforedive, "datetime").text = "{:0>4d}".format(dive_date.year) + "-" + "{:0>2d}".format(dive_date.month) + "-" + "{:0>2d}".format(dive_date.day) + "T" + "{:0>2d}".format(dive_hour) + ":" + "{:0>2d}".format(dive_date.minute) + ":" + "{:0>2d}".format(dive_date.second)

    ET.SubElement(uddf_informationafterdive, "diveduration").text = "{:.0f}".format(dive_duration)
    uddf_dive.append(uddf_informationbeforedive)
    uddf_dive.append(uddf_samples)
    uddf_dive.append(uddf_informationafterdive)
    uddf_repetitiongroup.append(uddf_dive)
    uddf_profiledata.append(uddf_repetitiongroup)
    uddf_doc.append(uddf_generator)
    uddf_divesite.append(uddf_site)
    uddf_doc.append(uddf_divesite)
    uddf_doc.append(uddf_gasdefinitions)
    uddf_doc.append(uddf_profiledata)
    tree = ET.ElementTree(uddf_doc)
    tree.write(uddf_file)
    print("Done!")

if __name__ == '__main__':
    main(sys.argv[1:])