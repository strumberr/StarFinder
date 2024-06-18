import numpy as np
import datetime
import math as m

class TimeKeeper:
    def __init__(self, time=None):
        if time is None:
            now = datetime.datetime.now(datetime.timezone.utc)
            self.time = now.strftime('%m%d%y %H%M')
        else:
            self.time = time
        
        self.GMSThh = None
        self.GMSTmm = None
        self.GMSTss = None

    def GMST(self):
        # The UTC time and date as MMDDYY HHMM. (UTC = EST+5, EDT+4)
        TD = self.time

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


class AltAz(TimeKeeper):
    def __init__(self, lat, lon, time=None):
        super().__init__(time)
        self.lat = lat
        self.lon = lon
        self.target_body_RA = None
        self.target_body_DEC = None
        self.HA = None
        self.lat_rad = None
        self.dec_rad = None
        self.HA_rad = None
        self.target_body_alt_rad = None
        self.target_body_alt = None
        self.target_body_az = None

    def TBRA(self, target_body_RA_h, target_body_RA_m, target_body_RA_s):
        self.target_body_RA_h = target_body_RA_h
        self.target_body_RA_m = target_body_RA_m
        self.target_body_RA_s = target_body_RA_s
        self.target_body_RA = target_body_RA_h + (target_body_RA_m / 60.0) + (target_body_RA_s / 3600.0)

    def TBDEC(self, target_body_DEC_deg, target_body_DEC_min, target_body_DEC_sec):
        self.target_body_DEC_deg = target_body_DEC_deg
        self.target_body_DEC_min = target_body_DEC_min
        self.target_body_DEC_sec = target_body_DEC_sec
        self.target_body_DEC = self.dms_to_deg(target_body_DEC_deg, target_body_DEC_min, target_body_DEC_sec)

    def TBName(self, target_body_name):
        self.target_body_name = target_body_name

    # Function to convert degrees, minutes, and seconds to decimal degrees
    def dms_to_deg(self, deg, min, sec):
        return deg + (min / 60.0) + (sec / 3600.0)

    # Function to convert degrees to radians
    def deg_to_rad(self, deg):
        return m.radians(deg)

    def lst(self):
        # Greenwich mean sidereal time (GMSThh, GMSTmm, GMSTss)
        GMST = self.GMST()
        print("GMST:", GMST)  # Debug print
        # Local sidereal time (LSThh, LSTmm, LSTss)
        LST = self.LST(self.lon, GMST[0], GMST[1], GMST[2])
        print("LST:", LST)  # Debug print

        return LST

    def ha(self, LST):
        # Calculate Hour Angle (HA)
        HA = (LST[0] + LST[1] / 60.0 + LST[2] / 3600.0) - self.target_body_RA
        self.HA = HA * 15  # Convert HA from hours to degrees

    def latDecToRad(self):
        # Convert latitude and declination to radians
        self.lat_rad = self.deg_to_rad(self.lat)
        self.dec_rad = self.deg_to_rad(self.target_body_DEC)
        self.HA_rad = self.deg_to_rad(self.HA)

    def altitude(self):
        # Altitude of the target body
        self.target_body_alt_rad = m.asin(m.sin(self.dec_rad) * m.sin(self.lat_rad) + m.cos(self.dec_rad) * m.cos(self.lat_rad) * m.cos(self.HA_rad))
        self.target_body_alt = m.degrees(self.target_body_alt_rad)

    def azimuth(self):
        # Azimuth calculation
        cos_A = (m.sin(self.dec_rad) - m.sin(self.target_body_alt_rad) * m.sin(self.lat_rad)) / (m.cos(self.target_body_alt_rad) * m.cos(self.lat_rad))
        # Ensure the value is within valid range for acos
        cos_A = min(1.0, max(-1.0, cos_A))
        A_rad = m.acos(cos_A)

        # If sin(HA) is negative, then AZ = A, otherwise AZ = 360 - A
        if m.sin(self.HA_rad) < 0:
            self.target_body_az = m.degrees(A_rad)
        else:
            self.target_body_az = 360 - m.degrees(A_rad)

        return self.target_body_az


# Example usage
# lat = 13.775006
# lon = 100.569991

# altitude_azimuth = AltAz(lat, lon)
# altitude_azimuth.TBRA(2, 9, 55)
# altitude_azimuth.TBDEC(11, 57, 22)
# altitude_azimuth.TBName("Mars")
# LST = altitude_azimuth.lst()
# altitude_azimuth.ha(LST)
# altitude_azimuth.latDecToRad()
# altitude_azimuth.altitude()
# azimuth = altitude_azimuth.azimuth()

# print("Altitude:", altitude_azimuth.target_body_alt)
# print("Azimuth:", azimuth)
