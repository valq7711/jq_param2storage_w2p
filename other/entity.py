# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Val
#
# Created:     26.02.2016
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
    t=Table
    f=Field


#from gluon.cache import Cache
from gluon import current
from gluon.dal import  DAL, Field, Table
from gluon.tools import Storage
import re
_SPLIT_PAIR =  re.compile('([a-z0-9_]+)\.?(.*)')
_GET_SET_UPD = re.compile(' SET (.+) WHERE ')


def __vw_json_agg_sel__(self):
    if self._table._entopt.type=='list':
        return 'json_agg(%s) AS %s'% (self._entopt.vw_name, self._entopt.vw_name)
    else:
        return self._entopt.vw_name


def json_agg_sql(flds_lst, as_alias):
        tables_list = [f._table for f in flds_lst]
        json_fld_sql = """ '"%s":' || to_json(%s) """
        json_row = [json_fld_sql  % (f.sqlsafe, f.sqlsafe) for  f in flds_lst]
        json_row_sql = "'{' || " + "|| ',' ||".join(json_row) + " || '}'"
        json_agg_sql =  'json_agg((%s)::json) AS %s' % (json_row_sql, as_alias)
        class _Json_Agg_Field_(str):
            pass
        ret = _Json_Agg_Field_(json_agg_sql)
        ret._tables_list = tables_list
        return ret


def def_PG_table(db, name, *flds, **kwargs):
    alt_key = kwargs.pop('alt_key', None)
    migrate=  kwargs.get('migrate', None)
    db.define_table(name, *flds, **kwargs)
    if alt_key:
        _add_uniq_cons(db[name], alt_key, migrate)

def _add_uniq_cons(table, uniq_flds, migrate=None):
    migrate = (migrate is not None and migrate) or (table._db._migrate and table._db._migrate_enabled)
    if migrate:
        sql_drop = "ALTER TABLE %(table_full)s DROP CONSTRAINT IF EXISTS %(table)s_idx;"
        sql_add = "ALTER TABLE %(table_full)s ADD CONSTRAINT %(table)s_idx UNIQUE(%(flds)s);"
        sql_args = dict(table_full = table.sqlsafe,
                        table = table._tablename,
                        flds = ','.join(uniq_flds)
                        )
        table._db.executesql(sql_drop % sql_args)
        table._db.executesql(sql_add % sql_args)



class Enum(object):


    def __init__(self, db, name,
                format = None,
                code_field = False,
                rname = None,
                schema = 'public',
                migrate = False,
                FK_name = None):
        self.db = db
        rname = rname or schema+ '.enm_'+ name
        flds = [    Field('id','integer'),
                    Field('name', unique=True),
               ]
        if code_field:
            flds.append(Field('code', unique=True))
            _format='%(code)s'
        else:
            _format='%(name)s'

        db.define_table(name, *flds,
                    primarykey = ['id'],
                    rname = rname,
                    format = format is None and _format or format,
                    migrate = migrate
                    )
        self.own = db[name]
        self.FK_name = FK_name or name+'_id'

        @property
        def FK_name(self):
            return self.FK_name



def ref_field(enm, name=None, **kwargs):
    name = name or enm.FK_name
    _type = 'reference '+ enm.own._tablename
    nocahe = kwargs.pop('nocache', None)
    fld = Field(name, _type, **kwargs)
    def _get_enm_rec(id):
        cache = current.cache
        _enm = enm
        _nocahe = nocahe
        if _nocahe:
            enm_rows= _enm.db().select(_enm.own.ALL)
        else:
            enm_rows= _enm.db().select(_enm.own.ALL, cache = (cache.ram,60), cachable=True)
        if enm_rows.first() and id is not None:
            enm_rec = enm_rows.find(lambda row: row.id==id)[0]
        else:
            enm_rec = None
        return enm_rec
    def _get_repr(v, r):
        rec=_get_enm_rec(v)
        if rec:
            repr_fld = hasattr(rec,'code') and rec.code or rec.name
        else:
            repr_fld = None
        return repr_fld
    fld.represent = _get_repr
    fld._enm_rec = _get_enm_rec
    return fld




class _Entity_(object):
    pass


