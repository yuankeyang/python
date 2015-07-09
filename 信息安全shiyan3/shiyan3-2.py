def highest_prime_factor(n):
    if isprime(n):
        return n
    for x in xrange(2,n**0.5+1):
        if not n % x:
            return highest_prime_factor(n/x)

def isprime(n):
    for x in xrange(2,n**0.5+1):
        if not n%x:
            return False
    return True

if __name__ == '__main__':
    import time
    start=time.time()
    print(highest_prime_factor(28560614905655176753))
    print(time.time()-start)
