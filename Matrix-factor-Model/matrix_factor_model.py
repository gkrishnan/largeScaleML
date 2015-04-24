import numpy as np
import sys

def recommend(rating_file, to_be_rated_file, r, mu, lam):
    f = open(rating_file,"r")
    N = 1000
    M = 2069
    R = np.zeros((N,M))
    for row in f:
        re = row.split(',')
        R[int(re[0])-1][int(re[1])-1] = int(re[2])
    f.close()
    
    steps = 500
    limit = 10^-5

    U = np.random.rand(N,r)
    V = np.random.rand(M,r) 

    error1 = np.sum(np.square(np.multiply((np.dot(U,V.T) - R),(R > 0)))) 

    for step in xrange(steps):
        print "Iteration Number: " + str(step)      
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
