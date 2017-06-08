# API Gateway Microservice
[![Build Status](https://travis-ci.org/ONSdigital/ras-api-gateway.svg?branch=master)](https://travis-ci.org/ONSdigital/ras-api-gateway)
[![codecov](https://codecov.io/gh/onsdigital/ras-api-gateway/branch/master/graph/badge.svg)](https://codecov.io/gh/onsdigital/ras-api-gateway)

## Overview

This Micro-service is under development and although it's working, will be subject
to frequent changes. Currently we're providing three discrete services;

* Proxying of incoming requests against connected Micro-sercices
* Native service registration functions such as /register
* An aggregated call interface for calling multiple endpoints and returning an aggregated response

The current CF deployment is available here; [Development API Gateway](https://api-dev.apps.mvp.onsclofo.uk/api/1.0.0/mygateway)
(this is not pretty, but it should be functional)

![api_gateway_architecture.png](api_gateway_architecture.png)


#### TODO

* Implement local UI screen (done)
* Implement a **real** example of an aggregated call (done)
* Inject JWT tokens depending on config.ini setting (done)
* Add service name to local.ini
* See if routing can be optimised a little
* Benchmark
* Implement a keep-alive / polling registration scheme (done)
* Drive router setup from swagger.yaml
