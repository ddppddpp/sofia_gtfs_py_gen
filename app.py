"""
A Python module that generates a gtfs dataset for the public transport
of Sofia, Bulgaria by scraping the APIs at
www.sofiatraffic.bg
This is an excercise in python programing, ispired by the great work at
https://github.com/Dimitar5555/sofiatraffic-schedules
The APIs are not documented, likely to change with no notice.
"""
import sys
import os
from pathlib import Path
import json
import urllib
from datetime import date
from datetime import timedelta
import zipfile
import logging
import requests


from const import (
    SCHEDULES_URL,
    STOPS_URL,
#    VIRTUAL_TABLE_URL,
    LINES_URL
)

logger = logging.getLogger(__name__)


def get_sofia_traffic_session():
    """open a session to Sofia TRaffic and return it to the calling funciton
      example from 
#     https://bobbyhadz.com/blog/how-to-use-cookies-in-python-requests
#   """
    session = requests.Session()
    r =  session.get('https://sofiatraffic.bg/bg/public-transport')
    return session


def fetch_data_from_sofiatraffic(url, payload):
    """
    Send a POST request to url and return the body
    """
    # check if this has already been called so we can re-use it?
    session = get_sofia_traffic_session()
    tokens = session.cookies.get_dict()
    #print(tokens)
    # custom headers
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "X-XSRF-TOKEN": urllib.parse.unquote(tokens['XSRF-TOKEN']),
            "Cookie": 'sofia_traffic_session='+urllib.parse.unquote(tokens['sofia_traffic_session']),
           "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Referrer": "https://www.sofiatraffic.bg/bg/public-transport",
            "TE": "trailers"}

    response = session.post(url, headers=headers, data=payload, timeout=(3.05, 27) )
    return response

def get_all_stops():
    """
    call the schedules url and get a list of all the stops
    """
    payload = json.dumps("{}")
    response = fetch_data_from_sofiatraffic(STOPS_URL,payload=payload)
    return response

def get_all_lines():
    """
    call the lines url and get a list of all the lines
    """
    payload = json.dumps("{}")
    response = fetch_data_from_sofiatraffic(LINES_URL,payload=payload)
    return response

def get_schedule(ext_id: str):
    """ 
    call the schedules url with a line id and return a schedule
    """
    payload = json.dumps({"ext_id":ext_id})
    response = fetch_data_from_sofiatraffic(SCHEDULES_URL,payload=payload)
    return response

def generate_stops_txt():
    """
    call get_all_stops() and generate a gtfs-compliant stops.txt file
    stop_id, stop_code, stop_name, stop_lat, stop_lon
    some of the names contain comma which trips a validator error
    dirty fix - replace comma with space
    """
    list_of_stops = get_all_stops().json()
    file_name = 'gtfs/stops.txt'
    with open(file_name, 'wt', encoding="utf-8") as fd:
        fd.write("stop_id, stop_code, stop_name, stop_lat, stop_lon\n")
        for cgm_stop in list_of_stops:
            ## testing with stop["code"] instead of stop["id"]
#            string = str(cgm_stop["id"])+\
            string = str(cgm_stop["code"])+\
                ","+str(cgm_stop["code"])+\
                ","+str(cgm_stop["name"]).replace(',',' ')+\
                ","+str(cgm_stop["latitude"])+\
                ","+str(cgm_stop["longitude"]+"\n")
            fd.write(string)

def generate_agency_txt():
    """
    generate the gtfs-comliant file agencies.txt
    format: agency_id,agency_name,agency_url,agency_timezone,agency_lang
    the contents of this file will be static until a proper source is found
    """
    agencies = []
    agencies.append("agency_id,agency_name,agency_url,agency_timezone,agency_lang\n")
    agencies.append("sfagency_001,Столичен електротранспорт ЕАД, http://www.elektrotransportsf.com, EET, bg\n")
    agencies.append("sfagency_002, Столичен автотранспорт ЕАД, https://www.sofiabus.bg, EET, bg\n")
    agencies.append("sfagency_003, Метрополитен ЕАД, https://www.metropolitan.bg, EET, bg\n")
    file_name = 'gtfs/agency.txt'
    with open(file_name, 'wt', encoding="utf-8") as fd:
        for agency in agencies:
            fd.write(agency)

