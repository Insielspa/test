#!/bin/bash

# Start Nginx
service nginx start

# Start sshd
/usr/sbin/sshd -D
