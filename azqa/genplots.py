import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import os, errno
from config import config

THRESHOLD = config.CONV_THRESHOLD
TIMESTAMP = config.EXP_TS
PLOT_LOC = config.TEST_RESULTS_LOC
HEATMAP_LOC = os.path.join(PLOT_LOC, 'heatmaps')

def genPlot(size, title="Plot"):    
    fig = plt.figure(figsize=(10.0,9.0))
    ax = fig.add_subplot(111)   
    ax.set_title(title)
    plt.plot(size, marker ='o', ms = 2)   

def genConvPlots(conversations):
    location = os.path.join(PLOT_LOC)
    if not os.path.exists(location):
        os.makedirs(location)
    i = 1
    for key, value in conversations.items():
        title = str(i) + "|" + key[0] +"->"+ key[1]
        genPlot(value, title)  
        plt.savefig(os.path.join(location,key[0]+key[1]+"_"+str(i)+".jpg"))
        i = i + 1
    
def genXYPlots(conversations, col): 
    keys = list(conversations.keys())
    for key, values in conversations.items():
        fig = plt.figure(figsize=(10.0,9.0))
        ax = fig.add_subplot(111)
        ax.set_title(key)                         
        plt.plot([pos[col] for pos in values][:THRESHOLD], 'b')
        plt.plot([pos[col] for pos in values][:THRESHOLD], 'b.')
        ax.xaxis.set_major_locator(ticker.MultipleLocator(4))
        location = os.path.join(PLOT_LOC, TIMESTAMP, 'C'+str(col))
        if not os.path.exists(location):
            os.makedirs(location)           
        plt.savefig(os.path.join(location,str(keys.index(key))))
    
def genScatterPlot(projection):
    plt.scatter(*projection.T)         
    plt.savefig(os.path.join(PLOT_LOC,TIMESTAMP+"-plot-tsne-result"))

def genSingleLinkageTreePlot(model):
    model.single_linkage_tree_.plot(cmap='viridis', colorbar=True)    
    plt.show()

def genCondensedTreePlot(model):
    model.condensed_tree_.plot(
        select_clusters=True, selection_palette=sns.color_palette())
    plt.show()

def genScatterPlotWithModel(model, distm, projection, labels, inv_mapping):
    cols = ['royalblue', 'red', 'darksalmon', 'sienna', 'mediumpurple', 'palevioletred', 'plum', 'darkgreen', 'lightseagreen',
            'mediumvioletred', 'gold', 'navy', 'sandybrown', 'darkorchid', 'olivedrab', 'rosybrown', 'maroon', 'deepskyblue', 'silver']
    pal = sns.color_palette(cols)
    extra_cols = len(set(model.labels_)) - 18
    pal_extra = sns.color_palette('Paired', extra_cols)
    pal.extend(pal_extra)
    col = [pal[x] for x in model.labels_]
    assert len(model.labels_) == len(distm)
    mem_col = [sns.desaturate(x, p) for x, p in zip(col, model.probabilities_)]
    plt.scatter(*projection.T, s=50, linewidth=0, c=mem_col, alpha=0.2)
    classes = ['Alexa', 'Hue', 'Somfy', 'malware'] #need to check; leave it for time being
    for i, txt in enumerate(model.labels_):
        realind = labels[i]
        name = inv_mapping[realind]
        thiscol = None
        thislab = None
        for cdx, cc in enumerate(classes):
            if cc in name:
                thiscol = col[cdx]
                thislab = cc
                break
        if txt == -1:
            continue
        plt.scatter(projection.T[0][i], projection.T[1][i], color=col[i], alpha=0.6)
        plt.annotate(thislab, (projection.T[0][i], projection.T[1][i]), color=thiscol, alpha=0.2)        
    plt.savefig(os.path.join(PLOT_LOC,TIMESTAMP+"plot-clustering-result"))

def readClusterfile(clusterfile):
    lines = []
    clusterinfo = {}
    print("\nReading ",clusterfile,"...")
    if not os.path.exists(clusterfile):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), clusterfile)    
    file = open(clusterfile)
    lines = file.readlines()[1:]
    for line in lines:
        li = line.split(",")   # clusnum, connnum, prob, srcip, dstip
        srcip = li[5]
        dstip = li[6][:-1]
        has = int(li[1])
        name = str('%12s->%12s' % (srcip, dstip))
        if li[0] not in clusterinfo.keys():
            clusterinfo[li[0]] = []
        clusterinfo[li[0]].append((has, name))    
    file.close()
    return clusterinfo #{'clusnum': [(connum, 'srcip->dstip'), ... conversations], ... clusters}
        
def genHeatMap(conversations, mapping, keys, clusterfile):
    values = list(conversations.values())
    
    print("\nWriting temporal heatmaps...")
    if not os.path.exists(HEATMAP_LOC):
        os.mkdir(HEATMAP_LOC)
       
    actlabels = []
    for a in range(len(values)):
        actlabels.append(mapping[keys[a]])
    clusterinfo = readClusterfile(clusterfile)    
                
    sns.set(font_scale=0.9)
    matplotlib.rcParams.update({'font.size': 10})
    for names, sname, q in [("Packet sizes", "bytes", 1), ("Interval", "gaps", 0), ("Source Port", "sport", 2), ("Dest. Port", "dport", 3)]:
        for clusnum, cluster in clusterinfo.items():
                                    
            labels = [x[1] for x in cluster] #scrip->dstip                        
            acha = [actlabels.index(int(x[0])) for x in cluster]            
            blah = [values[a] for a in acha]            
            dataf = []
            
            for b in blah:
                dataf.append([x[q] for x in b][:THRESHOLD])
            df = pd.DataFrame(dataf, index=labels)            
            
            g = sns.clustermap(df, xticklabels=False, col_cluster=False)
            ind = g.dendrogram_row.reordered_ind
            fig = plt.figure(figsize=(10.0, 9.0))
            plt.suptitle("Exp: " + TIMESTAMP + " | Cluster: " +clusnum + " | Feature: " + names)
            labelsnew = []
            lol = []
            
            for it in ind:
                labelsnew.append(labels[it])            
                lol.append(cluster[[x[1]
                           for x in cluster].index(labels[it])][0])

            acha = [actlabels.index(int(x)) for x in lol]
            blah = [values[a] for a in acha]
            dataf = []

            for b in blah:
                dataf.append([x[q] for x in b][:THRESHOLD])                
            df = pd.DataFrame(dataf, index=labelsnew)
            
            g = sns.heatmap(df, xticklabels=False)            
            plt.setp(g.get_yticklabels(), rotation=0)
            plt.subplots_adjust(top=0.92, bottom=0.02,
                                left=0.25, right=1, hspace=0.94)
            plt.savefig(os.path.join(HEATMAP_LOC,TIMESTAMP+"-heatmap-"+sname+"-c"+clusnum))
