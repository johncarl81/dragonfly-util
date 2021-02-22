#!/usr/bin/env python

import math

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

VIRTUAL_SOURCE = dotdict({
    "latitude": 35.19468,
    "longitude": -106.59625
})

def differenceInMeters(one, two):
    earthCircumference = 40008000
    return [
        ((one.longitude - two.longitude) * (earthCircumference / 360) * math.cos(one.latitude * 0.01745)),
        ((one.latitude - two.latitude) * (earthCircumference / 360))
    ]

def calculateCO2(position):


    [y, x] = differenceInMeters(position, VIRTUAL_SOURCE)

    if x >= 0 or y > 20 or y < -20:
        return 420

    Q = 50000
    K = 2
    H = 2
    u = 1

    value = (Q / (2 * math.pi * K * -x)) * math.exp(- (u * ((pow(y, 2) + pow(H, 2))) / (4 * K * -x)))

    if value < 0:
        return 420
    else:
        return 420 + value

def buildco2(x, y):
    values = []
    for i in range(len(x)):
        values.append(calculateCO2(dotdict({"longitude": float(x[i]), "latitude": float(y[i])})))
    return values
