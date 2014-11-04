import sys,os,re,string
import csv
from itertools import combinations, chain, islice
from collections import Counter

import urllib2
import numpy as np
import time

import json
import datetime
import pylab as pl

from pprint import pprint
from bs4 import BeautifulSoup as bs
sys.path.append("/Users/fbianco/randomprojs/astrotrend/word_cloud-master")

from wordcloud import make_wordcloud
from sklearn.feature_extraction.text import CountVectorizer

def most_common(lst):
    return max(set(lst), key=lst.count)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
class OrderedTuple(tuple):

    def __init__(self, init=()):
        if init:
            init = list(init)
            init.sort()
            init = tuple(init)
            self._oinit = init
            tuple.__init__(init)
        else:
            tuple.__init__(self)

    def __eq__(self, other):
        return self._oinit[0] == other._oinit[0] and self._oinit[1] == other._oinit[1]
        # return self._oinit == other._oinit

    def __hash__(self):
        return hash(self._oinit)

    def __repr__(self):
        return repr(self._oinit)

def mycounter(s):
    mydic = {}
    for w in s.split():
        print w
#        print len(re.findall(w, s))
        if len(w)<3:
            continue
        if w in mydic.keys():
            mydic[w]=mydic[w]+1
        else:
            mydic[w]=1
#        try:
#            mydic[w] = len(re.findall(w,s))
#        except:
#            print  len(re.findall(w,s))
#            pass

    print mydic
    return mydic

pl.ion()
if __name__ == '__main__':

    commonastrowords=['non','low','possible','probing','positive','negative','new','high','find','found','demonstrate','me','I','proof','prove','the','a','in','with','that','this','those','them','for', 'from','?','and','lat','long',':','.','of', 'used','using','use', 'lac','an','two','three','two','three','its','and','are','is','for']

    url="http://arxiv.org/list/astro-ph/recent"
    response=urllib2.urlopen(url)
    html = response.read()
    soup = bs(html)
    m= re.search(r'total of (...)', soup.get_text())
    totentries=int(m.group(1))
    url="http://arxiv.org/list/astro-ph/pastweek?show=%d"%totentries
    response=urllib2.urlopen(url)
    html = response.read()
    soup = bs(html)
    alltitles = soup.findAll(attrs={'class':re.compile("list-title")})
    allsubjects = soup.findAll(attrs={'class':re.compile("list-subjects")})
    mysubjects={'High Energy Physics - Phenomenology ':"HEPP", 'Instrumentation and Methods for Astrophysics ':"IMA", 'Popular Physics ':"PopP", 'History and Philosophy of Physics ':"HPP", 'Human-Computer Interaction ':"HCI", 'Fluid Dynamics ':"FD", 'Nuclear Theory ':"NT", 'General Physics ':"GP", 'Instrumentation and Detectors ':"ID", 'Computer Vision and Pattern Recognition ':"CVPR", 'General Relativity and Quantum Cosmology ':"GRQC", 'High Energy Astrophysical Phenomena ':"HEAP", 'Plasma Physics ':"PP", 'Earth and Planetary Astrophysics ':"EPA", 'High Energy Physics - Experiment ':"HEPE", 'Data Analysis, Statistics and Probability ':"DASP", 'Cosmology and Nongalactic Astrophysics ':"CNA", 'Solar and Stellar Astrophysics ':"SSA", 'Computational Physics ':"CP", 'Astrophysics of Galaxies ':"AG", 'other':'other'}
    mysubjectinv={}
    mysubjectind={}
    for i,ms in enumerate(mysubjects.iterkeys()):
        mysubjectind[mysubjects[ms]]=i
        mysubjectinv[i]=ms
    exclude = set(string.punctuation)
    print exclude
#    sys.exit()
    print exclude.add("'s")
    content=[]
    subs={}
    subs['other']=[]
    with open("weektitles.csv","w") as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for j,l in enumerate(alltitles):
#            print "here",alltitles[j].text[7:].strip().encode(encoding='UTF-8',errors='strict')  
            row=l.text[7:].strip().split(' ')
            

