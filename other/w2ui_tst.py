#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Val
#
# Created:     27.04.2016
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
    auth = Auth()


from gluon.html import *
from gluon.tools import Storage
import gluon.contrib.simplejson as sj
import re
import time
from entity import *
from jq_param2storage_w2p import jq_param_w2p
from smart_storage import Smart_Storage, Json_Args
#from w2ui_kit_rs import *




def JS_fun(*args_lst):
    """
    wraps fun_body in anonymous JS in ():
        (
            function(args_lst[0], args_lst[1], ...)
                    {   fun_body;   }
        )
    """
    def _inner(*body):
        return "(function(%s){ %s ;})" % (','.join(args_lst), '\n    '.join(body))
    return _inner

a= JS_fun('a', 'b')(
        'var sum = a+b;' ,
        'console.log(sum);',
        'return sum'
)


class _W2ui_option(Smart_Storage):
    __repr__ = lambda self: '<_W2ui_option %s>' % dict.__repr__(self)

    def __init__(self, name, **kwargs ):
        Smart_Storage.__init__(self, name=name, **kwargs )
        if 0: # just for autocomplite
            self.name=''
            self.box=''
            self.style=''

    def w2ui_name(self):
        return 'w2ui.%s' % self.name



class W2ui_App_Layout(_W2ui_option):
    def __init__(self,
                    name = 'app_layout',
                    box='main_box',
                    pages_data = None,
                    common_panels =None,
                    start_page =None,
                    **kwargs):

        common_panels = common_panels or Smart_Storage()
        _W2ui_option.__init__(self, name, box=box, **kwargs)
        self.pages_data = pages_data or Smart_Storage()
        self.start_page = start_page
        self.common_panels = common_panels

    def xml(self):
        return self.__json__()


    #------  Panel_Holder-------------------
    class Panel_Holder(Smart_Storage):
        def __init__(self,
                        name,
                        type ='html',
                        refresh ='static',
                        content = None,
                        url = None,
                        method = None,
                        post_data = None
                        ):
            Smart_Storage.__init__(self)
            self.name = name
            self.type = type
            self.refresh = refresh
            self.content = content
            self.url = url
            self.method= method
            self.post_data= post_data
            if 0:
                self.panel_opt = W2ui_App_Layout.Panel_Opt()
            #-------------------------------

        def __json__(self, **kwargs):
            for k, v in self.items():
                if v is None:
                    del self[k]
            return Smart_Storage.__json__(self, **kwargs)


    #------  Content-------------------
    class Content_Object(Smart_Storage):
        def __init__(self, obj_init, init_args):
            Smart_Storage.__init__(self, obj_init=obj_init, init_args=init_args)
            if 0:
                self.obj_init = None
                self.init_args = None


    #------  Panel_Opt-------------------
    class Panel_Opt(Smart_Storage):
        def __init__(self, **kwargs):
            Smart_Storage.__init__(self, **kwargs)
            if 0:
                self.title= ''
                self.size = 100
                self.minSize = 20
                self.maxSize = False
                self.hidden = False
                self.resizable = True
                self.overflow = 'auto'
                self.style = ''
                self.content = ''
                self.tabs = None
                self.toolbar = None

    class Page_Data(Smart_Storage):
          def __init__(self,  panels=None):
            panels = panels or Smart_Storage()
            Smart_Storage.__init__(self, panels=panels)


