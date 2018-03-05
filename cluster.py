import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import DBSCAN
from sklearn import datasets
import os
import datetime
import math

# Input the directory of the point cloud data here
# Tested on txt-files with X Y Z coordinates
directory = "./input.txt"
filelist = []
n=1
center = np.zeros(shape=(0,3))
center_static = np.zeros(shape=(0,3))
previouscenter = np.zeros(shape=(0,3))
previouspoints0 = np.zeros(shape=(0,3))
previouspoints1 = np.zeros(shape=(0,3))
previouspoints2 = np.zeros(shape=(0,3))
previouspoints3 = np.zeros(shape=(0,3))
velocity = np.zeros(shape=(0,3))
velocity1 = np.zeros(shape=(0,3))
previousvelocity = np.zeros(shape=(0,3))

for root, dirs, filenames in os.walk(directory):
    for f in sorted(filenames):
        filelist.append(f)

# Takes one file at a time from the chosen directory
for file in filelist:
    cluster_length= np.array([])
    starttime = datetime.datetime.now()
    file=open(directory+file,"r")
    X = np.zeros(shape=(0,3))
    Y = np.zeros(shape=(0,3))
    test = np.zeros(shape=(0,3))
    for line in file:
        s1 = line[0:].split(':')
        s2 = s1[0].split(' ')
        for idx,value in enumerate(s2):
            s2[idx] = float(value)
        s2 = np.delete(s2,3,0)
        test=np.concatenate((test,[s2]))
        comparison0 = np.isclose(previouspoints0, s2, atol=0.01).any(axis=1)
        comparison1 = np.isclose(previouspoints1, s2, atol=0.01).any(axis=1)
        comparison2 = np.isclose(previouspoints2, s2, atol=0.01).any(axis=1)
        comparison3 = np.isclose(previouspoints3, s2, atol=0.01).any(axis=1)
        
        if ("True  True" in str(comparison0) and "True  True" in str(comparison1) and \
            "True  True" in str(comparison2) and "True  True" in str(comparison3)):
            Y=np.concatenate((Y,[s2]))
        else:
            X=np.concatenate((X,[s2]))
    print("Frame number: " + str(n))
    print("Points: " + str(len(test)) + " - " + str(len(X)) + "\n")

    # Set up the figures and add in the points from the file
    fig = plt.figure('plot', figsize=(10, 10))
    ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=None, azim=None)

    # Change the parameters of DBSCAN here to fit the environment
    # Close quarters such as the calibration room has higher minimum samples and eps (radius between points)
    # More parameters are available if needed and can be found at http://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html
    estimators = DBSCAN(eps=5, min_samples=1, algorithm='ball_tree').fit(X)
    labels = estimators.labels_
    p1 = ax.scatter(X[:, 0], X[:, 1], X[:, 2],
            c=labels.astype(np.float), edgecolor='k') 

    try:
        estimators_static = DBSCAN(eps=3, min_samples=1, algorithm='ball_tree').fit(Y)
        labels_static = estimators_static.labels_
        p2 = ax.scatter(Y[:, 0], Y[:, 1], Y[:, 2],
            c=labels_static.astype(np.float), edgecolor='r')
    except ValueError:
        pass
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    print("Clusters: " + str(n_clusters_) + "\n")
    clusters = [X[labels == i] for i in range(n_clusters_)]
    outliers = X[labels == -1]
    for i,med in enumerate(clusters):
        cluster_count = len(med)
        cluster_length = np.append(cluster_length, cluster_count)
        #print(cluster_length)
        maxx = np.amax(clusters[i],axis=0)
        minx = np.amin(clusters[i],axis=0)
        centerp0 = (minx[0]+maxx[0])/2
        centerp1 = (minx[1]+maxx[1])/2
        centerp2 = (minx[2]+maxx[2])/2
        centerp = np.array([centerp0,centerp1,centerp2])
        center = np.concatenate((center,[centerp]))
        ax.scatter(centerp[0],centerp[1],centerp[2], c='r', s=100+(len(clusters[i])*3), edgecolor='k')

        # This part checks n-1 clusters to get the movement vectors for clusters in n
        for j in previouscenter:
            similarfar = np.isclose(j,centerp,atol=2.3)
            if ("True  True  True" in str(similarfar)):
                velocity = np.array([(centerp[0]-j[0]), (centerp[1]-j[1]),(centerp[2]-j[2])])
                velocity1 = np.concatenate((velocity1,[velocity]))
                
                ax.quiver3D(centerp[0],centerp[1],centerp[2], \
                            ((centerp[0]-j[0])-previousvelocity[0]),((centerp[1]-j[1])-previousvelocity[1]), \
                            ((centerp[2]-j[2])-previousvelocity[2]),length=6,arrow_length_ratio=0.4,color='r')
                break
                
        # Uncomment these two lines if you want to see the corners for each cluster
        #ax.scatter(minx[0],minx[1],minx[2], c='r', s=80, edgecolor='k', marker='^')
        #ax.scatter(maxx[0],maxx[1],maxx[2], c='r', s=80, edgecolor='k', marker='v')


    previousvelocity = (velocity1.mean(0))
    previouscenter = center

    previouspoints3 = previouspoints2
    previouspoints2 = previouspoints1
    previouspoints1 = previouspoints0
    previouspoints0 = X
    previouspoints0 = np.concatenate((previouspoints0,Y))
    #adds both regular points and static points
    try:
        print(previouspoints0[5])
        print(previouspoints1[5])
        print(previouspoints2[5])
        print(previouspoints3[5])
    except IndexError:
        print("Fixing previous points")

    center_static = np.zeros(shape=(0,3))
    center = np.zeros(shape=(0,3))
    velocity1 = np.zeros(shape=(0,3))

    # MAGIC PARAMETERS
    # if (n%8 == 1):
    #     print("RECALIBRATION")
    #     cluster_median = np.median(cluster_length)
    #     cluster_mean = np.mean(cluster_length)
    #     eps = 3000 / len(test)
    #     print(eps)
    #     print(cluster_median)
    #     if (cluster_median > 8):
    #         min_samples += 12
    #     else:
    #         if (min_samples > 1):
    #             min_samples -= 2
    # print(min_samples)


    ax.set_title('Number of clusters: ' + str(n_clusters_))
    ax.scatter(0,0,0,s=180,c='k', edgecolor='r', marker='v')
    ax.plot([0, 45], [0,50],zs=[0,0], color='r', ls='dashed')
    ax.plot([0, 45], [0,-50],zs=[0,0], color='r', ls='dashed')
    ax.view_init(90,180)
    plt.xlim(0,150)
    plt.ylim(-50,50)
    # Add the output directory and name of the figures you want to save
    plt.savefig("./figure"+str(n)+'.png', dpi=100)
    #plt.show()
    n+=1
    plt.clf()
    endtime = datetime.datetime.now() - starttime
    print("\n""Runtime: "+str(endtime)[5:]+" seconds")
    print ("--------------")
