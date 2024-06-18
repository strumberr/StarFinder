import datetime

class TimeKeeper:
    def __init__(self):
        self.now = datetime.datetime.now(datetime.timezone.utc)
        self.GMSThh = None
        self.GMSTmm = None
        self.GMSTss = None

    def GMST(self, lon, now):

        LongDeg = int(lon)
        LongMin = (lon - int(lon)) * 60
        LongSec = (LongMin - int(LongMin)) * 60
        LongMin = int(LongMin)
        LongSec = int(LongSec)

        # The UTC time and date as MMDDYY HHMM. (UTC = EST+5, EDT+4)
        TD = now.strftime('%m%d%y %H%M')

        # Split TD into individual variables for month, day, etc. and convert to floats:
        MM = float(TD[0:2])
        DD = float(TD[2:4])
        YY = float(TD[4:6])
        YY = YY + 2000 
        hh = float(TD[7:9])
        mm = float(TD[9:11])

        # Convert mm to fractional time:
        mm = mm / 60

        # Reformat UTC time as fractional hours:
        UT = hh + mm

        # Calculate the Julian date:
        JD = (367 * YY) - int((7 * (YY + int((MM + 9) / 12))) / 4) + int((275 * MM) / 9) + DD + 1721013.5 + (UT / 24)

        # Calculate the Greenwich mean sidereal time:
        GMST = 18.697374558 + 24.06570982441908 * (JD - 2451545)
        GMST = GMST % 24  # Use modulo operator to convert to 24 hours
        GMSTmm = (GMST - int(GMST)) * 60  # Convert fraction hours to minutes
        GMSTss = (GMSTmm - int(GMSTmm)) * 60  # Convert fractional minutes to seconds
        GMSThh = int(GMST)
        GMSTmm = int(GMSTmm)
        GMSTss = int(GMSTss)

        return GMSThh, GMSTmm, GMSTss

    def LST(self, lon, GMSThh, GMSTmm, GMSTss):
        # Calculate longitude in DegHHMM format for edification of user:
        hemisphere = 'W'
        if lon > 0:  # if the number is positive it's in the Eastern hemisphere
            hemisphere = 'E'
        LongDeg = int(lon)
        LongMin = (lon - int(lon)) * 60
        LongSec = (LongMin - int(LongMin)) * 60
        LongMin = int(LongMin)
        LongSec = int(LongSec)

        # Convert longitude to hours
        Long = lon / 15
        # Calculate the local sidereal time by adding the longitude (in hours) to the GMST
        LST = GMSThh + Long + GMSTmm / 60 + GMSTss / 3600
        LST = LST % 24  # Use modulo operator to convert to 24 hours
        LSTmm = (LST - int(LST)) * 60  # Convert fraction hours to minutes
        LSTss = (LSTmm - int(LSTmm)) * 60  # Convert fractional minutes to seconds
        LSThh = int(LST)
        LSTmm = int(LSTmm)
        LSTss = int(LSTss)

        return LSThh, LSTmm, LSTss