class W2ui_grid(_W2ui_option):
    def __init__(self, name,  **kwargs):
        _W2ui_option.__init__(self, name=name, **kwargs)
        self.show = W2ui_grid.Show()
        self.columns = self.columns or []
        self.recid ='id'

        if 0:
            self.routeData = ''
            self.url= ''
            self.header =''
            self.onAdd = ''
            self.onEdit = ''
            self.onDelete = ''
            self.onSubmit = ''

    class Show(Smart_Storage):
        #def __init__(self,  **kwargs):
            if 0:
                self.header         = False  # indicates if header is visible
                self.toolbar        = False  # indicates if toolbar is visible
                self.footer         = False  # indicates if footer is visible
                self.columnHeaders  = True   # indicates if columns is visible
                self.lineNumbers    = False  # indicates if line numbers column is visible
                self.expandColumn   = False  # indicates if expand column is visible
                self.selectColumn   = False  # indicates if select column is visible
                self.emptyRecords   = True   # indicates if empty records are visible
                self.toolbarReload  = True   # indicates if toolbar reload button is visible
                self.toolbarColumns = True   # indicates if toolbar columns button is visible
                self.toolbarSearch  = True   # indicates if toolbar search controls are visible
                self.toolbarAdd     = True   # indicates if toolbar add new button is visible
                self.toolbarEdit    = True   # indicates if toolbar edit button is visible
                self.toolbarDelete  = True   # indicates if toolbar delete button is visible
                self.toolbarSave    = True   # indicates if toolbar save button is visible
                self.selectionBorder= True   # display border arround selection (for selectType = 'cell')
                self.recordTitles   = True   # indicates if to define titles for records
                self.skipRecords    = True    # indicates if skip records should be visible
                self.columns=[]



    class Column(Smart_Storage):

        def __init__(self, field, **kwargs):
            Smart_Storage.__init__(self, field=field, **kwargs)
            self.size='5%'
            self.__formatters__['render'] = '%(v)s'

            if 0:
                self.editable  = Smart_Storage()      # editable object if column fields are editable
                self.caption        = ''     # column caption
                self.field          = ''     # field name to map column to a record
                self.size           = None   # size of column in px or %
                self.min            = 15     # minimum width of column in px
                self.max            = None   # maximum width of column in px
                self.gridMinWidth   = None   # minimum width of the grid when column is visible
                self.hidden         = False  # indicates if column is hidden
                self.sortable       = False  # indicates if column is sortable
                self.searchable     = False  # indicates if column is searchable, bool/string= int,float,date,...
                self.resizable      = True   # indicates if column is resiable
                self.hideable       = True   # indicates if column can be hidden
                self.attr           = ''     # string that will be inside the <td ... attr> tag
                self.style          = ''     # additional style for the td tag
                self.render         = None   # string or render function
                self.title          = None   # string or function for the title property for the column cells









def obj_html():
    time.sleep(1)
    ret = DIV(SPAN('привет HTML'), SPAN('posted: '+ str(request.vars.v))).xml()
    return ret



#@auth.requires_login()
@auth.requires_signature()
def obj_json():
    session.forget(response)
    #time.sleep(2)
    data = Smart_Storage()
    data.new = True
    data.obj_init = '$.Obj_Tst'
    data.init_args = dict(content = DIV(SPAN('привте json'), SPAN('posted: '+ str(request.vars.v))).xml() )
    return data


def obj_holder_json_tst():
    data = Smart_Storage()
    data.type='json'
    data.refresh='static'
    data.url = URL('obj_json.json', user_signature=True)
    data.method = 'POST'
    return data



def side_bar_opt():
    ret =Smart_Storage()
    ret.name= 'nav_bar'
    nodes = [
            Smart_Storage(id='n1', text='n1_txt' ),
            Smart_Storage(id='n2', text='n2_txt' ),
            Smart_Storage(id='page_3', text='pg3', pg_name ='page_3' )
            ]
    nodes[0].nodes=[
                    Smart_Storage(id='page_1', text='page_1', pg_name ='page_1' ),
                    Smart_Storage(id='page_2', text='page_2', pg_name ='page_2'  )
                    ]

    ret.nodes = nodes
    return ret

def side_bar_3():
    ret =Smart_Storage()
    ret.name= 'pg3_nav_bar'
    nodes = [
            Smart_Storage(id='page_2', text='pg2_n1_txt', pg_name ='page_2'  ),
            Smart_Storage(id='page_3', text='pg3', pg_name ='page_3' ),
            Smart_Storage(id='page_1', text='pg1', pg_name ='page_1' )
            ]

    ret.nodes = nodes
    return ret


def page_1():
    pg_data  = W2ui_App_Layout.Page_Data()
    #pg_data.panels.main = W2ui_App_Layout.Panel_Holder(name = 'com_panel_1')

    #side bar
    nav_bar = W2ui_App_Layout.Panel_Holder('nav_bar')

    #obj_tst =  W2ui_App_Layout.Panel_Holder('obj_tst')
    obj_tst  = obj_holder_json_tst()
    obj_tst.name = 'obj_tst'
    obj_tst.panel_opt = W2ui_App_Layout.Panel_Opt()
    obj_tst.panel_opt.size = 200

    #main
    main = W2ui_App_Layout.Panel_Holder('pg1_main')
    main.type = 'html'
    main.content = DIV('Привет from page 1').xml()
    #set page panels
    pg_data.panels.main = main
    pg_data.panels.left = nav_bar
    pg_data.panels.top = W2ui_App_Layout.Panel_Holder('top_bar')
    #pg_data.panels.right = obj_tst
    return pg_data