def generate_routes_txt(list_of_lines: list):
    """
    generate the gtfs-comliant file routes.txt
    route_id ,agency_id, route_short_name,route_type, route_color
    when parsing the results from get_all_lines, the types should be mapped:
    route_type 0 - Tram, Streetcar, Light Rail
    route_type 1 - Subway/Metro
    route_type 3 - Bus (both short and long distance)
    route_type 11 - Trolleybus
    More info at https://gtfs.org/documentation/schedule/reference/#routestxt
    cgm.line_id -> route_id
    cgm.ext_id -> route_short_name
    cgm.type -> route_type (see above)
    cgm.color -> route_color
    """
    #prep the data
    temp_type = 0
    temp_agency = ''
#    list_of_lines = (get_all_lines().json())
    logger.info("Generating routes.txt")
    file_name = 'gtfs/routes.txt'
    with open(file_name, 'wt', encoding="utf-8") as fd:
        fd.write("route_id,agency_id,route_short_name,route_type,route_color\n")
        for intput_line in list_of_lines:
            if intput_line["type"] == 1: #bus
                temp_type = 3
                temp_agency = 'sfagency_002'
            elif intput_line["type"] == 2: #tram
                temp_type = 0
                temp_agency = 'sfagency_001'
            elif intput_line["type"] == 3: #metro
                temp_type = 1
                temp_agency = 'sfagency_003'
            elif intput_line["type"] == 4: #trolleybus
                temp_type = 11
                temp_agency = 'sfagency_001'
            elif intput_line["type"] == 5: #nightbus
                temp_type = 3
                temp_agency = 'sfagency_002'
            else:
                temp_type = ''
            string = str(intput_line["line_id"])+","+\
                    str(temp_agency)+','+\
                    str(intput_line["ext_id"])+","+\
                    str(temp_type)+','+\
                    str(intput_line["color"]).replace("#","")+"\n"
            fd.write(string)

def generate_trips_and_stop_times_txt(list_of_lines: list):
    """
    - for every line in all_lines.json get a schedule
    - for every route in the json, get the route_id and set it as trip_id
    - for every route in the json, get the name and set it as trip_headsign
    - route["ext_id"] -> trip_short_name
    routes.route_id, calendar.service_id, trip_id, trip_headsign
    stop_times
    for every line from get_all_lines get a schedule
    for every route in the schedule get all segments
    each segment has a stop and an end_stop
    for every stop get all times.
    put the times in an array. sort them by time
    for every time in the array write a line in stop_times

    favour multiple itterations over arrays vs multiple calls to the api
    """
    file_name_trips = 'gtfs/trips.txt'
    file_name_stop_times = 'gtfs/stop_times.txt'
    timepoint = str(0) #arrival and departure times are approximate
    with open(file_name_trips, 'wt', encoding="utf-8") as fd_trips, open(file_name_stop_times, 'wt', encoding="utf-8") as fd_stop_times:
        logger.info('Generating trips.txt...')
        #header for the trips file
        fd_trips.write("route_id,service_id,trip_id,trip_headsign\n")
        logger.info('Generating stop_times.txt...')
        #header for the trips file
        fd_stop_times.write("trip_id,arrival_time,departure_time,stop_id,stop_sequence,timepoint\n")
        for line in list_of_lines:
            logger.info("processing line %s",line["ext_id"])
            schedule = get_schedule(line['ext_id'])
            for route in schedule.json()['routes']:
                ##!!! Don't forget to check if the route is active
                #try if route["details"].["is_active"]:
                logger.info('Processing route %s',str(route["id"]))
                
                sequence = 1
                for segment in route["segments"]:
                    stop = segment["stop"]
                    if stop["is_active"]:
                        # temp_time = []
                        for time in stop["times"]:
                        #     temp_time.append(time["time"])
                        # temp_time.sort()
                        # for new_time in temp_time:
                            # testing w/out sorting from here
                            #trips
                            ## TODO!!!!      write entries for all services operating on this trip
                            #route_id,service_id,trip_id,trip_headsign
                            fd_trips.write(str(line["line_id"])+","+"weekday_service,"+str(time["item_id"])+","+str(route["name"]).replace(',',' ')+"\n")
                            #repeat for holidays, etc. services
                            #stop_times
                            #trip_id,arrival_time,departure_time,stop_id,stop_sequence,timepoint                     
                            fd_stop_times.write(str(time["item_id"])+","+str(time["time"])+","+str(time["time"])+","+str(stop["code"])+","+str(sequence)+","+timepoint+"\n")
                    sequence+=1
                logger.info('Processing route %s complete',route["id"])
            logger.info("processing line %s complete",line["ext_id"])

