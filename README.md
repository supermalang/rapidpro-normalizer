[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)  
[![GitHub license](https://img.shields.io/github/license/supermalang/rapidpro-normalizer)](https://github.com/supermalang/rapidpro-normalizer/LICENSE)
[![GitHub tag](https://img.shields.io/github/tag/supermalang/rapidpro-normalizer)](https://GitHub.com/supermalang/PBI_ImproveReportAppeal/tags/)



RapidPro Normalizer
==============================

RapidPro Normalizer is a command line utility to flatten records of RapidPro API Responses in order to export them as files or database records.

# Features
- Interactive command line interface
- Easy Yaml configuration
- Export dataset to file and database
- Works on Linux and Windows (may be on Mac as well)

# Installation
## Prerequisites
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Python3](https://www.python.org/downloads/)
- [Pip3](https://www.educative.io/edpresso/installing-pip3-in-ubuntu)

## The easy way
The easiest way to install this utility is to clone it from GitHub:
```bash
$ git clone https://github.com/supermalang/rapidpro-normalizer.git
```

Navigate to the directory and install the python requirements
```bash
$ cd rapidpro-normalizer
$ pip3 install -r requirements.txt
``` 

# Configuration
## Create the .env file
Create the `.env` file from the `sample.env` file:
```bash
$ cp sample.env .env
```

Now open the `.env` file and configure it by putting the good values for `RAPIDPRO_TOKEN, DB_HOST, DB_NAME, DB_USER and DB_PASSWORD`
![.env file code](/docs/img/dotenv_code.svg)


- 🆘 *If you do not have a RapidPro token please contact your Technical Focal Point.*  
- 🆗 *If you do not export to database you can ignore the database credentials*


## Update the config file
Create the `config.yml` file and update the content.  
1. Create the config file:
```bash
$ cp sample.config.yml config.yml
```

2. Define the file export settings. The `path` must in the directory of the utility
3. Enable or disable the export to database
4. Give the field group to use to fetch columns that need to be exported. Here `covid_edu_poll` is the field group, but you can customize. Make sure it does not contain spaces, numbers or special characters. The field group will be refered in the command line as `fieldgroup`.  
5. Give your fields. The RapidPro field hierarchy from the API Response must be conserved.  
First you can use API clients like [Postman](https://www.postman.com/) to send a request and look into the response to see what the fields hierarchy looks like. You will need to consider only fields that are in the `results` property.


> You don't need to put all fields. Just give fields you want to be exported in the dataset.  

> You can add many field groups in your config file but only one `fielgroup` can be used at at time in the command line.


![config.yml file code](/docs/img/config_file.png)

## Customize the config file requests types
> *This part is optional*  

You can customize the values of the requests types `getcontacts, getruns and getmessages` directly in the `config.yml` file to add requests parameters as necessary.

Example: If you are only interested in runs that belong to a given flow you can customize the request type as following:

```yml
# Types of api requests you can use
# You can customize the requests by adding parameters that comply with the RapidPro API
rapidpro_api_settings:
    - request_types:
        - getruns: "https://api.rapidpro.io/api/v2/runs.json?flow=f5901b62-ba76-4003-9c62-72fdacc1b7b7"

```


## Update the database
> *You can ignore this part if you do not export to database*

⚠️ *Make sure your `databaseuser` has at least the `ALTER` privilege on the database.*

Update the database to use `utf8mb4` as the default character set.

```sql
ALTER SCHEMA `databasename`  DEFAULT CHARACTER SET utf8mb4 ;
```
Change `databasename` by the name of your database.



# Usage
#### Command line
The syntax to use the RapidPro Normalizer is:
```bash
$ python3 src/data/make.py [OPTIONS]
```

> ⚠️ *Depending on your environment you might need to use `python` (with version 3) instead of `python3`*

You can use the following options:
- `requesttype`: type of the RapidPro request. The `requesttype` needs to be defined in the config file
- `fieldgroup`: Group of fields to export. The `fieldgroup` needs to be defined in the config file.
- `datasetname`: name of the dataset to export.

**Interactive execution**  
![CLI Execution 1](/docs/img/cli_execution_1.svg)


**Inline execution**
```bash
$ python3 src/data/make.py --requesttype getcontacts --fieldgroup contact_fields --datasetname mycontacts
```

# Schedule automatic execution
> *This part is optional*  

You can schedule the automatic execution of the utility by creating a cron task on a Linux machine or using the [Task scheduler](https://www.windowscentral.com/how-create-automated-task-using-task-scheduler-windows-10) on Windows. Follow these steps, if you are using Linux:

1. Display and copy the command to be executed by the cron task  
⚠️ *Make sure you are still in the rapidpro-normalization directory*

Run the following to copy the command to give to the cron task. You will need to update the parameters accordingly.

```bash
$ echo "python3 $(pwd)/src/data/make.py --requesttype getcontacts --fieldgroup contact_fields --datasetname mycontacts"
```

You will have a result like:
![Command To Schedule](/docs/img/CommandToSchedule.png)


2. Edit the `crontab` file
> *The `crontab` file contains instructions for the cron daemon in the following simplified manner: "**run this command on this date at this time**".*

```bash
$ crontab -e
```

Add at the end of the file the command you have copied from the previous step in this way and save and close the file:
```
0 1 * * * python3 /home/user/path/to/rapidpro-mormalizer/src/data/make.py --requesttype getcontacts --fieldgroup contact_fields --datasetname mycontacts
```
This gives instruction to the cron daemon to run the command `python3 /home/user/path/to/rapidpro-mormalizer/src/data/make.py --requesttype getcontacts --fieldgroup contact_fields --datasetname mycontacts` every day at 1:00 AM. 