def w2ui_field(dal_fld):
    if 0:
        dal_fld = Field()
    def w2ui_field_type(dal_type):
        dal_type = dal_type.split(' ', 1)[0].split(':', 1)[0].split('[',1)[0].strip()
        dal_w2ui =   Storage({
        'string': 'text',
        'text':'textarea',
        'datetime': 'date',
        'integer': 'int',
        'reference': 'int',
        'boolean': 'checkbox',
        'double': 'float',
        'decimal': 'float'
        })
        return dal_w2ui[dal_type] or dal_type


    w2ui_fld = Smart_Storage(name= dal_fld.name)
    w2ui_fld.type = w2ui_field_type(dal_fld.type) or dal_fld.type
    w2ui_fld.required =  dal_fld.required
    w2ui_fld.html = dict(caption = dal_fld.label or dal_fld.name)
    return w2ui_fld


def company_grid(a=None):
    Col = Smart_Storage
    columns=[
        Col( field='id', caption='ID', size='50px'),
        Col( field='code', caption='Ник', size='50px'),
        Col( field='name', caption='Нименование', size='50px')
        ]
    #ret= W2ui_grid('grid', columns, URL('comp_rec.json'))

    grid= W2ui_grid(name='grid', columns = columns, url= URL('comp_rec.json'))
    grid.show.toolbar = True
    grid.show.toolbarAdd  = True
    grid.show.toolbarEdit  = True

    #add form
    w2ui_frm = Smart_Storage()
    w2ui_frm.name = 'grid_new_rec'
    w2ui_frm.postData =  Smart_Storage(_formkey = '123')
    w2ui_frm.fields=[]
    for fld in db.company:
        w2_fld = w2ui_field(fld)
        w2ui_frm.fields.append(w2_fld)
        if fld.type  in ['datetime']:
            w2_fld.writable = False

    w2ui_frm.url = URL('add_company_rec.json')
    w2ui_frm.actions ='default'
    #---- my prop -----
    w2ui_frm.submit_on_enter = True
    w2ui_frm.on_success=[JS_fun('data')('console.log("on_success data:",data)')]
    w2ui_frm.on_OK_close = True
    #w2ui_frm.on_close_destroy = True
    grid._onAdd = Smart_Storage(w2form = w2ui_frm)
    grid._onEdit = Smart_Storage(w2form = w2ui_frm)

    return grid

def comp_rec():
    js_vars = jq_param_w2p(request.body)
    if js_vars and js_vars.sort:
        sort_fld = js_vars.sort[0].field
        orderby = sort_fld =='recid' and db.company._id or db.company[sort_fld]
        orderby = js_vars.sort[0].direction=='asc' and orderby or ~orderby
    else:
        orderby = company.own.id

    ret = Storage(
    status= 'success',
    total=0
    )

    rows = db(db.company).select(orderby=orderby)
    ret.total = len(rows)
    ret.records= rows #.as_json()
    print 'comp_rec ', js_vars
    return ret

def add_company_rec():
    print request.vars
    js_vars = jq_param_w2p(request.body)
    print js_vars
    ret=Smart_Storage()
    ret.status = 'success'
    #ret.message = 'OK'
    return ret


@auth.requires_signature()
def grid_prox():
    data = Smart_Storage()
    data.obj_init = JS_fun('args', 'obj_holder')('var ret = new window.app.Grid(args, obj_holder); return ret.grid_obj;')
    data.init_args = dict(w2grid=company_grid())
    """
    data.callback = Smart_Storage()
    data.callback.obj_init = '$.FlyForm'
    data.callback.init_args = dict(w2form = w2ui_frm , options=dict(height=1500))
    data.callback.new = True
    """
    return data


