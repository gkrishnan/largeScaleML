Readme
-------

Showing	how	to run the code:

Move to this folder as your current directory

Now, run the following command on terminal:

a.) For running integrated_model.py

Best Values to run this programs are:
number of latent factors = 3
learning rate = 0.000001
regularization parameter = 0.05

python -W ignore integrated_model.py <filename for set of training ratings> <filename for set of testing ratings> <number of latent factors> <learning rate> <regularization parameter>

For eg:
python -W ignore integrated_model.py ratings.csv toBeRated.csv 3 0.00001 0.05

When the program has finished running, it will automatically create a file named "result.csv" which will contain the desired output.


b.) For running integrated_model_CV.py

Best Values to run this programs are:
number of latent factors = 3
learning rate = 0.000001
regularization parameter = 0.05

python -W ignore integrated_model_CV.py <filename for set of training ratings> <number of latent factors> <learning rate> <regularization parameter> <number of folds>

For eg:
python -W ignore integrated_model_CV.py ratings.csv 3 0.00001 0.05 10

When the program has finished running, the average RMSE will be printed on the console itself.