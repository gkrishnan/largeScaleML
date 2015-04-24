import numpy as np
from sklearn.cross_validation import KFold
from numpy import linalg as LA
import math
import sys

def recommend(rating_file, r, mu, lam, D):
    print "Recommender System - Cross Validation: \nr = " + str(r) + "\nmu = " + str(mu) + "\nlam = " + str(lam) + "\nNumber of Folds = " + str(D) + "\n" 
    print "If Number of Folds given is 10, then Complete Program will take about 10-15 mins to finish. So be Patient.... :) \n"
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
    steps = 500
    limit = 10^-5

    rmse_l = []

    counter = 1

    for train_indices, test_indices in k_fold:
        train = [data[i] for i in train_indices]
        test = [data[i] for i in test_indices]

        train_matrix = np.zeros((N,M))
        test_matrix = np.zeros((N,M))

        for e in train:
            i = e[0] - 1
            j = e[1] - 1
            rat = e[2]
            train_matrix[i][j] = rat

        for e in test:
            i = e[0] - 1
            j = e[1] - 1
            rat = e[2]
            test_matrix[i][j] = rat

        U = np.random.rand(N,r)
        V = np.random.rand(M,r)

        error1 = np.sum(np.square(np.multiply((np.dot(U,V.T) - train_matrix),(train_matrix > 0))))

        for step in xrange(steps):
            #print step
            new_U = (1-2*mu*lam)*U + 2*mu*np.dot((np.multiply((train_matrix - np.dot(U,V.T)),(train_matrix > 0))),V)
            new_V = (1-2*mu*lam)*V + 2*mu*np.dot((np.multiply((train_matrix - np.dot(U,V.T)),(train_matrix > 0))).T,U)
            U = new_U
            V = new_V

            error2 = np.sum(np.square(np.multiply((np.dot(U,V.T) - train_matrix),(train_matrix > 0))))

            if (error2 > error1) or (error2 < limit):
                break

        testRMSE = LA.norm(np.multiply((np.dot(U,V.T) - test_matrix), (test_matrix > 0))) / math.sqrt(np.count_nonzero(test_matrix > 0))

        rmse_l.append(testRMSE)
        print "Cross-Validation Step " + str(counter) + ":\t" + str(testRMSE)
        counter += 1

    rmse_avg = sum(rmse_l) / float(len(rmse_l))
    print "\nAverage RMSE: " + str(rmse_avg)
    #return rmse_avg

'''rank = [1,3,5]
learn = [0.0001, 0.0005, 0.001]
reg = [0.05, 0.1, 0.5]

fo = open("results_CV.txt", "w")
for i in rank:
    for j in learn:
        for l in reg:
            fo.write(str(i) + "\t" + str(j) + "\t" + str(l) + "\t")
            print str(i) + "\t" + str(j) + "\t" + str(l)
            rmse = recommend("ratings.csv",i,j,l,10)
            fo.write(str(rmse) + "\n")

fo.close()'''

if len(sys.argv) != 6:
    print "Not Enough Arguments"
    exit()

recommend(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]))