def page_2():
    pg_data  = W2ui_App_Layout.Page_Data()
    #pg_data.panels.main = W2ui_App_Layout.Panel_Holder(name = 'com_panel_1')

    #side bar
    nav_bar = W2ui_App_Layout.Panel_Holder('nav_bar')

    #obj_tst =  W2ui_App_Layout.Panel_Holder('obj_tst')
    obj_tst  = obj_holder_json_tst()
    obj_tst.name = 'obj_tst2'
    obj_tst.panel_opt = W2ui_App_Layout.Panel_Opt()
    obj_tst.panel_opt.size = 200
    obj_tst.refresh = 'dynamic'

    main = W2ui_App_Layout.Panel_Holder('pg2_main')
    main.type = 'json'
    main.url = URL( 'grid_prox.json', user_signature = True)
    main.method = 'POST'
    main.refresh = 'static'
    #obj_init = JS_fun('return $().w2grid(opt);',['opt'])
    #init_args = company_grid()
    #main.content =  W2ui_App_Layout.Content_Object(obj_init, init_args)

    #set page panels

    pg_data.panels.left = nav_bar
    pg_data.panels.right = obj_tst
    pg_data.panels.main = main
    pg_data.panels.top = W2ui_App_Layout.Panel_Holder('top_bar')
    return pg_data


def page_3():
    pg_data  = W2ui_App_Layout.Page_Data()
    #pg_data.panels.main = W2ui_App_Layout.Panel_Holder(name = 'com_panel_1')

    #side bar
    nav_bar = W2ui_App_Layout.Panel_Holder('pg3_nav_bar')
    nav_bar.type = 'json'
    nav_bar.panel_opt = W2ui_App_Layout.Panel_Opt(size=300)

    """
    obj_init = JS_fun(''.join([ 'var d=$.Deferred();',
                               'setTimeout(function(){ d.resolve($().w2sidebar(opt)) }, 5000);',
                               'return d;']),
                        ['opt'])
    """
    obj_init = JS_fun('opt')('return $().w2sidebar(opt);')

    nav_bar.content =  W2ui_App_Layout.Content_Object(obj_init = obj_init , init_args= side_bar_3())


    #obj_tst =  W2ui_App_Layout.Panel_Holder('obj_tst')
    html_tst  = W2ui_App_Layout.Panel_Holder('obj_html')
    html_tst.type = 'html'
    html_tst.method = 'GET'
    html_tst.url = 'obj_html'
    html_tst.refresh = 'static'
    html_tst.panel_opt = W2ui_App_Layout.Panel_Opt(size= 200)
    #set page panels
    main = W2ui_App_Layout.Panel_Holder('pg3_main')
    main.type = 'html'
    main.content = DIV('page_3').xml()

    pg_data.panels.left = nav_bar
    pg_data.panels.right = html_tst
    pg_data.panels.main= main
    pg_data.panels.top = W2ui_App_Layout.Panel_Holder('top_bar')

    return pg_data


def log_out():
    auth.logout()
    #print 'logout'


def login():
    #------ self-redirection from onaccept/onfail from auth.login()  ----------
    if request.args(0):
        ret = Smart_Storage()
        ret.postData = dict(_formkey = request.vars.pop('_formkey', None))
        ret.record  = dict(username = request.vars.username)
        if request.args(0)=='OK':
            ret.status = 'success'
            person_rec = person.own(auth.user_id)
            #ret.message = 'Welcome %s %s'% (person_rec.name, person_rec.patroname )
            ret.message = 'Welcome %s'% auth_user(auth.user_id).username
            #ret.next = URL(...)
        elif request.args(0)=='error':
            ret.status = 'error'
            ret.message = 'Не распознано'
        return ret

    #------ parsing ajax-request and setting post_vars (auth.login reads them) ----------
    jq_vars = jq_param_w2p(request.body)
    if jq_vars.cmd == 'save-record':
        request.post_vars.clear()
        request.post_vars.update(jq_vars.record)
        request.post_vars._formkey = jq_vars._formkey
        request.post_vars._formname = jq_vars.name

    #------ setting self-redirection ----------
    auth.settings.login_onaccept = \
            lambda frm: redirect(URL('login.json', args=['OK'],
                                     vars = dict(_formkey =  frm.formkey, **frm.vars)
                                     ),
                                 client_side=False
                                )
    auth.settings.login_onfail = \
            lambda frm: redirect(URL('login.json', args=['error'],
                                     vars = dict(_formkey =  frm.formkey, **frm.vars)
                                     ),
                                 client_side=False
                                 )
    login_frm = auth.login()

    # code below will be executed if only auth.login() doesn't accept post_vars
    # ---------- create own response form -------------------------
    if not jq_vars.cmd:
        w2ui_frm = Smart_Storage()
        w2ui_frm.name = login_frm.formname
        w2ui_frm.postData =  Smart_Storage(_formkey = login_frm.formkey)
        w2ui_frm.fields=[]
        for fld_name, label in [['username', 'Пользователь'], ['password', 'Пароль' ]]:
            w2p_fld_attr = login_frm.element('input', _name=fld_name).attributes
            w2ui_fld = Smart_Storage(name = fld_name)
            w2ui_fld.type = w2p_fld_attr['_type']
            w2ui_fld.required = True
            w2ui_fld.html=dict(caption = label)
            w2ui_frm.fields.append(w2ui_fld)
        w2ui_frm.url = URL('login.json')
        w2ui_frm.actions ='default'
        #---- my prop -----
        w2ui_frm.submit_on_enter = True
        w2ui_frm.on_OK_close = True
        w2ui_frm.on_close_destroy = True
        return w2ui_frm
    # --- form didn't accept  - send actual _formkey ------
    else:
        ret = Smart_Storage()
        ret.status = 'error'
        ret.message = 'Сигнатура устарела - попробуйте еще разок'
        ret.postData = Smart_Storage(_formkey = login_frm.formkey)
        ret.record  = dict(username = login_frm.vars.username)
        return ret


