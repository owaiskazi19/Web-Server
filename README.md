
# Web-Server for Multiple Clients

## Problem Statement

The goal is to create a web server that serves files from a directory on the local file system where multiple clients will make requests at the same time. The server should be able to support 50 client requests at any given time.

## Technologies

- Programming language: python3
- Libraries used: http.server, threading, requests
- Testing module: nose
- Load Testing: curl sequencing

## Architecture Diagram

![Architechture Diagram](https://github.com/owaiskazi19/Web-Server/blob/main/image.jpg?raw=true)

## To run:

1. Server: 
   - Need python version 3
   - python web_server.py
   To hit the server:
   curl http://localhost:4445/hello.txt

2. Tests:
    - Install nose using: 
    
        pip install nose
    - Command to run unit test: 
    
        nosetests --verbosity=2 tests 
    - Command to run load test (Make sure the server is running): 
    
        sudo chmod 777 load_test.sh 

        ./load_test 


## Approaches

1. Using multi-threading:

Since http.server is a single-threaded server to accommodate the request of multiple clients, multi-threading can be an option using &#39;ThreadingMixIn&#39;. It&#39;ll allow multiple clients to get the file requested from the server.

2. Priority-queue:

This approach is quite similar to the actor modal, where the request will be put in the priority queue with its timestamp, and later each request will be processed one after the other.

I followed Approach 1 for implementing the web server to serve files present in the local directory.


### In this approach:

1. Overridden the do\_Get() method provided by the BaseHandler of the http.server to accommodate new features like file reading, directory linking.
2. Ran the server using multithreading to process multiple requests
3. Listed local directory using dynamic HTML provided by I/O stream

### Testing:

1. Added unit test cases using the module nose for checking the response code return from the URL
2. Load tested for 50 requests using curl sequencing

### Future Enhancement:

1. To scale the system later, we can add the requests in the PriorityQueue in a multithreaded fashion.
2. Also, can use SQS/MemCache with Lambda function to make a single read instead of PQ for millions of request
3. Scale the server horizontally and can add a load balancer to distribute the requests.
