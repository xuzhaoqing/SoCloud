# Benchmark for Lab 2

#1. Maximum number of connections
Maximum number of connections that can be handled by the server before any connection drops is 900.

#2. Maximum RPS
Maximum number of requests per second (RPS) that can be sustained by the server when operating with maximum number of connections is 494.13.

#3. %50
it would be 13

#4. %99
it would be 217

#5. Output log
the output log is as below, and I didn't find the info related to utilization of CPU, memory, disk IO, and network


This is ApacheBench, Version 2.3 <$Revision: 1528965 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 34.228.18.60 (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Finished 900 requests


Server Software:        WSGIServer/0.1
Server Hostname:        34.228.18.60
Server Port:            80

Document Path:          /?keywords=helloworld+foo+bar
Document Length:        1279 bytes

Concurrency Level:      10
Time taken for tests:   1.821 seconds
Complete requests:      900
Failed requests:        0
Total transferred:      1290600 bytes
HTML transferred:       1151100 bytes
Requests per second:    494.13 [#/sec] (mean)
Time per request:       20.238 [ms] (mean)
Time per request:       2.024 [ms] (mean, across all concurrent requests)
Transfer rate:          691.97 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2  33.2      1     997
Processing:     2   16  31.3     13     455
Waiting:        0   15  31.3     12     454
Total:          4   18  50.3     13    1214

Percentage of the requests served within a certain time (ms)
  50%     13
  66%     13
  75%     14
  80%     14
  90%     14
  95%     15
  98%     19
  99%    217
 100%   1214 (longest request)

