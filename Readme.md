# CORSA-GENI ADAPTOR!

The Corsa-GENI adaptor is a simple tool for creating virtual switches (*bridges*), connecting those virtual switches through virtual ports to physical ports (*tunnels*) on a Corsa switch. There is a REST API, which can be seen by looking at the corsa_adaptor.py file. 

## What it does

Creates bridges and tunnels, while also getting information for users.



## What it does not do

* Have any security
* Have any resiliency
* Have any persistant storage across reboots of the application

## How to use

First, a user must create a proper configuration file. An example is provided.

Second, there is a provided Dockerfile that must be modified in order to use. On line 15, a proper config file must be pointed to.

Third, one must build and run the docker image:

```
docker build -t corsa-geni .
docker run -p 5000:5000 -it corsa-geni
```

Once running, you can then run the application itself, while pointing to the correct configuration file:

```
cd corsa-geni/; python corsa_adaptor.py -c ../corsa-a.config
```

On the host machine, you can use the REST API on 127.0.0.1:5000 using either a browser, cURL, or a controller application.

