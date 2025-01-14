'''
a collection of utility functions
'''

from string import capwords

def mixed_case(mystring: str):
    '''
    Turn i.e. STOP NAME into Stop Name
    '''
    return capwords(mystring)



def generate_track_from_segments(routes: list):
    '''
    For each route parse the segments array and return a route identificator
    and a list of stops
    '''
    tracks = []
    for route in routes:
        track = dict(ext_id = route['ext_id'],
                     name = route['name'],
                     stops = [])
        for segment in route['segments']:
            track['stops'].append(segment['stop']['code'])
        tracks.append(track)
    print(tracks)
    return tracks

def generate_timetables_for_schedule(schedule: dict, ext_trip_id: str):
    '''
    input structure
    schdeule -> json
    --line
    --routes []
    ----route['ext_id'] -> unuque (I think?)
    ------segments[]
    --------stop{}
    ----------id -> 'internal' stop id
    ----------ext_id i.e. TM0593
    ----------code - same as ext_id w/out prefix i.e. 0593
    ----------times[]
    ------------id -> check if this can be used to match trip

    output structure
    trip_id,arrival_time,departure_time,stop_id,stop_sequence,timepoint

    for each route
      for each segment
        for each time
          output:
            trip_id (times id + route id + stopid)

            
    debug structure
    dict(car_id = time.id,
        stop_time:[stop_id, time])
    '''
    entry = dict(trip_id=ext_trip_id,stop_times=[])
    for route in schedule.json()['routes']:
        print('route=',route['ext_id'],'\n')
        for segment in route['segments']:
            for time in segment['stop']['times']:
                # if time['time'] == '20:26:00' and segment['stop']['code']=='0593':
                #     print ('time_id=',time['id'])
                # if not time['weekend']:
                if str(time['id']) == str(ext_trip_id):
                    stop_time = {'stop':segment['stop']['code'],
                                 'time':time['time']}
                    entry['stop_times'].append(stop_time)

    print(entry)
    return entry
