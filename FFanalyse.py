#!/usr/bin/python

import sys,string
import getopt
import dns.resolver
import Geolocate
import pygeoip
import argparse

class ffanalyse():
    def main(self,domain,verbose):
        self.defaults= { 'protocol':'udp', 'port':53, 'opcode':'query',
                'qtype':'A', 'rd':1, 'timing':1, 'timeout': 3,
                'server_rotate': 0,'server':[] }
        self.verbose = verbose
        self.domain = domain
        self.gl = Geolocate.Geolocate('GeoIPCity.dat')
        self.geoIP = pygeoip.GeoIP('GeoIPASNum.dat')
        self.resolve_nameservers()
        self.get_dns(domain)
        
        
    def resolve_nameservers(self):
        #check if windows system
        if sys.platform in ('win32', 'nt'):
            import win32dns
            self.defaults['server']=win32dns.RegistryResolve()
        else:
           self.ParseResolvConf()

    #get nameservers for UNIX type systems
    def ParseResolvConf(self,resolv_path="/etc/resolv.conf"):
        "parses the /etc/resolv.conf file and sets defaults for name servers"
        lines=open(resolv_path).readlines()
        for line in lines:
            line = string.strip(line)
            if not line or line[0]==';' or line[0]=='#':
                continue
            fields=string.split(line)
            if len(fields) < 2: 
                continue
            if fields[0]=='domain' and len(fields) > 1:
                self.defaults['domain']=fields[1]
            if fields[0]=='search':
                pass
            if fields[0]=='options':
                pass
            if fields[0]=='sortlist':
                pass
            if fields[0]=='nameserver':
                self.defaults['server'].append(fields[1])

    def get_asn(self,ip):
        """
        Method to return the country and ASN of an IP address
        @param ip to get data for
        @return [asn record, country]
        """
        asnrec = self.geoIP.org_by_addr(ip)
        country = self.gl.getCountry(ip)
        if self.verbose:
            print asnrec,country
        if asnrec == None:
            return ['Unknown','Unknown']
        else:
            return [asnrec.split(' ')[0],country]

    def get_dns(self,qname):
        
        rdtype=dns.rdatatype.A
        rdclass=dns.rdataclass.IN
        request = dns.message.make_query(qname, rdtype, rdclass)
        response = dns.query.udp(request,self.defaults['server'][0])
        
        rcode = dns.rcode.from_flags(response.flags,response.ednsflags)
        
        if rcode == 3:
            #print '%s NXDomain, domain not found'%qname
            return
        if rcode == 2:
            #print '%s SERVFail, server failed trying to find domain'%qname
            return
        if rcode != 0:
            #print '%s Invalid response from dns server'%qname
            return
        if self.verbose:
            print 'QUERY RESPONSE:\n%s'%str(response)
        
        self.analyse(response)

    def analyse(self,response):
            
        qname = str(response.question).split()[1] #Query Name

        network_ranges = [] #A record responses
        nameserver_net_ranges = []
        a_count = 0
        ns_count = 0
        diff_count = 0
        ns_diff_count = 0
        a_ttl = 86400
        ns_ttl = 86400
        ar_count = -1
        country_count = 0
        asn_count = 0
        countries = []
        nameservers = []
        asns = []
        answers = []
        ttl_score = 0

        #check answers
        if response.rcode == 'NONE':
            print "We have a NONE record..."
            return False

        if len(response.authority)>0:
            rdata = response.authority[0]
            ans = str(rdata).split('\n')
            for a in ans:
                nameservers.append(a.split()[4])
                
        if len(response.answer)==0:
            print 'Empty Response section'
            return


        for a in response.answer[0]: #parse each line in the answer
            if '.' in str(a): #weak check that it is an IP address returned
                answers.append(str(a))

        a_ttl = response.answer[0].ttl
        a_count = len(answers)

        if a_count > 0:            
            for ip in answers:
                ip = str(ip)
                st = ip[:ip.rfind('.')]
                asnd = self.get_asn(st)
                if asnd: 
                    asn,country = asnd
                    if country not in countries:
                        countries.append(country)
                    if asn not in asns:
                        asns.append(asn)
                if st not in network_ranges:
                    network_ranges.append(st)

        
        diff_count = len(network_ranges) #number of IP ranges we have
        country_count= len(countries)
        asn_count = len(asns)
        if a_ttl <= 300:
            ttl_score = 1

        print "Qname{0:20}|TTL{0:5}|A Records{0:2}|Ranges{0:2}|ASNs{0:2}|Countries{0:2}|Nameservers{0:2}|".format('')
        print "{:25}|{:8}|{:11}|{:8}|{:6}|{:11}|{:13}|".format(qname,a_ttl,a_count,diff_count,asn_count,country_count,ns_count)
        #calculate score according to Thorsten
        #===================================================
        t_score = (1.32*a_count+18.54*asn_count+0*ns_count+ttl_score*5)-50
        #===================================================

        #calculate Jaroslaw/Patrycja score
        #===================================================
        jp_score = a_count+ns_count+diff_count*1.5+asn_count*1.5+ttl_score+country_count*2
        #===================================================
        print "\n---- Fast-Flux Scores ----"
        print "Modified Thorsten/Holz: Score (%i) Classified (%s)"%(t_score,"Fast-Flux" if t_score>0 else "Clean")
        print "Modified Jaroslaw/Patrycja: Score (%i) Classified (%s)"%(jp_score,"Fast-Flux" if jp_score>=18 else "Clean")
        print "\n---- Geolocation ----"

        self.gl.calcValues(answers)

def setOpts(argv):                         
    #defaults
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain',dest='domain',action='store',required=True,
        help="A Domain to analyse")
    parser.add_argument('-v', dest='verbose', action='store_true',default=False,
        help="Verbose output")
    arg = parser.parse_args()
    
    return (arg.__dict__['domain'],arg.__dict__['verbose'])

if __name__ == "__main__":
    opts = setOpts(sys.argv[1:])
    ff = ffanalyse()
    ff.main(opts[0],opts[1])