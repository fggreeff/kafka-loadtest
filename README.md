# kafka-loadtest

Load testing an event (food orders) service for kafka consumer &amp; producer using locust

## How to run load testing

The load test will run from your local machine

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- Python 3.7+ `brew install python3`
- The modules in `requirements.txt` (this is done in the *Local Configuration* instructions below)
- In the locust.py file change these variables:
	- Change the `in_topic_name` variable to align with the topic you want to put messages onto.
	- Change the `out_topic_name` variable to align with the topic you want to consume message from.

Note the out topic is only being used for visualisation that the load testing has started and the data being produced.

### Install into virtualenv

These steps should be familiar if you're familiar with python; if you're not, here's a brief guide to installing:

- Make sure you have virtualenvwrapper installed `pip3 install --user virtualenvwrapper`
- Create a virtualenv to hold the project, this will also create a virtual directory `python3 -m venv ~/.virtualenvs/kafka_load`
- Restart your terminal
- List virtual environments to verify they are showing up `lsvirtualenv`
- Activate using `workon kafka_load`

- Use `deactivate` to leave the virtual environment.

### Local Configuration

Configure the load tests to point to service. Install the python requirements:

> `pip install -r requirements.txt`

## Running load tests

In a seperate terminal run Zookeeper & Docker from docker-compose:

> `docker-compose up`

Run locust:

> `locust -f locust.py`

Visit:  

> `http://localhost:8089/`

Set up number of users and hatch rate and host as:

> `localhost:9092`

## Metrics

You can setup Grafana in the docker-compose to view the metrics in Grafana. 

