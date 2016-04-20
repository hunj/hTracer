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
Write a list of IP addresses to probe around, separated by newline, using your favorite text editor:

```
$ vi targets.txt
```

Sample:

```
123.12.123.123
132.132.12.132
231.231.231.23
...
```

Specify the filename as `targets.txt` in the same directory, then run using root privilege:

```
$ sudo python hTracer.py
```

The program will automatically run using the `targets.txt` file in the directory.

## Notes

A number of references has been used:

### References

- [Ksplice Blog - "Learning by doing: Writing your own traceroute in 8 easy steps"](https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your)
- [Black Hat Python: Building a UDP Scanner](http://bt3gl.github.io/black-hat-python-building-a-udp-scanner.html)

## Issues