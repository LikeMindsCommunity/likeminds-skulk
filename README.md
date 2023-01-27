
# Getting Started

These instructions will guide you through the process of setting up the project on your local machine for development and testing purposes.

## Prerequisites

-   Python 3.7.15	 
-   Postgres
-   Redis
-   RabbitMQ
-   Elasticsearch

## Installation

1. Make sure you have corrrect Python version installed on your machine. You can check your Python version by running the following command:
```
python --version
``` 
	
2.  Clone the repository to your local machine.

3. Setup a virtual environment in the cloned repository directory using the following command:
	```
	python -m venv env
	```
4. Activate the virtual environment by running the following command:
	```
	source env/bin/activate` 
	```
5.  Change directory to 'likeminds_payments' using command -
	```
	cd likeminds_payments
	``` 

6.  Install dependencies by running the following command:
	```
	pip install -r requirements 
	```
7.  Make sure you have all of the prerequisites installed and setup on your machine, including Postgres, Redis, RabbitMQ, and Elasticsearch.
    
8.  Create an .env file and place it under directory - 
```
init/settings/
```
    
9.  Create a new Postgres database and update the DB credentials in the .env file.
    
10.  Create a folder named <i>logs</i> under likeminds_payments directory & create a file named <i>subscription.log</i> in it.
```
	mkdir logs
	touch logs/subscription.log
```
12.  Apply database migrations:
	```
	python manage.py makemigrations
	python manage.py migrate
	``` 
13.  Run the Django server:
```
python manage.py runserver 
```
14. Your application should now be running on [http://localhost:8000](http://localhost:8000/).