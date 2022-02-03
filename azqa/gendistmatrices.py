from fastdtw import fastdtw
from scipy.spatial.distance import euclidean, cosine
from time import perf_counter
import sys

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    
    sys.stdout.write('[%s] %s%s ...%s\r'.format(x) % (bar, percents, '%', suffix))
    sys.stdout.flush()
    
    
def getLabelsIPMappings(connections):
    mapping = {}
    meta = {}
    labels = []
    ipmapping = []
    fno = 0;
    for i, v in connections.items():
        
        name = i[0] + "->" + i[1]
        if(len(i) == 3):
            name = i[0].split('.')[0] + "|" + i[1] + "->" + i[2]
            
        mapping[name] = fno
        fno += 1
        meta[name] = v
    keys = list(meta.keys())   
    inv_mapping = {v:k for k,v in mapping.items()} 
    for x in range(len(connections.values())):
        labels.append(mapping[keys[x]])
        ipmapping.append((mapping[keys[x]], inv_mapping[mapping[keys[x]]])) 
    return labels, inv_mapping, mapping, ipmapping, keys

def getNormalizedDistance (distm):
    ndistm = []
    minx = min(min(distm))
    maxx = max(max(distm))
    for x in range(len(distm)):
        ndistm.append([])
        for y in range(len(distm)):
            normed = (distm[x][y] - minx) / (maxx-minx)
            ndistm[x].append(normed)
    return ndistm
 
#fill matrix with -1           
def initializeMatrix (values):
    distm = [-1] * len(values)
    distm = [[-1] * len(values) for i in distm]
    return distm
    
def getEuclideanDistanceMatrix(connections, thresh, col):    
    start = perf_counter()    
    values = connections.values()
    distm = initializeMatrix(values)
    total = len(values)
    print("\nCalculating distance...")
    for x in range(total):    
        
        for y in range(x+1):

            i = [pos[col] for pos in list(values)[x]][:thresh]
            j = [pos[col] for pos in list(values)[y]][:thresh]
            if len(i) == 0 or len(j) == 0:
                continue

            if x == y:
                distm[x][y] = 0.0
            else:
                dist, _ = fastdtw(i, j, dist=euclidean)
                distm[x][y] = dist
                distm[y][x] = dist
        print('\r{}'.format(x),"/",len(values), end='\r')
        
    ndistm = getNormalizedDistance(distm)    
    print("OK. (", round(perf_counter()-start), "s )\n")            
    return ndistm


def getCosineDistanceMatrix(connections, thresh, col): 
    
    start = perf_counter()        
    values = connections.values()
    distm = initializeMatrix(values)
        
    print("\nCalculating distance...")        

    ngrams = []
    for x in range(len(values)):
        profile = dict()
        dat = [pos[col] for pos in list(values)[x]][:thresh]
        li = zip(dat, dat[1:], dat[2:])
        for b in li:
            if b not in profile.keys():
                profile[b] = 0            
            profile[b] += 1                    
        ngrams.append(profile)
    
    assert len(ngrams) == len(values)
    for x in range(len(ngrams)):
        for y in range(x+1):
            if x==y:
                distm[x][y] = 0.0
            else:                                
                i = ngrams[x]
                j = ngrams[y]
                ngram_all = list(set(i.keys()) | set(j.keys()))
                i_vec = [(i[item] if item in i.keys() else 0) for item in ngram_all]
                j_vec = [(j[item] if item in j.keys() else 0) for item in ngram_all]
                dist = cosine(i_vec, j_vec)
                distm[x][y] = dist
                distm[y][x] = dist                

    ndistm = []
    for a in range(len(distm)):
        ndistm.append([])
        for b in range(len(distm)):
            ndistm[a].append(distm[a][b])
            
    print("OK. (", round(perf_counter()-start), "s )\n")            
    return ndistm

def getDistanceMatrix(distSize, distDelta, distSport, distDport):
    distm = []
    for x in range(len(distSize)):
        distm.append([])
        for y in range(len(distSize)):
            distm[x].append((distSize[x][y]+distDelta[x][y]+distSport[x][y]+distDport[x][y])/4.0)
    return distm