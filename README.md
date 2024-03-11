# E-Commerce Data Pipeline

#### Practice Project
I wanted to learn more about Spark, Airflow, Kubernetes, Docker and APIs and used [this e-commerce data](https://www.kaggle.com/datasets/carrie1/ecommerce-data) from Kaggle

#### Chapters:  
- [Architecture](#Architechture)  
- [General Setup](#general-setup)  
   - [The vm](#the-vm)  
   - [Git](#git)  
   - [Virtual environment](#virtual-environment)
- [PostgreSQL Database & ETL with Apache Spark and Airflow](#postgresql-database-&-etl-with-apache-spark-and-airflow)
   - [Setup](#setup)
      - [Java](#java)  
      - [Apache Apark](#apache-spark)  
      - [PostgreSQL Server](#postgresql-server)  
      - [Airflow](#airflow)
      - [PySpark](#pyspark)
      - [Kaggle](#kaggle)
   - [Scripts](#scripts)
- [API](#api)
   - [Setup API](#setup-api)
   - [Scripts API](#scripts-api)

## Architecture 
![Pipeline Architecture](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/architecture.png)

## General Setup  
  
### The vm
First I tried installing Spark and Airflow on my laptop, but it died the minute I tried to start Airflow. Then I tried the free ec2 tier on AWS, but the same happened again. Now I'm trying my luck with this vm:  

Ubuntu, 4 CPUs, 16 GB RAM, 50 GB  
  
set up several ports for inbound (and outbound) traffic:  
7077 - Spark  
8080 - Spark UI  
5432 - Database  
3000 - API  
6443, 2379-2380, 10250, 10251, and 10252 - Kubernetes  
8081 - Airflow UI  
5000 - Docker 
  
### Git
created a git repo on github and cloned it onto my vm
```
git clone https://github.com/Jeahy/ecompipeline.git
```
  
### Virtual environment
created and activated a virtual environment "venv"
```
sudo apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate
```

## PostgreSQL Database & ETL with Apache Spark and Airflow

### Setup

#### Java
installed Java (for Spark)
```
sudo apt install openjdk-21-jdk
```
add path to Java
```
export JAVA_HOME=/bin/java
export PATH=$JAVA_HOME/bin:$PATH
```
activated it
```
source ~/.bashrc
```
installed the PostrgreSQL JDBC Driver
```
wget https://jdbc.postgresql.org/download/postgresql-42.7.2.jar
```

#### Apache Spark
I downloaded Apache Spark from the official website, unpacked it and saved it in /opt/spark
```
curl -O https://dlcdn.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar -xvzf spark-3.5.0-bin-hadoop3.tgz
sudo mv spark-3.5.0-bin-hadoop3 /opt/spark
```

edited the users shell profile in .bashrc
```
export SPARK_HOME=/opt/spark
export PATH=$SPARK_HOME/bin:$PATH
```
activated it
```
source ~/.bashrc
```
create spark-env.sh file
```
cp spark-env.sh.template spark-env.sh
```
added informatoin on master and worker node to the spark-env.sh file in conf directory for standalone mode:
```
# Set the master node
export SPARK_MASTER_HOST=10.11.1.81
export SPARK_MASTER_PORT=7077
export SPARK_MASTER_WEBUI_PORT=8080
# Set the worker nodes
export SPARK_WORKER_CORES=2
export SPARK_WORKER_MEMORY=2g
export SPARK_WORKER_WEBUI_PORT=8079
# Set JAVA_HOME variable to correct path of Java installation
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
```
started the master node:
```
sbin/start-master.sh
```
started the worker node:
```
sbin/start-worker.sh spark://10.11.1.81:7077
```
and opened the web UI under http://185.150.32.130:8080/
![Spark Web Ui](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/spark_ui.png)
  
#### PostgreSQL Server
I installed PostgreSQL with package manager
```
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```
started the server
```
sudo service postgresql start
sudo systemctl enable postgresql
```
created user and database for Airflow
```
sudo -u postgres psql
CREATE USER airflowuser WITH PASSWORD 'my_password';
CREATE DATABASE airflowdb;
ALTER ROLE airflowuser SET client_encoding TO 'utf8';
ALTER ROLE airflowuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE airflowuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE airflowdb TO airflowuser;
\q
```
created etluser
```
psql -U postgres
CREATE USER etluser WITH PASSWORD 'etlpassword' ;
ALTER USER etluser CREATEDB;
```
added line to postgresql.conf to allow connections from external machines
```
listen_addresses = '*'
```
added line to pg_hba.conf file to allow connections from specifies host:
```
host    etldb    etluser    10.11.1.81/32    md5
```
#### Airflow
I used pip to install Airflow
```
pip install apache-airflow[postgres]
```
set environment variable AIRFLOW_HOME:
```
export AIRFLOW_HOME=~/ecompipeline/airflow
```
initialised Airflow database, which didn't work, but it created the airflow.cfg file
```
airflow db init
```
edited airflow.cfg 
```
sql_alchemy_conn = postgresql+psycopg2://airflowuser:my_password@localhost/airflowdb
```
added this to the shell profile ~/.bashrc to make it persitent
```
export AIRFLOW_HOME=~/ecompipeline/airflow
```
had to install an older version of flask
```
pip install Flask-Session==0.5.0
```
created the airflow database
```
airflow db migrate
```
created airflow user
```
airflow users create -e jeticodes@gmail.com -f jessica -l ti -r Admin -u airflow -p airflow
```
installed  virtualenv in the Virtual Environment
```
pip install virtualenv
```
launched web UI (I had to change the spark worker web ui port first, because it's by default 8081) and opened the web UI under http://185.150.32.130:8081/
```
airflow webserver --port 8081
```
started the airflow scheduler
```
airflow scheduler
```
created dags, data, scripts directories and __init__.py files in the ecompipeline, dags and scripts directory.

#### PySpark
I installed findspark
```
pip install findspark
```
and added this to my scripts
```
import findspark
findspark.init('/opt/spark')
```

#### Kaggle
I installed kaggle
```
pip install kaggle
```

### Scripts
I created the following files
- etl_dag.py
- config.py
- download_data_script.py
- imp_clean_trans_script.py
- validate_data_script.py
- create_db_script.py
- create_tables_script.py
- load_data.py

   
launched and tested the process via the Airflow UI
![Airflow](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/airflow.png)


## API

### Setup API
created new virtual environment secapi_venv

installed fastAPI, Uvicorn and python-dotenv, the psycopg2 and SQLAlchemy library to execute SQL, the passlib, PyJWT libraries
```
pip install fastapi[all] uvicorn python-dotenv
pip install psycopg2-binary
pip install sqlalchemy
pip install passlib
pip install PyJWT
pip install python-multipart
pip install python-jose[cryptography]
```
create a separate database user for the API
```
CREATE USER apiuser WITH PASSWORD 'apipassword' ;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO apiuser;
```
### Scripts API
I created
- api_app.py file
   - JWT (JSON Web Token) to securely transmit information between two parties
   - OAuth 2.0 authorization tool, allowing users to grant third-party applications limited access to their       resources without sharing their credentials
   - 
- .env
- create_apidb.py  

optional further development:
   - HTTPS - Encrypting data in transit using TLS (Transport Layer Security) to ensure secure communication between cliet and server
   - Logs - Keeping detailed logs of API requests and responses for auditing purposes.

launched the API:
```
uvicorn api_app:app --host 0.0.0.0 --port 8000 --reload
```
accessed FastAPI via webbrowser
```
http://185.150.32.130:8000/docs
```
![API Branches](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/apibranches.png)
![API Authorization](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/apiauthorization.png)
![API Authorized](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/apiauthorized.png)
![Pull List](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/pulllist.png)
![CSV](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/csv.png)


