import numpy as np
from sklearn.cross_validation import KFold
from numpy import linalg as LA
import numpy.matlib
import math
import sys

def recommend(rating_file, r, mu, lam, D):
    #print "Recommender System - Cross Validation: \nr = " + str(r) + "\nmu = " + str(mu) + "\nlam = " + str(lam) + "\nNumber of Folds = " + str(D) + "\n" 
    #print "If Number of Folds given is 10, then Complete Program will take about 10-15 mins to finish. So be Patient.... :) \n"
    f = open(rating_file,"r")
    data = []
    for row in f:
        re = row.split(',')
        e = [int(re[0]), int(re[1]), int(re[2])]
        data.append(e)
    f.close()

    k_fold = KFold(n=len(data), n_folds=D)

    N = 1000
    M = 2069
    steps = 1000
    limit = 10^-5

    gamma1 = mu
    gamma2 = mu
    gamma3 = mu
    lambda6 = lam
    lambda7 = lam
    lambda8 = lam

    rmse_l = []

    counter = 1

    for train_indices, test_indices in k_fold:
        train = [data[i] for i in train_indices]
        test = [data[i] for i in test_indices]

        train_matrix = np.zeros((N,M))
        test_matrix = np.zeros((N,M))

        Nu = np.zeros((N,M))
        global_rating = 0.0
        count = 0

        for e in train:
            i = e[0] - 1
            j = e[1] - 1
            rat = e[2]
            train_matrix[i][j] = rat            
            Nu[i][j] = 1
            global_rating += rat
            count += 1

        for e in test:
            i = e[0] - 1
            j = e[1] - 1
            rat = e[2]
            test_matrix[i][j] = rat

        global_rating = global_rating/count
        b_u = (np.nan_to_num(train_matrix.sum(1)/(train_matrix != 0).sum(1))).reshape(N,1) - global_rating*np.ones((N,1))
        b_m = (np.nan_to_num(train_matrix.sum(0)/(train_matrix != 0).sum(0))).reshape(M,1) - global_rating*np.ones((M,1))

        b_u[np.isnan(b_u)] = 0
        b_u[np.isinf(b_u)] = 0
        b_m[np.isnan(b_m)] = 0
        b_m[np.isinf(b_m)] = 0

        U = np.random.rand(N,r)
        V = np.random.rand(M,r)
        W = np.random.rand(M,M)

        baseline = global_rating*np.ones((N,M)) + np.matlib.repmat(b_u,1,M) + np.matlib.repmat(b_m.T,N,1)
        matrix = np.dot(U,V.T)
        neighbourhood = np.dot(np.multiply((train_matrix - baseline),(train_matrix>0)), W.T) / math.sqrt(np.count_nonzero(train_matrix > 0))

        pred_rating = baseline + matrix + neighbourhood

        error1 = np.sum(np.square(np.multiply((train_matrix - pred_rating),(train_matrix > 0))))

        #print error1

        for step in xrange(steps):
            #print "Iteration step: "+ str(step)
            er = np.multiply((train_matrix - pred_rating),(train_matrix > 0))

            new_b_u = b_u + 2*gamma1*(((er).sum(axis=1)).reshape(N,1) - lambda6*np.multiply(((train_matrix>0).sum(1)).reshape(N,1),b_u))
            new_b_m = b_m + 2*gamma1*(((er).sum(axis=0)).reshape(M,1) - lambda6*np.multiply(((train_matrix>0).sum(0)).reshape(M,1),b_m))
            new_U = (1-2*gamma2*lambda7)*U + 2*gamma2*np.dot((er),V)
            new_V = (1-2*gamma2*lambda7)*V + 2*gamma2*np.dot((er).T,U)
            new_W = W + 2*gamma3*(np.dot((er).T,np.multiply((train_matrix - baseline),(train_matrix>0))) / math.sqrt(np.count_nonzero(train_matrix > 0)) - lambda8*W)

            b_u = new_b_u
            b_m = new_b_m
            V = new_V
            U = new_U
            W = new_W

            baseline = global_rating*np.ones((N,M)) + np.matlib.repmat(b_u,1,M) + np.matlib.repmat(b_m.T,N,1)
            matrix = np.dot(U,V.T)
            neighbourhood = np.dot(np.multiply((train_matrix - baseline),(train_matrix>0)), W.T) / math.sqrt(np.count_nonzero(train_matrix > 0))

            pred_rating = baseline + neighbourhood + matrix

            error2 = np.sum(np.square(np.multiply((train_matrix - pred_rating),(train_matrix > 0))))

            #print error2

            if (error2 > error1):
                #print "Error Increased. Cannot coverge to the global minima. Need to stop early."
                break

            if error2 < limit:
                #print "Error became less than the assigned limit"
                break

        testRMSE = LA.norm(np.multiply((test_matrix - pred_rating), (test_matrix > 0))) / math.sqrt(np.count_nonzero(test_matrix > 0))

        rmse_l.append(testRMSE)
        print "Cross-Validation Step " + str(counter) + ":\t" + str(testRMSE)
        counter += 1

    rmse_avg = sum(rmse_l) / float(len(rmse_l))
    print "\nAverage RMSE: " + str(rmse_avg)
    #return rmse_avg

rank = [1,3,5,50,100,150,200,350,300]
learn = [0.00001, 0.0001, 0.0005, 0.001]
reg = [0.005, 0.05, 0.1, 0.5]

fo = open("results_CV.txt", "w")
for i in rank:
    for j in learn:
        for l in reg:
            fo.write(str(i) + "\t" + str(j) + "\t" + str(l) + "\t")
            print str(i) + "\t" + str(j) + "\t" + str(l)
            rmse = recommend("ratings.csv",i,j,l,10)
            fo.write(str(rmse) + "\n")

fo.close()

'''if len(sys.argv) != 6:
    print "Not Enough Arguments"
    exit()

recommend(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]))'''


