import socket as s
from struct import pack as p

sock = s.socket(s.AF_INET, s.SOCK_STREAM)
sock.connect(("127.0.0.1", 42000))

dat1 = p("hh", 65, 66)
dat2 = p("hh", 67, 68)

print(dat1)
print(dat2)

sock.send(dat1)
sock.send(dat2)

sock.close()
