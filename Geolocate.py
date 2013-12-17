#!/usr/bin/python
"""
Helper class for doing Geolocation and Spatial Autocorrelation calculations.
Author: Etienne Stalmans
Version: 0.3a (2012)
"""
import pygeoip
from datetime import datetime
from pytz import timezone
import utmLL 
import mgrs
import math

class Geolocate:
    
    def __init__(self,path):
        if path == None:
            self.gi = pygeoip.GeoIP('GeoIPCity.dat',pygeoip.MEMORY_CACHE)
        else:
            self.gi = pygeoip.GeoIP(path)
    
        self.R = 6371.00 #earth radius in km
        
    def getCountry(self,addr):
        lc = self.getLocation(addr)
        if lc:
            return self.getLocation(addr)['country_code']
        else:
            return ""

    def getLocation(self,addr):
        return self.gi.record_by_addr(addr)
    
    def getLatLong(self,addr):
        loc = self.getLocation(addr)
        if not loc: return None           
        lon = loc['longitude']
        lat = loc['latitude']
        
        return {'lat':lat,'long':lon}

    def getMGRSVal(self,lat,lon):
        m = mgrs.MGRS()
        c = m.toMGRS(lat,lon)
        ind = 1
        for i in range(1,len(c)):
            if c[i].isalpha():
                ind = i
                break
                
        v1 = int(c[:ind])*(ord(c[ind:ind+1])+ord(c[ind+1:ind+2]))
        v2 = int(c[ind+3:])

        return (v1*v2,c)

    def getUTM(self,ll):
        return utmLL.LLtoUTM(23-1,ll['latitude'],ll['longitude']) 
        
    def calcSphericDistance(self,lat1,lat2,lon1,lon2):
        '''
        Calculate the Distance between two locations using the Spherical distance method
        @param latitude of location 1
        @param latitude of location 2
        @param longitude of location 1
        @param longitude of location 2
        @return the distance between the two locations         
        '''
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
        lon1 = math.radians(lon1)
        lon2 = math.radians(lon2)
        
        d = math.acos(math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2) * math.cos(lon2-lon1)) * self.R
        return d
        
    def calcHaverDistance(self,lat1,lat2,lon1,lon2):
        '''
        Calculate the Distance between two locations using the Haver method
        @param latitude of location 1
        @param latitude of location 2
        @param longitude of location 1
        @param longitude of location 2
        @return the distance between the two locations         
        '''
        dLat = math.radians(lat2-lat1)
        dLon = math.radians(lon2-lon1)

        a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = self.R * c
        return d 
    
    def calculateGeary(self,matrix,values,meanv,N):
        '''
        Calculate the Geary's C for a collection of points
        @param matrix of weights (distance between points)
        @param values assigned to each point
        @param longitude of location 1
        @param longitude of location 2
        @return the distance between the two locations         
        '''
    
        vx1 =vx2=vx3= 0
        W = 0

        for i,x1 in enumerate(values):
            for j,x2 in enumerate(values):
                vx1 += matrix[i][j]*((x1-x2)*(x1-x2))
                W += matrix[i][j]
            vx3 += (x1-meanv)*(x1-meanv)
        vx2 = 2*W
        
        if vx3 ==0 or vx2==0:
            Coef = 0
        else:        
            Coef = ((N-1)*vx1)/(vx2*vx3)
        
        return Coef

    def calculateMorans(self,matrix,values,mean,N):
        '''
        Calculate the Moran's I for a collection of points
        @param matrix of weights (distance between points)
        @param values assigned to each point
        @param longitude of location 1
        @param longitude of location 2
        @return the distance between the two locations         
        '''
        #print matrix,values,mean,N
        v1=v2=v3 = 0
        for i,x1 in enumerate(values):
            for j,x2 in enumerate(values):
              v1 += matrix[i][j]*(x1-mean)*(x2-mean)  
              v2 += matrix[i][j]
            v3 += (x1-mean)*(x1-mean)

        if v2 == 0 or v3 ==0: 
            Index = 0
        else:        
            Index = (N*v1)/(v2*v3)

        return Index

    def calcValues(self,ips):
        '''
        Calculates the Moran's and Geary's values for a supplied list of IP addresses
        @param ips to check
        '''
        meantz = 0 #mean value for timezone
        meantu = 0 #mean value for UTM
        meanmg = 0 #mean value for MGRS

        fmt = '%z' #timezone format
        N = len(ips)
        locations = []
        timezones = []
        utms = []
        mgrss = []

        for i in ips:
            location = self.getLocation(i) #get the location from ip
            if location: #Location exists in MaxMind
                locations.append('%s:%s'%(location['latitude'],location['longitude']))

                u = utmLL.LLtoUTM(23-1,location['latitude'],location['longitude'])
                
                uv = int(u[0][:2])*ord(u[0][2:])
                meantu += uv
                
                tt = location['time_zone'] #get the timezone
                if tt == '' or tt== None: #timezone not available, set to GMT as default
                    tt='GMT' 
                tz = timezone(tt)
                locd = tz.localize(datetime(2012,01,01,0,0,0))
                d = int(locd.strftime(fmt)) #convert timezone to numeric value
                if d < 0 : 
                    d *= -1 #make positive
                d*=100 #assign value (Timezone x 100)
                meantz += d #update mean

                mgr = self.getMGRSVal(location['latitude'],location['longitude'])
                mgrss.append(mgr[0])
                meanmg += mgr[0]

                timezones.append(d)
                utms.append(uv) 
                

        meantz = meantz/N
        meantu = meantu/N
        meanmg = meanmg/N

        if len(timezones) == 0 or len(utms)==0 or len(mgrss) ==0 :
            print "Error! Unable to retrieve location data"
            return
        #create matrix filled with 0        
        matrix = [[0 for i in range(N)] for j in range(N)]
       
        #fill the matrix with the distances between each node
        for i,l in enumerate(locations):
            loc = l.split(':')
            numN = 0
            for j,l2 in enumerate(locations):
                d = 0
                if l is not l2 and l != l2:
                    loc2 = l2.split(':')
                    d = self.calcSphericDistance(float(loc[0]),float(loc[1]),float(loc2[0]),float(loc2[1]))
                
                if d > 100.0:
                    numN += 1 #increase number of neighbours that are within 1000km    
                if d == 0: 
                    matrix[i][j] = 0
                else: 
                    matrix[i][j] = 1/d


        mit = self.calculateMorans(matrix,timezones,meantz,N)
        miu = self.calculateMorans(matrix,utms,meantu,N)
        mim = self.calculateMorans(matrix,mgrss,meanmg,N)

        print "----  Moran's Index ----"
        print "Timezones: Score (%s) Classified (%s)"%(mit,"\033[91mFast-Flux\033[0m" if mit != 0 else "\033[92mClean\033[0m")
        print "UTM: Score (%s) Classified (%s)"%(miu,"\033[91mFast-Flux\033[0m" if miu != 0 else "\033[92mClean\033[0m")
        print "MGRS: Score (%s) Classified (%s)"%(mim,"\033[91mFast-Flux\033[0m" if mim != 0 else "\033[92mClean\033[0m")
        print "Combined: Score (%s)"%(mit*miu*mim)                    

        gct=self.calculateGeary(matrix,timezones,meantz,N)
        gcu=self.calculateGeary(matrix,utms,meantu,N)
        gcm=self.calculateGeary(matrix,mgrss,meanmg,N)

        print "----  Geary's Coefficient ----"
        print "Timezones: Score (%s) Classified (%s)"%(gct,"\033[91mFast-Flux\033[0m" if gct != 0 else "\033[92mClean\033[0m")
        print "UTM: Score (%s) Classified (%s)"%(gcu,"\033[91mFast-Flux\033[0m" if gcu != 0 else "\033[92mClean\033[0m")
        print "MGRS: Score (%s) Classified (%s)"%(gcm,"\033[91mFast-Flux\033[0m" if gcm != 0 else "\033[92mClean\033[0m")
        print "Combined: Score(%s)"%(gct*gcu*gcm)