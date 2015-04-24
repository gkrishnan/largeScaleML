Showing	how	to run the code:

1. Open a terminal
2. Download the zipped folder and upzip it.
3. Move to the location where u have unzipped the folder
4. Change Directory to the folder containing the code.

Now, run the following command on terminal:

a.) For running Recommender.py

python Recommender.py <filename for set of training ratings> <filename for set of testing ratings> <number of latent factors> <learning rate> <regularization parameter>

For eg:
python Recommender.py ratings.csv toBeRated.csv 5 0.001 0.1

When the program has finished running, it will automatically create a file named "result.csv" which will contain the desired output.


b.) For running Recommender_CV.py

python Recommender.py <filename for set of training ratings> <number of latent factors> <learning rate> <regularization parameter> <number of folds>

For eg:
python Recommender CV.py ratings.csv 5 0.001 0.1 10

When the program has finished running, the average RMSE will be printed on the console itself.