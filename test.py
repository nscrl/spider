# -*- coding:utf-8 -*-
def fun(a, b, c, d=None):
    if c:
        print a,b,c,d
    else:
        print a,b,d

fun(a=1, b=2, c =3)
fun(a=1, b=2, c=4, d =3)