def generate_calendar_txt():
    """
    generate the calendars.txt file describing different schedules as needed.
    static information.
    """
    #set start_date and end_date
    start_date = date.today()
    end_date = start_date + timedelta(days=7)
    file_name = 'gtfs/calendar.txt'
    with open(file_name, 'wt', encoding="utf-8") as fd:
        #header
        fd.write("service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n")
        #weekday, week night, holiday + night
        fd.write("weekday_service,1,1,1,1,1,0,0,"+start_date.strftime("%Y%m%d")+","+end_date.strftime("%Y%m%d")+"\n")
        fd.write("holiday_service,0,0,0,0,0,1,1,"+start_date.strftime("%Y%m%d")+","+end_date.strftime("%Y%m%d")+"\n")
        fd.write("weekday_service_night,1,1,1,1,1,0,0,"+start_date.strftime("%Y%m%d")+","+end_date.strftime("%Y%m%d")+"\n")
        fd.write("holiday_service_night,0,0,0,0,0,1,1,"+start_date.strftime("%Y%m%d")+","+end_date.strftime("%Y%m%d")+"\n")

def generate_feed_info_txt():
    """
    Add metadata for the dataset
    """
    start_date = date.today()
    end_date = start_date + timedelta(days=7)
    file_name = 'gtfs/feed_info.txt'
    with open(file_name, 'wt', encoding="utf-8") as fd:
        fd.write("feed_publisher_name,feed_publisher_url,feed_lang,feed_start_date,feed_end_date\n")
        fd.write("ddppddpp,https://github.com/ddppddpp/sofia_gtfs_py_gen,bg,"+start_date.strftime("%Y%m%d")+","+end_date.strftime("%Y%m%d")+"\n")

def create_dataset_zip():
    """
    Create a .zip of the files
    """
    # check how not to create a directory
    fileset= ['gtfs/agency.txt','gtfs/calendar.txt','gtfs/routes.txt',
    'gtfs/stop_times.txt','gtfs/stops.txt','gtfs/trips.txt','gtfs/feed_info.txt']
    try:
        with zipfile.ZipFile('gtfs/SofiaTraffic.zip', 'a', compression=zipfile.ZIP_DEFLATED) as myzip:
            # myzip.write('gtfs/agency.txt')
            # myzip.write('gtfs/calendar.txt')
            # myzip.write('gtfs/routes.txt')
            # myzip.write('gtfs/stop_times.txt')
            # myzip.write('gtfs/stops.txt')
            # myzip.write('gtfs/trips.txt')
            # myzip.write('gtfs/feed_info.txt')
            for file in fileset:
                myzip.write(file,os.path.basename(file))
        myzip.close()
        os.sync()
    except zipfile.BadZipFile as error:
        logger.error(error)

def generate_gtfs():
    """
    call the various functions to generate the gtfs-compliant files
    """
    logging.basicConfig(filename='gtfs_gen.log', level=logging.INFO, format='%(asctime)s %(message)s')
    logger.info('Starting GTFS Generation')
    #check if folder exists?
    Path("./gtfs").mkdir(parents=True, exist_ok=True)
    generate_agency_txt()
    generate_stops_txt()
    list_of_lines = (get_all_lines().json())
    generate_routes_txt(list_of_lines)
    generate_calendar_txt()
    generate_trips_and_stop_times_txt(list_of_lines)
    generate_feed_info_txt()
    logger.info('Completing GTFS Generation')
    logger.info('Creating Archive...')
    #gzip the folder?
    create_dataset_zip()
    logger.info('Archive succesfully created. End.')


def main (argv):
    """"
    call generate_gtfs()
    """
    generate_gtfs()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
