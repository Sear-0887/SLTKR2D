from collections import defaultdict

def primefactor(n:int) -> dict[int, int]:
    # rbcavi implementation
    smallprimes=[2,3,5,7,11,13,17,19] # i hope i didn't miss any
    # you can add more primes
    # just don't skip any
    if n==1:
        return {1:1}
    factors:dict[int, int]=defaultdict(int) # a dict of primes to powers, all 0
    for prime in smallprimes:
        while n%prime==0: # assumes 1 isn't in the list
            n//=prime
            factors[prime]+=1
    p=max(smallprimes) # assumes the maximum prime is odd
    while n>1:
        while n%p==0:
            n//=p
            factors[p]+=1
        p+=2 # 100% faster!
        if p*p>n: # sqrt is a bit slower
            # n is now prime
            if n!=1:
                factors[n]+=1
            break
    return factors