#            print row
            for i,w in enumerate(row):
                if w.endswith('ies'):
                    row[i]=row[i].replace('ie','y')
                row[i]=row[i].lower().rstrip('s')

                for c in exclude:
                    if c in row[i]:
                        print "replacing "+ c +" with nothing"
                        row[i]=row[i].replace(c,'')
            for w in commonastrowords:
                while w.encode(encoding='UTF-8',errors='strict')  in row:
                    print row
                    print "replacing 2 "+ w +" with nothing"
                    row.remove(w.encode(encoding='UTF-8',errors='strict'))
                    print "replaced",row

            try:
                spamwriter.writerow(row)
            except UnicodeEncodeError:
                print "UnicodeEncodeError on ",row
                continue
                
            for w in row:
                if not w in subs.keys():
                    subs[w]=[]
                try:
                    subs[w].append(mysubjects[allsubjects[j].text[10:].strip().split('(')[0].encode(encoding='UTF-8',errors='strict')])  #.text, "Astrophysics of Galaxies" in allsubjects[j]
                except KeyError:
                    subs[w].append('other')


            content.append(row)

    mywords=' '.join([inner for outer in content for inner in outer ])
    mycounts=mycounter(mywords)        
    words=[]
    counts=[]
    for k in mycounts.iterkeys():
        words.append(k)
        counts.append(mycounts[k])
    words=np.array(words)
    counts=np.array(counts)
    # throw away some words, normalize
    words = words[counts > 1]
    counts = counts[counts > 1]
    subjects={}
    for w in words:
        subjects[w]=mysubjectind[most_common(subs[w])]

    output_filename = "%s/cloud.png"%datetime.date.today()
    print output_filename
    os.system("mkdir %s"%datetime.date.today())
    counts = make_wordcloud(words, counts, output_filename)

    os.system("rm  thisweekarxiv.png ")
    os.system("ln -s %s thisweekarxiv.png "%output_filename)
    

    _t = time.time()
    wordlists={}
    i=0
    for row in content:
        i+=1
        user = row[0]
        if (i%100==0):
            sys.stdout.write('\r%s' % user)
            sys.stdout.flush()
        wordlists[user] = {}
        wordlists[user]['words']=set([s for s in row[2:] if s != ''])
        _tuples = combinations(wordlists[user]['words'],2)
        tuples = set()
        for t in _tuples:
            tuples.add(OrderedTuple(t))
        wordlists[user]['tuples'] = tuples # unique ordered tuples
        wordlists[user]['hashes'] = set([ hash(t) for t in tuples ])
        assert len(tuples) == len(wordlists[user]['hashes'])
        # print('%s, %s' % (user, len(tuples)))
    delta = time.time()-_t
    print('\n%d data collected in %dsec.' % (i, delta))

    iterators = []
    for user in wordlists.iterkeys():
        iterators.append(iter(wordlists[user]['tuples']))

    hash_dict = {}
    # { hash_value: OrderTuple, ... }
    print('Making hash_dict ...')
    _t=time.time()
    i=0
    for _tuple in chain(*iterators):
        i+=1
        hash_dict[hash(_tuple)] = _tuple
        if (i%100000 == 0):
            sys.stdout.write('\r%d' % i)
            sys.stdout.flush()
    print('\n%d hash_dict done in %dsec.' % (i, delta))
    

    iterators = []
    for user in wordlists.iterkeys():
        iterators.append(iter(wordlists[user]['hashes']))
    _stats = {}
    done = []
    i=0

    print('Counting ...')
    _t = time.time()
    for t in chain(*iterators):
        if t in done:
            continue
        i+=1
        if (i%1000 == 0):
            sys.stdout.write("\r%s" % i)
            sys.stdout.flush()
        done.append(t)
        _count = 0
        for user in wordlists.iterkeys():
            if t in wordlists[user]['hashes']:
                _count += 1
        _stats[hash(t)]=_count

    delta = time.time() - _t
    print('\nDone writing %d in %dsec.' % (i, delta))

    print('Preparing data to write ... ')
    stats = []
    error_hashes = []
    for _hash, _tuple in hash_dict.iteritems():
        try:
            _count = _stats[_hash]
        except KeyError as e:
            error_hashes.append(e)
        else:
            stats.append((_tuple, _count))
    print('error_hashes=%r' % len(error_hashes))
    allstats={}

        

    for stat in stats:
            if not stat[0][0] in allstats.keys():
                allstats[stat[0][0]]={}
            allstats[stat[0][0]][stat[0][1]]=stat[1]
            if 'star' in stat[0][0]:
                print allstats[stat[0][0]]
#                for i in range(stat[1]):

#    raw_input()
    alllist=set(sum([[stat[0][0],stat[0][1]] for stat in stats if stat[0][0] not in   commonastrowords and not is_number(stat[0][0]) and stat[0][1] not in   commonastrowords and not is_number(stat[0][1]) and len(stat[0][0])>=3 and len(stat[0][1])>=3  and stat[1]>2],[]))
    print alllist,len(alllist)
    mymatrix=np.zeros((len(alllist),len(alllist)),int)
    print mymatrix.shape
    import csv
    with open('/Users/fbianco/Downloads/d3-chord-diagrams-master/data/arxiv.csv', 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar=' ',quoting=csv.QUOTE_NONE)
        spamwriter.writerow(['word1,word2,count,field,fielddef'])
        for i,word1 in enumerate(alllist):
            for j,word2 in  enumerate(alllist):
                if word1==word2:
                    try: subjects[word1]
                    except: 
                        subjects[word1] =0

                    #              subjects[word1]  print i,j
                    mymatrix[i][j]=0
                    spamwriter.writerow( ['"%s","%s",%d,%d,"%s"'%(word1,word2,0,subjects[word1],mysubjectinv[subjects[word1]].strip().replace(' ','-'))])
#                    spamwriter.writerow( ['"%s","%s",%d,%d'%(word1,word2,0,subjects[word1])])
                else:
#                    print '"%s","%s"' %(word1,word2)
#                    try: print allstats[word1][word2]
#                    except: 
#                        print "not there"
#                        pass
                    try:  
                        mymatrix[i][j]=allstats[word1][word2]
                        spamwriter.writerow( ['"%s","%s",%d,%d,"%s'%(word1,word2,allstats[word1][word2],subjects[word1],mysubjectinv[subjects[word1]].strip().replace(' ','-'))])
                    except: 
                        mymatrix[i][j]=0
                        spamwriter.writerow( ['"%s","%s",%d,%d,"%s"'%(word1,word2,0,subjects[word1],mysubjectinv[subjects[word1]].strip().replace(' ','-'))])


#        for stat in stats:
#            if stat[0][0] not in  commonastrowords and not is_number(stat[0][0]) and stat[0][1] not in   commonastrowords and not is_number(stat[0][1]) and len(stat[0][0])>=3 and len(stat[0][1])>=3  and stat[1]>1:


#    for word1 in alllist:
#        print word1,
#    for  i,word1 in enumerate(alllist):
#        print word1,"\t\t[" ,
#        for j,word2 in enumerate(alllist):
#            print mymatrix[i][j],",",
#        print "],"

#    print('Writing data')
#    with open('stats.json', 'w') as fo:
#        fo.write(json.dumps(stats))
    print('DONE.')
