from fastdtw import fastdtw
from scipy.spatial.distance import euclidean, cosine
from time import perf_counter

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
    
    print("\nCalculating distance...")
    for x in range(len(values)):    
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