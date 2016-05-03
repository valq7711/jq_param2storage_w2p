# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        jq_param2storage_w2p.py
# Purpose:
#
# Author:      Valery Kucheroff
#
# Created:     04.05.2016
# Copyright:   (c) Valery Kucheroff 2016
# Licence:     MIT
#-------------------------------------------------------------------------------

import urllib, re
try:
    # Used with web2py
    from gluon.tools import Storage
except ImportError:
    Storage = dict

__all__=['jq_param_w2p']

def jq_param_w2p(str_or_buffer, rewind = True):
    """
    return:
        Storage or dict (if couldn`t import Storage) of posted $.param()

    str_or_buffer is result of $.param(obj, false), could be:
         - string
         - StringIO - means request.body
    rewind:
        if rewind and str_or_buffer is StringIO:
            StringIO.seek(0) before return

    Usage in Web2py controller:
        jq_vars = jq_param_w2p(request.body)

    """

    if not str_or_buffer:
        return Storage()

    class State:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                self.__dict__[k]=v

    is_num_or_none = re.compile('^(\d)*$', re.I )
    def get_obj_fun(first_key):
        def _add_dict_(obj, k, v):
            if not is_num_or_none.match(k): # not is_num_or_none:
                obj.__setitem__(k,v)
                return True
            else:
                return False
        def _add_list_(obj, k, v):
                if is_num_or_none.match( k): #is_num_or_none:
                    obj.append(v)
                    return True
                else:
                    return False
        if not is_num_or_none.match(first_key):
            return [Storage(), _add_dict_]
        else:
            return [list(), _add_list_]

    def read_elem(pref, first_key):
        key_val = st.key_val
        key_val_len = st.key_val_len
        ret, add_fun = get_obj_fun(first_key)
        l=len(pref)
        go_on = True
        while go_on and st.cur_i < key_val_len and key_val[st.cur_i][0][:l+1] == pref+'[' :
            key_lst = re.findall('\[([a-z0-9_]*)\]', key_val[st.cur_i][0][l:], re.I )
            key_num = len(key_lst)
            if key_num == 0:
                break
            if key_num == 1:
                v = key_val[st.cur_i][1]
                go_on = add_fun(ret, key_lst[0], v if not v.isdigit() else long(v))
                st.cur_i+= 1
            else:
                go_on = add_fun(ret, key_lst[0],
                        read_elem(pref+'['+key_lst[0]+']', key_lst[1]))
        return ret

    #----   main loop ------------------
    ret = Storage()
    is_string = isinstance(str_or_buffer, basestring)
    param =  is_string and str_or_buffer or str_or_buffer.read()
    key_val=[unicode(urllib.unquote_plus( s ),'utf8').split('=',1) for s in  param.split('&')]
    #st = Storage(cur_i=0, key_val = key_val, key_val_len=len(key_val))
    st=State(cur_i=0, key_val = key_val, key_val_len=len(key_val))

    while st.cur_i < st.key_val_len:
        k, v = key_val[st.cur_i]
        var = k.split('[')
        if len(var) > 1:
             tmp_cur_i = st.cur_i
             ret[var[0]] = read_elem(var[0],var[1][:-1])
             if tmp_cur_i==st.cur_i:
                raise RuntimeError('Can`t parse jq_param ')
        else:
            ret[var[0]]= v if not v.isdigit() else long(v)
        st.cur_i+= 1

    if rewind and not is_string:
        str_or_buffer.seek(0)
    return ret


def main():

    tmp3=r"""
        cmd: get-records
        &limit: 50
        &offset: 0
        &selected[]: 1
        &selected[]: 2
        &searchLogic: AND
        &search[0][field]: fname
        &search[0][type]: text
        &search[0][operator]: is
        &search[0][value]: %D0%92%D0%B0%D0%BB%D0%B5%D1%80%D0%B8%D0%B9
        &search[1][field]: age
        &search[1][type]: int
        &search[1][operator]: between
        &search[1][value][]: 10
        &search[1][value][]: 0.333
        &sort[0][field]: fname
        &sort[0][direction]: asc
        &sort[1][field]: lname
        &sort[1][direction]: desc
"""
    tmp3 = tmp3.replace('\n','').replace(' ','').replace(':', '=').replace('[', '%5B').replace(']', '%5D')

    print 'Posted by JQuery:\n',tmp3
    print 'that is:\n', unicode(urllib.unquote_plus( tmp3), 'utf8').replace('&','\n')
    converted = jq_param_w2p(tmp3)
    print 'converted by jq_param_w2p:\n', converted, '\n'
    print 'converted.limit:\t\t\t', converted['limit']
    print 'converted.selected:\t\t\t', converted['selected']
    print 'converted.search[0].value:\t', converted['search'][0]['value']
    print 'converted.search[1].field:\t', converted['search'][1]['field']
    print 'converted.search[1].value:\t', converted['search'][1]['value']

if __name__ == '__main__':
    main()
