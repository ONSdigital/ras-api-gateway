#!/bin/bash
openssl genrsa -out client.key 4096
openssl req -new -x509 -days 999 -key client.key -out client.crt
