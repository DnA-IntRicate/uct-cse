# ToC1 Assignment Answers

## Question 1
``` math
S(q0,a)=(q1,a,R) \\
S(q1,b)=(q2,b,R) \\
S(q2,a)=(q3,a,R) \\
S(q3,c)=(q4,c,R) \\
S(q4,c)=(q4,c,R) \\
S(q4,a)=(q5,a,R) \\
S(q5,b)=(q6,b,R) \\
S(q6,a)=(q7,a,R) \\
S(q7,B)=(qf,B,R) \\
S(q0,b)=(qr,b,R) \\
S(qr,x)=(qr,x,R)
```

## Question 2:
``` math
S(q0,<1,B>)=(q0,<B,1>,<R,R>) \\
S(q0,<0,B>)=(q0,<B,0>,<R,R>) \\
S(q0,<Y,B>)=(q1,<B,B>,<R,L>) \\
S(q1,<1,1>)=(q1,<B,B>,<R,L>) \\
S(q1,<0,0>)=(q1,<B,B>,<R,L>) \\
S(q1,<!,B>)=(qf,<B,B>,<S,S>)
```

## Question 3.1
``` mathematica
q101#01B
xq21#01B
x1q2#01B
x1#q401B
x1q6#x1B
xq71#x1B
q7x1#x1B
xq11#x1B
xxq3#x1B
xx#q5x1B
xx#xq51B
xx#q6xxB
xxq6#xxB
xq7x#xxB
xxq1#xxB
xx#q8xxB
xx#xq8xB
xx#xxq8B
xx#xxBqaccept
```

## Question 3.2
``` mathematica
q10#0#B
xq2#0#B
x#q40#B
xq6#x#B
q7x#x#B
xq1#x#B
x#q8x#B
x#xq8#B
reject
```

## Question 4.1
``` math
S(q0,B)=(qacc,B,R) \\
S(q0,a)=(q2,X,R) \\
S(q0,b)=(q3,X,R) \\
S(q2,a)=(q2,a,R) \\
S(q2,Y)=(q2,Y,R) \\
S(q2,b)=(q4,Y,L) \\
S(q3,b)=(q3,b,R) \\
S(q3,Y)=(q3,Y,R) \\
S(q3,a)=(q4,Y,L) \\
S(q4,a)=(q4,a,L) \\
S(q4,b)=(q4,b,L) \\
S(q4,Y)=(q4,Y,L) \\
S(q4,X)=(q1,X,R) \\
S(q1,Y)=(q1,Y,R) \\
S(q1,a)=(q2,X,R) \\
S(q1,B)=(qacc,B,R) \\
S(q1,b)=(q3,X,R)
```

## Question 4.2
``` math
L(M)=\{ME\{a,b\}*|na=nb\}
```

## Question 5
``` math
S(q0,0)=(q1,X,R) = 0101001000100 \\
S(q0,Y)=(q3,Y,R) = 0100001000010000100 \\
S(q1,0)=(q1,0,R) = 001010010100 \\
S(q1,1)=(q2,Y,L) = 0010010001000010 \\
S(q1,Y)=(q1,Y,R) = 001000010010000100 \\
S(q2,0)=(q2,0,L) = 0001010001010 \\
S(q2,X)=(q0,X,R) = 0001000101000100 \\
S(q2,Y)=(q2,Y,L) = 0001000010001000010 \\
S(q3,Y)=(q3,Y,R) = 0000100001000010000100 \\
S(q3,B)=(q4,B,R) = 0000100000100000100000100
```
