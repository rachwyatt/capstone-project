# Here is a list of libraries we need to conduct the analysis:
import pandas as pd                                           
import numpy as np                                            
from tqdm.auto import tqdm                                    
import re

import matplotlib.pyplot as plt                               
import matplotlib.cm as cm

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
      
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.mixture import GaussianMixture

import nltk                                                   
from nltk.tokenize import sent_tokenize
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

def extract_relevantjobs(df, col=None):
    """
      this function is to extract jobs that are data science related

      Parameters
      ----------
      df: job postings DataFrame
      col (str): job title column name (str)

      Returns
      -------
      DataFrame
    """

    relevant_jobs = ['data analyst', 'data scientist', 'data engineer',
                'machine learning', 'business intelligence', 'data science',
                'artificial intelligence', 'bi ', 'ai ', 'ai/', 'ai,',
                'data analytics', 'mlops', 'data architect', 'nlp']
    pattern = re.compile('|'.join(relevant_jobs))
    if col==None: 
      df['job_title'] = df['job_title'].apply(lambda x:x.lower())
      filtered_df = df[df['job_title'].str.contains(pattern, regex=True)]
    else: 
      df[col] = df[col].apply(lambda x:x.lower())
      filtered_df = df[df['job_title'].str.contains(pattern, regex=True)]
        
    return filtered_df

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# SSE is the sum of the squared distance between centroid and each member of the cluster
# One way to find the optimal clusters is by finding the elbow point using the SSE plot
# As number of clusters increases (in KMeans model), SSE decreases and the "elbow point" is the point where SSE starts decreasing in linear manner
# In other words, pick the value of k, where the average distance falls suddenly
def generate_SSE_plot(data, max_k, model, RANDOM_SEED):
    """
      this function is to generate a SSE plot to find the optimal number of cluster either using MiniBatchKMeans or KMeans

      Parameters
      ----------
      data: numerical matrix (tfidf/tf transformation of the text data)
      max_k (int): the maximum number of clusters to draw for the SSE plot
      model (str): 'MiniBatchMeans' or 'KMeans' 
      RANDOM_SEED (int): set model to a random seed for reproducibility

    """
    sse = []
    clusters = range(2, max_k+1, 2)
    if model=='MiniBatchKMeans':
      for k in tqdm(clusters):
          sse.append(MiniBatchKMeans(n_clusters=k, init_size=800, batch_size=1300, random_state=RANDOM_SEED).fit(data).inertia_)
    elif model=='KMeans':
      for k in tqdm(clusters):
          sse.append(KMeans(n_clusters=k, random_state=RANDOM_SEED, n_jobs=-1).fit(data).inertia_)

    f, ax = plt.subplots(1, 1)
    ax.plot(clusters, sse, marker='o')
    ax.set_xlabel('Number of clusters (k)')
    ax.set_xticks(clusters)
    ax.set_xticklabels(clusters)
    ax.set_ylabel('Sum of squared errors')
    ax.set_title('Clustering SSE vs. Number of Clusters')

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# The silhouette plot shows how close each point in one cluster is to points in the neighboring clusters 
# near +1 indicate that the sample is far away from the neighboring clusters
# 0 indicates that the sample is on or very close to the decision boundary between two neighboring clusters
# negative values indicate that those samples might have been assigned to the wrong cluster
def generate_avg_silhouette_plot(data, max_k, model, RANDOM_SEED):
    """
      this function is to generate silhouette plot based on average silhouette score

      Parameters
      ----------
      data: numerical matrix (tfidf/tf transformation of the text data)
      max_k (int): the maximum number of clusters to draw for the SSE plot
      model (str): 'MiniBatchMeans' or 'KMeans' or 'GMM'
      RANDOM_SEED (int): set model to a random seed for reproducibility

    """
    ss = []
    clusters = range(2, max_k+1, 2)
    for k in tqdm(clusters):
        if model == 'MiniBatchKMeans':
          pred_clusters = MiniBatchKMeans(n_clusters=k, init_size=800, batch_size=1300, random_state=RANDOM_SEED).fit_predict(data)
          ss.append(silhouette_score(data, pred_clusters))
        elif model == 'KMeans':
          pred_clusters = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_jobs=-1).fit_predict(data)
          ss.append(silhouette_score(data, pred_clusters))
        elif model == 'GMM':
          pred_clusters = GaussianMixture(n_components=k, random_state=RANDOM_SEED).fit_predict(data)
          ss.append(silhouette_score(data, pred_clusters))
        
    f, ax = plt.subplots(1, 1, figsize=(10,5))

    ax.plot(clusters, ss, marker='o')
    ax.set_xlabel('Number of clusters')
    ax.set_xticks(clusters)
    ax.set_xticklabels(clusters)
    ax.set_ylabel('Average silhouette score')
    ax.set_title('Average Silhouette Score vs. Number of Clusters')

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# the code below is from https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
def generate_silhouette_plot(data, max_k, model, RANDOM_SEED):
    """
      this function is to generate silhouette plot

      Parameters
      ----------
      data: numerical matrix (tfidf/tf transformation of the text data)
      max_k (int): the maximum number of clusters to draw 
      model (str): 'MiniBatchMeans' or 'KMeans'
      RANDOM_SEED (int): set model to a random seed for reproducibility

    """
 
    clusters = range(2, max_k+1, 2)
    for k in tqdm(clusters):
        if model == 'MiniBatchKMeans':
          pred_clusters = MiniBatchKMeans(n_clusters=k, init_size=800, batch_size=1300, random_state=RANDOM_SEED).fit_predict(data)
        elif model == 'KMeans':
          pred_clusters = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_jobs=-1).fit_predict(data)

        sample_silhouette_values = silhouette_samples(data, pred_clusters)
        silhouette_avg = silhouette_score(data, pred_clusters)
        print("For n_clusters =", k, " ,the average silhouette_score is :", silhouette_avg)
        f, ax = plt.subplots(1, 1, figsize=(10,5))

        y_lower = 10
        for i in range(k):
            
            # Aggregate the silhouette scores for samples belonging to cluster i, and sort them
            ith_cluster_silhouette_values = sample_silhouette_values[pred_clusters == i]
            ith_cluster_silhouette_values.sort()


            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.hsv(i/k)
            ax.fill_betweenx(np.arange(y_lower, y_upper),
                              0, ith_cluster_silhouette_values,
                              facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax.set_title("Silhouette plot for n_clusters = %d" %k)
        ax.set_xlabel("Silhouette coefficient values")
        ax.set_ylabel("Clusters")

        # The vertical line for average silhouette score of all the values
        ax.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax.set_yticks([])  # Clear the yaxis labels / ticks
        ax.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

def generate_tsne_pca_plot(data, pred_clusters, n_clusters, RANDOM_SEED):
    """
      this function is to generate PCA cluster plot and TSNE cluster plot of 300 random samples from the data

      Parameters
      ----------
      data: numerical matrix (tfidf/tf transformation of the text data)
      pred_clusters (list): the clusters assignment from a trained classifier
      n_clusters (int): number of clusters generated by the trained model
      RANDOM_SEED (int): set model to a random seed for reproducibility

    """

    # sample 5000 from the data and apply PCA and TSNE - this is to speed up the process 
    np.random.seed(14)
    max_items = np.random.choice(range(data.shape[0]), size=5000, replace=False) 
    pca = PCA(n_components=2, random_state=RANDOM_SEED).fit_transform(data[max_items,:].todense()) 

    # notice reduce dimensions again to fit for the TSNE
    tsne = TSNE(random_state=RANDOM_SEED).fit_transform(PCA(n_components=50, random_state=RANDOM_SEED).fit_transform(data[max_items,:].todense()))
    
    # down sample again to 300 from the transformed data so that we don't have too many points on each plots
    idx = np.random.choice(range(pca.shape[0]), size=300, replace=False)
    label_subset = pred_clusters[max_items]
    label_color = [cm.hsv(i/n_clusters) for i in label_subset[idx]] 
    
    f, ax = plt.subplots(1, 2, figsize=(14, 6))
    
    ax[0].scatter(pca[idx, 0], pca[idx, 1], c=label_color)
    ax[0].set_title('PCA Clustering Plot from 300 Random Samples')
    
    ax[1].scatter(tsne[idx, 0], tsne[idx, 1], c=label_color)
    ax[1].set_title('TSNE Clustering Plot from 300 Random Samples')

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_top_keywords(data, pred_clusters, terms, n_terms):
    """
      this function is to get top n keywords for each clusters

      Parameters
      ----------
      data: numerical matrix (tfidf/tf transformation of the text data)
      pred_clusters (list): the clusters labels from a trained classifier
      terms (list): list of words/features from the tfidf/tf transformation
      n_terms (int): number of key terms 

      Returns
      -------
      Top n words for each cluster
    """
    df = pd.DataFrame(data.todense()).groupby(pred_clusters).mean()
    
    for i,r in df.iterrows():
        print('\nCluster {}'.format(i))
        print(','.join([terms[t] for t in np.argsort(r)[-n_terms:]]))

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_labels(domain_df, company_df, job_df, dropna=True):
    """
      this function is merge three dataframes to get the domain labels for the job postings

      Parameters
      ----------
      domain_df: a dataframe with a set of prelabeled domains using the "industry" column from the company_df
      company_df: a dataframe with companies' names and the industries they belong to
      job_df: a dataframe with job postings store in the database 
      dropna (bool): if true, dropna from industry column of the merged dataframe 

      Returns
      -------
      Dataframe
    """

    company_df = company_df.drop_duplicates(subset=['name'])
    company_df.rename(columns={'name':'company_name'}, inplace=True)

    company_df['company_name'] = company_df['company_name'].str.lower()
    job_df['company_name'] = job_df['company_name'].str.lower()
    
    merge_df = pd.merge(company_df[['company_name', 'industry']], job_df, how='right', on='company_name')
    if dropna: 
        merge_df = merge_df.dropna(subset=['industry'])
        print('There are', merge_df.shape[0], 'matches')

    final_df = pd.merge(merge_df, domain_df, how='left', on='industry')

    return final_df