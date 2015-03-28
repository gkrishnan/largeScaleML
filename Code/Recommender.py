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
    
    steps = 500
    limit = 10^-5

    gamma1 = 0.007
    gamma2 = 0.007
    gamma3 = 0.001
    lambda6 = 0.005
    lambda7 = 0.015
    lambda8 = 0.015

    b_u = np.random.rand(N,1)
    b_m = np.random.rand(M,1)
    U = np.random.rand(N,r)
    V = np.random.rand(M,r)     
    Y = np.random.rand(N,M,N,r)
    W = np.random.rand(M,M)
    C = np.random.rand(N,M,N,M)

    baseline = global_rating*np.ones((N,M)) + numpy.matlib.repmat(b_u,1,M) + numpy.matlib.repmat(b_i.T,N,1)
    matrix = np.dot((U+((Y[Nu>0].sum(axis=0)) / math.sqrt(np.count_nonzero(Nu > 0)))),V.T)
    neighbourhood = np.dot(np.multiply((R - baseline),(R>0)), W.T) / math.sqrt(np.count_nonzero(R > 0)) + C[Nu>0].sum(axis=0)

    pred_rating = baseline + matrix + neighbourhood

    error1 = np.sum(np.square(np.multiply((pred_rating - R),(R > 0))))

    for step in xrange(steps):
        print "Iteration Number: " + str(step)
        er = np.multiply((pred_rating - R),(R > 0))
        new_b_u = b_u + gamma1*(er.sum(axis=1) - lambda6*b_u)  
        new_b_m = b_m + gamma1*(er.sum(axis=0) - lambda6*b_m) 

        new_V = V + gamma2*(np.dot(er.T,(U+((Y[Nu>0].sum(axis=0)) / math.sqrt(np.count_nonzero(Nu > 0))))) - lambda7*V)
        new_U = U + gamma2*(np.dot(er,V) - lambda7*U)

        new_Y = Y + gamma2*(numpy.matlib.repmat(np.dot(er, (V / math.sqrt(np.count_nonzero(Nu > 0)))),N,M,N,r)-lambda7*Y)





        new_U = (1-2*mu*lam)*U + 2*mu*np.dot((np.multiply((R - np.dot(U,V.T)),(R > 0))),V)
        new_V = (1-2*mu*lam)*V + 2*mu*np.dot((np.multiply((R - np.dot(U,V.T)),(R > 0))).T,U)
        U = new_U
        V = new_V

        error2 = np.sum(np.square(np.multiply((np.dot(U,V.T) - R),(R > 0))))

        if (error2 > error1):
            print "Error Increased. Cannot coverge to the global minima. Need to stop early."
            break

        if error2 < limit:
            print "Error became less than the assigned limit"
            break

    new_R = np.dot(U,V.T)
    f = open(to_be_rated_file,"r")
    fr = open("result.csv", "w")
    for row in f:
        r = row.split(',')  
        rat = new_R[int(r[0])-1][int(r[1])-1]
        print rat
        fr.write(str(rat) + "\n")
    f.close()
    fr.close()

#recommend("ratings.csv", "toBeRated.csv",3, 0.0001, 0.05)
if len(sys.argv) != 6:
    print "Not Enough Arguments"
    exit()

recommend(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