class Entity(_Entity_):
    _init_args = ('D_field', 'parent', 'D_value', 'tracking')
    table_by_veiw = Storage()


    def _unlock_(fun):
        def _wrapper_(self, *args, **kwargs):
            self._is_locked_ = False
            ret = fun(self, *args, **kwargs)
            self._is_locked_ = True
            return ret
        return _wrapper_


    def def_option(self, name, *fields, **kwargs):
        db=self.db
        fields=list(fields)
        own = self.own
        own_name= own._tablename
        if kwargs.get('rname', None) is None:
            kwargs['rname'] = own_name+'_'+name

        # make FK field
        FK_field_name = own_name+'_id'
        if next((f for f in fields if f.name=='id'), None):
            option_type = 'list'
        else:
            option_type = 'one'
            kwargs['primarykey']=[FK_field_name]

        fields.append(Field(FK_field_name, 'reference %s' % own_name))
        db.define_table(name, *fields, **kwargs)
        option = self.option[name] = self.db[name]
        option._entopt = Storage(type = option_type ,
                                own_FK = option[FK_field_name] )

        if self.tracking:
            self._lock_table_(option)

    @staticmethod
    def _vw_opt_fld_name(fld):
        pref_fld_str = '%(tbl)s_%(fld)s'
        fld_str = '%(vw_name)s'
        opt_tbl=fld._table
        args = Storage(tbl = hasattr(opt_tbl, '_entopt') and opt_tbl._entopt.vw_pref or opt_tbl._tablename )
        args.fld=fld.name
        args.vw_name = hasattr(fld, '_entopt') and fld._entopt.vw_name
        name_str = args.vw_name and fld_str or pref_fld_str
        return name_str % args



    def _vw_agg_opt_flds_select(self, opt_tbl):
        if opt_tbl._entopt.type=='one':
            raise RuntimeError('_get_agg_flds: field is not list')
        ret = []
        for fld in opt_tbl:
            if fld is not opt_tbl._entopt.own_FK:
                ret.append('json_agg(%s) AS %s'% (self.view[fld._entopt.vw_name].sqlsafe, fld._entopt.vw_name))
        return ret


    def __vw_opt_fields_refresh(self):
        self.vw_opt_fields = []
        for opt_tbl in self.option.values():
            for fld in opt_tbl:
                if fld is opt_tbl._entopt.own_FK:
                    continue
                self.vw_opt_fields.append(fld)


    def _vw_opt_flds_select(self, opt_tbl, vw_opt_fields):
        name_str = '%(rname)s.%(fld)s AS %(vw_name)s'
        ret = []
        args = Storage( rname = opt_tbl._rname or opt_tbl._tablename,
                        tbl= opt_tbl._entopt.vw_pref or opt_tbl._tablename )
        for fld in opt_tbl:
            if fld is opt_tbl._entopt.own_FK:
                continue
            args.fld = fld.name
            if not hasattr(fld, '_entopt'):
                fld._entopt = Storage()
            if fld._entopt.vw_name:
                args.vw_name = fld._entopt.vw_name
            else:
                args.vw_name = fld._entopt.vw_name = '%(tbl)s_%(fld)s' % args
            vw_opt_fields.append(fld)
            ret.append(name_str % args)
        return ret

    def _vw_opt_flds_select_json(self, opt_tbl, vw_opt_fields):
        ret = []
        args = Storage( rname = opt_tbl._rname or opt_tbl._tablename,
                        tbl= opt_tbl._entopt.vw_pref or opt_tbl._tablename )
        if opt_tbl._entopt.type=='list':
            name_str_json = 'row_to_json(%(rname)s.*) AS %(vw_name)s'
            args.vw_name = args.tbl
            ret.append(name_str_json % args)
            fld = Field(args.vw_name, 'json')
            fld._entopt=Storage(vw_name = args.vw_name,
                                    is_optrow = True)
            vw_opt_fields.append(fld)
        else:
            name_str = '%(rname)s.%(fld)s AS %(vw_name)s'
            for fld in opt_tbl:
                if fld is opt_tbl._entopt.own_FK:
                    continue
                args.fld = fld.name
                if not hasattr(fld, '_entopt'):
                    fld._entopt = Storage()
                if fld._entopt.vw_name:
                    args.vw_name = fld._entopt.vw_name
                else:
                    args.vw_name = fld._entopt.vw_name = '%(tbl)s_%(fld)s' % args
                vw_opt_fields.append(fld)
                ret.append(name_str % args)
        return ret



    def _get_vw_select(self, as_json = False ):
        vw_opt_flds_select_fun= as_json and self._vw_opt_flds_select_json \
                                    or self._vw_opt_flds_select
        db = self.db
        sel_opt=[]
        vw_opt_fields = []
        for opt_tbl in self.option:
            sel_opt.extend(vw_opt_flds_select_fun(self.option[opt_tbl], vw_opt_fields))
        left = self.join_opt(*self.option.values())
        vw_def = self.db()._select( self.own.ALL, *sel_opt, left = left)
        return Storage(vw_def = vw_def, vw_opt_fields = vw_opt_fields)


    def _get_vw_agg_select(self):
        db = self.db
        groupby= []
        fld_lst =[self.view_json[f.name].sqlsafe for f in self.own]
        groupby = fld_lst[:]
        sel_str = {False:'%(fld_safe)s',  True:'json_agg(%(fld_safe)s) as %(fld)s'}
        opt_select=[]
        for fld in  self.vw_json_opt_fields:
            fld_name = dict(fld = fld.name,
                            fld_safe= self.vw_json_name +'.' + fld._entopt.vw_name)
            opt_select.append(sel_str[fld._entopt.is_optrow or False] % fld_name)
            not fld._entopt.is_optrow and groupby.append(fld_name['fld_safe'])

        vw_agg_def = self.db()._select(*(fld_lst + opt_select), groupby=', '.join(groupby))
        return vw_agg_def

    def _get_vw_join_parent_select(self):
        if not self.parent:
            return None
        db = self.db
        prnt_fid = self.parent.view_agg._id
        prnt_flds=[f for f in self.parent.view_agg if f is not  prnt_fid]
        ret = db(prnt_fid==self.view_agg._id)._select( self.view_agg.ALL, *prnt_flds)
        return ret



    def vw_def(self, vw_name, as_json = False):
        fld_lst =[f.clone() for f in self.own]
        opt_flds=[]
        vw_opt_fields = as_json and  self.vw_json_opt_fields or self.vw_opt_fields
        #vw_name =  as_json and  self.vw_json_name or self.vw_name
        for fld_opt in vw_opt_fields:
            f_type = fld_opt.type=='id' and 'reference '+fld_opt._tablename or fld_opt.type
            fld= fld_opt.clone(name = fld_opt._entopt.vw_name, type=f_type)
            opt_flds.append(fld)

        fld_lst.extend(opt_flds)
        self.db.define_table(vw_name, *fld_lst, migrate=False)

    def vw_agg_def(self):
        fld_lst =[f.clone() for f in self.own]
        opt_flds=[]
        for fld_opt in self.vw_json_opt_fields:

            #f_type= fld_opt._tabel._entopt.type =='list' and 'json' or fld_opt.type
            #f_type = f_type=='id' and 'reference '+fld_opt._tablename or f_type
            #fld= fld_opt.clone(name = fld_opt._entopt.vw_name, type=f_type )
            fld= fld_opt.clone(name=fld_opt._entopt.vw_name)
            opt_flds.append(fld)
        fld_lst.extend(opt_flds)
        self.db.define_table(self.vw_agg_name, *fld_lst, migrate=False)


    def vw_join_parent_def(self):
        prnt_fid = self.parent.view_agg._id
        own_fld_lst =[f.clone() for f in self.view_agg]
        prnt_fld_lst =[f.clone() for f in self.parent.view_agg if f is not prnt_fid]
        fld_lst = prnt_fld_lst + own_fld_lst
        self.db.define_table(self.vw_join_parent_name, *fld_lst, migrate=False)





    def _create_view(self, vw_name, schema='public', as_json = False, migrate=False):
        #def select(self, query, *fld_lst, **kwargs):
        ret = self._get_vw_select(as_json)
        if migrate:
            sql_str= 'CREATE OR REPLACE VIEW %s.%s AS ' % (schema, vw_name)
            sql_str+= ret.vw_def
            self.db.executesql(sql_str)
        return ret


    def create_view(self, **kwargs):
        vw_name = kwargs['vw_name'] = self.vw_name
        kwargs['as_json'] = False
        ret = self._create_view(**kwargs)
        self.vw_opt_fields = ret.vw_opt_fields
        self.vw_def(vw_name, False)
        self.view = self.db[vw_name]
        Entity.table_by_veiw[vw_name] = self.own

    def create_view_json(self, **kwargs):
        vw_name = kwargs['vw_name'] = self.vw_json_name
        kwargs['as_json'] = True
        ret = self._create_view(**kwargs)
        self.vw_json_opt_fields = ret.vw_opt_fields
        self.vw_def(vw_name , True)
        self.view_json = self.db[vw_name]
        Entity.table_by_veiw[vw_name] = self.own


    def create_view_agg(self, schema='public',  migrate=False):
        #def select(self, query, *fld_lst, **kwargs):
        ret = self._get_vw_agg_select()
        if migrate:
            sql_str= 'CREATE OR REPLACE VIEW %s.%s AS ' % (schema, self.vw_agg_name)
            sql_str+= ret
            self.db.executesql(sql_str)
        self.vw_agg_def()
        self.view_agg = self.db[self.vw_agg_name]
        Entity.table_by_veiw[self.vw_agg_name] = self.own


    def create_view_join_parent(self, schema='public',  migrate=False):
        if not self.parent:
            return None
        ret = self._get_vw_join_parent_select()
        if migrate:
            sql_str= 'CREATE OR REPLACE VIEW %s.%s AS ' % (schema, self.vw_join_parent_name)
            sql_str+= ret
            self.db.executesql(sql_str)
        self.vw_join_parent_def()
        self.view_join_parent = self.db[self.vw_join_parent_name]
        Entity.table_by_veiw[self.vw_join_parent_name] = self.own


    def join_opt(self, *opt_lst):
        join=[]
        for it in opt_lst:
            opt = isinstance(it, basestring) and self.option[it] or it
            join.append(opt.on(self.own._id == opt._entopt.own_FK))
        return join


    def get_field(self, fld_str):
        frst, sec = _SPLIT_PAIR.findall(fld_str)[0]
        if not sec:
            if frst in self.own.fields:
                return self.own[frst]
        else:
            return self.option[frst][sec]


    def _get_field_opt_lst(self, fld_lst):
        ret = dict( own_fld=[], opt_fld=[])
        for it in fld_lst:
            fld = isinstance(it, basestring) and self.get_field(it) or it
            selector = (fld._table is self.own) and 'own_fld' or 'opt_fld'
            ret[selector].append(fld)
        return ret


    def select(self, query, *fld_lst, **kwargs):
        db = self.db
        fld_opt_lst = self._get_field_opt_lst(fld_lst)
        left = kwargs.pop('left', [])
        left.extend(self.join_opt(*fld_opt_lst['opt_fld']))
        rows = self.db(q).select(*fld_opt_lst['own_fld'], left = left, **kwargs)
        return rows

    def select_vw_agg(self, query, *fld_lst, **kwargs):
        db = self.db
        ids_sel = db(query)._select(self.view_json.id)
        rows = self.db(self.view_agg.id.belongs(ids_sel)).select(*fld_lst, **kwargs)
        return rows


    def _split_args(self, kwargs):
        own_args = {}
        opt_args = {}

        for arg in kwargs:
            frst, sec = _SPLIT_PAIR.findall(arg)[0]
            if not sec:
                if frst in self.own.fields:
                    own_args[frst] = kwargs[arg]
            elif frst in self.option:
                if sec=='*':
                    opt_args[self.option[frst]] = kwargs[arg]
                else:
                    if not self.option[frst] in opt_args:
                        opt_args[self.option[frst]] = {}
                    opt_args[self.option[frst]][sec] = kwargs[arg]
        return dict(own_args = own_args, opt_args = opt_args)




    @_unlock_
    def insert(self, **kwargs):
        ret = Storage()
        if self.parent:
            kwargs[self.parent.D_field.name] = self.D_value
            ret.parent = self.parent.insert(**kwargs)
            kwargs['id'] =  ret.parent.own
        splited_args = self._split_args(kwargs)
        id = self.own.insert(**splited_args['own_args'])
        opt_args = splited_args['opt_args']
        for opt_tbl in opt_args:
            rows_to_insert = opt_args[opt_tbl]
            rows_to_insert = isinstance(rows_to_insert, (list, tuple)) and rows_to_insert \
                            or (rows_to_insert,)
            own_FK_name = opt_tbl._entopt.own_FK.name
            ret[opt_tbl._tablename] = []
            for row in rows_to_insert:
                if self.is_all_null(row,['id', own_FK_name]):
                    continue
                row.pop('id', None)
                row[own_FK_name] = id
                ret[opt_tbl._tablename].append( opt_tbl.insert(**row) )
        ret.own = id
        return ret


    def _select_tmp_ids():
        return self.db(self.db.tmp_ids)._select()

    @_unlock_
    def update_many(self, q, del_insert = False, **kwargs):
        ret = Storage()
        if self.parent:
           ret.parent = self.parent.update_many(q, del_insert, **kwargs)

        self._write_history(q)
        db = self.db
        #del_insert = kwargs.pop('del_insert', None)
        pg_com = db.executesql
        pg_com('CREATE TEMP TABLE  IF NOT EXISTS  tmp_ids (id bigint primary key);')
        pg_com(' TRUNCATE tmp_ids;')
        # select ids into temp
        sel_str = db(q)._select(self.own._id)
        save_str = ' INSERT INTO tmp_ids (%s);'%sel_str[:-1]
        pg_com(save_str)
        splited_args = self._split_args(kwargs)



        # update own
        sel_ids = 'select tmp_ids.id from tmp_ids;'
        ret.own = db(self.own.id.belongs(sel_ids)).update(**splited_args['own_args'])

        # update opt
        opt_args = splited_args['opt_args']

        for opt_tbl in opt_args:
            own_FK_name = opt_tbl._entopt.own_FK.name
            row_to_update = opt_args[opt_tbl]
            if opt_tbl._entopt.type == 'list':
            #if isinstance(row_to_update, (list, tuple)):
                if not del_insert:
                    raise RuntimeError('Can\'t update list option \'%s\' by query, set del_insert=True'%opt_tbl._tablename)
                else:
                    ids = db().select(db.tmp_ids.id)
                    ret_del_ins = ret[opt_tbl._tablename] = Storage()
                    ret_del_ins.deleted = db(opt_tbl._entopt.own_FK.belongs(sel_ids)).delete()
                    ret_del_ins.inserted_ids = []
                    row_to_ins=[r for r in row_to_update if not self.is_all_null(r, [own_FK_name, 'id'])]
                    for rid in ids:
                        for r in row_to_ins:
                            r.pop('id', None)
                            r[own_FK_name] = rid.id
                            ret_del_ins.inserted_ids.append(opt_tbl.insert(**r))
            else:
                ret_upd_ins =  ret[opt_tbl._tablename] = Storage()
                ret_upd_ins.updated = db(opt_tbl[own_FK_name].belongs(sel_ids)).update(**row_to_update)
                ret_upd_ins.inserted_ids=[]
                ret_upd_ins.deleted=[]
                if ret[opt_tbl._tablename] != db(db.tmp_ids).count():
                    #preform insert
                    ids= db(opt_tbl[own_FK_name]==None).select(db.tmp_ids.id, left = opt_tbl.on(opt_tbl[own_FK_name]==db.tmp_ids.id))
                    for r in ids:
                        row_to_update[own_FK_name] = r.id
                        ret_upd_ins.inserted_ids.append(opt_tbl.insert(**row_to_update))
                #delete nulls rows
                fld_lst= [f for f in  opt_tbl if f is not opt_tbl._entopt.own_FK]
                q_to_del = (fld_lst[0]==None) | ((fld_lst[0]==''))
                q_to_del=reduce( lambda q, f: q & ((f==None) | (f=='')) , fld_lst[1:] , q_to_del )
                ret_upd_ins.deleted = db(q_to_del).delete()
        return ret

    @staticmethod
    def is_all_null(rec, ex_fld_lst, nulls=(None, '')):
        return  not [f for f in rec if f not in ex_fld_lst and rec[f] not in nulls ]

    @_unlock_
    def update(self, id, **kwargs):
        ret = Storage()


        if self.parent:
           ret.parent = self.parent.update(id,**kwargs)

        self._write_history(id)
        db = self.db
        splited_args = self._split_args(kwargs)

        # update own
        if splited_args['own_args']:
            ret.own = db(self.own.id==id).update(**splited_args['own_args'])

        # update opt
        opt_args = splited_args['opt_args']
        if opt_args:
            for opt_tbl in opt_args:
                rows_to_update = opt_args[opt_tbl]
                if not rows_to_update:
                    continue

                rows_to_update = isinstance(rows_to_update, (list, tuple)) and rows_to_update \
                                or (rows_to_update,)
                own_FK_name = opt_tbl._entopt.own_FK.name
                ret_opt = ret[opt_tbl._tablename] = Storage(upd_ids=[], del_ids=[], ins_ids=[])
                for row in rows_to_update:
                    row[own_FK_name] = id
                    rec_id = row.get('id', None) or (opt_tbl._entopt.type=='one' and id)
                    rec = opt_tbl(rec_id)
                    if rec: # delete or update
                        rec = rec.as_dict()
                        if not rec:
                            raise RuntimeError('option update err: '+ opt_tbl._tablename+'[%s]'%rec_id+' - not found')
                        if rec[own_FK_name]!=id:
                            raise RuntimeError('option update err: '+ opt_tbl._tablename+'[%s]'%rec_id+' - has alien FK')
                        rec.update(row)
                        if  self.is_all_null(rec, ('id', own_FK_name)):
                            db(opt_tbl._id==rec_id).delete()
                            ret_opt.del_ids.append(rec_id)
                        else:
                            db(opt_tbl._id==rec_id).update(**rec)
                            ret_opt.upd_ids.append(rec_id)
                    elif not self.is_all_null(row, ('id', own_FK_name)): # insert
                        ret_opt.ins_ids.append(opt_tbl.insert(**row))
        return ret

    def create_all_views(self, schema='public',  migrate=False):
        self.create_view(schema=schema,  migrate=migrate)
        self.create_view_json(schema=schema,  migrate=migrate)
        self.create_view_agg(schema=schema,  migrate=migrate)
        self.create_view_join_parent(schema=schema,  migrate=migrate)

    @staticmethod
    def init_cls(db):

        db.define_table('tmp_ids',
            Field('id', 'id'), migrate=False
            )


    def __lock__(self, *a):
        if self._is_locked_:
            raise RuntimeError('Attempt to direct insert/update/delete on Table with history')



    def _lock_table_(self, t):
        t._before_insert.append(self.__lock__)
        t._before_update.append(self.__lock__)
        t._before_delete.append(self.__lock__)


    def def_history(self, schema = 'history', migrate=None):
        if not self.view_agg:
            raise RuntimeError('Definition of history-table requires view_agg has been defined')

        db = self.db
        hist_tbl_name = self.own._tablename + '_history'
        hist_tbl_rname = schema +'.'+ hist_tbl_name
        hist_FK_name = self.history_FK_name = self.own._tablename+'_id'

        hist_flds=[]
        for f in self.view_agg:
            if f is not self.view_agg._id:
                hist_flds.append(f.clone(unique = False))
        hist_flds.append(Field('audit_dtm', 'datetime', default= current.request.now))

        db.define_table(hist_tbl_name,
                        #Field(hist_FK_name, 'bigint'), #'reference '+self.own._tablename), - bug in web2py
                        Field(hist_FK_name, 'reference '+self.own._tablename),
                        *hist_flds,
                        rname = hist_tbl_rname,
                        migrate = migrate)

        self.history = db[hist_tbl_name]

    def _get_id_field(self, q):
        db = self.db
        tables = db._adapter.tables(q)
        for t in tables:
            if self.table_by_veiw[t] and self.table_by_veiw[t] is self.own:
                break
        return db[t]._id

    def _write_history(self, q_or_id):

        db = self.db
        src_tbl = self.view_agg

        id = isinstance(q_or_id, (int, long)) and q_or_id or None
        if id:
            q = src_tbl._id==id
            q_for_upd = self.own._id == id
        else:
            q = q_or_id
            q_for_upd =  self.own._id.belongs(db(q)._select(self._get_id_field(q)))

        db(q_for_upd).select(for_update=True)

        if not self.tracking:
            return
        if not self.history:
            raise RuntimeError('Trying backup record but history-table isn\'t defined')

        sql_ins = 'INSERT INTO %(history)s (%(h_flds_names)s) ( %(select)s )'
        flds_lst = []
        sql_args = Storage(
                        history = self.history._rname,
                        h_flds_names = [],
                        select = ''
                        )
        for f in self.view_agg:
            flds_lst.append(f)
            if f is not src_tbl._id:
                sql_args.h_flds_names.append(f.name)
            else:
                sql_args.h_flds_names.append(self.history_FK_name)

        import datetime as dt
        sql_args.h_flds_names.append(self.history.audit_dtm.name)
        flds_lst.append(" TIMESTAMP '%s' AS audit_dtm " % (dt.datetime.now())) #request.now !!!!!!!!!!!!!!!!!!!!!!!!!!

        sql_args.h_flds_names = ','.join(sql_args.h_flds_names)
        sql_args.select = db(q)._select(*flds_lst)[:-1]
        db.executesql(sql_ins % sql_args)




    def __init__(self, own_tbl, D_field=None, parent=None, D_value=None, tracking=None):
        db = self.db = own_tbl._db
        self._is_locked_ = False

        self.tracking = tracking
        if tracking:
            self._is_locked_ = True
            self._lock_table_(own_tbl)
        self.history = None # should be defined by def_history

        self.D_field = D_field and own_tbl[D_field]
        self.own = own_tbl
        self.option = Storage()
        self.vw_opt_fields = []
        self.vw_json_opt_fields = []

        self.vw_name = self.own._tablename+'_vw'
        self.vw_json_name = self.own._tablename+'_json_vw'
        self.vw_agg_name = self.own._tablename+'_vw_agg'
        self.vw_join_parent_name = self.own._tablename+'_jn_prnt'

        self.view = None
        self.view_json = None
        self.view_agg = None
        self.view_join_parent = None

        Entity.table_by_veiw[own_tbl._tablename] = own_tbl

        self.parent = parent
        if parent:
            if D_value is not None:
                self.D_value = D_value
            else:
                raise RuntimeError('D_value couldn\'t be None if parent is specified')
        #self.relation = relation





