# ANIPIN

### Problem introduction

This repository stores the Tensorflow model for predicting TV/Movie show ratings extracted from Recommendation-Engine-Data-Extractor repository.
The label of the data is the movie rating and the features of the data are divided into user features and item features.
The following are the features in each user and item.

#### User features

1. Genre: Feature contains number of shows of a specific genre that the user has watched.
2. Characters: Feature contains normalized 100 columns of embedding for number of characters who were present in the shows that the user watched. Since there were more than 36,000 characters, PCA technique was used to reduce dimension size to 100.
3. Staffs: Feature also contains normalized 50 columns of embedding for number of staffs who filmed the shows that the user watched.
4. Studios: Feature also contains normalized 10 columns of embedding for number of studios that produced the shows that the user watched.
5. Times: Feautre includes the number of certain time periods that certain TV shows were in out of the ones that the user watched.
6. User: Feature contains specific user features such as how many shows or hours were spent on watching TV shows.

#### Item features

1. Genre: One-hot-encoded columns containing the genre of the item
2. Characters: 100 columns of embedding containing characters who were present in the TV show. (PCA technique applied)
3. Staffs: 50 columns of embedding containing staffs who directed the TV show. (PCA technique applied)
4. Studios: 10 columns of embedding containing studios that produced the TV show. (PCA technique applied)
5. Time: One-hot-encoded column containing which time period the item was filmed in. (PCA technique applied)
6. Topic: 50 column of embedding extracted from LDA techique on topic modelling based on the synopsis text of the item.

Given these features, the goal of the recommendation engine is to accurately predict the movie's rating based on both item and user features.
**'./trainer'** directory contains **'model.py'** and **'task.py'** files which contains the main contents of the model and configurations
for running on Google Cloud ML for training purposes. Note that **'config.yaml'** file contains the server configuration (e.g. # of GPUs to use for training)
for training job.

The model implements Wide & Deep model described in this research paper: [Wide and Deep model](https://arxiv.org/abs/1606.07792)
However, unlike the article AdamOptimizer was used instead of AdaGradOptimzer on the deep part for customization and the model is still under 
hyperparameter tuning and training process. Currently, the tested model only gives rating between 7~8 or 8~9 out of 10.0 scale indicating
it still has to achieve much higher accuracy.

![](https://1.bp.blogspot.com/-Dw1mB9am1l8/V3MgtOzp3uI/AAAAAAAABGs/mP-3nZQCjWwdk6qCa5WraSpK8A7rSPj3ACLcB/s1600/image04.png
)
