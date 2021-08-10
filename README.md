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
    * python-----------3.7.4
    * pandas-----------0.25.1
    * nltk-------------3.5
    * numpy------------1.19.5
    * regex------------2020.11.13
    * tqdm-------------4.55.1
    * scikit-learn-----0.22.2.post1
* Visualization: 
    * matplotlib-------3.1.2
    * seaborn----------0.11.1
    * pyldavis---------2.1.2
* Database connection:
    * pymysql----------1.0.2

### Installing

* The libraries listed above can be install by "pip" command. 
* Example of installing a pymysql package in jupyter notebook:
```
!pip install pymysql
```

### Executing program

* How to run the program
* Step-by-step bullets
```
code blocks for commands
```

## Authors

* Ai Zhong
    * email: aizhong@umich.edu

* Rachel Wyatt 
    * contact info 

* Laiya Lubben
    * email: llubben@umich.edu
