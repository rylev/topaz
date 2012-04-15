from pypy.rlib.rerased import new_static_erasing_pair

from rupypy.module import ClassDef
from rupypy.objects.objectobject import W_BaseObject


class StringStrategy(object):
    def __init__(self, space):
        pass

class ConstantStringStrategy(StringStrategy):
    erase, unerase = new_static_erasing_pair("constant")

    def str_w(self, storage):
        return self.unerase(storage)

    def liststr_w(self, storage):
        strvalue = self.unerase(storage)
        return [c for c in strvalue]

    def copy(self, storage):
        return W_StringObject(storage, self)

    def to_mutable(self, space, s):
        s.strategy = strategy = space.fromcache(MutableStringStrategy)
        s.storage = strategy.erase(self.liststr_w(s.storage))

    def extend_into(self, src_storage, dst_storage):
        dst_storage += self.unerase(src_storage)

class MutableStringStrategy(StringStrategy):
    erase, unerase = new_static_erasing_pair("mutable")

    def str_w(self, storage):
        return "".join(self.unerase(storage))

    def liststr_w(self, storage):
        return self.unerase(storage)

    def to_mutable(self, space, s):
        pass

    def extend_into(self, src_storage, dst_storage):
        dst_storage += self.unerase(src_storage)


class W_StringObject(W_BaseObject):
    classdef = ClassDef("String")

    def __init__(self, storage, strategy):
        self.storage = storage
        self.strategy = strategy

    @staticmethod
    def newstr_fromstr(space, strvalue):
        strategy = space.fromcache(ConstantStringStrategy)
        storage = strategy.erase(strvalue)
        return W_StringObject(storage, strategy)

    @staticmethod
    def newstr_fromchars(space, chars):
        strategy = space.fromcache(MutableStringStrategy)
        storage = strategy.erase(chars)
        return W_StringObject(storage, strategy)

    def str_w(self, space):
        return self.strategy.str_w(self.storage)

    def liststr_w(self, space):
        return self.strategy.liststr_w(self.storage)

    def copy(self):
        return self.strategy.copy(self.storage)


    @classdef.method("<<")
    def method_lshift(self, space, w_other):
        assert isinstance(w_other, W_StringObject)
        self.strategy.to_mutable(space, self)
        strategy = self.strategy
        assert isinstance(strategy, MutableStringStrategy)
        storage = strategy.unerase(self.storage)
        w_other.strategy.extend_into(w_other.storage, storage)
        return self
