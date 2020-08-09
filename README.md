[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)  
[![GitHub license](https://img.shields.io/github/license/supermalang/rapidpro-normalizer)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)
[![GitHub tag](https://img.shields.io/github/tag/supermalang/rapidpro-normalizer)](https://GitHub.com/supermalang/PBI_ImproveReportAppeal/tags/)



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
$ git clone https://github.com/supermalang/rapidpro-normalizer.git
```

Navigate to the directory and install the requirements
```bash
$ cd rapidpro-normalizer
$ pip install -r requirements.txt
``` 

# Configuration
## Create the .env file
Create the `.env` file from the `sample.env` file:
```bash
$ cp sample.env .env
```

Now open the `.env` file and configure it by putting the good values for `RAPIDPRO_TOKEN, DB_HOST, DB_NAME, DB_USER and DB_PASSWORD`
![.env file code](/docs/img/dotenv_code.svg)

*If you do not have a RapidPro token please contact your Technical Focal Point.*  

To configure RapidPro Normalizer, open the config.yml file and 

## Update the config file
Open the `config.yml` file and update the content.  
1. Define the file export settings. The `path` must in the directory of the utility
2. Enable or disable the export to database
3. Give the field group to use to fetch columns that need to be exported. Here `Contact_fields` is the field group, but you can customize. Make sure it does not contain spaces, numbers or special characters. The field group will be refered in the command line as `fieldgroup`.  
4. Give your fields. The RapidPro field hierarchy from the API Response must be conserved. Top level fields are `name, urns, blocked, created_on, modified_on, uuid, fields`. Sub fields are under `fields`. Sub fields can change depending on your RapidPro instance.


> You don't need to put all fields. Just give fields you want to be exported in the dataset.


![config.yml file code](/docs/img/config_file.svg)

