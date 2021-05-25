from streamdemo import *


def test_sieved_primes():
    assert streamtools.sslice(primes, 4) == Stream(2, 3, 5, 7)
    assert primes[50] == 233


def test_ones():
    assert ones[100] == 1
    assert ones.tail is ones


def test_integers():
    assert integers[0] == 1
    assert integers[99] == 100


def test_fibs():
    assert fibs[0] == 0
    assert fibs[1] == 1
    assert fibs[9] == 34


def test_factorials():
    assert streamtools.sslice(factorials, 5) == Stream(1, 2, 6, 24, 120)


def test_sieved_primes2():
    assert streamtools.sslice(primes2, 4) == Stream(2, 3, 5, 7)
    assert primes2[50] == 233
