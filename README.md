
# sofia_gtfs_py_gen

GTFS Generator for Sofia, Bulgaria

A Python module that generates a gtfs dataset for the public transport
of Sofia, Bulgaria by scraping the APIs at
[www.sofiatraffic.bg](https://www.sofiatraffic.bg)
This is an excercise in python programing, ispired by the great work at
[https://github.com/Dimitar5555/sofiatraffic-schedules](https://github.com/Dimitar5555/sofiatraffic-schedules)
The APIs are not documented, likely to change with no notice.
The resulting dataset has been validated with the [Canonical GTFS Schedule Validator](https://gtfs-validator.mobilitydata.org/).

##Usage

Call ```python app.py``` to have the module call the APIs and generate the dataset.
The output is currently hardcoded to the gtfs/ subdirectory of the current path.

##TODO

- ~Fix inclomplete routes~
- Fix backwards time travel between stops (i.e. line A84, trip 9175)
- Investigate duplicate entires (i.e. M3 line)
- Error exceptions
- Eliminate commented-out code
- Optimize for performance
- Optimize for API calls
- Fix gtfs validator warnings
- Integrate dataset validation as a test