class Relation(Entity):

    def __init__(self, tables_list, *flds, **kwargs ):
        self.rel_tables = tables_list
        db = self.db = tables_list[0]._db
        if kwargs.get('name', None) is None:
            tbls_names=[t._tablename for t in tables_list]
            name = '__'.join(tbls_names)
            schema = kwargs.pop('schema', None)
            if schema and not kwargs.get('rname', None):
                kwargs['rname'] = schema+'.'+kwargs['rname']

        FK_flds = []
        for t_name in tbls_names:
            fk =  Field(t_name+'_id', 'reference '+ t_name )
            FK_flds.append(fk)
        all_flds = FK_flds + list(flds)

        ent_args = {}
        for arg in Entity._init_args:
            ent_args[arg] = kwargs.pop(arg, None)

        def_PG_table(db, name, *all_flds, **kwargs)
        Entity.__init__(self, db[name], **ent_args)

    @staticmethod
    def FK_name_by_table(tbl):
        return Entity.table_by_veiw(tbl._tablename)._tablename+'_id'

    def own_FK_name_by_table(self, tbl):
        root_tbl = Entity.table_by_veiw[tbl._tablename]
        if root_tbl in self.rel_tables:
            return root_tbl._tablename+'_id'
        else:
            return None
            #raise RuntimeError('There isn\'t table: %s in relation %s' % (root_tbl._tablename, self.own._tablename))

    def get_join(self, tables):
        join_lst=[]
        for t in tables:
            fk_name = self.own_FK_name_by_table(t)
            if fk_name:
                join_lst.append(t.on(t._id == self.own[fk_name]))
        return join_lst

    def _get_tables(self, q, flds, *opt):
        db = self.db
        ret_tables = set(db._adapter.tables(q, *opt))
        for f in flds:
            if hasattr(f, '_table'):
                ret_tables.add(f._table)
            elif hasattr(f, '_tables_list'):
                ret_tables.update(f._tables_list)
        #rel_tables.intersection_update(self.rel_tables)
        return ret_tables

    def _get_select_args(self,  q, flds, kwargs):
        db = self.db
        join = kwargs.get('join', [])
        join.extend(self.get_join(
                                self._get_tables(q,
                                                    flds,
                                                    kwargs.get('join',None),
                                                    kwargs.get('left',None),
                                                    kwargs.get('orderby',None),
                                                    kwargs.get('groupby',None),
                                        )
                                  )
                    )
        kwargs['join'] = join
        return Storage(flds=flds, kwargs=kwargs)

    def select(self, q, *flds, **kwargs):
        db = self.db
        sel_args = self._get_select_args(q, flds, kwargs)
        return db(q).select(*sel_args.flds, **sel_args.kwargs)

    def _select(self, q, *flds,  **kwargs):
        db = self.db
        sel_args = self._get_select_args(q, flds, kwargs)
        return db(q)._select(*sel_args.flds, **sel_args.kwargs)


