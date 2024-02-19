# E-Commerce Data Pipeline

#### Practice Project
I wanted to learn more about Spark, Airflow, Kubernetes, Docker and APIs and used [this e-commerce data](https://www.kaggle.com/datasets/carrie1/ecommerce-data) from Kaggle

#### Chapters:  
- [Architecture](#Architechture)  
- [Setup](#setup)  
   - [The vm](#the-vm)  
   - [Git](#git)  
   - [Virtual environment](#virtual-environment)  
   - [Java](#java)  
   - [Apache Apark](#apache-spark)  
   - [PostgreSQL Server](#postgresql-server)  
   - [Airflow](#airflow)  

## Architecture 
![Pipeline Architecture](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/architecture.png)

## Setup  
  
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
git clone 
```
  
### Virtual environment
created and activated a virtual environment "venv"
  
### Java
installed Java (for Spark)
  
### Apache Spark
I downloaded Apache Spark from the official website, unpacked it and saved it in /opt/spark
```
curl -O https://dlcdn.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar -xvzf spark-3.5.0-bin-hadoop3.tgz
mv spark-3.5.0-bin-hadoop3 /opt/spark
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
added informatoin on master and worker node to the spark-env.sh file in conf directory for standalone mode:
```
# Set the master node
export SPARK_MASTER_HOST=my_public_ip_address
export SPARK_MASTER_PORT=7077
export SPARK_MASTER_WEBUI_PORT=8080
# Set the worker nodes
export SPARK_WORKER_CORES=2
export SPARK_WORKER_MEMORY=2g
```
started the master node:
```
sbin/start-master.sh
```
started the worker node:
```
sbin/start-worker.sh spark://10.11.1.81:7077
```
and opened the web UI under http://my_public_ip_address:8080/
  
### PostgreSQL Server
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

  
### Airflow
I used pip to install Airflow
```
pip install apache-airflow[postgres]
```
set environment variable AIRFLOW_HOME:
```
export AIRFLOW_HOME=~/e-commerce_data_pipeline/airflow
```
initialised Airflow database, which didn't work, but created the airflow.cfg file
```
airflow db init
```
edited airflow.cfg 
```
sql_alchemy_conn = postgresql+psycopg2://airflowuser:my_password@localhost/airflowdb
```
added this to the shell profile ~/.bashrc to make it persitent
```
export AIRFLOW_HOME=~/e-commerce_data_pipeline/airflow
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
launched web UI (I had to change the spark worker web ui port first, because it's by default 8081)
```
airflow webserver --port 8081
```
started the airflow scheduler
```
airflow scheduler
```
created dags and plugins directoris in the airflow directory










