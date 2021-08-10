# Job Postings Analysis

This is our capstone project from the Master program in Applied Data Science at University of Michigan. With graduation approaching, we are interested in learning more about **the current job market for data science in different domains**. 

For this project, we collected over **18,000 job postings** that are all data science related by scraping popular job websites (ex. Glassdoor, Indeed, Cybercoders, etc.).  Fortunately, we were able to extract industries/domains information for some companies using a companies dataset and merge it with the job positings dataset.

For **data modeling**, it can be divided in two parts:

1. For job postings data with domains information (labeled dataset), we trained supervised machine learing model that is able to predict the domain of a given job desciption. 
2. For the full job postings dataset, we clustered the job postings based on job descriptions using unsupervised learning models. By doing this, we hope to uncover the domain information from each cluster. The main assumption we have is that job postings in the same cluster will likely to be in the same domain.  

To present the result in a meaningful way, we built a **dashboard that allow students or job seekers to filter jobs by domain**. Our dashboard will also include additional filtering by job location and allow people to compare the required skillsets across domains. 

## Getting Started

### Dependencies

* Data manipulation/modeling: 
    * [python(3.7.4)](https://www.python.org/downloads/release/python-374/)
    * [pandas(0.25.1)](https://pandas.pydata.org/pandas-docs/version/0.25.1/install.html)
    * [nltk(3.5)](https://pypi.org/project/nltk/3.5/)
    * [numpy(1.19.5)](https://pypi.org/project/numpy/1.19.5/)
    * [tqdm](https://pypi.org/project/tqdm/)
    * [scikit-learn(0.22.2.post1)](https://pypi.org/project/scikit-learn/0.22.2.post1/)
* Visualization: 
    * [matplotlib](https://pypi.org/project/matplotlib/)
    * [seaborn(0.11.1)](https://pypi.org/project/seaborn/)
    * [pyldavis(2.1.2)](https://pyldavis.readthedocs.io/en/latest/readme.html)
* Database connection:
    * [pymysql(1.0.2)](https://pypi.org/project/PyMySQL/)

### Installing

* The libraries listed above include links to the documentations and can be installed using pip. 
* Example of installing a pymysql package in jupyter notebook:
```
!pip install pymysql
```

### Executing program

* To run the notebooks in the *model_notebooks* folder, you will need to do the following: 
    1. Update the *config.json* file with the database connection information
    2. Download the [Common Crawl (42B tokens, 1.9M vocab, uncased, 300d vectors, 1.75 GB download)](https://nlp.stanford.edu/projects/glove/) - pretrained words embeddings used in *model_training_LDA_NMF* notebook. After you download the file, you will need to update the "file_path" inside *model_training_LDA_NMF* notebook:
        ```
        file_path = 'location you saved the embedding file'
        ```

## Authors

* Ai Zhong
    * email: aizhong@umich.edu

* Rachel Wyatt 
    * email: wyattra@umich.edu

* Laiya Lubben
    * email: llubben@umich.edu
