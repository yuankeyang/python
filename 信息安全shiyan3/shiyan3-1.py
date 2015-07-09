#杨元科
#大整数因式分解
import sys
import math
def prime_factorize(n):
    factors=[]
    number=int(n)
    print(number)
    while number>1:
        factor=get_next_prime_factor(number)
        factors.append(factor)
        number/=factor
    if n<-1:
        factors[0]= -factors[0]
    return tuple(factors)

def get_next_prime_factor(n):
    if int(n % 2)==0:
        print(n)
        return 2
    #素因子的下限为4294967295，上限为8589934591
    for x in range(4294967295,int("8589934591"),2):
        if n%x==0:
            return x
    return int(n)

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print("Usage:%s <integer>" % sys.argv[0])
        exit()
    try:
        number=int(sys.argv[1])
    except ValueError:
        print("'%s' is not an integer !" % sys.argv[1])
    else:
        print("结果：%d -> %s" % (number,prime_factorize(number)))
