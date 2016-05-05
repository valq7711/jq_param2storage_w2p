# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Val
#
# Created:     19.03.2016
# Copyright:   (c) Val 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------



if 0:
    from gluon.dal import *
    from gluon.validators import *
    from gluon.tools import *
    from gluon.globals import *
    from gluon.cache import Cache
    from gluon.sql import *
    from gluon.sqlhtml import *
    from gluon.html import *

    request = Request()
    response = Response()
    session = Session()
    cache = Cache()
    db = DAL()


from types import MethodType
from gluon.contrib  import simplejson as sj
from gluon.html import *

class Json_Args:
    __repr__ = lambda self: '<Json_Args %s>' % dict.__repr__(self)

    def __init__(self):
        self._.__json_args__= {}
        if 0:
            self.__json_args__={}

    def __json__(self, **kwargs):
        args = self.__json_args__.copy()
        args.update(kwargs)
        return Smart_Storage.__json__(self, **args)


class Smart_Storage(dict):
    """
    A Smart_Storage object is like a dictionary but:
    - set/get value:
        obj['foo'] == obj.foo
    - set/get attribute:
        # use `._.` or `._['attr_name']`  to set attribute
            obj._.attr = 'I`m attribute but not data!!!'
            obj._['another_attr'] = 'I`m another one'
        # set/update many attributes
            obj._.update(dict(...))

        # use dot only to get attribute
            print obj.attr
        # remember that
            obj['attr'] == None
        # but don't forget
            obj.__dict__['attr'] == obj.attr

    - bind/call method:
        # use `._['@...']` to bind method
            obj._['@my_meth'] = lambda self: 'I`m method of %s' % self
        # nothing new
            obj.my_meth()

    - finally obj.__json__():
        # works recursively
        # for item that is Smart_Storage instance - item.__json__() will be applied
            obj.__json__(only = None, exclude = None, values_only = False)

    - and obj.__formatters__():
        # use __formatters__ to control serialization (note double quote)
            obj.__formatters__['key_name'] = lambda self, k, v: self.check_access(k) and v or '"-access denied-"'
        # or just
            obj.__formatters__['key_name'] = '"key = %(k)s,  value = %(v)s"'
        # serialize web2py helpers
            obj.html = DIV()
            obj.__formatters__['html'] = lambda self, k, v: '"%s"' % v.xml()
        # serialize js-function/object for embedding as script
            obj.name='John'
            obj.surname='Smith'
            obj.who_are_you = "function(){ console.log( 'I`m ',this.name,' ',this.surname);}"
            obj.__formatters__['who_are_you'] = '%(v)s' # not '"%(v)s"'
            obj._['@xml'] = lambda self: \
                SCRIPT( '\n'.join([
                                    'var obj = %s;',
                                    'obj.who_are_you();',
                                 ]) % self.__json__()
                        ).xml()
            ...
            # in the view just
                {{ =obj }}
            # that will be
            <script><!--
                var obj = {"who_are_you":function(){ console.log( 'I`m ',this.name,' ',this.surname);},"surname":"Smith","name":"John"};
                obj.who_are_you();
            //--></script>
    """

    __getattr__ = dict.get
    __getitem__ = dict.get
    __delattr__ = dict.__delitem__
    __repr__ = lambda self: '<Smart_Storage %s>' % dict.__repr__(self)

    class Add_Attr:

        def __init__(self, mystor_obj, args=None):
            self.__dict__['mystor_obj'] = mystor_obj
            if args:
                self.update(args)

        def __setattr__(self, k, v):
            if k in self.mystor_obj:
                raise RuntimeError('"%s" is in keys' % k)
            self.mystor_obj.__dict__[k] = v

        def __setitem__(self, k ,v):
            if k[0] in '0123456789&#.%$':
                raise RuntimeError('"%s" is invalid name' % k)
            if k[0]=='@':
                v = MethodType(v, self.mystor_obj)
                k=k[1:]
            self.__setattr__(k ,v)


        def update(self, d):
            [self.__setattr__(k, d[k]) for k in d]


    def __setattr__(self, k, v):
        if k in self.__dict__:
            raise RuntimeError('"%s" is in __dict__' % k)
        dict.__setitem__(self, k, v)

    def __init__(self, *a, **kwargs):
        _ = kwargs.pop('_', None)
        if 0:
            self._ = None
            self.__formatters__ = {}
        dict.__init__(self, *a, **kwargs)
        self.__dict__['_'] = Smart_Storage.Add_Attr(self, _)
        self.__dict__['__formatters__'] = {}

    def __json_pair__(self, k, v):
        formatter = self.__formatters__.get(k, None)
        if formatter is not None:
            if callable( formatter):
                ret = formatter(self, k, v)
            elif isinstance(formatter, basestring):
                ret = formatter % dict(k=k, v=v)
            else:
                raise RuntimeError('Unsupported formatter for  %s : "%s"' % (k, formatter))
        else:
            if isinstance(v, Smart_Storage):
                ret = v.__json__()
            elif isinstance(v, (list, tuple)):
                json_lst= [isinstance(it, Smart_Storage) and it.__json__() or sj.dumps(it) \
                            for it in v]
                ret= '[%s]'% ','.join(json_lst)
            else:
                ret = sj.dumps(v)

        return (k, ret)


    def __json__(self, only = None, exclude = None, values_only = False):
        """
        - only / exclude - filter out keys, 'exclude' applies after 'only', so:
            (only = ['a', 'b', 'c'], exclude = ['b']) == (only = ['a', 'c'])
        - values_only = True - serialize as json list of values
        """

        f_dict = lambda pair: '"%s":%s' % pair
        f_lst = lambda pair: pair[1]
        ret_str, f_str= values_only and ('[%s]' , f_lst) or ('{%s}',f_dict)
        buf = []
        if only or exclude:
            keys = only or self
            if exclude:
                keys = set(keys)-set(exclude)
            for k in keys:
                pair = self.__json_pair__(k, self[k])
                if pair:
                    buf.append(f_str(pair))
        else:
            for k, v in self.iteritems():
                pair = self.__json_pair__(k,v)
                if pair:
                    buf.append(f_str(pair))
        return ret_str % ','.join(buf)