def main_0():
    migrate=True

    db = DAL('postgres://sqladmin:klop@localhost/Lean',pool_size=5,check_reserved=['postgres'], folder=None, bigint_id=True
              ) #fake_migrate_all=True migrate_enabled=True
    db.executesql('SET search_path TO public, admins, model_gen, history, tasks, trac;')
    db.define_table('person',
                Field('id',
                      type = 'id',
                      required = True,
                ),
                Field('name',
                      type = 'string',
                      required = True,
                ),
                Field('surname',
                      type = 'string',
                      required = True,
                ),
                Field('patroname',
                      type = 'string',
                      required = True,
                ),
                Field('is_hidden',
                      type = 'boolean',
                      default = False,
                      required = True,
                ),
                migrate=False
    )



    band_type = Enum(db, 'band_type', code_field=True, migrate=False)
    div_type = Enum(db, 'division_type', code_field=True, migrate=False)
    div_fntype = Enum(db, 'division_fntype', code_field=True, migrate=False)


    def_PG_table(db, 'band',
                Field('name'),
                ref_field(band_type, nocache=True),
                alt_key=['name', band_type.FK_name],
                migrate=False)

    def_PG_table(db, 'a_comp',
                Field('id', 'reference a_bands'),
                Field('comp_name'),
                primarykey=['id'],
                migrate=False)

    def_PG_table(db, 'a_dept',
                Field('id', 'reference a_bands'),
                Field('dept_name'),
                primarykey=['id'],
                migrate=False)


    def_PG_table(db, 'a_men',
                Field('name'),
                migrate=False)


    Entity.init_cls(db)
    band_ent = Entity(db.a_bands, D_field=band_type.FK_name, tracking=True)
    comp_ent = Entity(db.a_comp, parent = band_ent, D_value=1)
    dept_ent = Entity(db.a_dept, parent = band_ent, D_value=2)
    men_ent= Entity(db.a_men )




    band_ent.def_option('region',Field('name'))
    band_ent.def_option('brunch', Field('id'), Field('name'))
    """
    dept_ent.update(10, dept_name='вапвап', **{'region.name':'dept_ert',
                        'brunch.*':[
                                    {'id':14, 'name':''},
                                    ]


    })
    dept_ent.insert(dept_name='вапвап new', **{'region.name':'dept_ert_new',
                        'brunch.*':[
                                    {'id':14, 'name':'new34'},
                                    ]}
                                    )


    comp_ent.insert(name='prnt_name_cmp8', comp_name='comp_name_8',
                    **{'brunch.*':[
                                    {'name':'brunch_name6'},
                                    {'name':'brunch_name7'}
                                    ]
                      }
                    )
    """
    band_ent.create_all_views(migrate=True)
    comp_ent.create_all_views(migrate=True)
    dept_ent.create_all_views(migrate=True)

    men_ent.def_option('age', Field('age', 'integer'))
    men_ent.create_all_views(migrate=True)

    #men_ent.insert(name='Петя fg', **{'age.age':20} )
    band_ent.def_history()
    band_ent._write_history(1)


    band_men = Relation([db.a_bands, db.a_men], Field('men_role'), alt_key=['a_bands_id', 'a_men_id'])
    #band_men.insert(a_bands_id=1, a_men_id=1)
    #band_men.insert(a_bands_id=1, a_men_id=2 )
    #band_men.insert(a_bands_id=2, a_men_id=2 )



    r= band_men._select(None, db.a_men_vw_agg.id, json_agg_sql([db.a_men_vw_agg.name, db.a_bands_vw_agg.name], as_alias='ff'),
                    groupby=[db.a_men_vw_agg.id] )





    #band_ent.create_view( migrate=True )
    #dept_ent.insert(name='prnt_dpt_name', dept_name='dept_name')





    #enm_c=Enum(db, 'atstc_type', code_field=True, migrate=True)
    #enm_clr=Enum(db, 'aclr_type', code_field=True, migrate=True)
    #enm_clr.own.insert(id=1, name='Red', code='#red')
    #enm_clr.own.insert(id=2, name='Blue', code='#bl')
    #enm_clr.own.insert(id=3, name='Green', code='#gr')

    """
    db.define_table('a_entst',
                Field('name'),
                ref_field(enm_clr, nocache=True),
                migrate=True)


    ent= Entity(db.a_entst)
    ent.def_option('opt', Field('color'),  Field('shape') , migrate=True)
    ent.def_option('plan', Field('start', 'date'),  Field('finish', 'date') , migrate=True)
    ent.def_option('opt_lst', Field('id'), Field('this'),  Field('that') , migrate=True)
    #db.plan._entopt.vw_pref='pln'
    #db.plan.start._entopt=Storage(vw_name='start_')
    ent.create_view( migrate=True )
    ent.create_view_json( migrate=True)
    ent.create_view_agg(migrate=True)

    r = ent.update_many(db.a_entst._id<5, del_insert = True,
                    **{
                            'clr':2,
                            'opt.color':None,
                            'opt.shape':'',
                            'opt_lst.*': [dict(id=30, this='', that=''), dict(id=30, this='df0', that='that30')]

                    })

    #ent.update(7, **{'name':'Val', 'opt_lst.*': [dict(id=2 , this='', that='')
    #                                              ]})
    #ent.insert(**{'opt.color':'red'})
    """

    db.commit()


    rows = db().select(comp_ent.view_join_parent.ALL)
    print rows.as_list()
    #db.person._entopt=Storage(vw_pref='prsn')
    #db.person.name._entopt=Storage(vw_name='name')
    #g=Entity._vw_opt_fld_name(db.person.surname)

    pass


def qq():
    db = DAL('postgres://sqladmin:klop@localhost/Lean',pool_size=5,check_reserved=['postgres'], folder=None, bigint_id=True
              ) #fake_migrate_all=True migrate_enabled=True
    db.executesql('SET search_path TO public, admins, model_gen, history, tasks, trac;')

    db.define_table('a_tbl', Field('name'))
    db.define_table('b_tbl', Field('id', 'reference a_tbl') ,Field('name'), primarykey=['id'])
    db.define_table('c_tbl', Field('id', 'reference b_tbl') ,Field('name'), primarykey=['id'])




def  main():
    qq()

if __name__ == '__main__':
    main()
