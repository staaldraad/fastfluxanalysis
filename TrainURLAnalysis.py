#!/usr/bin/python
import sys
import pickle

"""
Simple script to generate frequencies distributions of characters and bigrams based on a dataset.
Author: Etienne Stalmans (etienne@sensepost.com)
Version: 1.0 (2013)
"""

class trainer:
    def __init__(self):
        if len(sys.argv)<4:
            print "Please supply an input file and a training size"
            print "Example: ./TrainURLAnalysis domains.txt 10000 output.dgt"
            sys.exit(1)

        inputset = sys.argv[1]
        self.train_size = int(sys.argv[2])
        self.outset = sys.argv[3]
        print "---- Training ----"
        self.initVars()
        self.prepopulate()
        self.train(inputset)

    def initVars(self):
        self.char_counts = {}
        self.bigram_counts = {}
        self.frequencies={}
        self.frequencies_bi={}
        self.uni_prob=[]
        self.bi_prob=[]
        self.b_count = 0
        self.c_count = 0
        self.vowels = 0
        self.consts = 0

    def prepopulate(self):

        for i in range(ord('a'),ord('z')+1):
            self.char_counts[chr(i)] = 0

        for i in range(10):
            self.char_counts["%i"%i] = 0
        
        self.char_counts["-"] = 0
        
        for i in range(ord('a'),ord('z')+1):
            ch = "%c-"%(i)
            self.bigram_counts[ch] = 0
            ch = "-%c"%(i)
            self.bigram_counts[ch] = 0
            
            for j in range(ord('a'),ord('z')+1):
                ch = "%c%c"%(i,j)
                self.bigram_counts[ch] = 0
                ch = "%c%c"%(j,i)
                self.bigram_counts[ch] = 0
                
                
            for k in range(10):
                ch = "%c%i"%(i,k)
                self.bigram_counts[ch] = 0
                ch = "%i%c"%(k,i)
                self.bigram_counts[ch] = 0
                
        for i in range(10):
            ch = "%i-"%(i)
            self.bigram_counts[ch] = 0
            ch = "-%i"%(i)
            self.bigram_counts[ch] = 0
            for j in range(10):
                ch = "%i%i"%(i,j)
                self.bigram_counts[ch] = 0
                ch = "%i%i"%(j,i)
                self.bigram_counts[ch] = 0


    def parse_url(self,url):
        
        i = url.find('http://')
        
        if i==0:
            i = 7
        else:
            if url.find('https://') == 0:
               i = 8
            else:
               i = 0
        
        e = url.find('/',i) #find end of domain
        short = url[i:e]    #trim excess
        
        domains = short.split('.')
        self.get_char_counts(domains[0])
        self.get_bigram_counts(domains[0])

    def get_char_counts(self,value):
     value = value.lower()
     if value != 'www' and len(value)>=3: #don't process www (too common)
        for c in value:
            if c in self.char_counts:
               self.char_counts[c] += 1             
            else:
               self.char_counts[c] = 1
                
            if c in ['a','e','i','o','u']:
               self.vowels += 1
            else:
               self.consts += 1    
        self.c_count += len(value)            
     

    def get_bigram_counts(self,value):
        value = value.lower()
        if value != 'www' and len(value)>=3: #don't process www (too common)
            for c in range(len(value)):
                if c != len(value)-1:
                    st = value[c:c+2]
                    if st in self.bigram_counts:
                        self.bigram_counts[st] += 1                               
                    else:
                        self.bigram_counts[st] = 1
                    self.b_count +=  1 

    def train(self,inputset):
        
        f = open(inputset,'r')

        for i in range(self.train_size):
            s = f.readline()
            self.parse_url(s)

        f.close()    
        sample_space = 1.0/self.c_count
        
        for k,v in sorted(self.char_counts.iteritems()):
            self.uni_prob.append(v*sample_space) #work out the probability
            self.frequencies[k] = v*sample_space
        
        sample_space_b = 1.0/self.b_count
        
        for k,v in sorted(self.bigram_counts.iteritems()):
             self.bi_prob.append(v*sample_space_b) #work out the probability
             self.frequencies_bi[k]=v*sample_space_b

        
        print 'Total chars: %i Sample Space: %f'%(self.c_count,sample_space)
        print 'Total bigrams: %i Sample Space: %f'%(self.b_count,sample_space_b)
        print 'Stats: vowels: %i consts: %i ratio: %f'%(self.vowels,self.consts,self.vowels*1.0/self.consts)
        self.save()

    def save(self):
        """
        Remember, remember, pickle isn't secure... pew pewpew 
        """
        f_out = open(self.outset,'w')
        pickle.dump(self.frequencies,f_out)
        pickle.dump(self.frequencies_bi,f_out)
        f_out.close()

if __name__ == "__main__":
    trainer = trainer()
