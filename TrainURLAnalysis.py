#!/usr/bin/python
import sys

class trainer:
    def __init__(self):
        if len(sys.argv)<3:
            print "Please supply an input file and a training size"
            print "Example: ./TrainURLAnalysis benigndomains.txt 10000"
            sys.exit(1)

        inputset = sys.argv[1]
        self.train_size = sys.argv[2]
        print "---- Training ----"
        self.initVars()
        self.prepopulate()
        self.train(inputset)

    def initVars(self):
        self.char_counts = {}

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

    def train(self,inputset):
        
        self.prepopulate()
        b_count = 0
        c_count = 0
        vowels = 0
        consts = 0
        
        f = open(inputset,'r')

        for i in range(self.train_size):
            s = f.readline()
            self.parse_url(s)

        f.close()    
        sample_space = 1.0/c_count
        
        for k,v in sorted(self.char_counts.iteritems()):
            benign_uni_prob.append(v*sample_space) #work out the probability
            frequencies[k] = v*sample_space
        
        sample_space = 1.0/b_count
        
        for k,v in sorted(self.bigram_counts.iteritems()):
             benign_bi_prob.append(v*sample_space) #work out the probability
             frequencies_bi[k]=v*sample_space

        
        print 'Total chars: %i Sample Space: %f'%(c_count,sample_space)
        print 'Total bigrams: %i Sample Space: %f'%(b_count,sample_space)
        print 'Stats: vowels: %i consts: %i ratio: %f'%(vowels,consts,vowels*1.0/consts)
        
if __name__ == "__main__":
    trainer = trainer()
