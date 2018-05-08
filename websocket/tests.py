from django.test import TestCase

# Create your tests here.
import uuid
import time

if __name__ == "__main__":
    i=0
    while i<20:
        print(int(time.time()*1000000))
        i+=1