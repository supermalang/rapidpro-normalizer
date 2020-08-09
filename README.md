[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)  
[![GitHub license](https://img.shields.io/github/license/supermalang/PBI_ImproveReportAppeal)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)
[![GitHub tag](https://img.shields.io/github/tag/supermalang/PBI_ImproveReportAppeal)](https://GitHub.com/supermalang/PBI_ImproveReportAppeal/tags/)



RapidPro Normalizer
==============================

RapidPro Normalizer is a command line utility to flatten RapidPro API Responses in order to export them

# Features
- Interactive command line interface
- Easy Yaml configuration
- Export dataset to file and database
- Works on Mac, Linux and (maybe) Windows

# Installation
## The easy way
The easiest way to install this utility is to clone it from GitHub:
```bash
git clone https://github.com/supermalang/rapidpro-normalizer.git
```

Navigate to the directory and install the requirements
```bash
cd rapidpro-normalizer
pip install -r requirements.txt
``` 

# Configuration
## Configure the .env file
Create the `.env` file from the `sample.env` file:
```bash
cp sample.env .env
```

Now open the `.env` file and configure it.
![.env file code](/docs/img/dotenv_code.svg)


To configure RapidPro Normalizer, open the config.yml file and 