def _mystorage_test():

    mys= Smart_Storage(a=23, f=56, _=dict(init_arg='init_arg'))
    mys.a='change a'
    mys.new='new'
    mys.never_attr #
    mys._['@new_meth']=lambda self: 'new meth'
    print mys.new_meth()
    if mys.new_meth() != 'new meth':
        raise RuntimeError('new meth problem')
    mys._.update(dict(upd='upd'))
    mys._.js_proc='js_proc'
    mys.lst = [Smart_Storage(a='a', b='b'), Smart_Storage(a='a1', b='b1'),]

    mys.format_by_str=u'значение'

    mys.__formatters__['format_by_fun'] = lambda self, k, v: '%s-- %s --'%(k,v)
    mys.__formatters__['format_by_str'] = u'Ключ=%(k)s Знач=%(v)s'
    mys.format_by_fun=dict(qq=23)



    print 'json' , mys.__json__()
    print 'json values only' , mys.__json__(values_only=True)
    print 'only keys a, f' , mys.__json__(only=['a', 'f'])
    print 'exclude key f' , mys.__json__(exclude=['f'])
    print 'only keys a,f, lst exclude f' , mys.__json__(only= ['a', 'f', 'lst'],exclude=['f'])
    print mys.init_arg
    print mys['init_arg']
    mys._['att'] = 23
    print mys.__json__()
    print mys.att
    mys._['@my_meth'] = lambda self: 'I`m method of %s' % self
    print mys.my_meth()

    obj = Smart_Storage()
    obj.name='John'
    obj.surname='Smith'
    obj.who_are_you = "function(){ console.log( 'I`m ',this.name,' ',this.surname);}"
    obj.__formatters__['who_are_you'] = '%(v)s' # not '"%(v)s"'
    obj._['@xml'] = lambda self: \
                SCRIPT( '\n'.join([
                                    'var obj = %s;',
                                    'obj.who_are_you();',
                                 ]) % self.__json__(),
                        ).xml()
    print obj.xml()



    return mys

def main():
    _mystorage_test()

if __name__ == '__main__':
    main()