def login_holder():
    #time.sleep(2)
    btn_data = Smart_Storage()
    btn_data.obj_init= '$.FlyForm'
    btn_data.init_args = Smart_Storage(w2form=login())
    btn_data.new =True
    return btn_data


def index():
    compile_pyj()
    app_layout = W2ui_App_Layout()
    nav_bar = W2ui_App_Layout.Panel_Holder('nav_bar')
    nav_bar.type='json'
    nav_bar.method = None
    nav_bar.content  = W2ui_App_Layout.Content_Object(obj_init= JS_fun('opt')('return $().w2sidebar(opt);'), init_args= side_bar_opt())
    panel_opt = W2ui_App_Layout.Panel_Opt()
    panel_opt.size=200
    nav_bar.panel_opt = panel_opt

    top_bar = W2ui_App_Layout.Panel_Holder('top_bar')
    top_bar.content = ''

    top_toolbar  =Smart_Storage()
    top_toolbar.name= 'top_toolbar'

    btn_data = Smart_Storage(
                              type='json',
                              refresh='static',
                              url=URL('login_holder.json'),
                              method='POST'
                              )

    log_out_data = [ Smart_Storage(
                              refresh = 'dynamic',
                              method = 'POST',
                              url = URL('log_out'),
                              type='html'
                              ),
                    Smart_Storage(
                              content = Smart_Storage(obj_init= JS_fun('url')('window.location = url;'), init_args = URL('default', 'user')  ),
                              type='json'
                              ),
                     ]


    top_toolbar.items= [
            Smart_Storage(type='spacer'),
            Smart_Storage(type='button', id='btn_login', caption = 'Login', icon='fa fa-star',
                        data= btn_data
                        ),
            Smart_Storage(type='button', id='btn_logout', caption = 'Logout', icon='fa fa-exit',
                        data= log_out_data
                        )
            ]
    top_bar.panel_opt = W2ui_App_Layout.Panel_Opt(toolbar = top_toolbar)
    top_bar.panel_opt.show = Smart_Storage(toolbar=True)
    top_bar.panel_opt.size=33

    app_layout.common_panels.nav_bar = nav_bar
    app_layout.common_panels.top_bar = top_bar

    app_layout.pages_data.page_1 = page_1()
    app_layout.pages_data.page_2 = page_2()
    app_layout.pages_data.page_3 = page_3()
    app_layout.start_page = 'page_1'

    main_box = DIV(_id='main_box', _style='height:900px;')
    return dict(main_box = main_box, w2ui_app_layout = app_layout)

import rs_compiler
def compile_pyj():

    node='C:/Program Files/nodejs/node.exe'
    rs_engine = 'D:/Program Files/RapydScript-master/bin/rapydscript'
    #rs_engine = 'D:/Program Files/repo/rapydscript-ng/bin/rapydscript'

    cc = rs_compiler.rs_compiler(node, rs_engine)
    src= os.path.join(request.folder, 'private')
    dst = os.path.join(request.folder, 'static/js')
    print '----------- beg compile-----------\n'
    print cc.rs_compile_dir(src,dst )
    print '----------- end compile-----------\n'
    return cc


def main():
    pass

if __name__ == '__main__':
    main()
