#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Val
#
# Created:     06.02.2016
# Copyright:   (c) Val 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
import os
from stat import ST_MTIME
import json as js
import subprocess as subp
#from   import    portalocker
from gluon import portalocker



get_fname = lambda full_name: os.path.split(full_name)[1]

def change_ext(f_name, ext):
    return os.path.splitext(f_name)[0] + ext


def clear_file(f):
    f.seek(0)
    f.truncate()


class _log(object):
    def __init__(self, f_name):
        self.f_name=f_name
        self.error={}
        self.f_obj=None
        self.log = None

    def open_read(self):
        f_name=self.f_name
        try:
            if os.path.isfile(f_name):  # no file.json  - create it
                md='r+'
            else:
                md='w'
            f = open(f_name, md)
            self.f_obj = f
            portalocker.lock(f, portalocker.LOCK_EX )
            if md=='r+':
                tmp= f.read()
                self.log = (tmp and js.loads(tmp)) or {}
            else:
                self.log = {}

        except :
             self.error['open_read'] = sys.exc_info()[0]
        return self.log

    def save(self):
        if not self.f_obj:
            return
        try:
            clear_file(self.f_obj)
            self.f_obj.write(js.dumps(self.log))
            self.f_obj.close()
        except :
             self.error['save'] = sys.exc_info()[0]

    def set_compile_time(self, pyj_fname):
        if self.log is None:
            return
        f_stat = os.stat(pyj_fname)
        self.log[ get_fname(pyj_fname) ] = f_stat[ST_MTIME]

    def is_up_to_date(self, pyj_fname):
        if self.log is None:
            return False
        log_mtime = self.log.get( get_fname(pyj_fname) , None)
        f_stat = os.stat(pyj_fname)
        return log_mtime == f_stat[ST_MTIME]


class rs_compiler(object):
    def __init__(self, path_to_nodejs, path_to_RS):
        self.node = path_to_nodejs
        self.rs_engine = path_to_RS
        self.last_ret_code = None
        self.last_rslts = None

    def _rs_compile(self, src, dst, log, force_compile=False):
        ret = None
        if force_compile or not log.is_up_to_date(src) or not os.path.isfile(dst):
            ret = subp.call(
                        #[self.node, self.rs_engine, src, '-p', '-o', '-j6', dst], #  - Kovid RS
                        [self.node, self.rs_engine, src, '-p', '-o', dst],
                        stdout= self.stdout, stderr= self.stderr
                        )
            if ret==0:
                 log.set_compile_time(src)
        self.last_ret_code = ret
        return ret


    def rs_compile_dir(self, src, dst, stdout=None, stderr=None, force_compile=False):
        self.stdout = stdout
        self.stderr = stderr

        log = _log(os.path.join(dst, 'compile_inf.json' ))
        log.open_read()

        joinp = os.path.join
        all_dir = os.listdir(src)
        src_files = [f for f in all_dir if os.path.isfile(joinp(src, f)) and f[-4:]=='.pyj']
        ret={}
        for f in src_files:
            src_f =  joinp(src, f)
            dst_f =  joinp(dst, change_ext(f, '.js'))
            self._rs_compile(src_f, dst_f, log,  force_compile=force_compile)
            rslt=dict(
                    ret_code = self.last_ret_code,
                    open_read = log.error.get('open_read', None),
                    log_save_err = log.error.get('save', None),
                    )
            ret[f] = rslt
        self.last_rslts=ret
        log.save()
        return ret


def __compile_pyj():

    node='C:/Program Files/nodejs/node.exe'
    rs_engine = 'D:/Program Files/RapydScript-master/bin/rapydscript'
    cc = rs_compiler(node, rs_engine)
    src=os.path.join('D:/web2py/applications/dt_tst', 'private')
    dst = os.path.join('D:/web2py/applications/dt_tst', 'static/js')
    print '----------- beg -----------'
    print cc.rs_compile_dir(src,dst)



def main():

    node='C:/Program Files/nodejs/node.exe'
    rs_engine = 'D:/Program Files/RapydScript-master/bin/rapydscript'

    tst=rs_compiler(node , rs_engine)

    ret =tst.rs_compile_dir('D:/Program Files/RapydScript-master/examples/asteroids',
                    'D:/Program Files/RapydScript-master/examples/asteroids/out',
                    False)

    """
    ret =tst.rs_compile_dir('D:/web2py/applications/popy/private',
                    'D:/web2py/applications/popy/static/js',
                    False)
    """

    print ret
    #__compile_pyj()

    #return ret


if __name__ == '__main__':
    main()
