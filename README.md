# hTracer
## a simple Python hop/RTT measurement tool
Made as a project for EECS325: Computer Networks class at Case Western Reserve University, Spring semester of 2016.

*hTracer* gives you the following:

1. The number of router hops between you and the destination
2. RTT between you and the destination
3. The number of bytes of the original datagram included in the ICMP error message

## Instructions

### Requirements

- Python 2.7.6
- root privilege (yes, this one is serious)

*Coming soon...*

### Running

Write a list of websites to probe around, separated by newline, using your favorite text editor:

```
$ vi targets.txt
```

Sample:

```
google.com
yahoo.com
twitter.com
naver.com
```

...and so on.

Specify the filename as `targets.txt` in the same directory, then run using root privilege:

```
$ sudo python3 hTracer.py
```

The program will automatically run using the `targets.txt` file in the directory.

### References

- [Ksplice Blog - "Learning by doing: Writing your own traceroute in 8 easy steps"](https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your)
- [Black Hat Python: Building a UDP Scanner](http://bt3gl.github.io/black-hat-python-building-a-udp-scanner.html)
- [@rochacbruno](http://github.com/rochacbruno)'s [haversine.py: Calculate distance between latitude longitude pairs with Python](https://gist.github.com/rochacbruno/2883505)