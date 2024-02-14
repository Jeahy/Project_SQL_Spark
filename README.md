# E-Commerce Data Pipeline

#### Practice Project
I wanted to learn more about Spark, Airflow, Kubernetes, Docker and APIs and used [this e-commerce data](https://www.kaggle.com/datasets/carrie1/ecommerce-data) from Kaggle

## Architecture 
![Pipeline Architecture](https://github.com/Jeahy/e-commerce_data_pipeline/blob/main/images/architecture.png)

## Setup

###The vm
   Ubuntu, 4 CPUs, 16 GB RAM, 50 GB,
   set up several ports for inbound (and outbound) traffic:
   7077 - Spark
   8080 - Spark UI
   5432 - Database
   3000 - API
   6443, 2379-2380, 10250, 10251, and 10252 - Kubernetes
   8081 - Airflow UI
   5000 - Docker
   
####Git
   created a git repo on github and cloned it onto my vm
   
####Apache Spark
   downloaded Apache Spark from the official website, unpacked it and saved it in /opt/spark
   edited the users shell profile in .bashrc
     ```
     export SPARK_HOME=/opt/spark
     export PATH=$SPARK_HOME/bin:$PATH
     ```
   and activated it
     ```
     source ~/.bashrc
     ```
   added to the spark-env.sh file in conf directory:
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

####Airflow
