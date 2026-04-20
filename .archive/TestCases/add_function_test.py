import random as r
import errno
import pytest
from add_function import add

class TestAddFunction:
    def make_int_pair(self):
        a=r.randint(-100,100)
        b=r.randint(-100,100)
        return a,b
    def make_float_pair(self):
        a=r.uniform(-100.0,100.0)
        b=r.uniform(-100.0,100.0)
        return a,b
    
    def make_str_pair(self):
        a=''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(5))
        b=''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(5))
        return a,b
    
    def make_list_pair(self):
        a=[r.randint(-100,100) for _ in range(5)]
        b=[r.randint(-100,100) for _ in range(5)]
        return a,b
    
    def make_tuple_pair(self):
        a=tuple(r.randint(-100,100) for _ in range(5))
        b=tuple(r.randint(-100,100) for _ in range(5))
        return a,b
    
    @pytest.mark.parametrize("casefactory",
                             [make_int_pair,
                              make_float_pair,
                              make_str_pair,
                              make_list_pair,
                              make_tuple_pair],ids=["int","float","str","list","tuple"])
    def test_add(self,casefactory):
        a, b = casefactory(self)
        assert add(a, b) == a + b

   

    @pytest.mark.parametrize("args,expectedException",[
        ((-1,'string'),TypeError),
        ((None,1),TypeError),
        ((1,),TypeError),
        ((1,2,3),TypeError),
     
    ])
    def test_negative(self,args,expectedException):
        with pytest.raises(expectedException):
            add(*args)

    def test_mark(self):
        with pytest.raises(ValueError, match="mark test"):
            add("mark",1)

    def test_excinfo(self):
        with pytest.raises((ValueError,TypeError)) as excinfo:
            add("mark",1)
        assert str(excinfo.value)=="mark test in this case"
        assert excinfo.type==ValueError

    def test_errorn(self):
        with pytest.raises(OSError,check=lambda e:e.errno==errno.EACCES and e.strerror=="errorn test in this case"):
            add("errorn",1)
    def test_errorn_excinfo(self):
        with pytest.raises(OSError) as excinfo:
            add("errorn",1)
        
        print(excinfo.value)
        assert excinfo.value.errno==errno.EACCES
        assert excinfo.value.strerror=="errorn test in this case"
     
       