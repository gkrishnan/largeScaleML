import numpy as np
import numpy.matlib
import sys
import math

def recommend(rating_file, to_be_rated_file, r, mu, lam):
    f = open(rating_file,"r")
    N = 1000
    M = 2069
    R = np.zeros((N,M))
    Nu = np.zeros((N,M))
    global_rating = 0.0
    count = 0
    for row in f:
        re = row.split(',')
        R[int(re[0])-1][int(re[1])-1] = int(re[2])
        Nu[int(re[0])-1][int(re[1])-1] = 1
        global_rating += int(re[2])
        count += 1
    f.close()

    global_rating = global_rating/count
    b_u = (np.nan_to_num(R.sum(1)/(R != 0).sum(1))).reshape(N,1) - global_rating*np.ones((N,1))
    b_m = (np.nan_to_num(R.sum(0)/(R != 0).sum(0))).reshape(M,1) - global_rating*np.ones((M,1))

    b_u[np.isnan(b_u)] = 0
    b_u[np.isinf(b_u)] = 0
    b_m[np.isnan(b_m)] = 0
    b_m[np.isinf(b_m)] = 0

    steps = 1500
    limit = 10^-5

    gamma1 = mu
    gamma2 = mu
    gamma3 = mu
    lambda6 = lam
    lambda7 = lam
    lambda8 = lam

    U = np.random.rand(N,r)
    V = np.random.rand(M,r)
    W = np.random.rand(M,M)

    #Y = np.random.rand(M,r)
    #C = np.random.rand(M,M)
    #C = (C + C.T) / 2

    baseline = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_m.T,N,1)
    matrix = np.dot(U,V.T)
    #matrix = np.dot((U + numpy.matlib.repmat((((np.dot(Nu,Y)).sum(0)).reshape(r,1)).T,N,1) / math.sqrt(np.count_nonzero(Nu > 0)) ),V.T)
    neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0))
    #neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0)) + (np.dot(C,Nu.T)).T  / math.sqrt(np.count_nonzero(Nu > 0))

    pred_rating = baseline + matrix + neighbourhood

    error1 = np.sum(np.square(np.multiply((R - pred_rating),(R > 0))))

    #print error1

    for step in range(steps):
        print "Iteration Number: " + str(step)

        er = np.multiply((R - pred_rating),(R > 0))

        new_b_u = b_u + 2*gamma1*(((er).sum(axis=1)).reshape(N,1) - lambda6*np.multiply(((R>0).sum(1)).reshape(N,1),b_u))
        new_b_m = b_m + 2*gamma1*(((er).sum(axis=0)).reshape(M,1) - lambda6*np.multiply(((R>0).sum(0)).reshape(M,1),b_m))
        new_U = (1-2*gamma2*lambda7)*U + 2*gamma2*np.dot((er),V)
        new_V = (1-2*gamma2*lambda7)*V + 2*gamma2*np.dot((er).T,U)
        #new_V = (1-2*gamma2*lambda7)*V + 2*gamma2*np.dot((er).T, U + numpy.matlib.repmat((((np.dot(Nu,Y)).sum(0)).reshape(r,1)).T,N,1) / math.sqrt(np.count_nonzero(Nu > 0)) )
        new_W = W + 2*gamma3*(np.dot((er).T,np.multiply((R - baseline),(R>0))) / math.sqrt(np.count_nonzero(R > 0)) - lambda8*W)

        #new_Y = Y + 2*gamma2*( np.dot(numpy.matlib.repmat((er.sum(0)).reshape(M,1),1,M),V) - lambda7*Y)
        #new_C = C + 2*gamma3*( numpy.matlib.repmat((er.sum(0)).reshape(M,1),1,M) - lambda8*C)

        b_u = new_b_u
        b_m = new_b_m
        V = new_V
        U = new_U
        W = new_W

        #Y = new_Y
        #C = new_C

        baseline = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_m.T,N,1)
        matrix = np.dot(U,V.T)
        neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0))
        #matrix = np.dot((U + numpy.matlib.repmat((((np.dot(Nu,Y)).sum(0)).reshape(r,1)).T,N,1) / math.sqrt(np.count_nonzero(Nu > 0)) ),V.T)
        #neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0)) + (np.dot(C,Nu.T)).T  / math.sqrt(np.count_nonzero(Nu > 0))


        pred_rating = baseline + neighbourhood + matrix

        error2 = np.sum(np.square(np.multiply((R - pred_rating),(R > 0))))

        #print error2

        '''if (error2 > error1):
            print "Error Increased. Cannot coverge to the global minima. Need to stop early."
            break'''

        if error2 < limit:
            print "Error became less than the assigned limit"
            break

    #print "out of loop"

    baseline = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_m.T,N,1)
    matrix = np.dot(U,V.T)
    neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0))

    #matrix = np.dot((U + numpy.matlib.repmat((((np.dot(Nu,Y)).sum(0)).reshape(r,1)).T,N,1) / math.sqrt(np.count_nonzero(Nu > 0)) ),V.T)
    #neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0)) + (np.dot(C,Nu.T)).T  / math.sqrt(np.count_nonzero(Nu > 0))

    pred_rating = baseline + matrix + neighbourhood

    #raw_input()

    f = open(to_be_rated_file,"r")
    fr = open("result.csv", "w")
    for row in f:
        r = row.split(',')  
        rat = pred_rating[int(r[0])-1][int(r[1])-1]
        print rat
        fr.write(str(rat) + "\n")
    f.close()
    fr.close()

#recommend("ratings.csv", "toBeRated.csv")
if len(sys.argv) != 6:
    print "Not Enough Arguments"
    print "Format: integrated_model.py <filename for set of training ratings> <filename for set of testing ratings> <number of latent factors> <learning rate> <regularization parameter>"
    print "For eg: python -W ignore integrated_model.py ratings.csv toBeRated.csv 3 0.00001 0.05"
    exit()

recommend(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
