import numpy as np
import numpy.matlib
import sys
import math

def recommend(rating_file, to_be_rated_file): #, r, mu, lam):
    f = open(rating_file,"r")
    N = 1000
    M = 2069
    R = np.zeros((N,M))
    Nu = np.zeros((N,M))
    global_rating = 0.0
    count = 0
    #print "Hello"
    for row in f:
        re = row.split(',')
        R[int(re[0])-1][int(re[1])-1] = int(re[2])
        Nu[int(re[0])-1][int(re[1])-1] = 1
        global_rating += int(re[2])
        count += 1
    f.close()

    #print "File Read"

    global_rating = global_rating/count
    b_u = (np.nan_to_num(R.sum(1)/(R != 0).sum(1))).reshape(N,1) - global_rating*np.ones((N,1))
    b_m = (np.nan_to_num(R.sum(0)/(R != 0).sum(0))).reshape(M,1) - global_rating*np.ones((M,1))

    b_u[np.isnan(b_u)] = 0
    b_u[np.isinf(b_u)] = 0
    b_m[np.isnan(b_m)] = 0
    b_m[np.isinf(b_m)] = 0

    steps = 100
    limit = 10^-5

    gamma1 = 0.00001
    gamma2 = 0.00001
    gamma3 = 0.00001
    lambda6 = 0.005
    lambda7 = 0.005
    lambda8 = 0.015
    r = 300

    #print "Parameters Done"

    #b_u = np.random.rand(N,1)
    #b_m = np.random.rand(M,1)
    U = np.random.rand(N,r)
    V = np.random.rand(M,r)     
    #Y = np.random.rand(M,N,r)
    W = np.random.rand(M,M)
    #C = np.random.rand(N,M)

    #print "Parameters Done"

    baseline = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_m.T,N,1)

    #print "Baseline"
    #print b_u.shape
    #print b_m.shape

    matrix = np.dot(U,V.T)
    #matrix = np.dot((U+((Y[Nu>0].sum(axis=0)) / math.sqrt(np.count_nonzero(Nu > 0)))),V.T)

    #print "matrix"

    neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0))
    #neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0)) + C[Nu>0].sum(axis=0) / math.sqrt(np.count_nonzero(Nu > 0))

    #print "neighbourhood"

    pred_rating = baseline + neighbourhood + matrix#baseline + matrix #baseline# + matrix + neighbourhood

    error = np.sum(np.square(np.multiply((R - pred_rating),(R > 0))))

    print error

    for step in range(steps):
        print "Iteration Number: " + str(step)
        #er = np.multiply((R - baseline - np.dot(U,V.T)),(R>0))
        #er = np.multiply((R - pred_rating),(R > 0))
        #er = np.multiply((pred_rating - R),(R > 0))
        #print "er done "

        baseline = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_m.T,N,1)
        matrix = np.dot(U,V.T)
        neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0))

        er = np.multiply((R - baseline - matrix - neighbourhood),(R > 0))

        new_b_u = b_u + 2*gamma1*(((er).sum(axis=1)).reshape(N,1) - lambda6*np.multiply(((R>0).sum(1)).reshape(N,1),b_u))
        new_b_m = b_m + 2*gamma1*(((er).sum(axis=0)).reshape(M,1) - lambda6*np.multiply(((R>0).sum(0)).reshape(M,1),b_m))
        new_U = (1-2*gamma2*lambda7)*U + 2*gamma2*np.dot((er),V)
        new_V = (1-2*gamma2*lambda7)*V + 2*gamma2*np.dot((er).T,U)
        new_W = W + 2*gamma3*(np.dot((er).T,np.multiply((R - baseline),(R>0))) / math.sqrt(np.count_nonzero(R > 0)) - lambda8*W)

        b_u = new_b_u
        b_m = new_b_m
        V = new_V
        U = new_U
        W = new_W

        baseline = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_m.T,N,1)
        matrix = np.dot(U,V.T)
        neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0))

        pred_rating = baseline + neighbourhood + matrix

        error = np.sum(np.square(np.multiply((R - pred_rating),(R > 0))))

        print error


        #print b_u.shape
        #print (er.sum(axis=1)).reshape(1000,1).shape
        #print new_b_u.shape 
        #print "B_u done"
        #new_b_m = b_m + gamma1*((er - lambda6*numpy.matlib.repmat(b_m.T,N,1)).sum(axis=0).reshape(M,1))
        #print new_b_m.shape
        #print "B_m done"

        #new_V = V + gamma2*(np.dot(er.T,U) - lambda7*V)
        #new_U = U + gamma2*(np.dot(er,V) - lambda7*U)

        

        #print "V done"
        #new_V = V + gamma2*(np.dot(er.T,(U+((Y[Nu>0].sum(axis=0)) / math.sqrt(np.count_nonzero(Nu > 0))))) - lambda7*V)
        
        #print "U done"

        #new_Y = Y + gamma2*((np.dot(er, (V / math.sqrt(np.count_nonzero(Nu > 0))))).reshape(1,N,r).repeat(M,0).reshape(1,M,N,r).repeat(N,0) - lambda7*Y)
        #new_Y = Y + gamma2*(numpy.matlib.repmat(np.dot(er, (V / math.sqrt(np.count_nonzero(Nu > 0)))),N,M,1,1)-lambda7*Y)

        
        #print "W done"

        #new_C = C + gamma3*((er/math.sqrt(np.count_nonzero(Nu > 0))).reshape(1,N,M).repeat(M,0).reshape(1,M,N,M).repeat(N,0) - lambda8*C)
        #new_C = C + gamma3*(numpy.matlib.repmat(er/math.sqrt(np.count_nonzero(Nu > 0)),N,M,1,1) - lambda8*C)

        #b_u = new_b_u
        #b_m = new_b_m
        ##V = new_V
        #U = new_U
        #Y = new_Y
        #W = new_W
        #C = new_C
        #print "Para,aters Done"

        #print b_u.shape
        #print b_m.shape

        #baseline1 = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_m.T,N,1)
        #print "Baseline done"
        #matrix1 = np.dot(U,V.T)
        #print "matrix done"
        #matrix1 = np.dot((U+((Y[Nu>0].sum(axis=0)) / math.sqrt(np.count_nonzero(Nu > 0)))),V.T)
        #neighbourhood1 = np.dot(np.multiply((R - baseline1),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0))# + C[Nu>0].sum(axis=0) / math.sqrt(np.count_nonzero(Nu > 0))
        #print "neigh done"

        #pred_rating1 = baseline1 + neighbourhood1 + matrix1 #baseline1# + matrix1 + neighbourhood1

        #print "pred done"

        #error2 = np.sum(np.square(np.multiply((pred_rating1 - R),(R > 0))))

        #print error2

        #gamma1 = 0.9*gamma1
        #gamma2 = 0.9*gamma2
        #gamma3 = 0.9*gamma3

        #print "error done"

        '''if (error2 > error1):
            print "Error Increased. Cannot coverge to the global minima. Need to stop early."
            break'''

        if error < limit:
            print "Error became less than the assigned limit"
            break

    print "out of loop"

    baseline = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_m.T,N,1)
    matrix = np.dot(U,V.T)
    #new_matrix = np.dot((U+((Y[Nu>0].sum(axis=0)) / math.sqrt(np.count_nonzero(Nu > 0)))),V.T)
    neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0))# + C[Nu>0].sum(axis=0) / math.sqrt(np.count_nonzero(Nu > 0))

    pred_rating = baseline + neighbourhood + matrix #new_baseline# + new_matrix + new_neighbourhood

    raw_input()

    f = open(to_be_rated_file,"r")
    fr = open("result.csv", "w")
    for row in f:
        r = row.split(',')  
        rat = pred_rating[int(r[0])-1][int(r[1])-1]
        print rat
        fr.write(str(rat) + "\n")
    f.close()
    fr.close()

recommend("ratings.csv", "toBeRated.csv")#,3, 0.0001, 0.05)
'''if len(sys.argv) != 6:
    print "Not Enough Arguments"
    exit()

recommend(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))'''
