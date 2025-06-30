# ETL Pipeline for Data Gatheting of Baldor's Industrial Machinery products


#### 📘 Overview

This project covers the entire data pipeline, from collection to storage, using an ETL process implemented in Python. The data collection was performed using frameworks and libraries such as BeautifulSoup, Selenium, and Requests. More details about the dependencies and tools used can be found in the requirements.txt file.


#### 🎯 Objectives

Automate the data gathering of technical especifications of Baldor's products.

Transform and clean the collected data.

Load into organized .json files.

Cover all previous objectives, while keeping the pipeline modular, organized, and robust.

Focus on Data Quality as a priority.


#### 🗂️ Project structure
```
web-scraping-challenge/
│
├── src/
│   ├── main.py                  # main file responsible for running the ETL pipeline
│   ├── global_vars.py           # declaration of global variables 
│   ├── multi_thread_module.py   # Multi Thread function for Selenium 
│   ├── utility.py               # utility functions such as data transformation and loading
│   └── web_scraper.py           # Data gathering functions 
├── .gitignore                   # Ignored files and folders ignored by git 
└── README.md                    # Project documentation
```
