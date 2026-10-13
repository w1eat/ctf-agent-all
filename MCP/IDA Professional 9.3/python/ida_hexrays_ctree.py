from __future__ import annotations
from sys import version_info as _swig_python_version_info
if __package__ or '.' in __name__:
    from . import _ida_hexrays_ctree
else:
    import _ida_hexrays_ctree
try:
    import builtins as __builtin__
except ImportError:
    import __builtin__


def _swig_repr(self):
    try:
        strthis = 'proxy of ' + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ''
    return '<%s.%s; %s >' % (self.__class__.__module__, self.__class__.
        __name__, strthis)


def _swig_setattr_nondynamic_instance_variable(set):

    def set_instance_attr(self, name, value):
        if name == 'this':
            set(self, name, value)
        elif name == 'thisown':
            self.this.own(value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name),
            property):
            set(self, name, value)
        else:
            raise AttributeError('You cannot add instance attributes to %s' %
                self)
    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):

    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError('You cannot add class attributes to %s' % cls)
    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""

    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)


import weakref
SWIG_PYTHON_LEGACY_BOOL = _ida_hexrays_ctree.SWIG_PYTHON_LEGACY_BOOL
from typing import Tuple, List, Union
import ida_idaapi
import ida_pro
import ida_xref
import ida_typeinf
import ida_idp
import ida_gdl
import ida_hexrays_defs


def _kludge_force_declare_TPopupMenu(arg1: 'TPopupMenu const *') ->None:
    return _ida_hexrays_ctree._kludge_force_declare_TPopupMenu(arg1)


def _kludge_force_declare_mcallinfo_t(arg1: 'mcallinfo_t const *') ->None:
    return _ida_hexrays_ctree._kludge_force_declare_mcallinfo_t(arg1)


class ctree_items_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.ctree_items_t_swiginit(self, _ida_hexrays_ctree.
            new_ctree_items_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_ctree_items_t

    def push_back(self, *args) ->'citem_t *&':
        return _ida_hexrays_ctree.ctree_items_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.ctree_items_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.ctree_items_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.ctree_items_t_empty(self)

    def at(self, _idx: int) ->'citem_t *const &':
        return _ida_hexrays_ctree.ctree_items_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.ctree_items_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.ctree_items_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.ctree_items_t_resize(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.ctree_items_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.ctree_items_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.ctree_items_t_truncate(self)

    def swap(self, r: 'ctree_items_t') ->None:
        return _ida_hexrays_ctree.ctree_items_t_swap(self, r)

    def extract(self) ->'citem_t **':
        return _ida_hexrays_ctree.ctree_items_t_extract(self)

    def inject(self, s: 'citem_t **', len: int) ->None:
        return _ida_hexrays_ctree.ctree_items_t_inject(self, s, len)

    def __eq__(self, r: 'ctree_items_t') ->bool:
        return _ida_hexrays_ctree.ctree_items_t___eq__(self, r)

    def __ne__(self, r: 'ctree_items_t') ->bool:
        return _ida_hexrays_ctree.ctree_items_t___ne__(self, r)

    def begin(self, *args) ->'qvector< citem_t * >::const_iterator':
        return _ida_hexrays_ctree.ctree_items_t_begin(self, *args)

    def end(self, *args) ->'qvector< citem_t * >::const_iterator':
        return _ida_hexrays_ctree.ctree_items_t_end(self, *args)

    def insert(self, it: 'qvector< citem_t * >::iterator', x: 'citem_t'
        ) ->'qvector< citem_t * >::iterator':
        return _ida_hexrays_ctree.ctree_items_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< citem_t * >::iterator':
        return _ida_hexrays_ctree.ctree_items_t_erase(self, *args)

    def find(self, *args) ->'qvector< citem_t * >::const_iterator':
        return _ida_hexrays_ctree.ctree_items_t_find(self, *args)

    def has(self, x: 'citem_t') ->bool:
        return _ida_hexrays_ctree.ctree_items_t_has(self, x)

    def add_unique(self, x: 'citem_t') ->bool:
        return _ida_hexrays_ctree.ctree_items_t_add_unique(self, x)

    def _del(self, x: 'citem_t') ->bool:
        return _ida_hexrays_ctree.ctree_items_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.ctree_items_t___len__(self)

    def __getitem__(self, i: int) ->'citem_t *const &':
        return _ida_hexrays_ctree.ctree_items_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'citem_t') ->None:
        return _ida_hexrays_ctree.ctree_items_t___setitem__(self, i, v)

    def append(self, x: 'citem_t') ->None:
        return _ida_hexrays_ctree.ctree_items_t_append(self, x)

    def extend(self, x: 'ctree_items_t') ->None:
        return _ida_hexrays_ctree.ctree_items_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.ctree_items_t_swigregister(ctree_items_t)


class user_labels_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def at(self, _Keyval: 'int const &') ->'_qstring< char > &':
        return _ida_hexrays_ctree.user_labels_t_at(self, _Keyval)

    def size(self) ->int:
        return _ida_hexrays_ctree.user_labels_t_size(self)

    def __init__(self):
        _ida_hexrays_ctree.user_labels_t_swiginit(self, _ida_hexrays_ctree.
            new_user_labels_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_user_labels_t


_ida_hexrays_ctree.user_labels_t_swigregister(user_labels_t)


class user_unions_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def at(self, _Keyval: 'unsigned long long const &') ->'qvector< int > &':
        return _ida_hexrays_ctree.user_unions_t_at(self, _Keyval)

    def size(self) ->int:
        return _ida_hexrays_ctree.user_unions_t_size(self)

    def __init__(self):
        _ida_hexrays_ctree.user_unions_t_swiginit(self, _ida_hexrays_ctree.
            new_user_unions_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_user_unions_t


_ida_hexrays_ctree.user_unions_t_swigregister(user_unions_t)


class user_cmts_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def at(self, _Keyval: 'treeloc_t') ->'citem_cmt_t &':
        return _ida_hexrays_ctree.user_cmts_t_at(self, _Keyval)

    def size(self) ->int:
        return _ida_hexrays_ctree.user_cmts_t_size(self)

    def __init__(self):
        _ida_hexrays_ctree.user_cmts_t_swiginit(self, _ida_hexrays_ctree.
            new_user_cmts_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_user_cmts_t


_ida_hexrays_ctree.user_cmts_t_swigregister(user_cmts_t)


class user_iflags_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def at(self, _Keyval: 'citem_locator_t') ->'int &':
        return _ida_hexrays_ctree.user_iflags_t_at(self, _Keyval)

    def size(self) ->int:
        return _ida_hexrays_ctree.user_iflags_t_size(self)

    def __init__(self):
        _ida_hexrays_ctree.user_iflags_t_swiginit(self, _ida_hexrays_ctree.
            new_user_iflags_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_user_iflags_t


_ida_hexrays_ctree.user_iflags_t_swigregister(user_iflags_t)


class cinsnptrvec_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.cinsnptrvec_t_swiginit(self, _ida_hexrays_ctree.
            new_cinsnptrvec_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_cinsnptrvec_t

    def push_back(self, *args) ->'cinsn_t *&':
        return _ida_hexrays_ctree.cinsnptrvec_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.cinsnptrvec_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.cinsnptrvec_t_empty(self)

    def at(self, _idx: int) ->'cinsn_t *const &':
        return _ida_hexrays_ctree.cinsnptrvec_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_resize(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.cinsnptrvec_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_truncate(self)

    def swap(self, r: 'cinsnptrvec_t') ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_swap(self, r)

    def extract(self) ->'cinsn_t **':
        return _ida_hexrays_ctree.cinsnptrvec_t_extract(self)

    def inject(self, s: 'cinsn_t **', len: int) ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_inject(self, s, len)

    def __eq__(self, r: 'cinsnptrvec_t') ->bool:
        return _ida_hexrays_ctree.cinsnptrvec_t___eq__(self, r)

    def __ne__(self, r: 'cinsnptrvec_t') ->bool:
        return _ida_hexrays_ctree.cinsnptrvec_t___ne__(self, r)

    def begin(self, *args) ->'qvector< cinsn_t * >::const_iterator':
        return _ida_hexrays_ctree.cinsnptrvec_t_begin(self, *args)

    def end(self, *args) ->'qvector< cinsn_t * >::const_iterator':
        return _ida_hexrays_ctree.cinsnptrvec_t_end(self, *args)

    def insert(self, it: 'qvector< cinsn_t * >::iterator', x: 'cinsn_t'
        ) ->'qvector< cinsn_t * >::iterator':
        return _ida_hexrays_ctree.cinsnptrvec_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< cinsn_t * >::iterator':
        return _ida_hexrays_ctree.cinsnptrvec_t_erase(self, *args)

    def find(self, *args) ->'qvector< cinsn_t * >::const_iterator':
        return _ida_hexrays_ctree.cinsnptrvec_t_find(self, *args)

    def has(self, x: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsnptrvec_t_has(self, x)

    def add_unique(self, x: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsnptrvec_t_add_unique(self, x)

    def _del(self, x: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsnptrvec_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.cinsnptrvec_t___len__(self)

    def __getitem__(self, i: int) ->'cinsn_t *const &':
        return _ida_hexrays_ctree.cinsnptrvec_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'cinsn_t') ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t___setitem__(self, i, v)

    def append(self, x: 'cinsn_t') ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_append(self, x)

    def extend(self, x: 'cinsnptrvec_t') ->None:
        return _ida_hexrays_ctree.cinsnptrvec_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.cinsnptrvec_t_swigregister(cinsnptrvec_t)


class eamap_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def at(self, _Keyval: 'unsigned long long const &') ->'cinsnptrvec_t &':
        return _ida_hexrays_ctree.eamap_t_at(self, _Keyval)

    def size(self) ->int:
        return _ida_hexrays_ctree.eamap_t_size(self)

    def __init__(self):
        _ida_hexrays_ctree.eamap_t_swiginit(self, _ida_hexrays_ctree.
            new_eamap_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_eamap_t


_ida_hexrays_ctree.eamap_t_swigregister(eamap_t)


class boundaries_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def at(self, _Keyval: 'cinsn_t') ->'rangeset_t &':
        return _ida_hexrays_ctree.boundaries_t_at(self, _Keyval)

    def size(self) ->int:
        return _ida_hexrays_ctree.boundaries_t_size(self)

    def __init__(self):
        _ida_hexrays_ctree.boundaries_t_swiginit(self, _ida_hexrays_ctree.
            new_boundaries_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_boundaries_t


_ida_hexrays_ctree.boundaries_t_swigregister(boundaries_t)


class cfuncptr_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.cfuncptr_t_swiginit(self, _ida_hexrays_ctree.
            new_cfuncptr_t(*args))

    def reset(self) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_reset(self)

    def __deref__(self) ->'cfunc_t *':
        return _ida_hexrays_ctree.cfuncptr_t___deref__(self)

    def __ref__(self) ->'cfunc_t &':
        return _ida_hexrays_ctree.cfuncptr_t___ref__(self)

    def __ptrval__(self) ->int:
        return _ida_hexrays_ctree.cfuncptr_t___ptrval__(self)
    __swig_destroy__ = _ida_hexrays_ctree.delete_cfuncptr_t
    entry_ea: ida_idaapi.ea_t = property(_ida_hexrays_ctree.
        cfuncptr_t_entry_ea_get, _ida_hexrays_ctree.cfuncptr_t_entry_ea_set)
    mba: 'mba_t *' = property(_ida_hexrays_ctree.cfuncptr_t_mba_get,
        _ida_hexrays_ctree.cfuncptr_t_mba_set)
    body: 'cinsn_t' = property(_ida_hexrays_ctree.cfuncptr_t_body_get,
        _ida_hexrays_ctree.cfuncptr_t_body_set)
    argidx: 'intvec_t &' = property(_ida_hexrays_ctree.cfuncptr_t_argidx_get)
    maturity: 'ctree_maturity_t' = property(_ida_hexrays_ctree.
        cfuncptr_t_maturity_get, _ida_hexrays_ctree.cfuncptr_t_maturity_set)
    user_labels: 'user_labels_t *' = property(_ida_hexrays_ctree.
        cfuncptr_t_user_labels_get, _ida_hexrays_ctree.
        cfuncptr_t_user_labels_set)
    user_cmts: 'user_cmts_t *' = property(_ida_hexrays_ctree.
        cfuncptr_t_user_cmts_get, _ida_hexrays_ctree.cfuncptr_t_user_cmts_set)
    numforms: 'user_numforms_t *' = property(_ida_hexrays_ctree.
        cfuncptr_t_numforms_get, _ida_hexrays_ctree.cfuncptr_t_numforms_set)
    user_iflags: 'user_iflags_t *' = property(_ida_hexrays_ctree.
        cfuncptr_t_user_iflags_get, _ida_hexrays_ctree.
        cfuncptr_t_user_iflags_set)
    user_unions: 'user_unions_t *' = property(_ida_hexrays_ctree.
        cfuncptr_t_user_unions_get, _ida_hexrays_ctree.
        cfuncptr_t_user_unions_set)
    refcnt: int = property(_ida_hexrays_ctree.cfuncptr_t_refcnt_get,
        _ida_hexrays_ctree.cfuncptr_t_refcnt_set)
    statebits: int = property(_ida_hexrays_ctree.cfuncptr_t_statebits_get,
        _ida_hexrays_ctree.cfuncptr_t_statebits_set)
    hdrlines: int = property(_ida_hexrays_ctree.cfuncptr_t_hdrlines_get,
        _ida_hexrays_ctree.cfuncptr_t_hdrlines_set)
    treeitems: 'citem_pointers_t' = property(_ida_hexrays_ctree.
        cfuncptr_t_treeitems_get, _ida_hexrays_ctree.cfuncptr_t_treeitems_set)

    def release(self) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_release(self)

    def build_c_tree(self) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_build_c_tree(self)

    def verify(self, aul: 'allow_unused_labels_t', even_without_debugger: bool
        ) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_verify(self, aul,
            even_without_debugger)

    def print_dcl(self) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_print_dcl(self)

    def print_func(self, vp: 'vc_printer_t') ->None:
        return _ida_hexrays_ctree.cfuncptr_t_print_func(self, vp)

    def get_func_type(self, type: 'tinfo_t') ->bool:
        return _ida_hexrays_ctree.cfuncptr_t_get_func_type(self, type)

    def get_lvars(self) ->'lvars_t *':
        return _ida_hexrays_ctree.cfuncptr_t_get_lvars(self)

    def get_stkoff_delta(self) ->int:
        return _ida_hexrays_ctree.cfuncptr_t_get_stkoff_delta(self)

    def find_label(self, label: int) ->'citem_t *':
        return _ida_hexrays_ctree.cfuncptr_t_find_label(self, label)

    def remove_unused_labels(self) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_remove_unused_labels(self)

    def get_user_cmt(self, loc: 'treeloc_t', rt: 'cmt_retrieval_type_t') ->str:
        return _ida_hexrays_ctree.cfuncptr_t_get_user_cmt(self, loc, rt)

    def set_user_cmt(self, loc: 'treeloc_t', cmt: str) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_set_user_cmt(self, loc, cmt)

    def get_user_iflags(self, loc: 'citem_locator_t') ->int:
        return _ida_hexrays_ctree.cfuncptr_t_get_user_iflags(self, loc)

    def set_user_iflags(self, loc: 'citem_locator_t', iflags: int) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_set_user_iflags(self, loc, iflags)

    def has_orphan_cmts(self) ->bool:
        return _ida_hexrays_ctree.cfuncptr_t_has_orphan_cmts(self)

    def del_orphan_cmts(self) ->int:
        return _ida_hexrays_ctree.cfuncptr_t_del_orphan_cmts(self)

    def get_user_union_selection(self, ea: ida_idaapi.ea_t, path: 'intvec_t'
        ) ->bool:
        return _ida_hexrays_ctree.cfuncptr_t_get_user_union_selection(self,
            ea, path)

    def set_user_union_selection(self, ea: ida_idaapi.ea_t, path: 'intvec_t'
        ) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_set_user_union_selection(self,
            ea, path)

    def save_user_labels(self) ->None:
        """Save user defined labels into the database. 
        """
        return _ida_hexrays_ctree.cfuncptr_t_save_user_labels(self)

    def save_user_cmts(self) ->None:
        """Save user defined comments into the database. 
        """
        return _ida_hexrays_ctree.cfuncptr_t_save_user_cmts(self)

    def save_user_numforms(self) ->None:
        """Save user defined number formats into the database. 
        """
        return _ida_hexrays_ctree.cfuncptr_t_save_user_numforms(self)

    def save_user_iflags(self) ->None:
        """Save user defined citem iflags into the database. 
        """
        return _ida_hexrays_ctree.cfuncptr_t_save_user_iflags(self)

    def save_user_unions(self) ->None:
        """Save user defined union field selections into the database. 
        """
        return _ida_hexrays_ctree.cfuncptr_t_save_user_unions(self)

    def get_line_item(self, line: str, x: int, is_ctree_line: bool, phead:
        'ctree_item_t', pitem: 'ctree_item_t', ptail: 'ctree_item_t') ->bool:
        return _ida_hexrays_ctree.cfuncptr_t_get_line_item(self, line, x,
            is_ctree_line, phead, pitem, ptail)

    def get_warnings(self) ->'hexwarns_t &':
        return _ida_hexrays_ctree.cfuncptr_t_get_warnings(self)

    def get_eamap(self) ->'eamap_t &':
        return _ida_hexrays_ctree.cfuncptr_t_get_eamap(self)

    def get_boundaries(self) ->'boundaries_t &':
        return _ida_hexrays_ctree.cfuncptr_t_get_boundaries(self)

    def get_pseudocode(self) ->'strvec_t const &':
        return _ida_hexrays_ctree.cfuncptr_t_get_pseudocode(self)

    def refresh_func_ctext(self) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_refresh_func_ctext(self)

    def recalc_item_addresses(self) ->None:
        return _ida_hexrays_ctree.cfuncptr_t_recalc_item_addresses(self)

    def gather_derefs(self, ci: 'ctree_item_t', udm: 'udt_type_data_t'=None
        ) ->bool:
        return _ida_hexrays_ctree.cfuncptr_t_gather_derefs(self, ci, udm)

    def find_item_coords(self, *args) ->'PyObject *':
        return _ida_hexrays_ctree.cfuncptr_t_find_item_coords(self, *args)

    def locked(self) ->bool:
        return _ida_hexrays_ctree.cfuncptr_t_locked(self)

    def serialize(self) ->bool:
        return _ida_hexrays_ctree.cfuncptr_t_serialize(self)

    def deserialize(self, mba: 'mba_t *', bytes: 'uchar const *'
        ) ->'cfunc_t *':
        return _ida_hexrays_ctree.cfuncptr_t_deserialize(self, mba, bytes)

    def __str__(self) ->str:
        return _ida_hexrays_ctree.cfuncptr_t___str__(self)


_ida_hexrays_ctree.cfuncptr_t_swigregister(cfuncptr_t)


class qvector_history_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.qvector_history_t_swiginit(self,
            _ida_hexrays_ctree.new_qvector_history_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_qvector_history_t

    def push_back(self, *args) ->'history_item_t &':
        return _ida_hexrays_ctree.qvector_history_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.qvector_history_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.qvector_history_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.qvector_history_t_empty(self)

    def at(self, _idx: int) ->'history_item_t const &':
        return _ida_hexrays_ctree.qvector_history_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.qvector_history_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.qvector_history_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_history_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_history_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.qvector_history_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.qvector_history_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.qvector_history_t_truncate(self)

    def swap(self, r: 'qvector_history_t') ->None:
        return _ida_hexrays_ctree.qvector_history_t_swap(self, r)

    def extract(self) ->'history_item_t *':
        return _ida_hexrays_ctree.qvector_history_t_extract(self)

    def inject(self, s: 'history_item_t', len: int) ->None:
        return _ida_hexrays_ctree.qvector_history_t_inject(self, s, len)

    def __eq__(self, r: 'qvector_history_t') ->bool:
        return _ida_hexrays_ctree.qvector_history_t___eq__(self, r)

    def __ne__(self, r: 'qvector_history_t') ->bool:
        return _ida_hexrays_ctree.qvector_history_t___ne__(self, r)

    def begin(self, *args) ->'qvector< history_item_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_history_t_begin(self, *args)

    def end(self, *args) ->'qvector< history_item_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_history_t_end(self, *args)

    def insert(self, it: 'history_item_t', x: 'history_item_t'
        ) ->'qvector< history_item_t >::iterator':
        return _ida_hexrays_ctree.qvector_history_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< history_item_t >::iterator':
        return _ida_hexrays_ctree.qvector_history_t_erase(self, *args)

    def find(self, *args) ->'qvector< history_item_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_history_t_find(self, *args)

    def has(self, x: 'history_item_t') ->bool:
        return _ida_hexrays_ctree.qvector_history_t_has(self, x)

    def add_unique(self, x: 'history_item_t') ->bool:
        return _ida_hexrays_ctree.qvector_history_t_add_unique(self, x)

    def _del(self, x: 'history_item_t') ->bool:
        return _ida_hexrays_ctree.qvector_history_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.qvector_history_t___len__(self)

    def __getitem__(self, i: int) ->'history_item_t const &':
        return _ida_hexrays_ctree.qvector_history_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'history_item_t') ->None:
        return _ida_hexrays_ctree.qvector_history_t___setitem__(self, i, v)

    def append(self, x: 'history_item_t') ->None:
        return _ida_hexrays_ctree.qvector_history_t_append(self, x)

    def extend(self, x: 'qvector_history_t') ->None:
        return _ida_hexrays_ctree.qvector_history_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.qvector_history_t_swigregister(qvector_history_t)


class history_t(qvector_history_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def pop(self) ->'history_item_t':
        return _ida_hexrays_ctree.history_t_pop(self)

    def top(self, *args) ->'history_item_t &':
        return _ida_hexrays_ctree.history_t_top(self, *args)

    def push(self, v: 'history_item_t') ->None:
        return _ida_hexrays_ctree.history_t_push(self, v)

    def __init__(self):
        _ida_hexrays_ctree.history_t_swiginit(self, _ida_hexrays_ctree.
            new_history_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_history_t


_ida_hexrays_ctree.history_t_swigregister(history_t)


class cinsn_list_t_iterator(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    cur: 'cinsn_t const &' = property(_ida_hexrays_ctree.
        cinsn_list_t_iterator_cur_get)

    def __next__(self) ->None:
        return _ida_hexrays_ctree.cinsn_list_t_iterator___next__(self)

    def __eq__(self, x: 'cinsn_list_t_iterator') ->bool:
        return _ida_hexrays_ctree.cinsn_list_t_iterator___eq__(self, x)

    def __ne__(self, x: 'cinsn_list_t_iterator') ->bool:
        return _ida_hexrays_ctree.cinsn_list_t_iterator___ne__(self, x)
    next = __next__

    def __init__(self):
        _ida_hexrays_ctree.cinsn_list_t_iterator_swiginit(self,
            _ida_hexrays_ctree.new_cinsn_list_t_iterator())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cinsn_list_t_iterator


_ida_hexrays_ctree.cinsn_list_t_iterator_swigregister(cinsn_list_t_iterator)


class cinsn_list_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.cinsn_list_t_swiginit(self, _ida_hexrays_ctree.
            new_cinsn_list_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_cinsn_list_t

    def swap(self, x: 'cinsn_list_t') ->None:
        return _ida_hexrays_ctree.cinsn_list_t_swap(self, x)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.cinsn_list_t_empty(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.cinsn_list_t_size(self)

    def front(self, *args) ->'cinsn_t const &':
        return _ida_hexrays_ctree.cinsn_list_t_front(self, *args)

    def back(self, *args) ->'cinsn_t const &':
        return _ida_hexrays_ctree.cinsn_list_t_back(self, *args)

    def rbegin(self, *args) ->'qlist< cinsn_t >::const_reverse_iterator':
        return _ida_hexrays_ctree.cinsn_list_t_rbegin(self, *args)

    def rend(self, *args) ->'qlist< cinsn_t >::const_reverse_iterator':
        return _ida_hexrays_ctree.cinsn_list_t_rend(self, *args)

    def push_front(self, x: 'cinsn_t') ->None:
        return _ida_hexrays_ctree.cinsn_list_t_push_front(self, x)

    def push_back(self, *args) ->'cinsn_t &':
        return _ida_hexrays_ctree.cinsn_list_t_push_back(self, *args)

    def clear(self) ->None:
        return _ida_hexrays_ctree.cinsn_list_t_clear(self)

    def pop_front(self) ->None:
        return _ida_hexrays_ctree.cinsn_list_t_pop_front(self)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.cinsn_list_t_pop_back(self)

    def splice(self, pos: 'qlist< cinsn_t >::iterator', other:
        'cinsn_list_t', first: 'qlist< cinsn_t >::iterator', last:
        'qlist< cinsn_t >::iterator') ->None:
        return _ida_hexrays_ctree.cinsn_list_t_splice(self, pos, other,
            first, last)

    def __eq__(self, x: 'cinsn_list_t') ->bool:
        return _ida_hexrays_ctree.cinsn_list_t___eq__(self, x)

    def __ne__(self, x: 'cinsn_list_t') ->bool:
        return _ida_hexrays_ctree.cinsn_list_t___ne__(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.cinsn_list_t___len__(self)

    def __getitem__(self, i: int) ->'cinsn_t const &':
        return _ida_hexrays_ctree.cinsn_list_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'cinsn_t') ->None:
        return _ida_hexrays_ctree.cinsn_list_t___setitem__(self, i, v)

    def remove(self, v: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsn_list_t_remove(self, v)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator

    def find(self, item):
        if item is not None:
            it = self.begin()
            for i in range(self.size()):
                if it.cur == item:
                    return it
                next(it)

    def index(self, item):
        if item is not None:
            it = self.begin()
            for i in range(self.size()):
                if it.cur == item:
                    return i
                next(it)

    def at(self, index):
        it = self.begin()
        for i in range(self.size()):
            if i == index:
                return it.cur
            next(it)

    def begin(self) ->'cinsn_list_t_iterator':
        return _ida_hexrays_ctree.cinsn_list_t_begin(self)

    def end(self) ->'cinsn_list_t_iterator':
        return _ida_hexrays_ctree.cinsn_list_t_end(self)

    def insert(self, *args) ->'cinsn_list_t_iterator':
        return _ida_hexrays_ctree.cinsn_list_t_insert(self, *args)

    def erase(self, p: 'cinsn_list_t_iterator') ->None:
        return _ida_hexrays_ctree.cinsn_list_t_erase(self, p)


_ida_hexrays_ctree.cinsn_list_t_swigregister(cinsn_list_t)


class qvector_carg_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.qvector_carg_t_swiginit(self, _ida_hexrays_ctree
            .new_qvector_carg_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_qvector_carg_t

    def push_back(self, *args) ->'carg_t &':
        return _ida_hexrays_ctree.qvector_carg_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.qvector_carg_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.qvector_carg_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.qvector_carg_t_empty(self)

    def at(self, _idx: int) ->'carg_t const &':
        return _ida_hexrays_ctree.qvector_carg_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.qvector_carg_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.qvector_carg_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_carg_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_carg_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.qvector_carg_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.qvector_carg_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.qvector_carg_t_truncate(self)

    def swap(self, r: 'qvector_carg_t') ->None:
        return _ida_hexrays_ctree.qvector_carg_t_swap(self, r)

    def extract(self) ->'carg_t *':
        return _ida_hexrays_ctree.qvector_carg_t_extract(self)

    def inject(self, s: 'carg_t', len: int) ->None:
        return _ida_hexrays_ctree.qvector_carg_t_inject(self, s, len)

    def __eq__(self, r: 'qvector_carg_t') ->bool:
        return _ida_hexrays_ctree.qvector_carg_t___eq__(self, r)

    def __ne__(self, r: 'qvector_carg_t') ->bool:
        return _ida_hexrays_ctree.qvector_carg_t___ne__(self, r)

    def begin(self, *args) ->'qvector< carg_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_carg_t_begin(self, *args)

    def end(self, *args) ->'qvector< carg_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_carg_t_end(self, *args)

    def insert(self, it: 'carg_t', x: 'carg_t'
        ) ->'qvector< carg_t >::iterator':
        return _ida_hexrays_ctree.qvector_carg_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< carg_t >::iterator':
        return _ida_hexrays_ctree.qvector_carg_t_erase(self, *args)

    def find(self, *args) ->'qvector< carg_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_carg_t_find(self, *args)

    def has(self, x: 'carg_t') ->bool:
        return _ida_hexrays_ctree.qvector_carg_t_has(self, x)

    def add_unique(self, x: 'carg_t') ->bool:
        return _ida_hexrays_ctree.qvector_carg_t_add_unique(self, x)

    def _del(self, x: 'carg_t') ->bool:
        return _ida_hexrays_ctree.qvector_carg_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.qvector_carg_t___len__(self)

    def __getitem__(self, i: int) ->'carg_t const &':
        return _ida_hexrays_ctree.qvector_carg_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'carg_t') ->None:
        return _ida_hexrays_ctree.qvector_carg_t___setitem__(self, i, v)

    def append(self, x: 'carg_t') ->None:
        return _ida_hexrays_ctree.qvector_carg_t_append(self, x)

    def extend(self, x: 'qvector_carg_t') ->None:
        return _ida_hexrays_ctree.qvector_carg_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.qvector_carg_t_swigregister(qvector_carg_t)


class qvector_ccase_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.qvector_ccase_t_swiginit(self,
            _ida_hexrays_ctree.new_qvector_ccase_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_qvector_ccase_t

    def push_back(self, *args) ->'ccase_t &':
        return _ida_hexrays_ctree.qvector_ccase_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.qvector_ccase_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.qvector_ccase_t_empty(self)

    def at(self, _idx: int) ->'ccase_t const &':
        return _ida_hexrays_ctree.qvector_ccase_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.qvector_ccase_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_truncate(self)

    def swap(self, r: 'qvector_ccase_t') ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_swap(self, r)

    def extract(self) ->'ccase_t *':
        return _ida_hexrays_ctree.qvector_ccase_t_extract(self)

    def inject(self, s: 'ccase_t', len: int) ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_inject(self, s, len)

    def __eq__(self, r: 'qvector_ccase_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccase_t___eq__(self, r)

    def __ne__(self, r: 'qvector_ccase_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccase_t___ne__(self, r)

    def begin(self, *args) ->'qvector< ccase_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_ccase_t_begin(self, *args)

    def end(self, *args) ->'qvector< ccase_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_ccase_t_end(self, *args)

    def insert(self, it: 'ccase_t', x: 'ccase_t'
        ) ->'qvector< ccase_t >::iterator':
        return _ida_hexrays_ctree.qvector_ccase_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< ccase_t >::iterator':
        return _ida_hexrays_ctree.qvector_ccase_t_erase(self, *args)

    def find(self, *args) ->'qvector< ccase_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_ccase_t_find(self, *args)

    def has(self, x: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccase_t_has(self, x)

    def add_unique(self, x: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccase_t_add_unique(self, x)

    def _del(self, x: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccase_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.qvector_ccase_t___len__(self)

    def __getitem__(self, i: int) ->'ccase_t const &':
        return _ida_hexrays_ctree.qvector_ccase_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'ccase_t') ->None:
        return _ida_hexrays_ctree.qvector_ccase_t___setitem__(self, i, v)

    def append(self, x: 'ccase_t') ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_append(self, x)

    def extend(self, x: 'qvector_ccase_t') ->None:
        return _ida_hexrays_ctree.qvector_ccase_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.qvector_ccase_t_swigregister(qvector_ccase_t)


class qvector_catchexprs_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.qvector_catchexprs_t_swiginit(self,
            _ida_hexrays_ctree.new_qvector_catchexprs_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_qvector_catchexprs_t

    def push_back(self, *args) ->'catchexpr_t &':
        return _ida_hexrays_ctree.qvector_catchexprs_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.qvector_catchexprs_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.qvector_catchexprs_t_empty(self)

    def at(self, _idx: int) ->'catchexpr_t const &':
        return _ida_hexrays_ctree.qvector_catchexprs_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.qvector_catchexprs_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_truncate(self)

    def swap(self, r: 'qvector_catchexprs_t') ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_swap(self, r)

    def extract(self) ->'catchexpr_t *':
        return _ida_hexrays_ctree.qvector_catchexprs_t_extract(self)

    def inject(self, s: 'catchexpr_t', len: int) ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_inject(self, s, len)

    def __eq__(self, r: 'qvector_catchexprs_t') ->bool:
        return _ida_hexrays_ctree.qvector_catchexprs_t___eq__(self, r)

    def __ne__(self, r: 'qvector_catchexprs_t') ->bool:
        return _ida_hexrays_ctree.qvector_catchexprs_t___ne__(self, r)

    def begin(self, *args) ->'qvector< catchexpr_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_catchexprs_t_begin(self, *args)

    def end(self, *args) ->'qvector< catchexpr_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_catchexprs_t_end(self, *args)

    def insert(self, it: 'catchexpr_t', x: 'catchexpr_t'
        ) ->'qvector< catchexpr_t >::iterator':
        return _ida_hexrays_ctree.qvector_catchexprs_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< catchexpr_t >::iterator':
        return _ida_hexrays_ctree.qvector_catchexprs_t_erase(self, *args)

    def find(self, *args) ->'qvector< catchexpr_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_catchexprs_t_find(self, *args)

    def has(self, x: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.qvector_catchexprs_t_has(self, x)

    def add_unique(self, x: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.qvector_catchexprs_t_add_unique(self, x)

    def _del(self, x: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.qvector_catchexprs_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.qvector_catchexprs_t___len__(self)

    def __getitem__(self, i: int) ->'catchexpr_t const &':
        return _ida_hexrays_ctree.qvector_catchexprs_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'catchexpr_t') ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t___setitem__(self, i, v)

    def append(self, x: 'catchexpr_t') ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_append(self, x)

    def extend(self, x: 'qvector_catchexprs_t') ->None:
        return _ida_hexrays_ctree.qvector_catchexprs_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.qvector_catchexprs_t_swigregister(qvector_catchexprs_t)


class qvector_ccatchvec_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.qvector_ccatchvec_t_swiginit(self,
            _ida_hexrays_ctree.new_qvector_ccatchvec_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_qvector_ccatchvec_t

    def push_back(self, *args) ->'ccatch_t &':
        return _ida_hexrays_ctree.qvector_ccatchvec_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_empty(self)

    def at(self, _idx: int) ->'ccatch_t const &':
        return _ida_hexrays_ctree.qvector_ccatchvec_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_truncate(self)

    def swap(self, r: 'qvector_ccatchvec_t') ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_swap(self, r)

    def extract(self) ->'ccatch_t *':
        return _ida_hexrays_ctree.qvector_ccatchvec_t_extract(self)

    def inject(self, s: 'ccatch_t', len: int) ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_inject(self, s, len)

    def __eq__(self, r: 'qvector_ccatchvec_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccatchvec_t___eq__(self, r)

    def __ne__(self, r: 'qvector_ccatchvec_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccatchvec_t___ne__(self, r)

    def begin(self, *args) ->'qvector< ccatch_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_ccatchvec_t_begin(self, *args)

    def end(self, *args) ->'qvector< ccatch_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_ccatchvec_t_end(self, *args)

    def insert(self, it: 'ccatch_t', x: 'ccatch_t'
        ) ->'qvector< ccatch_t >::iterator':
        return _ida_hexrays_ctree.qvector_ccatchvec_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< ccatch_t >::iterator':
        return _ida_hexrays_ctree.qvector_ccatchvec_t_erase(self, *args)

    def find(self, *args) ->'qvector< ccatch_t >::const_iterator':
        return _ida_hexrays_ctree.qvector_ccatchvec_t_find(self, *args)

    def has(self, x: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_has(self, x)

    def add_unique(self, x: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_add_unique(self, x)

    def _del(self, x: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.qvector_ccatchvec_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.qvector_ccatchvec_t___len__(self)

    def __getitem__(self, i: int) ->'ccatch_t const &':
        return _ida_hexrays_ctree.qvector_ccatchvec_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'ccatch_t') ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t___setitem__(self, i, v)

    def append(self, x: 'ccatch_t') ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_append(self, x)

    def extend(self, x: 'qvector_ccatchvec_t') ->None:
        return _ida_hexrays_ctree.qvector_ccatchvec_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.qvector_ccatchvec_t_swigregister(qvector_ccatchvec_t)


class cblock_posvec_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.cblock_posvec_t_swiginit(self,
            _ida_hexrays_ctree.new_cblock_posvec_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_cblock_posvec_t

    def push_back(self, *args) ->'cblock_pos_t &':
        return _ida_hexrays_ctree.cblock_posvec_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.cblock_posvec_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.cblock_posvec_t_empty(self)

    def at(self, _idx: int) ->'cblock_pos_t const &':
        return _ida_hexrays_ctree.cblock_posvec_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.cblock_posvec_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_truncate(self)

    def swap(self, r: 'cblock_posvec_t') ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_swap(self, r)

    def extract(self) ->'cblock_pos_t *':
        return _ida_hexrays_ctree.cblock_posvec_t_extract(self)

    def inject(self, s: 'cblock_pos_t', len: int) ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_inject(self, s, len)

    def begin(self, *args) ->'qvector< cblock_pos_t >::const_iterator':
        return _ida_hexrays_ctree.cblock_posvec_t_begin(self, *args)

    def end(self, *args) ->'qvector< cblock_pos_t >::const_iterator':
        return _ida_hexrays_ctree.cblock_posvec_t_end(self, *args)

    def insert(self, it: 'cblock_pos_t', x: 'cblock_pos_t'
        ) ->'qvector< cblock_pos_t >::iterator':
        return _ida_hexrays_ctree.cblock_posvec_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< cblock_pos_t >::iterator':
        return _ida_hexrays_ctree.cblock_posvec_t_erase(self, *args)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.cblock_posvec_t___len__(self)

    def __getitem__(self, i: int) ->'cblock_pos_t const &':
        return _ida_hexrays_ctree.cblock_posvec_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'cblock_pos_t') ->None:
        return _ida_hexrays_ctree.cblock_posvec_t___setitem__(self, i, v)

    def append(self, x: 'cblock_pos_t') ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_append(self, x)

    def extend(self, x: 'cblock_posvec_t') ->None:
        return _ida_hexrays_ctree.cblock_posvec_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.cblock_posvec_t_swigregister(cblock_posvec_t)


class ui_stroff_ops_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.ui_stroff_ops_t_swiginit(self,
            _ida_hexrays_ctree.new_ui_stroff_ops_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_ui_stroff_ops_t

    def push_back(self, *args) ->'ui_stroff_op_t &':
        return _ida_hexrays_ctree.ui_stroff_ops_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_ctree.ui_stroff_ops_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_ctree.ui_stroff_ops_t_empty(self)

    def at(self, _idx: int) ->'ui_stroff_op_t const &':
        return _ida_hexrays_ctree.ui_stroff_ops_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_ctree.ui_stroff_ops_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_truncate(self)

    def swap(self, r: 'ui_stroff_ops_t') ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_swap(self, r)

    def extract(self) ->'ui_stroff_op_t *':
        return _ida_hexrays_ctree.ui_stroff_ops_t_extract(self)

    def inject(self, s: 'ui_stroff_op_t', len: int) ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_inject(self, s, len)

    def __eq__(self, r: 'ui_stroff_ops_t') ->bool:
        return _ida_hexrays_ctree.ui_stroff_ops_t___eq__(self, r)

    def __ne__(self, r: 'ui_stroff_ops_t') ->bool:
        return _ida_hexrays_ctree.ui_stroff_ops_t___ne__(self, r)

    def begin(self, *args) ->'qvector< ui_stroff_op_t >::const_iterator':
        return _ida_hexrays_ctree.ui_stroff_ops_t_begin(self, *args)

    def end(self, *args) ->'qvector< ui_stroff_op_t >::const_iterator':
        return _ida_hexrays_ctree.ui_stroff_ops_t_end(self, *args)

    def insert(self, it: 'ui_stroff_op_t', x: 'ui_stroff_op_t'
        ) ->'qvector< ui_stroff_op_t >::iterator':
        return _ida_hexrays_ctree.ui_stroff_ops_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< ui_stroff_op_t >::iterator':
        return _ida_hexrays_ctree.ui_stroff_ops_t_erase(self, *args)

    def find(self, *args) ->'qvector< ui_stroff_op_t >::const_iterator':
        return _ida_hexrays_ctree.ui_stroff_ops_t_find(self, *args)

    def has(self, x: 'ui_stroff_op_t') ->bool:
        return _ida_hexrays_ctree.ui_stroff_ops_t_has(self, x)

    def add_unique(self, x: 'ui_stroff_op_t') ->bool:
        return _ida_hexrays_ctree.ui_stroff_ops_t_add_unique(self, x)

    def _del(self, x: 'ui_stroff_op_t') ->bool:
        return _ida_hexrays_ctree.ui_stroff_ops_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_ctree.ui_stroff_ops_t___len__(self)

    def __getitem__(self, i: int) ->'ui_stroff_op_t const &':
        return _ida_hexrays_ctree.ui_stroff_ops_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'ui_stroff_op_t') ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t___setitem__(self, i, v)

    def append(self, x: 'ui_stroff_op_t') ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_append(self, x)

    def extend(self, x: 'ui_stroff_ops_t') ->None:
        return _ida_hexrays_ctree.ui_stroff_ops_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_ctree.ui_stroff_ops_t_swigregister(ui_stroff_ops_t)


def qswap(a: 'cinsn_t', b: 'cinsn_t') ->None:
    return _ida_hexrays_ctree.qswap(a, b)


class Hexrays_Hooks(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, _flags: int=0, _hkcb_flags: int=1):
        if self.__class__ == Hexrays_Hooks:
            _self = None
        else:
            _self = self
        _ida_hexrays_ctree.Hexrays_Hooks_swiginit(self, _ida_hexrays_ctree.
            new_Hexrays_Hooks(_self, _flags, _hkcb_flags))
    __swig_destroy__ = _ida_hexrays_ctree.delete_Hexrays_Hooks

    def hook(self) ->bool:
        return _ida_hexrays_ctree.Hexrays_Hooks_hook(self)

    def unhook(self) ->bool:
        return _ida_hexrays_ctree.Hexrays_Hooks_unhook(self)

    def flowchart(self, fc: 'qflow_chart_t', mba: 'mba_t *',
        reachable_blocks: 'bitset_t *', decomp_flags: int) ->int:
        """Flowchart has been generated. 
          
:param fc: (qflow_chart_t *)
:param mba: (mba_t *)
:param reachable_blocks: (bitset_t *)
:param decomp_flags: (int)
:returns: Microcode error code"""
        return _ida_hexrays_ctree.Hexrays_Hooks_flowchart(self, fc, mba,
            reachable_blocks, decomp_flags)

    def stkpnts(self, mba: 'mba_t *', _sps: 'stkpnts_t *') ->int:
        """SP change points have been calculated. 
          
:param mba: (mba_t *)
:returns: Microcode error code This event is generated for each inlined range as well."""
        return _ida_hexrays_ctree.Hexrays_Hooks_stkpnts(self, mba, _sps)

    def prolog(self, mba: 'mba_t *', fc: 'qflow_chart_t', reachable_blocks:
        'bitset_t const *', decomp_flags: int) ->int:
        """Prolog analysis has been finished. 
          
:param mba: (mba_t *)
:param fc: (qflow_chart_t *)
:param reachable_blocks: (const bitset_t *)
:param decomp_flags: (int)
:returns: Microcode error code This event is generated for each inlined range as well."""
        return _ida_hexrays_ctree.Hexrays_Hooks_prolog(self, mba, fc,
            reachable_blocks, decomp_flags)

    def microcode(self, mba: 'mba_t *') ->int:
        """Microcode has been generated. 
          
:param mba: (mba_t *)
:returns: Microcode error code"""
        return _ida_hexrays_ctree.Hexrays_Hooks_microcode(self, mba)

    def preoptimized(self, mba: 'mba_t *') ->int:
        """Microcode has been preoptimized. 
          
:param mba: (mba_t *)
:returns: Microcode error code"""
        return _ida_hexrays_ctree.Hexrays_Hooks_preoptimized(self, mba)

    def locopt(self, mba: 'mba_t *') ->int:
        """Basic block level optimization has been finished. 
          
:param mba: (mba_t *)
:returns: Microcode error code"""
        return _ida_hexrays_ctree.Hexrays_Hooks_locopt(self, mba)

    def prealloc(self, mba: 'mba_t *') ->int:
        """Local variables: preallocation step begins. 
          
:param mba: (mba_t *) This event may occur several times. Should return: 1 if modified microcode Negative values are Microcode error code"""
        return _ida_hexrays_ctree.Hexrays_Hooks_prealloc(self, mba)

    def glbopt(self, mba: 'mba_t *') ->int:
        """Global optimization has been finished. If microcode is modified, MERR_LOOP must be returned. It will cause a complete restart of the optimization. 
          
:param mba: (mba_t *)
:returns: Microcode error code"""
        return _ida_hexrays_ctree.Hexrays_Hooks_glbopt(self, mba)

    def pre_structural(self, ct: 'control_graph_t *', cfunc: 'cfunc_t', g:
        'simple_graph_t const *') ->int:
        """Structure analysis is starting. 
          
:param ct: (control_graph_t *) in/out: control graph
:param cfunc: (cfunc_t *) in: the current function
:param g: (const simple_graph_t *) in: control flow graph
:returns: Microcode error code; MERR_BLOCK means that the analysis has been performed by a plugin"""
        return _ida_hexrays_ctree.Hexrays_Hooks_pre_structural(self, ct,
            cfunc, g)

    def structural(self, ct: 'control_graph_t *') ->int:
        """Structural analysis has been finished. 
          
:param ct: (control_graph_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_structural(self, ct)

    def maturity(self, cfunc: 'cfunc_t', new_maturity: 'ctree_maturity_t'
        ) ->int:
        """Ctree maturity level is being changed. 
          
:param cfunc: (cfunc_t *)
:param new_maturity: (ctree_maturity_t)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_maturity(self, cfunc,
            new_maturity)

    def interr(self, errcode: int) ->int:
        """Internal error has occurred. 
          
:param errcode: (int )"""
        return _ida_hexrays_ctree.Hexrays_Hooks_interr(self, errcode)

    def combine(self, blk: 'mblock_t *', insn: 'minsn_t *') ->int:
        """Trying to combine instructions of basic block. 
          
:param blk: (mblock_t *)
:param insn: (minsn_t *) Should return: 1 if combined the current instruction with a preceding one -1 if the instruction should not be combined 0 else"""
        return _ida_hexrays_ctree.Hexrays_Hooks_combine(self, blk, insn)

    def print_func(self, cfunc: 'cfunc_t', vp: 'vc_printer_t') ->int:
        """Printing ctree and generating text. 
          
:param cfunc: (cfunc_t *)
:param vp: (vc_printer_t *) Returns: 1 if text has been generated by the plugin It is forbidden to modify ctree at this event."""
        return _ida_hexrays_ctree.Hexrays_Hooks_print_func(self, cfunc, vp)

    def func_printed(self, cfunc: 'cfunc_t') ->int:
        """Function text has been generated. Plugins may modify the text in cfunc_t::sv. However, it is too late to modify the ctree or microcode. The text uses regular color codes (see lines.hpp) COLOR_ADDR is used to store pointers to ctree items. 
          
:param cfunc: (cfunc_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_func_printed(self, cfunc)

    def resolve_stkaddrs(self, mba: 'mba_t *') ->int:
        """The optimizer is about to resolve stack addresses. 
          
:param mba: (mba_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_resolve_stkaddrs(self, mba)

    def build_callinfo(self, blk: 'mblock_t *', type: 'tinfo_t'
        ) ->'PyObject *':
        """Analyzing a call instruction. 
          
:param blk: (mblock_t *) blk->tail is the call.
:param type: (tinfo_t *) buffer for the output type."""
        return _ida_hexrays_ctree.Hexrays_Hooks_build_callinfo(self, blk, type)

    def callinfo_built(self, blk: 'mblock_t *') ->int:
        """A call instruction has been anallyzed. 
          
:param blk: (mblock_t *) blk->tail is the call."""
        return _ida_hexrays_ctree.Hexrays_Hooks_callinfo_built(self, blk)

    def calls_done(self, mba: 'mba_t *') ->int:
        """All calls have been analyzed. 
          
:param mba: (mba_t *) This event is generated immediately after analyzing all calls, before any optimizitions, call unmerging and block merging."""
        return _ida_hexrays_ctree.Hexrays_Hooks_calls_done(self, mba)

    def begin_inlining(self, cdg: 'codegen_t *', decomp_flags: int) ->int:
        """Starting to inline outlined functions. 
          
:param cdg: (codegen_t *)
:param decomp_flags: (int)
:returns: Microcode error code This is an opportunity to inline other ranges."""
        return _ida_hexrays_ctree.Hexrays_Hooks_begin_inlining(self, cdg,
            decomp_flags)

    def inlining_func(self, cdg: 'codegen_t *', blk: int, mbr: 'mba_ranges_t'
        ) ->int:
        """A set of ranges is going to be inlined. 
          
:param cdg: (codegen_t *)
:param blk: (int) the block containing call/jump to inline
:param mbr: (mba_ranges_t *) the range to inline"""
        return _ida_hexrays_ctree.Hexrays_Hooks_inlining_func(self, cdg,
            blk, mbr)

    def inlined_func(self, cdg: 'codegen_t *', blk: int, mbr:
        'mba_ranges_t', i1: int, i2: int) ->int:
        """A set of ranges got inlined. 
          
:param cdg: (codegen_t *)
:param blk: (int) the block containing call/jump to inline
:param mbr: (mba_ranges_t *) the range to inline
:param i1: (int) blknum of the first inlined block
:param i2: (int) blknum of the last inlined block (excluded)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_inlined_func(self, cdg, blk,
            mbr, i1, i2)

    def collect_warnings(self, cfunc: 'cfunc_t') ->int:
        """Collect warning messages from plugins. These warnings will be displayed at the function header, after the user-defined comments. 
          
:param cfunc: (cfunc_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_collect_warnings(self, cfunc)

    def open_pseudocode(self, vu: 'vdui_t') ->int:
        """New pseudocode view has been opened. 
          
:param vu: (vdui_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_open_pseudocode(self, vu)

    def switch_pseudocode(self, vu: 'vdui_t') ->int:
        """Existing pseudocode view has been reloaded with a new function. Its text has not been refreshed yet, only cfunc and mba pointers are ready. 
          
:param vu: (vdui_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_switch_pseudocode(self, vu)

    def refresh_pseudocode(self, vu: 'vdui_t') ->int:
        """Existing pseudocode text has been refreshed. Adding/removing pseudocode lines is forbidden in this event. 
          
:param vu: (vdui_t *) See also hxe_text_ready, which happens earlier"""
        return _ida_hexrays_ctree.Hexrays_Hooks_refresh_pseudocode(self, vu)

    def close_pseudocode(self, vu: 'vdui_t') ->int:
        """Pseudocode view is being closed. 
          
:param vu: (vdui_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_close_pseudocode(self, vu)

    def keyboard(self, vu: 'vdui_t', key_code: int, shift_state: int) ->int:
        """Keyboard has been hit. 
          
:param vu: (vdui_t *)
:param key_code: (int) VK_...
:param shift_state: (int) Should return: 1 if the event has been handled"""
        return _ida_hexrays_ctree.Hexrays_Hooks_keyboard(self, vu, key_code,
            shift_state)

    def right_click(self, vu: 'vdui_t') ->int:
        """Mouse right click. Use hxe_populating_popup instead, in case you want to add items in the popup menu. 
          
:param vu: (vdui_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_right_click(self, vu)

    def double_click(self, vu: 'vdui_t', shift_state: int) ->int:
        """Mouse double click. 
          
:param vu: (vdui_t *)
:param shift_state: (int) Should return: 1 if the event has been handled"""
        return _ida_hexrays_ctree.Hexrays_Hooks_double_click(self, vu,
            shift_state)

    def curpos(self, vu: 'vdui_t') ->int:
        """Current cursor position has been changed. (for example, by left-clicking or using keyboard)

          
:param vu: (vdui_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_curpos(self, vu)

    def create_hint(self, vu: 'vdui_t') ->'PyObject *':
        """Create a hint for the current item. 
          
:param vu: (vdui_t *)
:returns: 0: continue collecting hints with other subscribers
:returns: 1: stop collecting hints"""
        return _ida_hexrays_ctree.Hexrays_Hooks_create_hint(self, vu)

    def text_ready(self, vu: 'vdui_t') ->int:
        """Decompiled text is ready. 
          
:param vu: (vdui_t *) This event can be used to modify the output text (sv). Obsolete. Please use hxe_func_printed instead."""
        return _ida_hexrays_ctree.Hexrays_Hooks_text_ready(self, vu)

    def populating_popup(self, widget: 'TWidget *', popup_handle:
        'TPopupMenu *', vu: 'vdui_t') ->int:
        """Populating popup menu. We can add menu items now. 
          
:param widget: (TWidget *)
:param popup_handle: (TPopupMenu *)
:param vu: (vdui_t *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_populating_popup(self,
            widget, popup_handle, vu)

    def lvar_name_changed(self, vu: 'vdui_t', v: 'lvar_t *', name: str,
        is_user_name: bool) ->int:
        """Local variable got renamed. 
          
:param vu: (vdui_t *)
:param v: (lvar_t *)
:param name: (const char *)
:param is_user_name: (bool) Please note that it is possible to read/write user settings for lvars directly from the idb."""
        return _ida_hexrays_ctree.Hexrays_Hooks_lvar_name_changed(self, vu,
            v, name, is_user_name)

    def lvar_type_changed(self, vu: 'vdui_t', v: 'lvar_t *', tinfo: 'tinfo_t'
        ) ->int:
        """Local variable type got changed. 
          
:param vu: (vdui_t *)
:param v: (lvar_t *)
:param tinfo: (const tinfo_t *) Please note that it is possible to read/write user settings for lvars directly from the idb."""
        return _ida_hexrays_ctree.Hexrays_Hooks_lvar_type_changed(self, vu,
            v, tinfo)

    def lvar_cmt_changed(self, vu: 'vdui_t', v: 'lvar_t *', cmt: str) ->int:
        """Local variable comment got changed. 
          
:param vu: (vdui_t *)
:param v: (lvar_t *)
:param cmt: (const char *) Please note that it is possible to read/write user settings for lvars directly from the idb."""
        return _ida_hexrays_ctree.Hexrays_Hooks_lvar_cmt_changed(self, vu,
            v, cmt)

    def lvar_mapping_changed(self, vu: 'vdui_t', frm: 'lvar_t *', to:
        'lvar_t *') ->int:
        """Local variable mapping got changed. 
          
:param vu: (vdui_t *)
:param to: (lvar_t *) Please note that it is possible to read/write user settings for lvars directly from the idb."""
        return _ida_hexrays_ctree.Hexrays_Hooks_lvar_mapping_changed(self,
            vu, frm, to)

    def cmt_changed(self, cfunc: 'cfunc_t', loc: 'treeloc_t', cmt: str) ->int:
        """Comment got changed. 
          
:param cfunc: (cfunc_t *)
:param loc: (const treeloc_t *)
:param cmt: (const char *)"""
        return _ida_hexrays_ctree.Hexrays_Hooks_cmt_changed(self, cfunc,
            loc, cmt)

    def mba_maturity(self, mba: 'mba_t *', reqmat: 'mba_maturity_t') ->int:
        """Maturity level of an MBA was changed. 
          
:param mba: (mba_t *)
:param reqmat: (mba_maturity_t) requested maturity level
:returns: Microcode error code"""
        return _ida_hexrays_ctree.Hexrays_Hooks_mba_maturity(self, mba, reqmat)

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_ctree.disown_Hexrays_Hooks(self)
        return weakref.proxy(self)


_ida_hexrays_ctree.Hexrays_Hooks_swigregister(Hexrays_Hooks)


def remitem(e: 'citem_t') ->None:
    return _ida_hexrays_ctree.remitem(e)


cot_empty = _ida_hexrays_ctree.cot_empty
cot_comma = _ida_hexrays_ctree.cot_comma
"""x, y
"""
cot_asg = _ida_hexrays_ctree.cot_asg
"""x = y
"""
cot_asgbor = _ida_hexrays_ctree.cot_asgbor
"""x |= y
"""
cot_asgxor = _ida_hexrays_ctree.cot_asgxor
"""x ^= y
"""
cot_asgband = _ida_hexrays_ctree.cot_asgband
"""x &= y
"""
cot_asgadd = _ida_hexrays_ctree.cot_asgadd
"""x += y
"""
cot_asgsub = _ida_hexrays_ctree.cot_asgsub
"""x -= y
"""
cot_asgmul = _ida_hexrays_ctree.cot_asgmul
"""x *= y
"""
cot_asgsshr = _ida_hexrays_ctree.cot_asgsshr
"""x >>= y signed
"""
cot_asgushr = _ida_hexrays_ctree.cot_asgushr
"""x >>= y unsigned
"""
cot_asgshl = _ida_hexrays_ctree.cot_asgshl
"""x <<= y
"""
cot_asgsdiv = _ida_hexrays_ctree.cot_asgsdiv
"""x /= y signed
"""
cot_asgudiv = _ida_hexrays_ctree.cot_asgudiv
"""x /= y unsigned
"""
cot_asgsmod = _ida_hexrays_ctree.cot_asgsmod
"""x %= y signed
"""
cot_asgumod = _ida_hexrays_ctree.cot_asgumod
"""x %= y unsigned
"""
cot_tern = _ida_hexrays_ctree.cot_tern
"""x ? y : z
"""
cot_lor = _ida_hexrays_ctree.cot_lor
"""x || y
"""
cot_land = _ida_hexrays_ctree.cot_land
"""x && y
"""
cot_bor = _ida_hexrays_ctree.cot_bor
"""x | y
"""
cot_xor = _ida_hexrays_ctree.cot_xor
"""x ^ y
"""
cot_band = _ida_hexrays_ctree.cot_band
"""x & y
"""
cot_eq = _ida_hexrays_ctree.cot_eq
"""x == y int or fpu (see EXFL_FPOP)
"""
cot_ne = _ida_hexrays_ctree.cot_ne
"""x != y int or fpu (see EXFL_FPOP)
"""
cot_sge = _ida_hexrays_ctree.cot_sge
"""x >= y signed or fpu (see EXFL_FPOP)
"""
cot_uge = _ida_hexrays_ctree.cot_uge
"""x >= y unsigned
"""
cot_sle = _ida_hexrays_ctree.cot_sle
"""x <= y signed or fpu (see EXFL_FPOP)
"""
cot_ule = _ida_hexrays_ctree.cot_ule
"""x <= y unsigned
"""
cot_sgt = _ida_hexrays_ctree.cot_sgt
"""x > y signed or fpu (see EXFL_FPOP)
"""
cot_ugt = _ida_hexrays_ctree.cot_ugt
"""x > y unsigned
"""
cot_slt = _ida_hexrays_ctree.cot_slt
"""x < y signed or fpu (see EXFL_FPOP)
"""
cot_ult = _ida_hexrays_ctree.cot_ult
"""x < y unsigned
"""
cot_sshr = _ida_hexrays_ctree.cot_sshr
"""x >> y signed
"""
cot_ushr = _ida_hexrays_ctree.cot_ushr
"""x >> y unsigned
"""
cot_shl = _ida_hexrays_ctree.cot_shl
"""x << y
"""
cot_add = _ida_hexrays_ctree.cot_add
"""x + y
"""
cot_sub = _ida_hexrays_ctree.cot_sub
"""x - y
"""
cot_mul = _ida_hexrays_ctree.cot_mul
"""x * y
"""
cot_sdiv = _ida_hexrays_ctree.cot_sdiv
"""x / y signed
"""
cot_udiv = _ida_hexrays_ctree.cot_udiv
"""x / y unsigned
"""
cot_smod = _ida_hexrays_ctree.cot_smod
"""x % y signed
"""
cot_umod = _ida_hexrays_ctree.cot_umod
"""x % y unsigned
"""
cot_fadd = _ida_hexrays_ctree.cot_fadd
"""x + y fp
"""
cot_fsub = _ida_hexrays_ctree.cot_fsub
"""x - y fp
"""
cot_fmul = _ida_hexrays_ctree.cot_fmul
"""x * y fp
"""
cot_fdiv = _ida_hexrays_ctree.cot_fdiv
"""x / y fp
"""
cot_fneg = _ida_hexrays_ctree.cot_fneg
"""-x fp
"""
cot_neg = _ida_hexrays_ctree.cot_neg
"""-x
"""
cot_cast = _ida_hexrays_ctree.cot_cast
"""(type)x
"""
cot_lnot = _ida_hexrays_ctree.cot_lnot
"""!x
"""
cot_bnot = _ida_hexrays_ctree.cot_bnot
"""~x
"""
cot_ptr = _ida_hexrays_ctree.cot_ptr
"""*x, access size in 'ptrsize'
"""
cot_ref = _ida_hexrays_ctree.cot_ref
"""&x
"""
cot_postinc = _ida_hexrays_ctree.cot_postinc
"""x++
"""
cot_postdec = _ida_hexrays_ctree.cot_postdec
"""x-
"""
cot_preinc = _ida_hexrays_ctree.cot_preinc
"""++x
"""
cot_predec = _ida_hexrays_ctree.cot_predec
"""-x
"""
cot_call = _ida_hexrays_ctree.cot_call
"""x(...)
"""
cot_idx = _ida_hexrays_ctree.cot_idx
"""x[y]
"""
cot_memref = _ida_hexrays_ctree.cot_memref
"""x.m
"""
cot_memptr = _ida_hexrays_ctree.cot_memptr
"""x->m, access size in 'ptrsize'
"""
cot_num = _ida_hexrays_ctree.cot_num
"""n
"""
cot_fnum = _ida_hexrays_ctree.cot_fnum
"""fpc
"""
cot_str = _ida_hexrays_ctree.cot_str
"""string constant (user representation)
"""
cot_obj = _ida_hexrays_ctree.cot_obj
"""obj_ea
"""
cot_var = _ida_hexrays_ctree.cot_var
"""v
"""
cot_insn = _ida_hexrays_ctree.cot_insn
"""instruction in expression, internal representation only
"""
cot_sizeof = _ida_hexrays_ctree.cot_sizeof
"""sizeof(x)
"""
cot_helper = _ida_hexrays_ctree.cot_helper
"""arbitrary name
"""
cot_type = _ida_hexrays_ctree.cot_type
"""arbitrary type
"""
cot_last = _ida_hexrays_ctree.cot_last
cit_empty = _ida_hexrays_ctree.cit_empty
"""instruction types start here
"""
cit_block = _ida_hexrays_ctree.cit_block
"""block-statement: { ... }
"""
cit_expr = _ida_hexrays_ctree.cit_expr
"""expression-statement: expr;
"""
cit_if = _ida_hexrays_ctree.cit_if
"""if-statement
"""
cit_for = _ida_hexrays_ctree.cit_for
"""for-statement
"""
cit_while = _ida_hexrays_ctree.cit_while
"""while-statement
"""
cit_do = _ida_hexrays_ctree.cit_do
"""do-statement
"""
cit_switch = _ida_hexrays_ctree.cit_switch
"""switch-statement
"""
cit_break = _ida_hexrays_ctree.cit_break
"""break-statement
"""
cit_continue = _ida_hexrays_ctree.cit_continue
"""continue-statement
"""
cit_return = _ida_hexrays_ctree.cit_return
"""return-statement
"""
cit_goto = _ida_hexrays_ctree.cit_goto
"""goto-statement
"""
cit_asm = _ida_hexrays_ctree.cit_asm
"""asm-statement
"""
cit_try = _ida_hexrays_ctree.cit_try
"""C++ try-statement.
"""
cit_throw = _ida_hexrays_ctree.cit_throw
"""C++ throw-statement.
"""
cit_end = _ida_hexrays_ctree.cit_end


def negated_relation(op: 'ctype_t') ->'ctype_t':
    """Negate a comparison operator. For example, cot_sge becomes cot_slt.
"""
    return _ida_hexrays_ctree.negated_relation(op)


def swapped_relation(op: 'ctype_t') ->'ctype_t':
    """Swap a comparison operator. For example, cot_sge becomes cot_sle.
"""
    return _ida_hexrays_ctree.swapped_relation(op)


def get_op_signness(op: 'ctype_t') ->'type_sign_t':
    """Get operator sign. Meaningful for sign-dependent operators, like cot_sdiv.
"""
    return _ida_hexrays_ctree.get_op_signness(op)


def asgop(cop: 'ctype_t') ->'ctype_t':
    """Convert plain operator into assignment operator. For example, cot_add returns cot_asgadd.
"""
    return _ida_hexrays_ctree.asgop(cop)


def asgop_revert(cop: 'ctype_t') ->'ctype_t':
    """Convert assignment operator into plain operator. For example, cot_asgadd returns cot_add 
        
:returns: cot_empty is the input operator is not an assignment operator."""
    return _ida_hexrays_ctree.asgop_revert(cop)


def op_uses_x(op: 'ctype_t') ->bool:
    """Does operator use the 'x' field of cexpr_t?
"""
    return _ida_hexrays_ctree.op_uses_x(op)


def op_uses_y(op: 'ctype_t') ->bool:
    """Does operator use the 'y' field of cexpr_t?
"""
    return _ida_hexrays_ctree.op_uses_y(op)


def op_uses_z(op: 'ctype_t') ->bool:
    """Does operator use the 'z' field of cexpr_t?
"""
    return _ida_hexrays_ctree.op_uses_z(op)


def is_binary(op: 'ctype_t') ->bool:
    """Is binary operator?
"""
    return _ida_hexrays_ctree.is_binary(op)


def is_unary(op: 'ctype_t') ->bool:
    """Is unary operator?
"""
    return _ida_hexrays_ctree.is_unary(op)


def is_relational(op: 'ctype_t') ->bool:
    """Is comparison operator?
"""
    return _ida_hexrays_ctree.is_relational(op)


def is_assignment(op: 'ctype_t') ->bool:
    """Is assignment operator?
"""
    return _ida_hexrays_ctree.is_assignment(op)


def accepts_udts(op: 'ctype_t') ->bool:
    return _ida_hexrays_ctree.accepts_udts(op)


def is_prepost(op: 'ctype_t') ->bool:
    """Is pre/post increment/decrement operator?
"""
    return _ida_hexrays_ctree.is_prepost(op)


def is_commutative(op: 'ctype_t') ->bool:
    """Is commutative operator?
"""
    return _ida_hexrays_ctree.is_commutative(op)


def is_additive(op: 'ctype_t') ->bool:
    """Is additive operator?
"""
    return _ida_hexrays_ctree.is_additive(op)


def is_multiplicative(op: 'ctype_t') ->bool:
    """Is multiplicative operator?
"""
    return _ida_hexrays_ctree.is_multiplicative(op)


def is_bitop(op: 'ctype_t') ->bool:
    """Is bit related operator?
"""
    return _ida_hexrays_ctree.is_bitop(op)


def is_logical(op: 'ctype_t') ->bool:
    """Is logical operator?
"""
    return _ida_hexrays_ctree.is_logical(op)


def is_loop(op: 'ctype_t') ->bool:
    """Is loop statement code?
"""
    return _ida_hexrays_ctree.is_loop(op)


def is_break_consumer(op: 'ctype_t') ->bool:
    """Does a break statement influence the specified statement code?
"""
    return _ida_hexrays_ctree.is_break_consumer(op)


def is_lvalue(op: 'ctype_t') ->bool:
    """Is Lvalue operator?
"""
    return _ida_hexrays_ctree.is_lvalue(op)


def accepts_small_udts(op: 'ctype_t') ->bool:
    """Is the operator allowed on small structure or union?
"""
    return _ida_hexrays_ctree.accepts_small_udts(op)


class cnumber_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    _value: 'uint64' = property(_ida_hexrays_ctree.cnumber_t__value_get,
        _ida_hexrays_ctree.cnumber_t__value_set)
    """its value
"""
    nf: 'number_format_t' = property(_ida_hexrays_ctree.cnumber_t_nf_get,
        _ida_hexrays_ctree.cnumber_t_nf_set)
    """how to represent it
"""

    def __init__(self, _opnum: int=0):
        _ida_hexrays_ctree.cnumber_t_swiginit(self, _ida_hexrays_ctree.
            new_cnumber_t(_opnum))

    def _print(self, type: 'tinfo_t', parent: 'citem_t'=None, nice_stroff:
        'bool *'=None) ->None:
        return _ida_hexrays_ctree.cnumber_t__print(self, type, parent,
            nice_stroff)

    def value(self, type: 'tinfo_t') ->'uint64':
        """Get value. This function will properly extend the number sign to 64bits depending on the type sign. 
        """
        return _ida_hexrays_ctree.cnumber_t_value(self, type)

    def assign(self, v: 'uint64', nbytes: int, sign: 'type_sign_t') ->None:
        """Assign new value 
        
:param v: new value
:param nbytes: size of the new value in bytes
:param sign: sign of the value"""
        return _ida_hexrays_ctree.cnumber_t_assign(self, v, nbytes, sign)

    def __eq__(self, r: 'cnumber_t') ->bool:
        return _ida_hexrays_ctree.cnumber_t___eq__(self, r)

    def __ne__(self, r: 'cnumber_t') ->bool:
        return _ida_hexrays_ctree.cnumber_t___ne__(self, r)

    def __lt__(self, r: 'cnumber_t') ->bool:
        return _ida_hexrays_ctree.cnumber_t___lt__(self, r)

    def __gt__(self, r: 'cnumber_t') ->bool:
        return _ida_hexrays_ctree.cnumber_t___gt__(self, r)

    def __le__(self, r: 'cnumber_t') ->bool:
        return _ida_hexrays_ctree.cnumber_t___le__(self, r)

    def __ge__(self, r: 'cnumber_t') ->bool:
        return _ida_hexrays_ctree.cnumber_t___ge__(self, r)

    def compare(self, r: 'cnumber_t') ->int:
        return _ida_hexrays_ctree.cnumber_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_cnumber_t


_ida_hexrays_ctree.cnumber_t_swigregister(cnumber_t)


class var_ref_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    mba: 'mba_t *' = property(_ida_hexrays_ctree.var_ref_t_mba_get,
        _ida_hexrays_ctree.var_ref_t_mba_set)
    """pointer to the underlying micro array
"""
    idx: int = property(_ida_hexrays_ctree.var_ref_t_idx_get,
        _ida_hexrays_ctree.var_ref_t_idx_set)
    """index into lvars_t
"""

    def __eq__(self, r: 'var_ref_t') ->bool:
        return _ida_hexrays_ctree.var_ref_t___eq__(self, r)

    def __ne__(self, r: 'var_ref_t') ->bool:
        return _ida_hexrays_ctree.var_ref_t___ne__(self, r)

    def __lt__(self, r: 'var_ref_t') ->bool:
        return _ida_hexrays_ctree.var_ref_t___lt__(self, r)

    def __gt__(self, r: 'var_ref_t') ->bool:
        return _ida_hexrays_ctree.var_ref_t___gt__(self, r)

    def __le__(self, r: 'var_ref_t') ->bool:
        return _ida_hexrays_ctree.var_ref_t___le__(self, r)

    def __ge__(self, r: 'var_ref_t') ->bool:
        return _ida_hexrays_ctree.var_ref_t___ge__(self, r)

    def compare(self, r: 'var_ref_t') ->int:
        return _ida_hexrays_ctree.var_ref_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.var_ref_t_swiginit(self, _ida_hexrays_ctree.
            new_var_ref_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_var_ref_t


_ida_hexrays_ctree.var_ref_t_swigregister(var_ref_t)
CMAT_ZERO = _ida_hexrays_ctree.CMAT_ZERO
"""does not exist
"""
CMAT_BUILT = _ida_hexrays_ctree.CMAT_BUILT
"""just generated
"""
CMAT_TRANS1 = _ida_hexrays_ctree.CMAT_TRANS1
"""applied first wave of transformations
"""
CMAT_NICE = _ida_hexrays_ctree.CMAT_NICE
"""nicefied expressions
"""
CMAT_TRANS2 = _ida_hexrays_ctree.CMAT_TRANS2
"""applied second wave of transformations
"""
CMAT_CPA = _ida_hexrays_ctree.CMAT_CPA
"""corrected pointer arithmetic
"""
CMAT_TRANS3 = _ida_hexrays_ctree.CMAT_TRANS3
"""applied third wave of transformations
"""
CMAT_CASTED = _ida_hexrays_ctree.CMAT_CASTED
"""added necessary casts
"""
CMAT_FINAL = _ida_hexrays_ctree.CMAT_FINAL
"""ready-to-use
"""
ITP_EMPTY = _ida_hexrays_ctree.ITP_EMPTY
"""nothing
"""
ITP_ARG1 = _ida_hexrays_ctree.ITP_ARG1
""", (64 entries are reserved for 64 call arguments)
"""
ITP_ARG64 = _ida_hexrays_ctree.ITP_ARG64
ITP_BRACE1 = _ida_hexrays_ctree.ITP_BRACE1
ITP_INNER_LAST = _ida_hexrays_ctree.ITP_INNER_LAST
ITP_ASM = _ida_hexrays_ctree.ITP_ASM
"""__asm-line
"""
ITP_ELSE = _ida_hexrays_ctree.ITP_ELSE
"""else-line
"""
ITP_DO = _ida_hexrays_ctree.ITP_DO
"""do-line
"""
ITP_SEMI = _ida_hexrays_ctree.ITP_SEMI
"""semicolon
"""
ITP_CURLY1 = _ida_hexrays_ctree.ITP_CURLY1
"""{
"""
ITP_CURLY2 = _ida_hexrays_ctree.ITP_CURLY2
"""}
"""
ITP_BRACE2 = _ida_hexrays_ctree.ITP_BRACE2
""")
"""
ITP_COLON = _ida_hexrays_ctree.ITP_COLON
""": (label)
"""
ITP_BLOCK1 = _ida_hexrays_ctree.ITP_BLOCK1
"""opening block comment. this comment is printed before the item (other comments are indented and printed after the item) 
          """
ITP_BLOCK2 = _ida_hexrays_ctree.ITP_BLOCK2
"""closing block comment.
"""
ITP_TRY = _ida_hexrays_ctree.ITP_TRY
"""C++ try statement.
"""
ITP_CASE = _ida_hexrays_ctree.ITP_CASE
"""bit for switch cases
"""
ITP_SIGN = _ida_hexrays_ctree.ITP_SIGN
"""if this bit is set too, then we have a negative case value
"""


class treeloc_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ea: ida_idaapi.ea_t = property(_ida_hexrays_ctree.treeloc_t_ea_get,
        _ida_hexrays_ctree.treeloc_t_ea_set)
    itp: 'item_preciser_t' = property(_ida_hexrays_ctree.treeloc_t_itp_get,
        _ida_hexrays_ctree.treeloc_t_itp_set)

    def __lt__(self, r: 'treeloc_t') ->bool:
        return _ida_hexrays_ctree.treeloc_t___lt__(self, r)

    def __eq__(self, r: 'treeloc_t') ->bool:
        return _ida_hexrays_ctree.treeloc_t___eq__(self, r)

    def __init__(self):
        _ida_hexrays_ctree.treeloc_t_swiginit(self, _ida_hexrays_ctree.
            new_treeloc_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_treeloc_t


_ida_hexrays_ctree.treeloc_t_swigregister(treeloc_t)
RETRIEVE_ONCE = _ida_hexrays_ctree.RETRIEVE_ONCE
"""Retrieve comment if it has not been used yet.
"""
RETRIEVE_ALWAYS = _ida_hexrays_ctree.RETRIEVE_ALWAYS
"""Retrieve comment even if it has been used.
"""


class citem_cmt_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    used: bool = property(_ida_hexrays_ctree.citem_cmt_t_used_get,
        _ida_hexrays_ctree.citem_cmt_t_used_set)
    """the comment has been retrieved?
"""

    def __init__(self, *args):
        _ida_hexrays_ctree.citem_cmt_t_swiginit(self, _ida_hexrays_ctree.
            new_citem_cmt_t(*args))

    def c_str(self) ->str:
        return _ida_hexrays_ctree.citem_cmt_t_c_str(self)

    def __str__(self) ->str:
        return _ida_hexrays_ctree.citem_cmt_t___str__(self)
    __swig_destroy__ = _ida_hexrays_ctree.delete_citem_cmt_t


_ida_hexrays_ctree.citem_cmt_t_swigregister(citem_cmt_t)


class citem_locator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ea: ida_idaapi.ea_t = property(_ida_hexrays_ctree.
        citem_locator_t_ea_get, _ida_hexrays_ctree.citem_locator_t_ea_set)
    """citem address
"""
    op: 'ctype_t' = property(_ida_hexrays_ctree.citem_locator_t_op_get,
        _ida_hexrays_ctree.citem_locator_t_op_set)
    """citem operation
"""

    def __init__(self, *args):
        _ida_hexrays_ctree.citem_locator_t_swiginit(self,
            _ida_hexrays_ctree.new_citem_locator_t(*args))

    def __eq__(self, r: 'citem_locator_t') ->bool:
        return _ida_hexrays_ctree.citem_locator_t___eq__(self, r)

    def __ne__(self, r: 'citem_locator_t') ->bool:
        return _ida_hexrays_ctree.citem_locator_t___ne__(self, r)

    def __lt__(self, r: 'citem_locator_t') ->bool:
        return _ida_hexrays_ctree.citem_locator_t___lt__(self, r)

    def __gt__(self, r: 'citem_locator_t') ->bool:
        return _ida_hexrays_ctree.citem_locator_t___gt__(self, r)

    def __le__(self, r: 'citem_locator_t') ->bool:
        return _ida_hexrays_ctree.citem_locator_t___le__(self, r)

    def __ge__(self, r: 'citem_locator_t') ->bool:
        return _ida_hexrays_ctree.citem_locator_t___ge__(self, r)

    def compare(self, r: 'citem_locator_t') ->int:
        return _ida_hexrays_ctree.citem_locator_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_citem_locator_t


_ida_hexrays_ctree.citem_locator_t_swigregister(citem_locator_t)


class bit_bound_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    nbits: 'int16' = property(_ida_hexrays_ctree.bit_bound_t_nbits_get,
        _ida_hexrays_ctree.bit_bound_t_nbits_set)
    sbits: 'int16' = property(_ida_hexrays_ctree.bit_bound_t_sbits_get,
        _ida_hexrays_ctree.bit_bound_t_sbits_set)

    def __init__(self, n: int=0, s: int=0):
        _ida_hexrays_ctree.bit_bound_t_swiginit(self, _ida_hexrays_ctree.
            new_bit_bound_t(n, s))
    __swig_destroy__ = _ida_hexrays_ctree.delete_bit_bound_t


_ida_hexrays_ctree.bit_bound_t_swigregister(bit_bound_t)


class citem_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ea: ida_idaapi.ea_t = property(_ida_hexrays_ctree.citem_t_ea_get,
        _ida_hexrays_ctree.citem_t_ea_set)
    """address that corresponds to the item. may be BADADDR
"""
    label_num: int = property(_ida_hexrays_ctree.citem_t_label_num_get,
        _ida_hexrays_ctree.citem_t_label_num_set)
    """label number. -1 means no label. items of the expression types (cot_...) should not have labels at the final maturity level, but at the intermediate levels any ctree item may have a label. Labels must be unique. Usually they correspond to the basic block numbers. 
        """
    index: int = property(_ida_hexrays_ctree.citem_t_index_get,
        _ida_hexrays_ctree.citem_t_index_set)
    """an index in cfunc_t::treeitems. meaningful only after print_func() 
        """

    def __init__(self, o: 'ctype_t'=cot_empty):
        _ida_hexrays_ctree.citem_t_swiginit(self, _ida_hexrays_ctree.
            new_citem_t(o))

    def swap(self, r: 'citem_t') ->None:
        """Swap two citem_t.
"""
        return _ida_hexrays_ctree.citem_t_swap(self, r)

    def is_expr(self) ->bool:
        """Is an expression?
"""
        return _ida_hexrays_ctree.citem_t_is_expr(self)

    def contains_expr(self, e: 'cexpr_t') ->bool:
        """Does the item contain an expression?
"""
        return _ida_hexrays_ctree.citem_t_contains_expr(self, e)

    def contains_label(self) ->bool:
        """Does the item contain a label?
"""
        return _ida_hexrays_ctree.citem_t_contains_label(self)

    def find_parent_of(self, item: 'citem_t') ->'citem_t *':
        """Find parent of the specified item. 
        
:param item: Item to find the parent of. The search will be performed among the children of the item pointed by `this`.
:returns: nullptr if not found"""
        return _ida_hexrays_ctree.citem_t_find_parent_of(self, item)

    def find_closest_addr(self, _ea: ida_idaapi.ea_t) ->'citem_t *':
        return _ida_hexrays_ctree.citem_t_find_closest_addr(self, _ea)

    def print1(self, func: 'cfunc_t') ->None:
        """Print item into one line. 
        
:param func: parent function. This argument is used to find out the referenced variable names.
:returns: length of the generated text."""
        return _ida_hexrays_ctree.citem_t_print1(self, func)
    __swig_destroy__ = _ida_hexrays_ctree.delete_citem_t
    cinsn: 'cinsn_t *const' = property(_ida_hexrays_ctree.citem_t_cinsn_get)
    cexpr: 'cexpr_t *const' = property(_ida_hexrays_ctree.citem_t_cexpr_get)

    def _get_op(self) ->'ctype_t':
        return _ida_hexrays_ctree.citem_t__get_op(self)

    def _set_op(self, v: 'ctype_t') ->None:
        return _ida_hexrays_ctree.citem_t__set_op(self, v)

    def _ensure_no_op(self):
        if self.op not in [cot_empty, cit_empty]:
            raise Exception('%s has op %s; cannot be modified' % (self,
                self.op))
        return True
    op = property(_get_op, lambda self, v: self._ensure_no_op() and self.
        _set_op(v))
    """item type
"""

    def __dbg_get_meminfo(self) ->str:
        return _ida_hexrays_ctree.citem_t___dbg_get_meminfo(self)

    def __dbg_get_registered_kind(self) ->int:
        return _ida_hexrays_ctree.citem_t___dbg_get_registered_kind(self)

    def _obj_id(self) ->'PyObject *':
        return _ida_hexrays_ctree.citem_t__obj_id(self)
    obj_id = property(_obj_id)

    def _ensure_cond(self, ok, cond_str):
        if not ok:
            raise Exception('Condition "%s" not verified' % cond_str)
        return True

    def _ensure_no_obj(self, o, attr, attr_is_acquired):
        if attr_is_acquired and o is not None:
            raise Exception(
                '%s already owns attribute "%s" (%s); cannot be modified' %
                (self, attr, o))
        return True

    def _ensure_ownership_transferrable(self, v):
        if not v.thisown:
            raise Exception('%s is already owned, and cannot be reused' % v)

    def _acquire_ownership(self, v, acquire):
        if acquire and v is not None and not isinstance(v, ida_idaapi.
            integer_types):
            self._ensure_ownership_transferrable(v)
            v.thisown = False
            dereg = getattr(v, '_deregister', None)
            if dereg:
                dereg()
        return True

    def _maybe_disown_and_deregister(self):
        if self.thisown:
            self.thisown = False
            self._deregister()

    def _own_and_register(self):
        assert not self.thisown
        self.thisown = True
        self._register()

    def replace_by(self, o):
        assert isinstance(o, (cexpr_t, cinsn_t))
        o._maybe_disown_and_deregister()
        self._replace_by(o)

    def _meminfo(self):
        cpp = self.__dbg_get_meminfo()
        rkind = self.__dbg_get_registered_kind()
        rkind_str = ['(not owned)', 'cfuncptr_t', 'cinsn_t', 'cexpr_t',
            'cblock_t', 'mba_t', 'mop_t', 'minsn_t', 'optinsn_t',
            'optblock_t', 'valrng_t', 'udc_filter_t'][rkind]
        return '%s [thisown=%s, owned by IDAPython as=%s]' % (cpp, self.
            thisown, rkind_str)
    meminfo = property(_meminfo)


_ida_hexrays_ctree.citem_t_swigregister(citem_t)


class cexpr_t(citem_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    type: 'tinfo_t' = property(_ida_hexrays_ctree.cexpr_t_type_get,
        _ida_hexrays_ctree.cexpr_t_type_set)
    """expression type. must be carefully maintained
"""
    exflags: int = property(_ida_hexrays_ctree.cexpr_t_exflags_get,
        _ida_hexrays_ctree.cexpr_t_exflags_set)
    """Expression attributes 
        """

    def cpadone(self) ->bool:
        """Pointer arithmetic correction done for this expression?
"""
        return _ida_hexrays_ctree.cexpr_t_cpadone(self)

    def is_odd_lvalue(self) ->bool:
        return _ida_hexrays_ctree.cexpr_t_is_odd_lvalue(self)

    def is_fpop(self) ->bool:
        return _ida_hexrays_ctree.cexpr_t_is_fpop(self)

    def is_cstr(self) ->bool:
        return _ida_hexrays_ctree.cexpr_t_is_cstr(self)

    def is_undef_val(self) ->bool:
        return _ida_hexrays_ctree.cexpr_t_is_undef_val(self)

    def is_jumpout(self) ->bool:
        return _ida_hexrays_ctree.cexpr_t_is_jumpout(self)

    def is_vftable(self) ->bool:
        return _ida_hexrays_ctree.cexpr_t_is_vftable(self)

    def set_cpadone(self) ->None:
        return _ida_hexrays_ctree.cexpr_t_set_cpadone(self)

    def set_vftable(self) ->None:
        return _ida_hexrays_ctree.cexpr_t_set_vftable(self)

    def __init__(self, *args):
        for arg in args[1:]:
            if isinstance(arg, cexpr_t):
                self._ensure_ownership_transferrable(arg)
        _ida_hexrays_ctree.cexpr_t_swiginit(self, _ida_hexrays_ctree.
            new_cexpr_t(*args))
        for arg in args[1:]:
            if isinstance(arg, cexpr_t):
                self._acquire_ownership(arg, True)

    def swap(self, r: 'cexpr_t') ->None:
        return _ida_hexrays_ctree.cexpr_t_swap(self, r)

    def assign(self, r: 'cexpr_t') ->'cexpr_t &':
        return _ida_hexrays_ctree.cexpr_t_assign(self, r)

    def __eq__(self, r: 'cexpr_t') ->bool:
        return _ida_hexrays_ctree.cexpr_t___eq__(self, r)

    def __ne__(self, r: 'cexpr_t') ->bool:
        return _ida_hexrays_ctree.cexpr_t___ne__(self, r)

    def __lt__(self, r: 'cexpr_t') ->bool:
        return _ida_hexrays_ctree.cexpr_t___lt__(self, r)

    def __gt__(self, r: 'cexpr_t') ->bool:
        return _ida_hexrays_ctree.cexpr_t___gt__(self, r)

    def __le__(self, r: 'cexpr_t') ->bool:
        return _ida_hexrays_ctree.cexpr_t___le__(self, r)

    def __ge__(self, r: 'cexpr_t') ->bool:
        return _ida_hexrays_ctree.cexpr_t___ge__(self, r)

    def compare(self, r: 'cexpr_t') ->int:
        return _ida_hexrays_ctree.cexpr_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_cexpr_t

    def _replace_by(self, r: 'cexpr_t') ->None:
        return _ida_hexrays_ctree.cexpr_t__replace_by(self, r)

    def cleanup(self) ->None:
        """Cleanup the expression. This function properly deletes all children and sets the item type to cot_empty. 
        """
        return _ida_hexrays_ctree.cexpr_t_cleanup(self)

    def put_number(self, *args) ->None:
        """Assign a number to the expression. 
        
:param func: current function
:param value: number value
:param nbytes: size of the number in bytes
:param sign: number sign"""
        return _ida_hexrays_ctree.cexpr_t_put_number(self, *args)

    def print1(self, func: 'cfunc_t') ->None:
        """Print expression into one line. 
        
:param func: parent function. This argument is used to find out the referenced variable names."""
        return _ida_hexrays_ctree.cexpr_t_print1(self, func)

    def calc_type(self, recursive: bool) ->None:
        """Calculate the type of the expression. Use this function to calculate the expression type when a new expression is built 
        
:param recursive: if true, types of all children expression will be calculated before calculating our type"""
        return _ida_hexrays_ctree.cexpr_t_calc_type(self, recursive)

    def equal_effect(self, r: 'cexpr_t') ->bool:
        """Compare two expressions. This function tries to compare two expressions in an 'intelligent' manner. For example, it knows about commutitive operators and can ignore useless casts. 
        
:param r: the expression to compare against the current expression
:returns: true expressions can be considered equal"""
        return _ida_hexrays_ctree.cexpr_t_equal_effect(self, r)

    def is_child_of(self, parent: 'citem_t') ->bool:
        """Verify if the specified item is our parent. 
        
:param parent: possible parent item
:returns: true if the specified item is our parent"""
        return _ida_hexrays_ctree.cexpr_t_is_child_of(self, parent)

    def contains_operator(self, needed_op: 'ctype_t', times: int=1) ->bool:
        """Check if the expression contains the specified operator. 
        
:param needed_op: operator code to search for
:param times: how many times the operator code should be present
:returns: true if the expression has at least TIMES children with NEEDED_OP"""
        return _ida_hexrays_ctree.cexpr_t_contains_operator(self, needed_op,
            times)

    def contains_comma(self, times: int=1) ->bool:
        """Does the expression contain a comma operator?
"""
        return _ida_hexrays_ctree.cexpr_t_contains_comma(self, times)

    def contains_insn(self, times: int=1) ->bool:
        """Does the expression contain an embedded statement operator?
"""
        return _ida_hexrays_ctree.cexpr_t_contains_insn(self, times)

    def contains_insn_or_label(self) ->bool:
        """Does the expression contain an embedded statement operator or a label?
"""
        return _ida_hexrays_ctree.cexpr_t_contains_insn_or_label(self)

    def contains_comma_or_insn_or_label(self, maxcommas: int=1) ->bool:
        """Does the expression contain a comma operator or an embedded statement operator or a label?
"""
        return _ida_hexrays_ctree.cexpr_t_contains_comma_or_insn_or_label(self,
            maxcommas)

    def is_nice_expr(self) ->bool:
        """Is nice expression? Nice expressions do not contain comma operators, embedded statements, or labels. 
        """
        return _ida_hexrays_ctree.cexpr_t_is_nice_expr(self)

    def is_nice_cond(self) ->bool:
        """Is nice condition?. Nice condition is a nice expression of the boolean type. 
        """
        return _ida_hexrays_ctree.cexpr_t_is_nice_cond(self)

    def is_call_object_of(self, parent: 'citem_t') ->bool:
        """Is call object? 
        
:returns: true if our expression is the call object of the specified parent expression."""
        return _ida_hexrays_ctree.cexpr_t_is_call_object_of(self, parent)

    def is_call_arg_of(self, parent: 'citem_t') ->bool:
        """Is call argument? 
        
:returns: true if our expression is a call argument of the specified parent expression."""
        return _ida_hexrays_ctree.cexpr_t_is_call_arg_of(self, parent)

    def get_type_sign(self) ->'type_sign_t':
        """Get expression sign.
"""
        return _ida_hexrays_ctree.cexpr_t_get_type_sign(self)

    def is_type_unsigned(self) ->bool:
        """Is expression unsigned?
"""
        return _ida_hexrays_ctree.cexpr_t_is_type_unsigned(self)

    def is_type_signed(self) ->bool:
        """Is expression signed?
"""
        return _ida_hexrays_ctree.cexpr_t_is_type_signed(self)

    def get_high_nbit_bound(self) ->'bit_bound_t':
        """Get max number of bits that can really be used by the expression. For example, x % 16 can yield only 4 non-zero bits, higher bits are zero 
        """
        return _ida_hexrays_ctree.cexpr_t_get_high_nbit_bound(self)

    def get_low_nbit_bound(self) ->int:
        """Get min number of bits that are certainly required to represent the expression. For example, constant 16 always uses 5 bits: 10000. 
        """
        return _ida_hexrays_ctree.cexpr_t_get_low_nbit_bound(self)

    def requires_lvalue(self, child: 'cexpr_t') ->bool:
        """Check if the expression requires an lvalue. 
        
:param child: The function will check if this child of our expression must be an lvalue.
:returns: true if child must be an lvalue."""
        return _ida_hexrays_ctree.cexpr_t_requires_lvalue(self, child)

    def has_side_effects(self) ->bool:
        """Check if the expression has side effects. Calls, pre/post inc/dec, and assignments have side effects. 
        """
        return _ida_hexrays_ctree.cexpr_t_has_side_effects(self)

    def numval(self) ->'uint64':
        """Get numeric value of the expression. This function can be called only on cot_num expressions! 
        """
        return _ida_hexrays_ctree.cexpr_t_numval(self)

    def is_const_value(self, _v: 'uint64') ->bool:
        """Check if the expression is a number with the specified value.
"""
        return _ida_hexrays_ctree.cexpr_t_is_const_value(self, _v)

    def is_negative_const(self) ->bool:
        """Check if the expression is a negative number.
"""
        return _ida_hexrays_ctree.cexpr_t_is_negative_const(self)

    def is_non_negative_const(self) ->bool:
        """Check if the expression is a non-negative number.
"""
        return _ida_hexrays_ctree.cexpr_t_is_non_negative_const(self)

    def is_non_zero_const(self) ->bool:
        """Check if the expression is a non-zero number.
"""
        return _ida_hexrays_ctree.cexpr_t_is_non_zero_const(self)

    def is_zero_const(self) ->bool:
        """Check if the expression is a zero.
"""
        return _ida_hexrays_ctree.cexpr_t_is_zero_const(self)

    def get_const_value(self) ->bool:
        """Get expression value. 
        
:returns: true if the expression is a number."""
        return _ida_hexrays_ctree.cexpr_t_get_const_value(self)

    def maybe_ptr(self) ->bool:
        """May the expression be a pointer?
"""
        return _ida_hexrays_ctree.cexpr_t_maybe_ptr(self)

    def get_ptr_or_array(self) ->'cexpr_t *':
        """Find pointer or array child.
"""
        return _ida_hexrays_ctree.cexpr_t_get_ptr_or_array(self)

    def find_op(self, _op: 'ctype_t') ->'cexpr_t *':
        """Find the child with the specified operator.
"""
        return _ida_hexrays_ctree.cexpr_t_find_op(self, _op)

    def find_num_op(self) ->'cexpr_t *':
        """Find the operand with a numeric value.
"""
        return _ida_hexrays_ctree.cexpr_t_find_num_op(self)

    def theother(self, what: 'cexpr_t') ->'cexpr_t *':
        """Get the other operand. This function returns the other operand (not the specified one) for binary expressions. 
        """
        return _ida_hexrays_ctree.cexpr_t_theother(self, what)

    def get_1num_op(self, o1: 'cexpr_t **', o2: 'cexpr_t **') ->bool:
        """Get pointers to operands. at last one operand should be a number o1 will be pointer to the number 
        """
        return _ida_hexrays_ctree.cexpr_t_get_1num_op(self, o1, o2)

    def dstr(self) ->str:
        return _ida_hexrays_ctree.cexpr_t_dstr(self)

    def _register(self) ->None:
        return _ida_hexrays_ctree.cexpr_t__register(self)

    def _deregister(self) ->None:
        return _ida_hexrays_ctree.cexpr_t__deregister(self)

    def get_v(self) ->'var_ref_t *':
        return _ida_hexrays_ctree.cexpr_t_get_v(self)

    def set_v(self, v: 'var_ref_t') ->None:
        return _ida_hexrays_ctree.cexpr_t_set_v(self, v)
    v = property(lambda self: self.get_v(), lambda self, v: self.set_v(v))
    """used for cot_var
"""

    def _get_n(self) ->'cnumber_t *':
        return _ida_hexrays_ctree.cexpr_t__get_n(self)

    def _set_n(self, _v: 'cnumber_t') ->None:
        return _ida_hexrays_ctree.cexpr_t__set_n(self, _v)

    @property
    def n(self):
        return self._get_n() if self.op == cot_num else None

    @n.setter
    def n(self, value):
        return self._ensure_cond(self.op == cot_num, 'self.op == cot_num'
            ) and self._ensure_no_obj(self._get_n(), 'n', True
            ) and self._acquire_ownership(value, True) and self._set_n(value)

    def _get_fpc(self) ->'fnumber_t *':
        return _ida_hexrays_ctree.cexpr_t__get_fpc(self)

    def _set_fpc(self, _v: 'fnumber_t *') ->None:
        return _ida_hexrays_ctree.cexpr_t__set_fpc(self, _v)

    @property
    def fpc(self):
        return self._get_fpc() if self.op == cot_fnum else None

    @fpc.setter
    def fpc(self, value):
        return self._ensure_cond(self.op == cot_fnum, 'self.op == cot_fnum'
            ) and self._ensure_no_obj(self._get_fpc(), 'fpc', True
            ) and self._acquire_ownership(value, True) and self._set_fpc(value)

    def _get_x(self) ->'cexpr_t *':
        return _ida_hexrays_ctree.cexpr_t__get_x(self)

    def _set_x(self, _v: 'cexpr_t') ->None:
        return _ida_hexrays_ctree.cexpr_t__set_x(self, _v)

    @property
    def x(self):
        return self._get_x() if op_uses_x(self.op) else None

    @x.setter
    def x(self, value):
        return self._ensure_cond(op_uses_x(self.op), 'op_uses_x(self.op)'
            ) and self._ensure_no_obj(self._get_x(), 'x', True
            ) and self._acquire_ownership(value, True) and self._set_x(value)

    def _get_y(self) ->'cexpr_t *':
        return _ida_hexrays_ctree.cexpr_t__get_y(self)

    def _set_y(self, _v: 'cexpr_t') ->None:
        return _ida_hexrays_ctree.cexpr_t__set_y(self, _v)

    @property
    def y(self):
        return self._get_y() if op_uses_y(self.op) else None

    @y.setter
    def y(self, value):
        return self._ensure_cond(op_uses_y(self.op), 'op_uses_y(self.op)'
            ) and self._ensure_no_obj(self._get_y(), 'y', True
            ) and self._acquire_ownership(value, True) and self._set_y(value)

    def _get_z(self) ->'cexpr_t *':
        return _ida_hexrays_ctree.cexpr_t__get_z(self)

    def _set_z(self, _v: 'cexpr_t') ->None:
        return _ida_hexrays_ctree.cexpr_t__set_z(self, _v)

    @property
    def z(self):
        return self._get_z() if op_uses_z(self.op) else None

    @z.setter
    def z(self, value):
        return self._ensure_cond(op_uses_z(self.op), 'op_uses_z(self.op)'
            ) and self._ensure_no_obj(self._get_z(), 'z', True
            ) and self._acquire_ownership(value, True) and self._set_z(value)

    def _get_a(self) ->'carglist_t *':
        return _ida_hexrays_ctree.cexpr_t__get_a(self)

    def _set_a(self, _v: 'carglist_t') ->None:
        return _ida_hexrays_ctree.cexpr_t__set_a(self, _v)

    @property
    def a(self):
        return self._get_a() if self.op == cot_call else None

    @a.setter
    def a(self, value):
        return self._ensure_cond(self.op == cot_call, 'self.op == cot_call'
            ) and self._ensure_no_obj(self._get_a(), 'a', True
            ) and self._acquire_ownership(value, True) and self._set_a(value)

    def _get_insn(self) ->'cinsn_t *':
        return _ida_hexrays_ctree.cexpr_t__get_insn(self)

    def _set_insn(self, _v: 'cinsn_t') ->None:
        return _ida_hexrays_ctree.cexpr_t__set_insn(self, _v)

    @property
    def insn(self):
        return self._get_insn() if self.op == cot_insn else None

    @insn.setter
    def insn(self, value):
        return self._ensure_cond(self.op == cot_insn, 'self.op == cot_insn'
            ) and self._ensure_no_obj(self._get_insn(), 'insn', True
            ) and self._acquire_ownership(value, True) and self._set_insn(value
            )

    def _get_m(self) ->int:
        return _ida_hexrays_ctree.cexpr_t__get_m(self)

    def _set_m(self, _v: int) ->None:
        return _ida_hexrays_ctree.cexpr_t__set_m(self, _v)

    @property
    def m(self):
        return self._get_m(
            ) if self.op == cot_memptr or self.op == cot_memref else 0

    @m.setter
    def m(self, value):
        return self._ensure_cond(self.op == cot_memptr or self.op ==
            cot_memref, 'self.op == cot_memptr or self.op == cot_memref'
            ) and self._set_m(value)

    def _get_ptrsize(self) ->int:
        return _ida_hexrays_ctree.cexpr_t__get_ptrsize(self)

    def _set_ptrsize(self, _v: int) ->None:
        return _ida_hexrays_ctree.cexpr_t__set_ptrsize(self, _v)

    @property
    def ptrsize(self):
        return self._get_ptrsize(
            ) if self.op == cot_ptr or self.op == cot_memptr else 0

    @ptrsize.setter
    def ptrsize(self, value):
        return self._ensure_cond(self.op == cot_ptr or self.op ==
            cot_memptr, 'self.op == cot_ptr or self.op == cot_memptr'
            ) and self._set_ptrsize(value)

    def _get_obj_ea(self) ->ida_idaapi.ea_t:
        return _ida_hexrays_ctree.cexpr_t__get_obj_ea(self)

    def _set_obj_ea(self, _v: ida_idaapi.ea_t) ->None:
        return _ida_hexrays_ctree.cexpr_t__set_obj_ea(self, _v)

    @property
    def obj_ea(self):
        return self._get_obj_ea() if self.op == cot_obj else ida_idaapi.BADADDR

    @obj_ea.setter
    def obj_ea(self, value):
        return self._ensure_cond(self.op == cot_obj, 'self.op == cot_obj'
            ) and self._set_obj_ea(value)

    def _get_refwidth(self) ->int:
        return _ida_hexrays_ctree.cexpr_t__get_refwidth(self)

    def _set_refwidth(self, _v: int) ->None:
        return _ida_hexrays_ctree.cexpr_t__set_refwidth(self, _v)

    @property
    def refwidth(self):
        return self._get_refwidth() if True else 0

    @refwidth.setter
    def refwidth(self, value):
        return self._ensure_cond(True, 'True') and self._set_refwidth(value)

    def _get_helper(self) ->str:
        return _ida_hexrays_ctree.cexpr_t__get_helper(self)

    def _set_helper(self, _v: str) ->None:
        return _ida_hexrays_ctree.cexpr_t__set_helper(self, _v)

    @property
    def helper(self):
        return self._get_helper() if self.op == cot_helper else None

    @helper.setter
    def helper(self, value):
        return self._ensure_cond(self.op == cot_helper, 'self.op == cot_helper'
            ) and self._ensure_no_obj(self._get_helper(), 'helper', False
            ) and self._acquire_ownership(value, False) and self._set_helper(
            value)

    def _get_string(self) ->str:
        return _ida_hexrays_ctree.cexpr_t__get_string(self)

    def _set_string(self, _v: str) ->None:
        return _ida_hexrays_ctree.cexpr_t__set_string(self, _v)

    @property
    def string(self):
        return self._get_string() if self.op == cot_str else None

    @string.setter
    def string(self, value):
        return self._ensure_cond(self.op == cot_str, 'self.op == cot_str'
            ) and self._ensure_no_obj(self._get_string(), 'string', False
            ) and self._acquire_ownership(value, False) and self._set_string(
            value)


_ida_hexrays_ctree.cexpr_t_swigregister(cexpr_t)
EXFL_CPADONE = _ida_hexrays_ctree.EXFL_CPADONE
"""pointer arithmetic correction done
"""
EXFL_LVALUE = _ida_hexrays_ctree.EXFL_LVALUE
"""expression is lvalue even if it doesn't look like it
"""
EXFL_FPOP = _ida_hexrays_ctree.EXFL_FPOP
"""floating point operation
"""
EXFL_ALONE = _ida_hexrays_ctree.EXFL_ALONE
"""standalone helper
"""
EXFL_CSTR = _ida_hexrays_ctree.EXFL_CSTR
"""string literal
"""
EXFL_PARTIAL = _ida_hexrays_ctree.EXFL_PARTIAL
"""type of the expression is considered partial
"""
EXFL_UNDEF = _ida_hexrays_ctree.EXFL_UNDEF
"""expression uses undefined value
"""
EXFL_JUMPOUT = _ida_hexrays_ctree.EXFL_JUMPOUT
"""jump out-of-function
"""
EXFL_VFTABLE = _ida_hexrays_ctree.EXFL_VFTABLE
"""is ptr to vftable (used for cot_memptr, cot_memref)
"""
EXFL_ALL = _ida_hexrays_ctree.EXFL_ALL
"""all currently defined bits
"""


class ceinsn_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    expr: 'cexpr_t' = property(_ida_hexrays_ctree.ceinsn_t_expr_get,
        _ida_hexrays_ctree.ceinsn_t_expr_set)
    """Expression of the statement.
"""

    def __init__(self):
        _ida_hexrays_ctree.ceinsn_t_swiginit(self, _ida_hexrays_ctree.
            new_ceinsn_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_ceinsn_t


_ida_hexrays_ctree.ceinsn_t_swigregister(ceinsn_t)
CALC_CURLY_BRACES = _ida_hexrays_ctree.CALC_CURLY_BRACES
"""print curly braces if necessary
"""
NO_CURLY_BRACES = _ida_hexrays_ctree.NO_CURLY_BRACES
"""don't print curly braces
"""
USE_CURLY_BRACES = _ida_hexrays_ctree.USE_CURLY_BRACES
"""print curly braces without any checks
"""


class cif_t(ceinsn_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ithen: 'cinsn_t *' = property(_ida_hexrays_ctree.cif_t_ithen_get,
        _ida_hexrays_ctree.cif_t_ithen_set)
    """Then-branch of the if-statement.
"""
    ielse: 'cinsn_t *' = property(_ida_hexrays_ctree.cif_t_ielse_get,
        _ida_hexrays_ctree.cif_t_ielse_set)
    """Else-branch of the if-statement. May be nullptr.
"""

    def __init__(self, *args):
        _ida_hexrays_ctree.cif_t_swiginit(self, _ida_hexrays_ctree.
            new_cif_t(*args))

    def assign(self, r: 'cif_t') ->'cif_t &':
        return _ida_hexrays_ctree.cif_t_assign(self, r)

    def __eq__(self, r: 'cif_t') ->bool:
        return _ida_hexrays_ctree.cif_t___eq__(self, r)

    def __ne__(self, r: 'cif_t') ->bool:
        return _ida_hexrays_ctree.cif_t___ne__(self, r)

    def __lt__(self, r: 'cif_t') ->bool:
        return _ida_hexrays_ctree.cif_t___lt__(self, r)

    def __gt__(self, r: 'cif_t') ->bool:
        return _ida_hexrays_ctree.cif_t___gt__(self, r)

    def __le__(self, r: 'cif_t') ->bool:
        return _ida_hexrays_ctree.cif_t___le__(self, r)

    def __ge__(self, r: 'cif_t') ->bool:
        return _ida_hexrays_ctree.cif_t___ge__(self, r)

    def compare(self, r: 'cif_t') ->int:
        return _ida_hexrays_ctree.cif_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_cif_t

    def cleanup(self) ->None:
        return _ida_hexrays_ctree.cif_t_cleanup(self)


_ida_hexrays_ctree.cif_t_swigregister(cif_t)


class cloop_t(ceinsn_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    body: 'cinsn_t *' = property(_ida_hexrays_ctree.cloop_t_body_get,
        _ida_hexrays_ctree.cloop_t_body_set)

    def __init__(self, *args):
        _ida_hexrays_ctree.cloop_t_swiginit(self, _ida_hexrays_ctree.
            new_cloop_t(*args))

    def assign(self, r: 'cloop_t') ->'cloop_t &':
        return _ida_hexrays_ctree.cloop_t_assign(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_cloop_t

    def cleanup(self) ->None:
        return _ida_hexrays_ctree.cloop_t_cleanup(self)


_ida_hexrays_ctree.cloop_t_swigregister(cloop_t)


class cfor_t(cloop_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    init: 'cexpr_t' = property(_ida_hexrays_ctree.cfor_t_init_get,
        _ida_hexrays_ctree.cfor_t_init_set)
    """Initialization expression.
"""
    step: 'cexpr_t' = property(_ida_hexrays_ctree.cfor_t_step_get,
        _ida_hexrays_ctree.cfor_t_step_set)
    """Step expression.
"""

    def __eq__(self, r: 'cfor_t') ->bool:
        return _ida_hexrays_ctree.cfor_t___eq__(self, r)

    def __ne__(self, r: 'cfor_t') ->bool:
        return _ida_hexrays_ctree.cfor_t___ne__(self, r)

    def __lt__(self, r: 'cfor_t') ->bool:
        return _ida_hexrays_ctree.cfor_t___lt__(self, r)

    def __gt__(self, r: 'cfor_t') ->bool:
        return _ida_hexrays_ctree.cfor_t___gt__(self, r)

    def __le__(self, r: 'cfor_t') ->bool:
        return _ida_hexrays_ctree.cfor_t___le__(self, r)

    def __ge__(self, r: 'cfor_t') ->bool:
        return _ida_hexrays_ctree.cfor_t___ge__(self, r)

    def compare(self, r: 'cfor_t') ->int:
        return _ida_hexrays_ctree.cfor_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.cfor_t_swiginit(self, _ida_hexrays_ctree.
            new_cfor_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cfor_t


_ida_hexrays_ctree.cfor_t_swigregister(cfor_t)


class cwhile_t(cloop_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __eq__(self, r: 'cwhile_t') ->bool:
        return _ida_hexrays_ctree.cwhile_t___eq__(self, r)

    def __ne__(self, r: 'cwhile_t') ->bool:
        return _ida_hexrays_ctree.cwhile_t___ne__(self, r)

    def __lt__(self, r: 'cwhile_t') ->bool:
        return _ida_hexrays_ctree.cwhile_t___lt__(self, r)

    def __gt__(self, r: 'cwhile_t') ->bool:
        return _ida_hexrays_ctree.cwhile_t___gt__(self, r)

    def __le__(self, r: 'cwhile_t') ->bool:
        return _ida_hexrays_ctree.cwhile_t___le__(self, r)

    def __ge__(self, r: 'cwhile_t') ->bool:
        return _ida_hexrays_ctree.cwhile_t___ge__(self, r)

    def compare(self, r: 'cwhile_t') ->int:
        return _ida_hexrays_ctree.cwhile_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.cwhile_t_swiginit(self, _ida_hexrays_ctree.
            new_cwhile_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cwhile_t


_ida_hexrays_ctree.cwhile_t_swigregister(cwhile_t)


class cdo_t(cloop_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __eq__(self, r: 'cdo_t') ->bool:
        return _ida_hexrays_ctree.cdo_t___eq__(self, r)

    def __ne__(self, r: 'cdo_t') ->bool:
        return _ida_hexrays_ctree.cdo_t___ne__(self, r)

    def __lt__(self, r: 'cdo_t') ->bool:
        return _ida_hexrays_ctree.cdo_t___lt__(self, r)

    def __gt__(self, r: 'cdo_t') ->bool:
        return _ida_hexrays_ctree.cdo_t___gt__(self, r)

    def __le__(self, r: 'cdo_t') ->bool:
        return _ida_hexrays_ctree.cdo_t___le__(self, r)

    def __ge__(self, r: 'cdo_t') ->bool:
        return _ida_hexrays_ctree.cdo_t___ge__(self, r)

    def compare(self, r: 'cdo_t') ->int:
        return _ida_hexrays_ctree.cdo_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.cdo_t_swiginit(self, _ida_hexrays_ctree.new_cdo_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cdo_t


_ida_hexrays_ctree.cdo_t_swigregister(cdo_t)


class creturn_t(ceinsn_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __eq__(self, r: 'creturn_t') ->bool:
        return _ida_hexrays_ctree.creturn_t___eq__(self, r)

    def __ne__(self, r: 'creturn_t') ->bool:
        return _ida_hexrays_ctree.creturn_t___ne__(self, r)

    def __lt__(self, r: 'creturn_t') ->bool:
        return _ida_hexrays_ctree.creturn_t___lt__(self, r)

    def __gt__(self, r: 'creturn_t') ->bool:
        return _ida_hexrays_ctree.creturn_t___gt__(self, r)

    def __le__(self, r: 'creturn_t') ->bool:
        return _ida_hexrays_ctree.creturn_t___le__(self, r)

    def __ge__(self, r: 'creturn_t') ->bool:
        return _ida_hexrays_ctree.creturn_t___ge__(self, r)

    def compare(self, r: 'creturn_t') ->int:
        return _ida_hexrays_ctree.creturn_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.creturn_t_swiginit(self, _ida_hexrays_ctree.
            new_creturn_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_creturn_t


_ida_hexrays_ctree.creturn_t_swigregister(creturn_t)


class cgoto_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    label_num: int = property(_ida_hexrays_ctree.cgoto_t_label_num_get,
        _ida_hexrays_ctree.cgoto_t_label_num_set)
    """Target label number.
"""

    def __eq__(self, r: 'cgoto_t') ->bool:
        return _ida_hexrays_ctree.cgoto_t___eq__(self, r)

    def __ne__(self, r: 'cgoto_t') ->bool:
        return _ida_hexrays_ctree.cgoto_t___ne__(self, r)

    def __lt__(self, r: 'cgoto_t') ->bool:
        return _ida_hexrays_ctree.cgoto_t___lt__(self, r)

    def __gt__(self, r: 'cgoto_t') ->bool:
        return _ida_hexrays_ctree.cgoto_t___gt__(self, r)

    def __le__(self, r: 'cgoto_t') ->bool:
        return _ida_hexrays_ctree.cgoto_t___le__(self, r)

    def __ge__(self, r: 'cgoto_t') ->bool:
        return _ida_hexrays_ctree.cgoto_t___ge__(self, r)

    def compare(self, r: 'cgoto_t') ->int:
        return _ida_hexrays_ctree.cgoto_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.cgoto_t_swiginit(self, _ida_hexrays_ctree.
            new_cgoto_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cgoto_t


_ida_hexrays_ctree.cgoto_t_swigregister(cgoto_t)


class casm_t(ida_pro.eavec_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_ctree.casm_t_swiginit(self, _ida_hexrays_ctree.
            new_casm_t(*args))

    def __eq__(self, r: 'casm_t') ->bool:
        return _ida_hexrays_ctree.casm_t___eq__(self, r)

    def __ne__(self, r: 'casm_t') ->bool:
        return _ida_hexrays_ctree.casm_t___ne__(self, r)

    def __lt__(self, r: 'casm_t') ->bool:
        return _ida_hexrays_ctree.casm_t___lt__(self, r)

    def __gt__(self, r: 'casm_t') ->bool:
        return _ida_hexrays_ctree.casm_t___gt__(self, r)

    def __le__(self, r: 'casm_t') ->bool:
        return _ida_hexrays_ctree.casm_t___le__(self, r)

    def __ge__(self, r: 'casm_t') ->bool:
        return _ida_hexrays_ctree.casm_t___ge__(self, r)

    def compare(self, r: 'casm_t') ->int:
        return _ida_hexrays_ctree.casm_t_compare(self, r)

    def one_insn(self) ->bool:
        return _ida_hexrays_ctree.casm_t_one_insn(self)
    __swig_destroy__ = _ida_hexrays_ctree.delete_casm_t


_ida_hexrays_ctree.casm_t_swigregister(casm_t)


class cinsn_t(citem_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ctry: 'ctry_t *' = property(_ida_hexrays_ctree.cinsn_t_ctry_get,
        _ida_hexrays_ctree.cinsn_t_ctry_set)
    """details of try-statement
"""
    cthrow: 'cthrow_t *' = property(_ida_hexrays_ctree.cinsn_t_cthrow_get,
        _ida_hexrays_ctree.cinsn_t_cthrow_set)
    """details of throw-statement
"""

    def __init__(self, *args):
        _ida_hexrays_ctree.cinsn_t_swiginit(self, _ida_hexrays_ctree.
            new_cinsn_t(*args))

    def swap(self, r: 'cinsn_t') ->None:
        return _ida_hexrays_ctree.cinsn_t_swap(self, r)

    def assign(self, r: 'cinsn_t') ->'cinsn_t &':
        return _ida_hexrays_ctree.cinsn_t_assign(self, r)

    def __eq__(self, r: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsn_t___eq__(self, r)

    def __ne__(self, r: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsn_t___ne__(self, r)

    def __lt__(self, r: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsn_t___lt__(self, r)

    def __gt__(self, r: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsn_t___gt__(self, r)

    def __le__(self, r: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsn_t___le__(self, r)

    def __ge__(self, r: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsn_t___ge__(self, r)

    def compare(self, r: 'cinsn_t') ->int:
        return _ida_hexrays_ctree.cinsn_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_cinsn_t

    def _replace_by(self, r: 'cinsn_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__replace_by(self, r)

    def cleanup(self) ->None:
        """Cleanup the statement. This function properly deletes all children and sets the item type to cit_empty. 
        """
        return _ida_hexrays_ctree.cinsn_t_cleanup(self)

    def zero(self) ->None:
        """Overwrite with zeroes without cleaning memory or deleting children.
"""
        return _ida_hexrays_ctree.cinsn_t_zero(self)

    def new_insn(self, insn_ea: ida_idaapi.ea_t) ->'cinsn_t &':
        """Create a new statement. The current statement must be a block. The new statement will be appended to it. 
        
:param insn_ea: statement address"""
        return _ida_hexrays_ctree.cinsn_t_new_insn(self, insn_ea)

    def create_if(self, cnd: 'cexpr_t') ->'cif_t &':
        """Create a new if-statement. The current statement must be a block. The new statement will be appended to it. 
        
:param cnd: if condition. It will be deleted after being copied."""
        return _ida_hexrays_ctree.cinsn_t_create_if(self, cnd)

    def _print(self, indent: int, vp: 'vc_printer_t', use_curly:
        'use_curly_t'=CALC_CURLY_BRACES) ->None:
        return _ida_hexrays_ctree.cinsn_t__print(self, indent, vp, use_curly)

    def print1(self, func: 'cfunc_t') ->None:
        """Print the statement into one line. Currently this function is not available. 
        
:param func: parent function. This argument is used to find out the referenced variable names."""
        return _ida_hexrays_ctree.cinsn_t_print1(self, func)

    def is_ordinary_flow(self) ->bool:
        """Check if the statement passes execution to the next statement. 
        
:returns: false if the statement breaks the control flow (like goto, return, etc)"""
        return _ida_hexrays_ctree.cinsn_t_is_ordinary_flow(self)

    def contains_insn(self, type: 'ctype_t', times: int=1) ->bool:
        """Check if the statement contains a statement of the specified type. 
        
:param type: statement opcode to look for
:param times: how many times TYPE should be present
:returns: true if the statement has at least TIMES children with opcode == TYPE"""
        return _ida_hexrays_ctree.cinsn_t_contains_insn(self, type, times)

    def collect_free_breaks(self, breaks: 'cinsnptrvec_t') ->bool:
        """Collect free `break` statements. This function finds all free `break` statements within the current statement. A `break` statement is free if it does not have a loop or switch parent that that is also within the current statement. 
        
:param breaks: pointer to the variable where the vector of all found free `break` statements is returned. This argument can be nullptr.
:returns: true if some free `break` statements have been found"""
        return _ida_hexrays_ctree.cinsn_t_collect_free_breaks(self, breaks)

    def collect_free_continues(self, continues: 'cinsnptrvec_t') ->bool:
        """Collect free `continue` statements. This function finds all free `continue` statements within the current statement. A `continue` statement is free if it does not have a loop parent that that is also within the current statement. 
        
:param continues: pointer to the variable where the vector of all found free `continue` statements is returned. This argument can be nullptr.
:returns: true if some free `continue` statements have been found"""
        return _ida_hexrays_ctree.cinsn_t_collect_free_continues(self,
            continues)

    def contains_free_break(self) ->bool:
        """Check if the statement has free `break` statements.
"""
        return _ida_hexrays_ctree.cinsn_t_contains_free_break(self)

    def contains_free_continue(self) ->bool:
        """Check if the statement has free `continue` statements.
"""
        return _ida_hexrays_ctree.cinsn_t_contains_free_continue(self)

    def dstr(self) ->str:
        return _ida_hexrays_ctree.cinsn_t_dstr(self)

    def _register(self) ->None:
        return _ida_hexrays_ctree.cinsn_t__register(self)

    def _deregister(self) ->None:
        return _ida_hexrays_ctree.cinsn_t__deregister(self)

    @staticmethod
    def insn_is_epilog(insn: 'cinsn_t') ->bool:
        return _ida_hexrays_ctree.cinsn_t_insn_is_epilog(insn)

    def is_epilog(self):
        return cinsn_t.insn_is_epilog(self)

    def _get_cblock(self) ->'cblock_t *':
        return _ida_hexrays_ctree.cinsn_t__get_cblock(self)

    def _set_cblock(self, _v: 'cblock_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_cblock(self, _v)

    @property
    def cblock(self):
        return self._get_cblock() if self.op == cit_block else None

    @cblock.setter
    def cblock(self, value):
        return self._ensure_cond(self.op == cit_block, 'self.op == cit_block'
            ) and self._ensure_no_obj(self._get_cblock(), 'cblock', True
            ) and self._acquire_ownership(value, True) and self._set_cblock(
            value)

    def _get_cexpr(self) ->'cexpr_t *':
        return _ida_hexrays_ctree.cinsn_t__get_cexpr(self)

    def _set_cexpr(self, _v: 'cexpr_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_cexpr(self, _v)

    @property
    def cexpr(self):
        return self._get_cexpr() if self.op == cit_expr else None

    @cexpr.setter
    def cexpr(self, value):
        return self._ensure_cond(self.op == cit_expr, 'self.op == cit_expr'
            ) and self._ensure_no_obj(self._get_cexpr(), 'cexpr', True
            ) and self._acquire_ownership(value, True) and self._set_cexpr(
            value)

    def _get_cif(self) ->'cif_t *':
        return _ida_hexrays_ctree.cinsn_t__get_cif(self)

    def _set_cif(self, _v: 'cif_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_cif(self, _v)

    @property
    def cif(self):
        return self._get_cif() if self.op == cit_if else None

    @cif.setter
    def cif(self, value):
        return self._ensure_cond(self.op == cit_if, 'self.op == cit_if'
            ) and self._ensure_no_obj(self._get_cif(), 'cif', True
            ) and self._acquire_ownership(value, True) and self._set_cif(value)

    def _get_cfor(self) ->'cfor_t *':
        return _ida_hexrays_ctree.cinsn_t__get_cfor(self)

    def _set_cfor(self, _v: 'cfor_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_cfor(self, _v)

    @property
    def cfor(self):
        return self._get_cfor() if self.op == cit_for else None

    @cfor.setter
    def cfor(self, value):
        return self._ensure_cond(self.op == cit_for, 'self.op == cit_for'
            ) and self._ensure_no_obj(self._get_cfor(), 'cfor', True
            ) and self._acquire_ownership(value, True) and self._set_cfor(value
            )

    def _get_cwhile(self) ->'cwhile_t *':
        return _ida_hexrays_ctree.cinsn_t__get_cwhile(self)

    def _set_cwhile(self, _v: 'cwhile_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_cwhile(self, _v)

    @property
    def cwhile(self):
        return self._get_cwhile() if self.op == cit_while else None

    @cwhile.setter
    def cwhile(self, value):
        return self._ensure_cond(self.op == cit_while, 'self.op == cit_while'
            ) and self._ensure_no_obj(self._get_cwhile(), 'cwhile', True
            ) and self._acquire_ownership(value, True) and self._set_cwhile(
            value)

    def _get_cdo(self) ->'cdo_t *':
        return _ida_hexrays_ctree.cinsn_t__get_cdo(self)

    def _set_cdo(self, _v: 'cdo_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_cdo(self, _v)

    @property
    def cdo(self):
        return self._get_cdo() if self.op == cit_do else None

    @cdo.setter
    def cdo(self, value):
        return self._ensure_cond(self.op == cit_do, 'self.op == cit_do'
            ) and self._ensure_no_obj(self._get_cdo(), 'cdo', True
            ) and self._acquire_ownership(value, True) and self._set_cdo(value)

    def _get_cswitch(self) ->'cswitch_t *':
        return _ida_hexrays_ctree.cinsn_t__get_cswitch(self)

    def _set_cswitch(self, _v: 'cswitch_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_cswitch(self, _v)

    @property
    def cswitch(self):
        return self._get_cswitch() if self.op == cit_switch else None

    @cswitch.setter
    def cswitch(self, value):
        return self._ensure_cond(self.op == cit_switch, 'self.op == cit_switch'
            ) and self._ensure_no_obj(self._get_cswitch(), 'cswitch', True
            ) and self._acquire_ownership(value, True) and self._set_cswitch(
            value)

    def _get_creturn(self) ->'creturn_t *':
        return _ida_hexrays_ctree.cinsn_t__get_creturn(self)

    def _set_creturn(self, _v: 'creturn_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_creturn(self, _v)

    @property
    def creturn(self):
        return self._get_creturn() if self.op == cit_return else None

    @creturn.setter
    def creturn(self, value):
        return self._ensure_cond(self.op == cit_return, 'self.op == cit_return'
            ) and self._ensure_no_obj(self._get_creturn(), 'creturn', True
            ) and self._acquire_ownership(value, True) and self._set_creturn(
            value)

    def _get_cgoto(self) ->'cgoto_t *':
        return _ida_hexrays_ctree.cinsn_t__get_cgoto(self)

    def _set_cgoto(self, _v: 'cgoto_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_cgoto(self, _v)

    @property
    def cgoto(self):
        return self._get_cgoto() if self.op == cit_goto else None

    @cgoto.setter
    def cgoto(self, value):
        return self._ensure_cond(self.op == cit_goto, 'self.op == cit_goto'
            ) and self._ensure_no_obj(self._get_cgoto(), 'cgoto', True
            ) and self._acquire_ownership(value, True) and self._set_cgoto(
            value)

    def _get_casm(self) ->'casm_t *':
        return _ida_hexrays_ctree.cinsn_t__get_casm(self)

    def _set_casm(self, _v: 'casm_t') ->None:
        return _ida_hexrays_ctree.cinsn_t__set_casm(self, _v)

    @property
    def casm(self):
        return self._get_casm() if self.op == cit_asm else None

    @casm.setter
    def casm(self, value):
        return self._ensure_cond(self.op == cit_asm, 'self.op == cit_asm'
            ) and self._ensure_no_obj(self._get_casm(), 'casm', True
            ) and self._acquire_ownership(value, True) and self._set_casm(value
            )


_ida_hexrays_ctree.cinsn_t_swigregister(cinsn_t)


class cblock_t(cinsn_list_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __eq__(self, r: 'cblock_t') ->bool:
        return _ida_hexrays_ctree.cblock_t___eq__(self, r)

    def __ne__(self, r: 'cblock_t') ->bool:
        return _ida_hexrays_ctree.cblock_t___ne__(self, r)

    def __lt__(self, r: 'cblock_t') ->bool:
        return _ida_hexrays_ctree.cblock_t___lt__(self, r)

    def __gt__(self, r: 'cblock_t') ->bool:
        return _ida_hexrays_ctree.cblock_t___gt__(self, r)

    def __le__(self, r: 'cblock_t') ->bool:
        return _ida_hexrays_ctree.cblock_t___le__(self, r)

    def __ge__(self, r: 'cblock_t') ->bool:
        return _ida_hexrays_ctree.cblock_t___ge__(self, r)

    def compare(self, r: 'cblock_t') ->int:
        return _ida_hexrays_ctree.cblock_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.cblock_t_swiginit(self, _ida_hexrays_ctree.
            new_cblock_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cblock_t

    def _deregister(self) ->None:
        return _ida_hexrays_ctree.cblock_t__deregister(self)


_ida_hexrays_ctree.cblock_t_swigregister(cblock_t)


class carg_t(cexpr_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    is_vararg: bool = property(_ida_hexrays_ctree.carg_t_is_vararg_get,
        _ida_hexrays_ctree.carg_t_is_vararg_set)
    """is a vararg (matches ...)
"""
    formal_type: 'tinfo_t' = property(_ida_hexrays_ctree.
        carg_t_formal_type_get, _ida_hexrays_ctree.carg_t_formal_type_set)
    """formal parameter type (if known)
"""

    def consume_cexpr(self, e: 'cexpr_t') ->None:
        return _ida_hexrays_ctree.carg_t_consume_cexpr(self, e)

    def __eq__(self, r: 'carg_t') ->bool:
        return _ida_hexrays_ctree.carg_t___eq__(self, r)

    def __ne__(self, r: 'carg_t') ->bool:
        return _ida_hexrays_ctree.carg_t___ne__(self, r)

    def __lt__(self, r: 'carg_t') ->bool:
        return _ida_hexrays_ctree.carg_t___lt__(self, r)

    def __gt__(self, r: 'carg_t') ->bool:
        return _ida_hexrays_ctree.carg_t___gt__(self, r)

    def __le__(self, r: 'carg_t') ->bool:
        return _ida_hexrays_ctree.carg_t___le__(self, r)

    def __ge__(self, r: 'carg_t') ->bool:
        return _ida_hexrays_ctree.carg_t___ge__(self, r)

    def compare(self, r: 'carg_t') ->int:
        return _ida_hexrays_ctree.carg_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.carg_t_swiginit(self, _ida_hexrays_ctree.
            new_carg_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_carg_t


_ida_hexrays_ctree.carg_t_swigregister(carg_t)


class carglist_t(qvector_carg_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    functype: 'tinfo_t' = property(_ida_hexrays_ctree.
        carglist_t_functype_get, _ida_hexrays_ctree.carglist_t_functype_set)
    """function object type
"""
    flags: int = property(_ida_hexrays_ctree.carglist_t_flags_get,
        _ida_hexrays_ctree.carglist_t_flags_set)
    """call flags
"""

    def __init__(self, *args):
        _ida_hexrays_ctree.carglist_t_swiginit(self, _ida_hexrays_ctree.
            new_carglist_t(*args))

    def __eq__(self, r: 'carglist_t') ->bool:
        return _ida_hexrays_ctree.carglist_t___eq__(self, r)

    def __ne__(self, r: 'carglist_t') ->bool:
        return _ida_hexrays_ctree.carglist_t___ne__(self, r)

    def __lt__(self, r: 'carglist_t') ->bool:
        return _ida_hexrays_ctree.carglist_t___lt__(self, r)

    def __gt__(self, r: 'carglist_t') ->bool:
        return _ida_hexrays_ctree.carglist_t___gt__(self, r)

    def __le__(self, r: 'carglist_t') ->bool:
        return _ida_hexrays_ctree.carglist_t___le__(self, r)

    def __ge__(self, r: 'carglist_t') ->bool:
        return _ida_hexrays_ctree.carglist_t___ge__(self, r)

    def compare(self, r: 'carglist_t') ->int:
        return _ida_hexrays_ctree.carglist_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_carglist_t


_ida_hexrays_ctree.carglist_t_swigregister(carglist_t)
CFL_FINAL = _ida_hexrays_ctree.CFL_FINAL
"""call type is final, should not be changed
"""
CFL_HELPER = _ida_hexrays_ctree.CFL_HELPER
"""created from a decompiler helper function
"""
CFL_NORET = _ida_hexrays_ctree.CFL_NORET
"""call does not return
"""


class ccase_t(cinsn_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    values: 'uint64vec_t' = property(_ida_hexrays_ctree.ccase_t_values_get,
        _ida_hexrays_ctree.ccase_t_values_set)
    """List of case values. if empty, then 'default' case 
        """

    def __eq__(self, r: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.ccase_t___eq__(self, r)

    def __ne__(self, r: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.ccase_t___ne__(self, r)

    def __lt__(self, r: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.ccase_t___lt__(self, r)

    def __gt__(self, r: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.ccase_t___gt__(self, r)

    def __le__(self, r: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.ccase_t___le__(self, r)

    def __ge__(self, r: 'ccase_t') ->bool:
        return _ida_hexrays_ctree.ccase_t___ge__(self, r)

    def compare(self, r: 'ccase_t') ->int:
        return _ida_hexrays_ctree.ccase_t_compare(self, r)

    def size(self) ->int:
        return _ida_hexrays_ctree.ccase_t_size(self)

    def value(self, i: int) ->'uint64 const &':
        return _ida_hexrays_ctree.ccase_t_value(self, i)

    def __init__(self):
        _ida_hexrays_ctree.ccase_t_swiginit(self, _ida_hexrays_ctree.
            new_ccase_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_ccase_t


_ida_hexrays_ctree.ccase_t_swigregister(ccase_t)


class ccases_t(qvector_ccase_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __eq__(self, r: 'ccases_t') ->bool:
        return _ida_hexrays_ctree.ccases_t___eq__(self, r)

    def __ne__(self, r: 'ccases_t') ->bool:
        return _ida_hexrays_ctree.ccases_t___ne__(self, r)

    def __lt__(self, r: 'ccases_t') ->bool:
        return _ida_hexrays_ctree.ccases_t___lt__(self, r)

    def __gt__(self, r: 'ccases_t') ->bool:
        return _ida_hexrays_ctree.ccases_t___gt__(self, r)

    def __le__(self, r: 'ccases_t') ->bool:
        return _ida_hexrays_ctree.ccases_t___le__(self, r)

    def __ge__(self, r: 'ccases_t') ->bool:
        return _ida_hexrays_ctree.ccases_t___ge__(self, r)

    def compare(self, r: 'ccases_t') ->int:
        return _ida_hexrays_ctree.ccases_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.ccases_t_swiginit(self, _ida_hexrays_ctree.
            new_ccases_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_ccases_t


_ida_hexrays_ctree.ccases_t_swigregister(ccases_t)


class cswitch_t(ceinsn_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    mvnf: 'cnumber_t' = property(_ida_hexrays_ctree.cswitch_t_mvnf_get,
        _ida_hexrays_ctree.cswitch_t_mvnf_set)
    """Maximal switch value and number format.
"""
    cases: 'ccases_t' = property(_ida_hexrays_ctree.cswitch_t_cases_get,
        _ida_hexrays_ctree.cswitch_t_cases_set)
    """Switch cases: values and instructions.
"""

    def __eq__(self, r: 'cswitch_t') ->bool:
        return _ida_hexrays_ctree.cswitch_t___eq__(self, r)

    def __ne__(self, r: 'cswitch_t') ->bool:
        return _ida_hexrays_ctree.cswitch_t___ne__(self, r)

    def __lt__(self, r: 'cswitch_t') ->bool:
        return _ida_hexrays_ctree.cswitch_t___lt__(self, r)

    def __gt__(self, r: 'cswitch_t') ->bool:
        return _ida_hexrays_ctree.cswitch_t___gt__(self, r)

    def __le__(self, r: 'cswitch_t') ->bool:
        return _ida_hexrays_ctree.cswitch_t___le__(self, r)

    def __ge__(self, r: 'cswitch_t') ->bool:
        return _ida_hexrays_ctree.cswitch_t___ge__(self, r)

    def compare(self, r: 'cswitch_t') ->int:
        return _ida_hexrays_ctree.cswitch_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.cswitch_t_swiginit(self, _ida_hexrays_ctree.
            new_cswitch_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cswitch_t


_ida_hexrays_ctree.cswitch_t_swigregister(cswitch_t)


class catchexpr_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    obj: 'cexpr_t' = property(_ida_hexrays_ctree.catchexpr_t_obj_get,
        _ida_hexrays_ctree.catchexpr_t_obj_set)
    """the caught object. if obj.op==cot_empty, no object. ideally, obj.op==cot_var 
        """
    fake_type: str = property(_ida_hexrays_ctree.catchexpr_t_fake_type_get,
        _ida_hexrays_ctree.catchexpr_t_fake_type_set)
    """if not empty, type of the caught object. ideally, obj.type should be enough. however, in some cases the detailed type info is not available. 
        """

    def __eq__(self, r: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.catchexpr_t___eq__(self, r)

    def __ne__(self, r: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.catchexpr_t___ne__(self, r)

    def __lt__(self, r: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.catchexpr_t___lt__(self, r)

    def __gt__(self, r: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.catchexpr_t___gt__(self, r)

    def __le__(self, r: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.catchexpr_t___le__(self, r)

    def __ge__(self, r: 'catchexpr_t') ->bool:
        return _ida_hexrays_ctree.catchexpr_t___ge__(self, r)

    def compare(self, r: 'catchexpr_t') ->int:
        return _ida_hexrays_ctree.catchexpr_t_compare(self, r)

    def swap(self, r: 'catchexpr_t') ->None:
        return _ida_hexrays_ctree.catchexpr_t_swap(self, r)

    def is_catch_all(self) ->bool:
        return _ida_hexrays_ctree.catchexpr_t_is_catch_all(self)

    def __init__(self):
        _ida_hexrays_ctree.catchexpr_t_swiginit(self, _ida_hexrays_ctree.
            new_catchexpr_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_catchexpr_t


_ida_hexrays_ctree.catchexpr_t_swigregister(catchexpr_t)


class ccatch_t(cblock_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined')
    __repr__ = _swig_repr
    exprs: 'catchexprs_t' = property(_ida_hexrays_ctree.ccatch_t_exprs_get,
        _ida_hexrays_ctree.ccatch_t_exprs_set)

    def __eq__(self, r: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.ccatch_t___eq__(self, r)

    def __ne__(self, r: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.ccatch_t___ne__(self, r)

    def __lt__(self, r: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.ccatch_t___lt__(self, r)

    def __gt__(self, r: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.ccatch_t___gt__(self, r)

    def __le__(self, r: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.ccatch_t___le__(self, r)

    def __ge__(self, r: 'ccatch_t') ->bool:
        return _ida_hexrays_ctree.ccatch_t___ge__(self, r)

    def compare(self, r: 'ccatch_t') ->int:
        return _ida_hexrays_ctree.ccatch_t_compare(self, r)

    def is_catch_all(self) ->bool:
        return _ida_hexrays_ctree.ccatch_t_is_catch_all(self)

    def swap(self, r: 'ccatch_t') ->None:
        return _ida_hexrays_ctree.ccatch_t_swap(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_ccatch_t


_ida_hexrays_ctree.ccatch_t_swigregister(ccatch_t)


class ctry_t(cblock_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined')
    __repr__ = _swig_repr
    catchs: 'ccatchvec_t' = property(_ida_hexrays_ctree.ctry_t_catchs_get,
        _ida_hexrays_ctree.ctry_t_catchs_set)
    """"catch all", if present, must be the last element. wind-statements must have "catch all" and nothing else. 
        """
    old_state: int = property(_ida_hexrays_ctree.ctry_t_old_state_get,
        _ida_hexrays_ctree.ctry_t_old_state_set)
    """old state number (internal, MSVC related)
"""
    new_state: int = property(_ida_hexrays_ctree.ctry_t_new_state_get,
        _ida_hexrays_ctree.ctry_t_new_state_set)
    """new state number (internal, MSVC related)
"""
    is_wind: bool = property(_ida_hexrays_ctree.ctry_t_is_wind_get,
        _ida_hexrays_ctree.ctry_t_is_wind_set)
    """Is C++ wind statement? (not part of the C++ language) MSVC generates code like the following to keep track of constructed objects and destroy them upon an exception. Example:
// an object is constructed at this point __wind { // some other code that may throw an exception } __unwind { // this code is executed only if there was an exception // in the __wind block. normally here we destroy the object // after that the exception is passed to the // exception handler, regular control flow is interrupted here. } // regular logic continues here, if there were no exceptions // also the object's destructor is called 
        """

    def __eq__(self, r: 'ctry_t') ->bool:
        return _ida_hexrays_ctree.ctry_t___eq__(self, r)

    def __ne__(self, r: 'ctry_t') ->bool:
        return _ida_hexrays_ctree.ctry_t___ne__(self, r)

    def __lt__(self, r: 'ctry_t') ->bool:
        return _ida_hexrays_ctree.ctry_t___lt__(self, r)

    def __gt__(self, r: 'ctry_t') ->bool:
        return _ida_hexrays_ctree.ctry_t___gt__(self, r)

    def __le__(self, r: 'ctry_t') ->bool:
        return _ida_hexrays_ctree.ctry_t___le__(self, r)

    def __ge__(self, r: 'ctry_t') ->bool:
        return _ida_hexrays_ctree.ctry_t___ge__(self, r)

    def compare(self, r: 'ctry_t') ->int:
        return _ida_hexrays_ctree.ctry_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_ctree.delete_ctry_t


_ida_hexrays_ctree.ctry_t_swigregister(ctry_t)


class cthrow_t(ceinsn_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __eq__(self, r: 'cthrow_t') ->bool:
        return _ida_hexrays_ctree.cthrow_t___eq__(self, r)

    def __ne__(self, r: 'cthrow_t') ->bool:
        return _ida_hexrays_ctree.cthrow_t___ne__(self, r)

    def __lt__(self, r: 'cthrow_t') ->bool:
        return _ida_hexrays_ctree.cthrow_t___lt__(self, r)

    def __gt__(self, r: 'cthrow_t') ->bool:
        return _ida_hexrays_ctree.cthrow_t___gt__(self, r)

    def __le__(self, r: 'cthrow_t') ->bool:
        return _ida_hexrays_ctree.cthrow_t___le__(self, r)

    def __ge__(self, r: 'cthrow_t') ->bool:
        return _ida_hexrays_ctree.cthrow_t___ge__(self, r)

    def compare(self, r: 'cthrow_t') ->int:
        return _ida_hexrays_ctree.cthrow_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_ctree.cthrow_t_swiginit(self, _ida_hexrays_ctree.
            new_cthrow_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cthrow_t


_ida_hexrays_ctree.cthrow_t_swigregister(cthrow_t)


class cblock_pos_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    blk: 'cblock_t *' = property(_ida_hexrays_ctree.cblock_pos_t_blk_get,
        _ida_hexrays_ctree.cblock_pos_t_blk_set)
    p: 'cblock_t::iterator' = property(_ida_hexrays_ctree.
        cblock_pos_t_p_get, _ida_hexrays_ctree.cblock_pos_t_p_set)

    def is_first_insn(self) ->bool:
        return _ida_hexrays_ctree.cblock_pos_t_is_first_insn(self)

    def insn(self) ->'cinsn_t *':
        return _ida_hexrays_ctree.cblock_pos_t_insn(self)

    def prev_insn(self) ->'cinsn_t *':
        return _ida_hexrays_ctree.cblock_pos_t_prev_insn(self)

    def __init__(self):
        _ida_hexrays_ctree.cblock_pos_t_swiginit(self, _ida_hexrays_ctree.
            new_cblock_pos_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_cblock_pos_t


_ida_hexrays_ctree.cblock_pos_t_swigregister(cblock_pos_t)


class ctree_visitor_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    cv_flags: int = property(_ida_hexrays_ctree.
        ctree_visitor_t_cv_flags_get, _ida_hexrays_ctree.
        ctree_visitor_t_cv_flags_set)
    """Ctree visitor property bits 
        """

    def maintain_parents(self) ->bool:
        """Should the parent information by maintained?
"""
        return _ida_hexrays_ctree.ctree_visitor_t_maintain_parents(self)

    def must_prune(self) ->bool:
        """Should the traversal skip the children of the current item?
"""
        return _ida_hexrays_ctree.ctree_visitor_t_must_prune(self)

    def must_restart(self) ->bool:
        """Should the traversal restart?
"""
        return _ida_hexrays_ctree.ctree_visitor_t_must_restart(self)

    def is_postorder(self) ->bool:
        """Should the leave...() functions be called?
"""
        return _ida_hexrays_ctree.ctree_visitor_t_is_postorder(self)

    def only_insns(self) ->bool:
        """Should all expressions be automatically pruned?
"""
        return _ida_hexrays_ctree.ctree_visitor_t_only_insns(self)

    def prune_now(self) ->None:
        """Prune children. This function may be called by a visitor() to skip all children of the current item. 
        """
        return _ida_hexrays_ctree.ctree_visitor_t_prune_now(self)

    def clr_prune(self) ->None:
        """Do not prune children. This is an internal function, no need to call it.
"""
        return _ida_hexrays_ctree.ctree_visitor_t_clr_prune(self)

    def set_restart(self) ->None:
        """Restart the travesal. Meaningful only in apply_to_exprs()
"""
        return _ida_hexrays_ctree.ctree_visitor_t_set_restart(self)

    def clr_restart(self) ->None:
        """Do not restart. This is an internal function, no need to call it.
"""
        return _ida_hexrays_ctree.ctree_visitor_t_clr_restart(self)
    parents: 'parents_t' = property(_ida_hexrays_ctree.
        ctree_visitor_t_parents_get, _ida_hexrays_ctree.
        ctree_visitor_t_parents_set)
    """Vector of parents of the current item.
"""
    bposvec: 'cblock_posvec_t' = property(_ida_hexrays_ctree.
        ctree_visitor_t_bposvec_get, _ida_hexrays_ctree.
        ctree_visitor_t_bposvec_set)
    """Vector of block positions. Only cit_block and cit_try parents have the corresponding element in this vector. 
        """

    def __init__(self, _flags: int):
        if self.__class__ == ctree_visitor_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_ctree.ctree_visitor_t_swiginit(self,
            _ida_hexrays_ctree.new_ctree_visitor_t(_self, _flags))
    __swig_destroy__ = _ida_hexrays_ctree.delete_ctree_visitor_t

    def apply_to(self, item: 'citem_t', parent: 'citem_t') ->int:
        """Traverse ctree. The traversal will start at the specified item and continue until of one the visit_...() functions return a non-zero value. 
        
:param item: root of the ctree to traverse
:param parent: parent of the specified item. can be specified as nullptr.
:returns: 0 or a non-zero value returned by a visit_...() function"""
        return _ida_hexrays_ctree.ctree_visitor_t_apply_to(self, item, parent)

    def apply_to_exprs(self, item: 'citem_t', parent: 'citem_t') ->int:
        """Traverse only expressions. The traversal will start at the specified item and continue until of one the visit_...() functions return a non-zero value. 
        
:param item: root of the ctree to traverse
:param parent: parent of the specified item. can be specified as nullptr.
:returns: 0 or a non-zero value returned by a visit_...() function"""
        return _ida_hexrays_ctree.ctree_visitor_t_apply_to_exprs(self, item,
            parent)

    def parent_item(self) ->'citem_t *':
        """Get parent of the current item as an item (statement or expression)
"""
        return _ida_hexrays_ctree.ctree_visitor_t_parent_item(self)

    def parent_expr(self) ->'cexpr_t *':
        """Get parent of the current item as an expression.
"""
        return _ida_hexrays_ctree.ctree_visitor_t_parent_expr(self)

    def parent_insn(self) ->'cinsn_t *':
        """Get parent of the current item as a statement.
"""
        return _ida_hexrays_ctree.ctree_visitor_t_parent_insn(self)

    def visit_insn(self, arg0: 'cinsn_t') ->int:
        """Visit a statement. This is a visitor function which should be overridden by a derived class to do some useful work. This visitor performs pre-order traserval, i.e. an item is visited before its children. 
        
:returns: 0 to continue the traversal, nonzero to stop."""
        return _ida_hexrays_ctree.ctree_visitor_t_visit_insn(self, arg0)

    def visit_expr(self, arg0: 'cexpr_t') ->int:
        """Visit an expression. This is a visitor function which should be overridden by a derived class to do some useful work. This visitor performs pre-order traserval, i.e. an item is visited before its children. 
        
:returns: 0 to continue the traversal, nonzero to stop."""
        return _ida_hexrays_ctree.ctree_visitor_t_visit_expr(self, arg0)

    def leave_insn(self, arg0: 'cinsn_t') ->int:
        """Visit a statement after having visited its children. This is a visitor function which should be overridden by a derived class to do some useful work. This visitor performs post-order traserval, i.e. an item is visited after its children. 
        
:returns: 0 to continue the traversal, nonzero to stop."""
        return _ida_hexrays_ctree.ctree_visitor_t_leave_insn(self, arg0)

    def leave_expr(self, arg0: 'cexpr_t') ->int:
        """Visit an expression after having visited its children. This is a visitor function which should be overridden by a derived class to do some useful work. This visitor performs post-order traserval, i.e. an item is visited after its children. 
        
:returns: 0 to continue the traversal, nonzero to stop."""
        return _ida_hexrays_ctree.ctree_visitor_t_leave_expr(self, arg0)

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_ctree.disown_ctree_visitor_t(self)
        return weakref.proxy(self)


_ida_hexrays_ctree.ctree_visitor_t_swigregister(ctree_visitor_t)
CV_FAST = _ida_hexrays_ctree.CV_FAST
"""do not maintain parent information
"""
CV_PRUNE = _ida_hexrays_ctree.CV_PRUNE
"""this bit is set by visit...() to prune the walk
"""
CV_PARENTS = _ida_hexrays_ctree.CV_PARENTS
"""maintain parent information
"""
CV_POST = _ida_hexrays_ctree.CV_POST
"""call the leave...() functions
"""
CV_RESTART = _ida_hexrays_ctree.CV_RESTART
"""restart enumeration at the top expr (apply_to_exprs)
"""
CV_INSNS = _ida_hexrays_ctree.CV_INSNS
"""visit only statements, prune all expressions do not use before the final ctree maturity because expressions may contain statements at intermediate stages (see cot_insn). Otherwise you risk missing statements embedded into expressions. 
        """


class ctree_parentee_t(ctree_visitor_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, post: bool=False):
        if self.__class__ == ctree_parentee_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_ctree.ctree_parentee_t_swiginit(self,
            _ida_hexrays_ctree.new_ctree_parentee_t(_self, post))

    def recalc_parent_types(self) ->bool:
        """Recalculate type of parent nodes. If a node type has been changed, the visitor must recalculate all parent types, otherwise the ctree becomes inconsistent. If during this recalculation a parent node is added/deleted, this function returns true. In this case the traversal must be stopped because the information about parent nodes is stale. 
        
:returns: false-ok to continue the traversal, true-must stop."""
        return _ida_hexrays_ctree.ctree_parentee_t_recalc_parent_types(self)
    __swig_destroy__ = _ida_hexrays_ctree.delete_ctree_parentee_t

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_ctree.disown_ctree_parentee_t(self)
        return weakref.proxy(self)


_ida_hexrays_ctree.ctree_parentee_t_swigregister(ctree_parentee_t)


class cfunc_parentee_t(ctree_parentee_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    func: 'cfunc_t *' = property(_ida_hexrays_ctree.
        cfunc_parentee_t_func_get, _ida_hexrays_ctree.cfunc_parentee_t_func_set
        )
    """Pointer to current function.
"""

    def __init__(self, f: 'cfunc_t', post: bool=False):
        if self.__class__ == cfunc_parentee_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_ctree.cfunc_parentee_t_swiginit(self,
            _ida_hexrays_ctree.new_cfunc_parentee_t(_self, f, post))

    def calc_rvalue_type(self, target: 'tinfo_t', e: 'cexpr_t') ->bool:
        """Calculate rvalue type. This function tries to determine the type of the specified item based on its context. For example, if the current expression is the right side of an assignment operator, the type of its left side will be returned. This function can be used to determine the 'best' type of the specified expression. 
        
:param target: 'best' type of the expression will be returned here
:param e: expression to determine the desired type
:returns: false if failed"""
        return _ida_hexrays_ctree.cfunc_parentee_t_calc_rvalue_type(self,
            target, e)
    __swig_destroy__ = _ida_hexrays_ctree.delete_cfunc_parentee_t

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_ctree.disown_cfunc_parentee_t(self)
        return weakref.proxy(self)


_ida_hexrays_ctree.cfunc_parentee_t_swigregister(cfunc_parentee_t)


class ctree_anchor_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    value: int = property(_ida_hexrays_ctree.ctree_anchor_t_value_get,
        _ida_hexrays_ctree.ctree_anchor_t_value_set)

    def get_index(self) ->int:
        return _ida_hexrays_ctree.ctree_anchor_t_get_index(self)

    def get_itp(self) ->'item_preciser_t':
        return _ida_hexrays_ctree.ctree_anchor_t_get_itp(self)

    def is_valid_anchor(self) ->bool:
        return _ida_hexrays_ctree.ctree_anchor_t_is_valid_anchor(self)

    def is_citem_anchor(self) ->bool:
        return _ida_hexrays_ctree.ctree_anchor_t_is_citem_anchor(self)

    def is_lvar_anchor(self) ->bool:
        return _ida_hexrays_ctree.ctree_anchor_t_is_lvar_anchor(self)

    def is_itp_anchor(self) ->bool:
        return _ida_hexrays_ctree.ctree_anchor_t_is_itp_anchor(self)

    def is_blkcmt_anchor(self) ->bool:
        return _ida_hexrays_ctree.ctree_anchor_t_is_blkcmt_anchor(self)

    def __init__(self):
        _ida_hexrays_ctree.ctree_anchor_t_swiginit(self, _ida_hexrays_ctree
            .new_ctree_anchor_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_ctree_anchor_t


_ida_hexrays_ctree.ctree_anchor_t_swigregister(ctree_anchor_t)
ANCHOR_INDEX = _ida_hexrays_ctree.ANCHOR_INDEX
ANCHOR_MASK = _ida_hexrays_ctree.ANCHOR_MASK
ANCHOR_CITEM = _ida_hexrays_ctree.ANCHOR_CITEM
"""c-tree item
"""
ANCHOR_LVAR = _ida_hexrays_ctree.ANCHOR_LVAR
"""declaration of local variable
"""
ANCHOR_ITP = _ida_hexrays_ctree.ANCHOR_ITP
"""item type preciser
"""
ANCHOR_BLKCMT = _ida_hexrays_ctree.ANCHOR_BLKCMT
"""block comment (for ctree items)
"""
VDI_NONE = _ida_hexrays_ctree.VDI_NONE
"""undefined
"""
VDI_EXPR = _ida_hexrays_ctree.VDI_EXPR
"""c-tree item
"""
VDI_LVAR = _ida_hexrays_ctree.VDI_LVAR
"""declaration of local variable
"""
VDI_FUNC = _ida_hexrays_ctree.VDI_FUNC
"""the function itself (the very first line with the function prototype)
"""
VDI_TAIL = _ida_hexrays_ctree.VDI_TAIL
"""cursor is at (beyond) the line end (commentable line)
"""


class ctree_item_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    citype: 'cursor_item_type_t' = property(_ida_hexrays_ctree.
        ctree_item_t_citype_get, _ida_hexrays_ctree.ctree_item_t_citype_set)
    """Item type.
"""
    it: 'citem_t *' = property(_ida_hexrays_ctree.ctree_item_t_it_get,
        _ida_hexrays_ctree.ctree_item_t_it_set)
    e: 'cexpr_t *' = property(_ida_hexrays_ctree.ctree_item_t_e_get,
        _ida_hexrays_ctree.ctree_item_t_e_set)
    """VDI_EXPR: Expression.
"""
    i: 'cinsn_t *' = property(_ida_hexrays_ctree.ctree_item_t_i_get,
        _ida_hexrays_ctree.ctree_item_t_i_set)
    """VDI_EXPR: Statement.
"""
    l: 'lvar_t *' = property(_ida_hexrays_ctree.ctree_item_t_l_get,
        _ida_hexrays_ctree.ctree_item_t_l_set)
    """VDI_LVAR: Local variable.
"""
    f: 'cfunc_t *' = property(_ida_hexrays_ctree.ctree_item_t_f_get,
        _ida_hexrays_ctree.ctree_item_t_f_set)
    """VDI_FUNC: Function.
"""

    def get_udm(self, udm: 'udm_t'=None, parent: 'tinfo_t'=None, p_offset:
        'uint64 *'=None) ->int:
        """Get type of a structure field. If the current item is a structure/union field, this function will return information about it. 
        
:param udm: pointer to buffer for the udt member info.
:param parent: pointer to buffer for the struct/union type.
:param p_offset: pointer to the offset in bits inside udt.
:returns: member index or -1 if failed Both output parameters can be nullptr."""
        return _ida_hexrays_ctree.ctree_item_t_get_udm(self, udm, parent,
            p_offset)

    def get_edm(self, parent: 'tinfo_t') ->int:
        """Get type of an enum member. If the current item is a symbolic constant, this function will return information about it. 
        
:param parent: pointer to buffer for the enum type.
:returns: member index or -1 if failed"""
        return _ida_hexrays_ctree.ctree_item_t_get_edm(self, parent)

    def get_lvar(self) ->'lvar_t *':
        """Get pointer to local variable. If the current item is a local variable, this function will return pointer to its definition. 
        
:returns: nullptr if failed"""
        return _ida_hexrays_ctree.ctree_item_t_get_lvar(self)

    def get_ea(self) ->ida_idaapi.ea_t:
        """Get address of the current item. Each ctree item has an address. 
        
:returns: BADADDR if failed"""
        return _ida_hexrays_ctree.ctree_item_t_get_ea(self)

    def get_label_num(self, gln_flags: int) ->int:
        """Get label number of the current item. 
        
:param gln_flags: Combination of get_label_num control bits
:returns: -1 if failed or no label"""
        return _ida_hexrays_ctree.ctree_item_t_get_label_num(self, gln_flags)

    def is_citem(self) ->bool:
        """Is the current item is a ctree item?
"""
        return _ida_hexrays_ctree.ctree_item_t_is_citem(self)

    def _print(self) ->None:
        return _ida_hexrays_ctree.ctree_item_t__print(self)

    def dstr(self) ->str:
        return _ida_hexrays_ctree.ctree_item_t_dstr(self)

    def _get_it(self) ->'citem_t *':
        return _ida_hexrays_ctree.ctree_item_t__get_it(self)
    it = property(lambda self: self._get_it())

    def _get_e(self) ->'cexpr_t *':
        return _ida_hexrays_ctree.ctree_item_t__get_e(self)
    e = property(lambda self: self._get_e())
    """VDI_EXPR: Expression.
"""

    def _get_i(self) ->'cinsn_t *':
        return _ida_hexrays_ctree.ctree_item_t__get_i(self)
    i = property(lambda self: self._get_i())
    """VDI_EXPR: Statement.
"""

    def _get_l(self) ->'lvar_t *':
        return _ida_hexrays_ctree.ctree_item_t__get_l(self)
    l = property(lambda self: self._get_l())
    """VDI_LVAR: Local variable.
"""

    def _get_f(self) ->'cfunc_t *':
        return _ida_hexrays_ctree.ctree_item_t__get_f(self)
    f = property(lambda self: self._get_f())
    """VDI_FUNC: Function.
"""
    loc: 'treeloc_t *const' = property(_ida_hexrays_ctree.ctree_item_t_loc_get)
    """VDI_TAIL: Line tail.
"""

    def __init__(self):
        _ida_hexrays_ctree.ctree_item_t_swiginit(self, _ida_hexrays_ctree.
            new_ctree_item_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_ctree_item_t


_ida_hexrays_ctree.ctree_item_t_swigregister(ctree_item_t)
GLN_CURRENT = _ida_hexrays_ctree.GLN_CURRENT
"""get label of the current item
"""
GLN_GOTO_TARGET = _ida_hexrays_ctree.GLN_GOTO_TARGET
"""get goto target
"""
GLN_ALL = _ida_hexrays_ctree.GLN_ALL
"""get both
"""
FORBID_UNUSED_LABELS = _ida_hexrays_ctree.FORBID_UNUSED_LABELS
"""Unused labels cause interr.
"""
ALLOW_UNUSED_LABELS = _ida_hexrays_ctree.ALLOW_UNUSED_LABELS
"""Unused labels are permitted.
"""


def _ll_lnot(e: 'cexpr_t') ->'cexpr_t *':
    return _ida_hexrays_ctree._ll_lnot(e)


def _ll_new_block() ->'cinsn_t *':
    return _ida_hexrays_ctree._ll_new_block()


def _ll_create_helper(*args) ->'cexpr_t *':
    return _ida_hexrays_ctree._ll_create_helper(*args)


def _ll_call_helper(*args) ->'cexpr_t *':
    return _ida_hexrays_ctree._ll_call_helper(*args)


def _ll_make_num(*args) ->'cexpr_t *':
    return _ida_hexrays_ctree._ll_make_num(*args)


def _ll_make_ref(e: 'cexpr_t') ->'cexpr_t *':
    return _ida_hexrays_ctree._ll_make_ref(e)


def _ll_dereference(e: 'cexpr_t', ptrsize: int, is_flt: bool=False
    ) ->'cexpr_t *':
    return _ida_hexrays_ctree._ll_dereference(e, ptrsize, is_flt)


def save_user_labels(func_ea: ida_idaapi.ea_t, user_labels: 'user_labels_t',
    func: 'cfunc_t'=None) ->None:
    """Save user defined labels into the database. 
        
:param func_ea: the entry address of the function, ignored if FUNC != nullptr
:param user_labels: collection of user defined labels
:param func: pointer to current function, if FUNC != nullptr, then save labels using a more stable method that preserves them even when the decompiler output drastically changes"""
    return _ida_hexrays_ctree.save_user_labels(func_ea, user_labels, func)


def save_user_cmts(func_ea: ida_idaapi.ea_t, user_cmts: 'user_cmts_t') ->None:
    """Save user defined comments into the database. 
        
:param func_ea: the entry address of the function
:param user_cmts: collection of user defined comments"""
    return _ida_hexrays_ctree.save_user_cmts(func_ea, user_cmts)


def save_user_numforms(func_ea: ida_idaapi.ea_t, numforms: 'user_numforms_t'
    ) ->None:
    """Save user defined number formats into the database. 
        
:param func_ea: the entry address of the function
:param numforms: collection of user defined comments"""
    return _ida_hexrays_ctree.save_user_numforms(func_ea, numforms)


def save_user_iflags(func_ea: ida_idaapi.ea_t, iflags: 'user_iflags_t') ->None:
    """Save user defined citem iflags into the database. 
        
:param func_ea: the entry address of the function
:param iflags: collection of user defined citem iflags"""
    return _ida_hexrays_ctree.save_user_iflags(func_ea, iflags)


def save_user_unions(func_ea: ida_idaapi.ea_t, unions: 'user_unions_t') ->None:
    """Save user defined union field selections into the database. 
        
:param func_ea: the entry address of the function
:param unions: collection of union field selections"""
    return _ida_hexrays_ctree.save_user_unions(func_ea, unions)


def restore_user_labels(func_ea: ida_idaapi.ea_t, func: 'cfunc_t'=None
    ) ->'user_labels_t *':
    """Restore user defined labels from the database. 
        
:param func_ea: the entry address of the function, ignored if FUNC != nullptr
:param func: pointer to current function
:returns: collection of user defined labels. The returned object must be deleted by the caller using delete_user_labels()"""
    return _ida_hexrays_ctree.restore_user_labels(func_ea, func)


def restore_user_cmts(func_ea: ida_idaapi.ea_t) ->'user_cmts_t *':
    """Restore user defined comments from the database. 
        
:param func_ea: the entry address of the function
:returns: collection of user defined comments. The returned object must be deleted by the caller using delete_user_cmts()"""
    return _ida_hexrays_ctree.restore_user_cmts(func_ea)


def restore_user_numforms(func_ea: ida_idaapi.ea_t) ->'user_numforms_t *':
    """Restore user defined number formats from the database. 
        
:param func_ea: the entry address of the function
:returns: collection of user defined number formats. The returned object must be deleted by the caller using delete_user_numforms()"""
    return _ida_hexrays_ctree.restore_user_numforms(func_ea)


def restore_user_iflags(func_ea: ida_idaapi.ea_t) ->'user_iflags_t *':
    """Restore user defined citem iflags from the database. 
        
:param func_ea: the entry address of the function
:returns: collection of user defined iflags. The returned object must be deleted by the caller using delete_user_iflags()"""
    return _ida_hexrays_ctree.restore_user_iflags(func_ea)


def restore_user_unions(func_ea: ida_idaapi.ea_t) ->'user_unions_t *':
    """Restore user defined union field selections from the database. 
        
:param func_ea: the entry address of the function
:returns: collection of union field selections The returned object must be deleted by the caller using delete_user_unions()"""
    return _ida_hexrays_ctree.restore_user_unions(func_ea)


class cfunc_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined')
    __repr__ = _swig_repr
    entry_ea: ida_idaapi.ea_t = property(_ida_hexrays_ctree.
        cfunc_t_entry_ea_get, _ida_hexrays_ctree.cfunc_t_entry_ea_set)
    """function entry address
"""
    mba: 'mba_t *' = property(_ida_hexrays_ctree.cfunc_t_mba_get,
        _ida_hexrays_ctree.cfunc_t_mba_set)
    """underlying microcode
"""
    body: 'cinsn_t' = property(_ida_hexrays_ctree.cfunc_t_body_get,
        _ida_hexrays_ctree.cfunc_t_body_set)
    """function body, must be a block
"""
    argidx: 'intvec_t &' = property(_ida_hexrays_ctree.cfunc_t_argidx_get)
    """list of arguments (indexes into vars)
"""
    maturity: 'ctree_maturity_t' = property(_ida_hexrays_ctree.
        cfunc_t_maturity_get, _ida_hexrays_ctree.cfunc_t_maturity_set)
    """maturity level
"""
    user_labels: 'user_labels_t *' = property(_ida_hexrays_ctree.
        cfunc_t_user_labels_get, _ida_hexrays_ctree.cfunc_t_user_labels_set)
    """user-defined labels.
"""
    user_cmts: 'user_cmts_t *' = property(_ida_hexrays_ctree.
        cfunc_t_user_cmts_get, _ida_hexrays_ctree.cfunc_t_user_cmts_set)
    """user-defined comments.
"""
    numforms: 'user_numforms_t *' = property(_ida_hexrays_ctree.
        cfunc_t_numforms_get, _ida_hexrays_ctree.cfunc_t_numforms_set)
    """user-defined number formats.
"""
    user_iflags: 'user_iflags_t *' = property(_ida_hexrays_ctree.
        cfunc_t_user_iflags_get, _ida_hexrays_ctree.cfunc_t_user_iflags_set)
    """user-defined item flags ctree item iflags bits
"""
    user_unions: 'user_unions_t *' = property(_ida_hexrays_ctree.
        cfunc_t_user_unions_get, _ida_hexrays_ctree.cfunc_t_user_unions_set)
    """user-defined union field selections. 
        """
    refcnt: int = property(_ida_hexrays_ctree.cfunc_t_refcnt_get,
        _ida_hexrays_ctree.cfunc_t_refcnt_set)
    """reference count to this object. use cfuncptr_t
"""
    statebits: int = property(_ida_hexrays_ctree.cfunc_t_statebits_get,
        _ida_hexrays_ctree.cfunc_t_statebits_set)
    """current cfunc_t state. see cfunc state bits 
        """
    hdrlines: int = property(_ida_hexrays_ctree.cfunc_t_hdrlines_get,
        _ida_hexrays_ctree.cfunc_t_hdrlines_set)
    """number of lines in the declaration area
"""
    treeitems: 'citem_pointers_t' = property(_ida_hexrays_ctree.
        cfunc_t_treeitems_get, _ida_hexrays_ctree.cfunc_t_treeitems_set)
    """vector of pointers to citem_t objects (nodes constituting the ctree)
"""
    __swig_destroy__ = _ida_hexrays_ctree.delete_cfunc_t

    def release(self) ->None:
        return _ida_hexrays_ctree.cfunc_t_release(self)

    def build_c_tree(self) ->None:
        """Generate the function body. This function (re)generates the function body from the underlying microcode. 
        """
        return _ida_hexrays_ctree.cfunc_t_build_c_tree(self)

    def verify(self, aul: 'allow_unused_labels_t', even_without_debugger: bool
        ) ->None:
        """Verify the ctree. This function verifies the ctree. If the ctree is malformed, an internal error is generated. Use it to verify the ctree after your modifications. 
        
:param aul: Are unused labels acceptable?
:param even_without_debugger: if false and there is no debugger, the verification will be skipped"""
        return _ida_hexrays_ctree.cfunc_t_verify(self, aul,
            even_without_debugger)

    def print_dcl(self) ->None:
        """Print function prototype. 
        """
        return _ida_hexrays_ctree.cfunc_t_print_dcl(self)

    def print_func(self, vp: 'vc_printer_t') ->None:
        """Print function text. 
        
:param vp: printer helper class to receive the generated text."""
        return _ida_hexrays_ctree.cfunc_t_print_func(self, vp)

    def get_func_type(self, type: 'tinfo_t') ->bool:
        """Get the function type. 
        
:param type: variable where the function type is returned
:returns: false if failure"""
        return _ida_hexrays_ctree.cfunc_t_get_func_type(self, type)

    def get_lvars(self) ->'lvars_t *':
        """Get vector of local variables. 
        
:returns: pointer to the vector of local variables. If you modify this vector, the ctree must be regenerated in order to have correct cast operators. Use build_c_tree() for that. Removing lvars should be done carefully: all references in ctree and microcode must be corrected after that."""
        return _ida_hexrays_ctree.cfunc_t_get_lvars(self)

    def get_stkoff_delta(self) ->int:
        """Get stack offset delta. The local variable stack offsets retrieved by v.location.stkoff() should be adjusted before being used as stack frame offsets in IDA. 
        
:returns: the delta to apply. example: ida_stkoff = v.location.stkoff() - f->get_stkoff_delta()"""
        return _ida_hexrays_ctree.cfunc_t_get_stkoff_delta(self)

    def find_label(self, label: int) ->'citem_t *':
        """Find the label. 
        
:returns: pointer to the ctree item with the specified label number."""
        return _ida_hexrays_ctree.cfunc_t_find_label(self, label)

    def remove_unused_labels(self) ->None:
        """Remove unused labels. This function checks what labels are really used by the function and removes the unused ones. You must call it after deleting a goto statement. 
        """
        return _ida_hexrays_ctree.cfunc_t_remove_unused_labels(self)

    def get_user_cmt(self, loc: 'treeloc_t', rt: 'cmt_retrieval_type_t') ->str:
        """Retrieve a user defined comment. 
        
:param loc: ctree location
:param rt: should already retrieved comments retrieved again?
:returns: pointer to the comment string or nullptr"""
        return _ida_hexrays_ctree.cfunc_t_get_user_cmt(self, loc, rt)

    def set_user_cmt(self, loc: 'treeloc_t', cmt: str) ->None:
        """Set a user defined comment. This function stores the specified comment in the cfunc_t structure. The save_user_cmts() function must be called after it. 
        
:param loc: ctree location
:param cmt: new comment. if empty or nullptr, then an existing comment is deleted."""
        return _ida_hexrays_ctree.cfunc_t_set_user_cmt(self, loc, cmt)

    def get_user_iflags(self, loc: 'citem_locator_t') ->int:
        """Retrieve citem iflags. 
        
:param loc: citem locator
:returns: ctree item iflags bits or 0"""
        return _ida_hexrays_ctree.cfunc_t_get_user_iflags(self, loc)

    def set_user_iflags(self, loc: 'citem_locator_t', iflags: int) ->None:
        """Set citem iflags. 
        
:param loc: citem locator
:param iflags: new iflags"""
        return _ida_hexrays_ctree.cfunc_t_set_user_iflags(self, loc, iflags)

    def has_orphan_cmts(self) ->bool:
        """Check if there are orphan comments.
"""
        return _ida_hexrays_ctree.cfunc_t_has_orphan_cmts(self)

    def del_orphan_cmts(self) ->int:
        """Delete all orphan comments. The save_user_cmts() function must be called after this call. 
        """
        return _ida_hexrays_ctree.cfunc_t_del_orphan_cmts(self)

    def get_user_union_selection(self, ea: ida_idaapi.ea_t, path: 'intvec_t'
        ) ->bool:
        """Retrieve a user defined union field selection. 
        
:param ea: address
:param path: out: path describing the union selection.
:returns: pointer to the path or nullptr"""
        return _ida_hexrays_ctree.cfunc_t_get_user_union_selection(self, ea,
            path)

    def set_user_union_selection(self, ea: ida_idaapi.ea_t, path: 'intvec_t'
        ) ->None:
        """Set a union field selection. The save_user_unions() function must be called after calling this function. 
        
:param ea: address
:param path: in: path describing the union selection."""
        return _ida_hexrays_ctree.cfunc_t_set_user_union_selection(self, ea,
            path)

    def save_user_labels(self) ->None:
        """Save user-defined labels into the database.
"""
        return _ida_hexrays_ctree.cfunc_t_save_user_labels(self)

    def save_user_cmts(self) ->None:
        """Save user-defined comments into the database.
"""
        return _ida_hexrays_ctree.cfunc_t_save_user_cmts(self)

    def save_user_numforms(self) ->None:
        """Save user-defined number formats into the database.
"""
        return _ida_hexrays_ctree.cfunc_t_save_user_numforms(self)

    def save_user_iflags(self) ->None:
        """Save user-defined iflags into the database.
"""
        return _ida_hexrays_ctree.cfunc_t_save_user_iflags(self)

    def save_user_unions(self) ->None:
        """Save user-defined union field selections into the database.
"""
        return _ida_hexrays_ctree.cfunc_t_save_user_unions(self)

    def get_line_item(self, line: str, x: int, is_ctree_line: bool, phead:
        'ctree_item_t', pitem: 'ctree_item_t', ptail: 'ctree_item_t') ->bool:
        """Get ctree item for the specified cursor position. 
        
:param line: line of decompilation text (element of sv)
:param x: x cursor coordinate in the line
:param is_ctree_line: does the line belong to statement area? (if not, it is assumed to belong to the declaration area)
:param phead: ptr to the first item on the line (used to attach block comments). May be nullptr
:param pitem: ptr to the current item. May be nullptr
:param ptail: ptr to the last item on the line (used to attach indented comments). May be nullptr
:returns: false if failed to get the current item"""
        return _ida_hexrays_ctree.cfunc_t_get_line_item(self, line, x,
            is_ctree_line, phead, pitem, ptail)

    def get_warnings(self) ->'hexwarns_t &':
        """Get information about decompilation warnings. 
        
:returns: reference to the vector of warnings"""
        return _ida_hexrays_ctree.cfunc_t_get_warnings(self)

    def get_eamap(self) ->'eamap_t &':
        """Get pointer to ea->insn map. This function initializes eamap if not done yet. 
        """
        return _ida_hexrays_ctree.cfunc_t_get_eamap(self)

    def get_boundaries(self) ->'boundaries_t &':
        """Get pointer to map of instruction boundaries. This function initializes the boundary map if not done yet. 
        """
        return _ida_hexrays_ctree.cfunc_t_get_boundaries(self)

    def get_pseudocode(self) ->'strvec_t const &':
        """Get pointer to decompilation output: the pseudocode. This function generates pseudocode if not done yet. 
        """
        return _ida_hexrays_ctree.cfunc_t_get_pseudocode(self)

    def refresh_func_ctext(self) ->None:
        """Refresh ctext after a ctree modification. This function informs the decompiler that ctree (body) have been modified and ctext (sv) does not correspond to it anymore. It also refreshes the pseudocode windows if there is any. 
        """
        return _ida_hexrays_ctree.cfunc_t_refresh_func_ctext(self)

    def recalc_item_addresses(self) ->None:
        """Recalculate item adresses. This function may be required after shuffling ctree items. For example, when adding or removing statements of a block, or changing 'if' statements. 
        """
        return _ida_hexrays_ctree.cfunc_t_recalc_item_addresses(self)

    def gather_derefs(self, ci: 'ctree_item_t', udm: 'udt_type_data_t'=None
        ) ->bool:
        return _ida_hexrays_ctree.cfunc_t_gather_derefs(self, ci, udm)

    def locked(self) ->bool:
        return _ida_hexrays_ctree.cfunc_t_locked(self)

    def serialize(self) ->bool:
        """Serialize cfunc into a sequence of bytes.
"""
        return _ida_hexrays_ctree.cfunc_t_serialize(self)

    @staticmethod
    def deserialize(mba: 'mba_t *', bytes: 'uchar const *') ->'cfunc_t *':
        """Deserialize a byte sequence into cfunc_t 
        
:param mba: the matching mba object
:param bytes: pointer to the beginning of the byte sequence.
:returns: new cfunc_t object"""
        return _ida_hexrays_ctree.cfunc_t_deserialize(mba, bytes)

    def find_item_coords(self, *args):
        """This method has the following signatures:

    1. find_item_coords(item: citem_t) -> Tuple[int, int]
    2. find_item_coords(item: citem_t, x: int_pointer, y: int_pointer) -> bool

NOTE: The second form is retained for backward-compatibility,
but we strongly recommend using the first.

:param item: The item to find coordinates for in the pseudocode listing"""
        return _ida_hexrays_ctree.cfunc_t_find_item_coords(self, *args)

    def __str__(self) ->str:
        return _ida_hexrays_ctree.cfunc_t___str__(self)
    __repr__ = __str__


_ida_hexrays_ctree.cfunc_t_swigregister(cfunc_t)
CIT_COLLAPSED = _ida_hexrays_ctree.CIT_COLLAPSED
"""display ctree item in collapsed form
"""
CFS_BOUNDS = _ida_hexrays_ctree.CFS_BOUNDS
"""'eamap' and 'boundaries' are ready
"""
CFS_TEXT = _ida_hexrays_ctree.CFS_TEXT
"""'sv' is ready (and hdrlines)
"""
CFS_LVARS_HIDDEN = _ida_hexrays_ctree.CFS_LVARS_HIDDEN
"""local variable definitions are collapsed
"""
CFS_LOCKED = _ida_hexrays_ctree.CFS_LOCKED
"""cfunc is temporarily locked
"""


def close_hexrays_waitbox() ->None:
    """Close the waitbox displayed by the decompiler. Useful if DECOMP_NO_HIDE was used during decompilation. 
        """
    return _ida_hexrays_ctree.close_hexrays_waitbox()


def decompile(mbr: 'mba_ranges_t', hf: 'hexrays_failure_t *'=None,
    decomp_flags: int=0) ->'cfuncptr_t':
    """Decompile a snippet or a function. 
        
:param mbr: what to decompile
:param hf: extended error information (if failed)
:param decomp_flags: bitwise combination of decompile() flags... bits
:returns: pointer to the decompilation result (a reference counted pointer). nullptr if failed."""
    return _ida_hexrays_ctree.decompile(mbr, hf, decomp_flags)


def decompile_func(pfn: 'func_t *', hf: 'hexrays_failure_t *'=None,
    decomp_flags: int=0) ->'cfuncptr_t':
    """Decompile a function. Multiple decompilations of the same function return the same object. 
        
:param pfn: pointer to function to decompile
:param hf: extended error information (if failed)
:param decomp_flags: bitwise combination of decompile() flags... bits
:returns: pointer to the decompilation result (a reference counted pointer). nullptr if failed."""
    val = _ida_hexrays_ctree.decompile_func(pfn, hf, decomp_flags)
    if val.__deref__() is None:
        val = None
    return val


def create_cfunc(mba: 'mba_t *') ->'cfuncptr_t':
    """Create a new cfunc_t object. 
        
:param mba: microcode object. After creating the cfunc object it takes the ownership of MBA."""
    return _ida_hexrays_ctree.create_cfunc(mba)


def mark_cfunc_dirty(ea: ida_idaapi.ea_t, close_views: bool=False) ->bool:
    """Flush the cached decompilation results. Erases a cache entry for the specified function. 
        
:param ea: function to erase from the cache
:param close_views: close pseudocode windows that show the function
:returns: if a cache entry existed."""
    return _ida_hexrays_ctree.mark_cfunc_dirty(ea, close_views)


def clear_cached_cfuncs() ->None:
    """Flush all cached decompilation results.
"""
    return _ida_hexrays_ctree.clear_cached_cfuncs()


def has_cached_cfunc(ea: ida_idaapi.ea_t) ->bool:
    """Do we have a cached decompilation result for 'ea'?
"""
    return _ida_hexrays_ctree.has_cached_cfunc(ea)


def get_ctype_name(op: 'ctype_t') ->str:
    return _ida_hexrays_ctree.get_ctype_name(op)


def create_field_name(*args) ->str:
    return _ida_hexrays_ctree.create_field_name(*args)


hxe_flowchart = _ida_hexrays_ctree.hxe_flowchart
"""Flowchart has been generated. 
          """
hxe_stkpnts = _ida_hexrays_ctree.hxe_stkpnts
"""SP change points have been calculated. 
          """
hxe_prolog = _ida_hexrays_ctree.hxe_prolog
"""Prolog analysis has been finished. 
          """
hxe_microcode = _ida_hexrays_ctree.hxe_microcode
"""Microcode has been generated. 
          """
hxe_preoptimized = _ida_hexrays_ctree.hxe_preoptimized
"""Microcode has been preoptimized. 
          """
hxe_locopt = _ida_hexrays_ctree.hxe_locopt
"""Basic block level optimization has been finished. 
          """
hxe_prealloc = _ida_hexrays_ctree.hxe_prealloc
"""Local variables: preallocation step begins. 
          """
hxe_glbopt = _ida_hexrays_ctree.hxe_glbopt
"""Global optimization has been finished. If microcode is modified, MERR_LOOP must be returned. It will cause a complete restart of the optimization. 
          """
hxe_pre_structural = _ida_hexrays_ctree.hxe_pre_structural
"""Structure analysis is starting. 
          """
hxe_structural = _ida_hexrays_ctree.hxe_structural
"""Structural analysis has been finished. 
          """
hxe_maturity = _ida_hexrays_ctree.hxe_maturity
"""Ctree maturity level is being changed. 
          """
hxe_interr = _ida_hexrays_ctree.hxe_interr
"""Internal error has occurred. 
          """
hxe_combine = _ida_hexrays_ctree.hxe_combine
"""Trying to combine instructions of basic block. 
          """
hxe_print_func = _ida_hexrays_ctree.hxe_print_func
"""Printing ctree and generating text. 
          """
hxe_func_printed = _ida_hexrays_ctree.hxe_func_printed
"""Function text has been generated. Plugins may modify the text in cfunc_t::sv. However, it is too late to modify the ctree or microcode. The text uses regular color codes (see lines.hpp) COLOR_ADDR is used to store pointers to ctree items. 
          """
hxe_resolve_stkaddrs = _ida_hexrays_ctree.hxe_resolve_stkaddrs
"""The optimizer is about to resolve stack addresses. 
          """
hxe_build_callinfo = _ida_hexrays_ctree.hxe_build_callinfo
"""Analyzing a call instruction. 
          """
hxe_callinfo_built = _ida_hexrays_ctree.hxe_callinfo_built
"""A call instruction has been anallyzed. 
          """
hxe_calls_done = _ida_hexrays_ctree.hxe_calls_done
"""All calls have been analyzed. 
          """
hxe_begin_inlining = _ida_hexrays_ctree.hxe_begin_inlining
"""Starting to inline outlined functions. 
          """
hxe_inlining_func = _ida_hexrays_ctree.hxe_inlining_func
"""A set of ranges is going to be inlined. 
          """
hxe_inlined_func = _ida_hexrays_ctree.hxe_inlined_func
"""A set of ranges got inlined. 
          """
hxe_collect_warnings = _ida_hexrays_ctree.hxe_collect_warnings
"""Collect warning messages from plugins. These warnings will be displayed at the function header, after the user-defined comments. 
          """
hxe_open_pseudocode = _ida_hexrays_ctree.hxe_open_pseudocode
"""New pseudocode view has been opened. 
          """
hxe_switch_pseudocode = _ida_hexrays_ctree.hxe_switch_pseudocode
"""Existing pseudocode view has been reloaded with a new function. Its text has not been refreshed yet, only cfunc and mba pointers are ready. 
          """
hxe_refresh_pseudocode = _ida_hexrays_ctree.hxe_refresh_pseudocode
"""Existing pseudocode text has been refreshed. Adding/removing pseudocode lines is forbidden in this event. 
          """
hxe_close_pseudocode = _ida_hexrays_ctree.hxe_close_pseudocode
"""Pseudocode view is being closed. 
          """
hxe_keyboard = _ida_hexrays_ctree.hxe_keyboard
"""Keyboard has been hit. 
          """
hxe_right_click = _ida_hexrays_ctree.hxe_right_click
"""Mouse right click. Use hxe_populating_popup instead, in case you want to add items in the popup menu. 
          """
hxe_double_click = _ida_hexrays_ctree.hxe_double_click
"""Mouse double click. 
          """
hxe_curpos = _ida_hexrays_ctree.hxe_curpos
"""Current cursor position has been changed. (for example, by left-clicking or using keyboard)

          """
hxe_create_hint = _ida_hexrays_ctree.hxe_create_hint
"""Create a hint for the current item. 
          """
hxe_text_ready = _ida_hexrays_ctree.hxe_text_ready
"""Decompiled text is ready. 
          """
hxe_populating_popup = _ida_hexrays_ctree.hxe_populating_popup
"""Populating popup menu. We can add menu items now. 
          """
lxe_lvar_name_changed = _ida_hexrays_ctree.lxe_lvar_name_changed
"""Local variable got renamed. 
          """
lxe_lvar_type_changed = _ida_hexrays_ctree.lxe_lvar_type_changed
"""Local variable type got changed. 
          """
lxe_lvar_cmt_changed = _ida_hexrays_ctree.lxe_lvar_cmt_changed
"""Local variable comment got changed. 
          """
lxe_lvar_mapping_changed = _ida_hexrays_ctree.lxe_lvar_mapping_changed
"""Local variable mapping got changed. 
          """
hxe_cmt_changed = _ida_hexrays_ctree.hxe_cmt_changed
"""Comment got changed. 
          """
hxe_mba_maturity = _ida_hexrays_ctree.hxe_mba_maturity
"""Maturity level of an MBA was changed. 
          """
USE_KEYBOARD = _ida_hexrays_ctree.USE_KEYBOARD
"""Keyboard.
"""
USE_MOUSE = _ida_hexrays_ctree.USE_MOUSE
"""Mouse.
"""


class ctext_position_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    lnnum: int = property(_ida_hexrays_ctree.ctext_position_t_lnnum_get,
        _ida_hexrays_ctree.ctext_position_t_lnnum_set)
    """Line number.
"""
    x: int = property(_ida_hexrays_ctree.ctext_position_t_x_get,
        _ida_hexrays_ctree.ctext_position_t_x_set)
    """x coordinate of the cursor within the window
"""
    y: int = property(_ida_hexrays_ctree.ctext_position_t_y_get,
        _ida_hexrays_ctree.ctext_position_t_y_set)
    """y coordinate of the cursor within the window 
        """

    def in_ctree(self, hdrlines: int) ->bool:
        """Is the cursor in the variable/type declaration area? 
        
:param hdrlines: Number of lines of the declaration area"""
        return _ida_hexrays_ctree.ctext_position_t_in_ctree(self, hdrlines)

    def __eq__(self, r: 'ctext_position_t') ->bool:
        return _ida_hexrays_ctree.ctext_position_t___eq__(self, r)

    def __ne__(self, r: 'ctext_position_t') ->bool:
        return _ida_hexrays_ctree.ctext_position_t___ne__(self, r)

    def __lt__(self, r: 'ctext_position_t') ->bool:
        return _ida_hexrays_ctree.ctext_position_t___lt__(self, r)

    def __gt__(self, r: 'ctext_position_t') ->bool:
        return _ida_hexrays_ctree.ctext_position_t___gt__(self, r)

    def __le__(self, r: 'ctext_position_t') ->bool:
        return _ida_hexrays_ctree.ctext_position_t___le__(self, r)

    def __ge__(self, r: 'ctext_position_t') ->bool:
        return _ida_hexrays_ctree.ctext_position_t___ge__(self, r)

    def compare(self, r: 'ctext_position_t') ->int:
        return _ida_hexrays_ctree.ctext_position_t_compare(self, r)

    def __init__(self, _lnnum: int=-1, _x: int=0, _y: int=0):
        _ida_hexrays_ctree.ctext_position_t_swiginit(self,
            _ida_hexrays_ctree.new_ctext_position_t(_lnnum, _x, _y))
    __swig_destroy__ = _ida_hexrays_ctree.delete_ctext_position_t


_ida_hexrays_ctree.ctext_position_t_swigregister(ctext_position_t)
cvar = _ida_hexrays_ctree.cvar
HEXRAYS_API_MAGIC = cvar.HEXRAYS_API_MAGIC


class history_item_t(ctext_position_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    func_ea: ida_idaapi.ea_t = property(_ida_hexrays_ctree.
        history_item_t_func_ea_get, _ida_hexrays_ctree.
        history_item_t_func_ea_set)
    """The entry address of the decompiled function.
"""
    curr_ea: ida_idaapi.ea_t = property(_ida_hexrays_ctree.
        history_item_t_curr_ea_get, _ida_hexrays_ctree.
        history_item_t_curr_ea_set)
    """Current address.
"""
    end: ida_idaapi.ea_t = property(_ida_hexrays_ctree.
        history_item_t_end_get, _ida_hexrays_ctree.history_item_t_end_set)
    """BADADDR-decompile a function; otherwise end of the range.
"""

    def __init__(self, *args):
        _ida_hexrays_ctree.history_item_t_swiginit(self, _ida_hexrays_ctree
            .new_history_item_t(*args))
    __swig_destroy__ = _ida_hexrays_ctree.delete_history_item_t


_ida_hexrays_ctree.history_item_t_swigregister(history_item_t)


class vdui_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined')
    __repr__ = _swig_repr
    flags: int = property(_ida_hexrays_ctree.vdui_t_flags_get,
        _ida_hexrays_ctree.vdui_t_flags_set)
    """Properties of pseudocode window 
        """

    def visible(self) ->bool:
        """Is the pseudocode window visible? if not, it might be invisible or destroyed 
        """
        return _ida_hexrays_ctree.vdui_t_visible(self)

    def valid(self) ->bool:
        """Does the pseudocode window contain valid code? It can become invalid if the function type gets changed in IDA. 
        """
        return _ida_hexrays_ctree.vdui_t_valid(self)

    def locked(self) ->bool:
        """Does the pseudocode window contain valid code? We lock windows before modifying them, to avoid recursion due to the events generated by the IDA kernel. 
        
:returns: true: The window is locked and may have stale info"""
        return _ida_hexrays_ctree.vdui_t_locked(self)

    def set_visible(self, v: bool) ->None:
        return _ida_hexrays_ctree.vdui_t_set_visible(self, v)

    def set_valid(self, v: bool) ->None:
        return _ida_hexrays_ctree.vdui_t_set_valid(self, v)

    def set_locked(self, v: bool) ->bool:
        return _ida_hexrays_ctree.vdui_t_set_locked(self, v)
    view_idx: int = property(_ida_hexrays_ctree.vdui_t_view_idx_get,
        _ida_hexrays_ctree.vdui_t_view_idx_set)
    """pseudocode window index (0..)
"""
    ct: 'TWidget *' = property(_ida_hexrays_ctree.vdui_t_ct_get,
        _ida_hexrays_ctree.vdui_t_ct_set)
    """pseudocode view
"""
    toplevel: 'TWidget *' = property(_ida_hexrays_ctree.vdui_t_toplevel_get,
        _ida_hexrays_ctree.vdui_t_toplevel_set)
    mba: 'mba_t *' = property(_ida_hexrays_ctree.vdui_t_mba_get,
        _ida_hexrays_ctree.vdui_t_mba_set)
    """pointer to underlying microcode
"""
    cfunc: 'cfuncptr_t' = property(_ida_hexrays_ctree.vdui_t_cfunc_get,
        _ida_hexrays_ctree.vdui_t_cfunc_set)
    """pointer to function object
"""
    last_code: 'merror_t' = property(_ida_hexrays_ctree.
        vdui_t_last_code_get, _ida_hexrays_ctree.vdui_t_last_code_set)
    """result of the last user action. See Microcode error code
"""
    cpos: 'ctext_position_t' = property(_ida_hexrays_ctree.vdui_t_cpos_get,
        _ida_hexrays_ctree.vdui_t_cpos_set)
    """Current ctext position.
"""
    head: 'ctree_item_t' = property(_ida_hexrays_ctree.vdui_t_head_get)
    """First ctree item on the current line (for block comments)
"""
    item: 'ctree_item_t' = property(_ida_hexrays_ctree.vdui_t_item_get)
    """Current ctree item.
"""
    tail: 'ctree_item_t' = property(_ida_hexrays_ctree.vdui_t_tail_get)
    """Tail ctree item on the current line (for indented comments)
"""

    def refresh_view(self, redo_mba: bool) ->None:
        """Refresh pseudocode window. This is the highest level refresh function. It causes the most profound refresh possible and can lead to redecompilation of the current function. Please consider using refresh_ctext() if you need a more superficial refresh. 
        
:param redo_mba: true means to redecompile the current function
 false means to rebuild ctree without regenerating microcode"""
        return _ida_hexrays_ctree.vdui_t_refresh_view(self, redo_mba)

    def refresh_ctext(self, activate: bool=True) ->None:
        """Refresh pseudocode window. This function refreshes the pseudocode window by regenerating its text from cfunc_t. Instead of this function use refresh_func_ctext(), which refreshes all pseudocode windows for the function. 
        """
        return _ida_hexrays_ctree.vdui_t_refresh_ctext(self, activate)

    def switch_to(self, f: 'cfuncptr_t', activate: bool) ->None:
        """Display the specified pseudocode. This function replaces the pseudocode window contents with the specified cfunc_t. 
        
:param f: pointer to the function to display.
:param activate: should the pseudocode window get focus?"""
        return _ida_hexrays_ctree.vdui_t_switch_to(self, f, activate)

    def in_ctree(self) ->bool:
        """Is the current item a statement?

:returns: false if the cursor is in the local variable/type declaration area
 true if the cursor is in the statement area"""
        return _ida_hexrays_ctree.vdui_t_in_ctree(self)

    def get_number(self) ->'cnumber_t *':
        """Get current number. If the current item is a number, return pointer to it. 
        
:returns: nullptr if the current item is not a number This function returns non-null for the cases of a 'switch' statement Also, if the current item is a casted number, then this function will succeed."""
        return _ida_hexrays_ctree.vdui_t_get_number(self)

    def get_current_label(self) ->int:
        """Get current label. If there is a label under the cursor, return its number. 
        
:returns: -1 if there is no label under the cursor. prereq: get_current_item() has been called"""
        return _ida_hexrays_ctree.vdui_t_get_current_label(self)

    def clear(self) ->None:
        """Clear the pseudocode window. It deletes the current function and microcode. 
        """
        return _ida_hexrays_ctree.vdui_t_clear(self)

    def refresh_cpos(self, idv: 'input_device_t') ->bool:
        """Refresh the current position. This function refreshes the cpos field. 
        
:param idv: keyboard or mouse
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_refresh_cpos(self, idv)

    def get_current_item(self, idv: 'input_device_t') ->bool:
        """Get current item. This function refreshes the cpos, item, tail fields. 
        
:param idv: keyboard or mouse
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_get_current_item(self, idv)

    def ui_rename_lvar(self, v: 'lvar_t *') ->bool:
        """Rename local variable. This function displays a dialog box and allows the user to rename a local variable. 
        
:param v: pointer to local variable
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_ui_rename_lvar(self, v)

    def rename_lvar(self, v: 'lvar_t *', name: str, is_user_name: bool) ->bool:
        """Rename local variable. This function permanently renames a local variable. 
        
:param v: pointer to local variable
:param name: new variable name
:param is_user_name: use true to save the new name into the database. use false to delete the saved name.
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_rename_lvar(self, v, name,
            is_user_name)

    def ui_set_call_type(self, e: 'cexpr_t') ->bool:
        """Set type of a function call This function displays a dialog box and allows the user to change the type of a function call 
        
:param e: pointer to call expression
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_ui_set_call_type(self, e)

    def ui_set_lvar_type(self, v: 'lvar_t *') ->bool:
        """Set local variable type. This function displays a dialog box and allows the user to change the type of a local variable. 
        
:param v: pointer to local variable
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_ui_set_lvar_type(self, v)

    def set_lvar_type(self, v: 'lvar_t *', type: 'tinfo_t') ->bool:
        """Set local variable type. This function permanently sets a local variable type and clears NOPTR flag if it was set before by function 'set_noptr_lvar' 
        
:param v: pointer to local variable
:param type: new variable type
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_set_lvar_type(self, v, type)

    def set_noptr_lvar(self, v: 'lvar_t *') ->bool:
        """Inform that local variable should have a non-pointer type This function permanently sets a corresponding variable flag (NOPTR) and removes type if it was set before by function 'set_lvar_type' 
        
:param v: pointer to local variable
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_set_noptr_lvar(self, v)

    def ui_edit_lvar_cmt(self, v: 'lvar_t *') ->bool:
        """Set local variable comment. This function displays a dialog box and allows the user to edit the comment of a local variable. 
        
:param v: pointer to local variable
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_ui_edit_lvar_cmt(self, v)

    def set_lvar_cmt(self, v: 'lvar_t *', cmt: str) ->bool:
        """Set local variable comment. This function permanently sets a variable comment. 
        
:param v: pointer to local variable
:param cmt: new comment
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_set_lvar_cmt(self, v, cmt)

    def ui_map_lvar(self, v: 'lvar_t *') ->bool:
        """Map a local variable to another. This function displays a variable list and allows the user to select mapping. 
        
:param v: pointer to local variable
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_ui_map_lvar(self, v)

    def ui_unmap_lvar(self, v: 'lvar_t *') ->bool:
        """Unmap a local variable. This function displays list of variables mapped to the specified variable and allows the user to select a variable to unmap. 
        
:param v: pointer to local variable
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_ui_unmap_lvar(self, v)

    def ui_noprop_lvar(self, v: 'lvar_t *') ->bool:
        """Forbid variable propagation. 
        
:param v: pointer to local variable
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_ui_noprop_lvar(self, v)

    def map_lvar(self, frm: 'lvar_t *', to: 'lvar_t *') ->bool:
        """Map a local variable to another. This function permanently maps one lvar to another. All occurrences of the mapped variable are replaced by the new variable 
        
:param to: the variable to map to. if nullptr, unmaps the variable
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_map_lvar(self, frm, to)

    def set_udm_type(self, udt_type: 'tinfo_t', udm_idx: int) ->bool:
        """Set structure field type. This function displays a dialog box and allows the user to change the type of a structure field. 
        
:param udt_type: structure/union type
:param udm_idx: index of the structure/union member
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_set_udm_type(self, udt_type, udm_idx)

    def rename_udm(self, udt_type: 'tinfo_t', udm_idx: int) ->bool:
        """Rename structure field. This function displays a dialog box and allows the user to rename a structure field. 
        
:param udt_type: structure/union type
:param udm_idx: index of the structure/union member
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_rename_udm(self, udt_type, udm_idx)

    def set_global_type(self, ea: ida_idaapi.ea_t) ->bool:
        """Set global item type. This function displays a dialog box and allows the user to change the type of a global item (data or function). 
        
:param ea: address of the global item
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_set_global_type(self, ea)

    def rename_global(self, ea: ida_idaapi.ea_t) ->bool:
        """Rename global item. This function displays a dialog box and allows the user to rename a global item (data or function). 
        
:param ea: address of the global item
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_rename_global(self, ea)

    def rename_label(self, label: int) ->bool:
        """Rename a label. This function displays a dialog box and allows the user to rename a statement label. 
        
:param label: label number
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_rename_label(self, label)

    def jump_enter(self, idv: 'input_device_t', omflags: int) ->bool:
        """Process the Enter key. This function jumps to the definition of the item under the cursor. If the current item is a function, it will be decompiled. If the current item is a global data, its disassemly text will be displayed. 
        
:param idv: what cursor must be used, the keyboard or the mouse
:param omflags: OM_NEWWIN: new pseudocode window will open, 0: reuse the existing window
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_jump_enter(self, idv, omflags)

    def ctree_to_disasm(self) ->bool:
        """Jump to disassembly. This function jumps to the address in the disassembly window which corresponds to the current item. The current item is determined based on the current keyboard cursor position. 
        
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_ctree_to_disasm(self)

    def calc_cmt_type(self, lnnum: int, cmttype: 'cmt_type_t') ->'cmt_type_t':
        """Check if the specified line can have a comment. Due to the coordinate system for comments: ([https://hex-rays.com/blog/coordinate-system-for-hex-rays](https://hex-rays.com/blog/coordinate-system-for-hex-rays)) some function lines cannot have comments. This function checks if a comment can be attached to the specified line. 
        
:param lnnum: line number (0 based)
:param cmttype: comment types to check
:returns: possible comment types"""
        return _ida_hexrays_ctree.vdui_t_calc_cmt_type(self, lnnum, cmttype)

    def edit_cmt(self, loc: 'treeloc_t') ->bool:
        """Edit an indented comment. This function displays a dialog box and allows the user to edit the comment for the specified ctree location. 
        
:param loc: comment location
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_edit_cmt(self, loc)

    def edit_func_cmt(self) ->bool:
        """Edit a function comment. This function displays a dialog box and allows the user to edit the function comment. 
        
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_edit_func_cmt(self)

    def del_orphan_cmts(self) ->bool:
        """Delete all orphan comments. Delete all orphan comments and refresh the screen. 
        
:returns: true"""
        return _ida_hexrays_ctree.vdui_t_del_orphan_cmts(self)

    def set_num_radix(self, base: int) ->bool:
        """Change number base. This function changes the current number representation. 
        
:param base: number radix (10 or 16)
 0 means a character constant
:returns: false if failed"""
        return _ida_hexrays_ctree.vdui_t_set_num_radix(self, base)

    def set_num_enum(self) ->bool:
        """Convert number to symbolic constant. This function displays a dialog box and allows the user to select a symbolic constant to represent the number. 
        
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_set_num_enum(self)

    def set_num_stroff(self) ->bool:
        """Convert number to structure field offset. Currently not implemented. 
        
:returns: false if failed or cancelled"""
        return _ida_hexrays_ctree.vdui_t_set_num_stroff(self)

    def invert_sign(self) ->bool:
        """Negate a number. This function negates the current number. 
        
:returns: false if failed."""
        return _ida_hexrays_ctree.vdui_t_invert_sign(self)

    def invert_bits(self) ->bool:
        """Bitwise negate a number. This function inverts all bits of the current number. 
        
:returns: false if failed."""
        return _ida_hexrays_ctree.vdui_t_invert_bits(self)

    def collapse_item(self, hide: bool) ->bool:
        """Collapse/uncollapse item. This function collapses the current item. 
        
:returns: false if failed."""
        return _ida_hexrays_ctree.vdui_t_collapse_item(self, hide)

    def collapse_lvars(self, hide: bool) ->bool:
        """Collapse/uncollapse local variable declarations. 
        
:returns: false if failed."""
        return _ida_hexrays_ctree.vdui_t_collapse_lvars(self, hide)

    def split_item(self, split: bool) ->bool:
        """Split/unsplit item. This function splits the current assignment expression. 
        
:returns: false if failed."""
        return _ida_hexrays_ctree.vdui_t_split_item(self, split)
    __swig_destroy__ = _ida_hexrays_ctree.delete_vdui_t


_ida_hexrays_ctree.vdui_t_swigregister(vdui_t)
CMT_NONE = cvar.CMT_NONE
"""No comment is possible.
"""
CMT_TAIL = cvar.CMT_TAIL
"""Indented comment.
"""
CMT_BLOCK1 = cvar.CMT_BLOCK1
"""Anterioir block comment.
"""
CMT_BLOCK2 = cvar.CMT_BLOCK2
"""Posterior block comment.
"""
CMT_LVAR = cvar.CMT_LVAR
"""Local variable comment.
"""
CMT_FUNC = cvar.CMT_FUNC
"""Function comment.
"""
CMT_ALL = cvar.CMT_ALL
"""All comments.
"""
VDUI_VISIBLE = _ida_hexrays_ctree.VDUI_VISIBLE
"""is visible?
"""
VDUI_VALID = _ida_hexrays_ctree.VDUI_VALID
"""is valid?
"""


class ui_stroff_op_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    text: str = property(_ida_hexrays_ctree.ui_stroff_op_t_text_get,
        _ida_hexrays_ctree.ui_stroff_op_t_text_set)
    """any text for the column "Operand" of widget
"""
    offset: int = property(_ida_hexrays_ctree.ui_stroff_op_t_offset_get,
        _ida_hexrays_ctree.ui_stroff_op_t_offset_set)
    """operand offset, will be used when calculating the UDT path
"""

    def __eq__(self, r: 'ui_stroff_op_t') ->bool:
        return _ida_hexrays_ctree.ui_stroff_op_t___eq__(self, r)

    def __ne__(self, r: 'ui_stroff_op_t') ->bool:
        return _ida_hexrays_ctree.ui_stroff_op_t___ne__(self, r)

    def __init__(self):
        _ida_hexrays_ctree.ui_stroff_op_t_swiginit(self, _ida_hexrays_ctree
            .new_ui_stroff_op_t())
    __swig_destroy__ = _ida_hexrays_ctree.delete_ui_stroff_op_t


_ida_hexrays_ctree.ui_stroff_op_t_swigregister(ui_stroff_op_t)


class ui_stroff_applicator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    __swig_destroy__ = _ida_hexrays_ctree.delete_ui_stroff_applicator_t

    def apply(self, opnum: int, path: 'intvec_t', top_tif: 'tinfo_t', spath:
        str) ->bool:
        """:param opnum: operand ordinal number, see below
:param path: path describing the union selection, maybe empty
:param top_tif: tinfo_t of the selected toplevel UDT
:param spath: selected path"""
        return _ida_hexrays_ctree.ui_stroff_applicator_t_apply(self, opnum,
            path, top_tif, spath)

    def __init__(self):
        if self.__class__ == ui_stroff_applicator_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_ctree.ui_stroff_applicator_t_swiginit(self,
            _ida_hexrays_ctree.new_ui_stroff_applicator_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_ctree.disown_ui_stroff_applicator_t(self)
        return weakref.proxy(self)


_ida_hexrays_ctree.ui_stroff_applicator_t_swigregister(ui_stroff_applicator_t)


def select_udt_by_offset(udts: 'qvector< tinfo_t > const *', ops:
    'ui_stroff_ops_t', applicator: 'ui_stroff_applicator_t') ->int:
    """Select UDT 
        
:param udts: list of UDT tinfo_t for the selection, if nullptr or empty then UDTs from the "Local types" will be used
:param ops: operands
:param applicator: callback will be called to apply the selection for every operand"""
    return _ida_hexrays_ctree.select_udt_by_offset(udts, ops, applicator)


import ida_idaapi
is_allowed_on_small_struni = accepts_small_udts


class DecompilationFailure(Exception):
    pass


def decompile(ea, hf=None, flags=0):
    """Decompile a snippet or a function. 
        
:param hf: extended error information (if failed)
:returns: pointer to the decompilation result (a reference counted pointer). nullptr if failed."""
    return decompile_func(ea, hf, flags)


ida_idaapi._listify_types(cinsnptrvec_t, ctree_items_t, qvector_carg_t,
    qvector_ccase_t, history_t, ui_stroff_ops_t)


def citem_to_specific_type(self):
    """ cast the citem_t object to its more specific type, either cexpr_t or cinsn_t. """
    if self.op >= cot_empty and self.op <= cot_last:
        return self.cexpr
    elif self.op >= cit_empty and self.op < cit_end:
        return self.cinsn
    raise RuntimeError('unknown op type %s' % (repr(self.op),))


citem_t.to_specific_type = property(citem_to_specific_type)
""" array used for translating cinsn_t->op type to their names. """
cinsn_t.op_to_typename = {}
for k in dir(_ida_hexrays_ctree):
    if k.startswith('cit_'):
        cinsn_t.op_to_typename[getattr(_ida_hexrays_ctree, k)] = k[4:]
""" array used for translating cexpr_t->op type to their names. """
cexpr_t.op_to_typename = {}
for k in dir(_ida_hexrays_ctree):
    if k.startswith('cot_'):
        cexpr_t.op_to_typename[getattr(_ida_hexrays_ctree, k)] = k[4:]


def property_op_to_typename(self):
    return self.op_to_typename[self.op]


cinsn_t.opname = property(property_op_to_typename)
cexpr_t.opname = property(property_op_to_typename)


def cexpr_operands(self):
    """ return a dictionary with the operands of a cexpr_t. """
    if (self.op >= cot_comma and self.op <= cot_asgumod or self.op >=
        cot_lor and self.op <= cot_fdiv or self.op == cot_idx):
        return {'x': self.x, 'y': self.y}
    elif self.op == cot_tern:
        return {'x': self.x, 'y': self.y, 'z': self.z}
    elif self.op in [cot_fneg, cot_neg, cot_sizeof
        ] or self.op >= cot_lnot and self.op <= cot_predec:
        return {'x': self.x}
    elif self.op == cot_cast:
        return {'type': self.type, 'x': self.x}
    elif self.op == cot_call:
        return {'x': self.x, 'a': self.a}
    elif self.op in [cot_memref, cot_memptr]:
        return {'x': self.x, 'm': self.m}
    elif self.op == cot_num:
        return {'n': self.n}
    elif self.op == cot_fnum:
        return {'fpc': self.fpc}
    elif self.op == cot_str:
        return {'string': self.string}
    elif self.op == cot_obj:
        return {'obj_ea': self.obj_ea}
    elif self.op == cot_var:
        return {'v': self.v}
    elif self.op == cot_helper:
        return {'helper': self.helper}
    raise RuntimeError('unknown op type %s' % self.opname)


cexpr_t.operands = property(cexpr_operands)


def cinsn_details(self):
    """
    return the details pointer for the cinsn_t object depending on the value of its op member.     this is one of the cblock_t, cif_t, etc. objects.
    """
    if self.op not in self.op_to_typename:
        raise RuntimeError('unknown item->op type')
    opname = self.opname
    if opname == 'empty':
        return self
    if opname in ['break', 'continue']:
        return None
    return getattr(self, 'c' + opname)


cinsn_t.details = property(cinsn_details)
cfuncptr_t.__str__ = lambda self: str(self.__deref__())
cfuncptr_t.__repr__ = lambda self: repr(self.__deref__())
cfuncptr_t.__eq__ = lambda self, other: self.__ptrval__() == other.__ptrval__(
    ) if isinstance(other, cfuncptr_t) else False
import ida_typeinf


def cfunc_type(self):
    """ Get the function's return type tinfo_t object. """
    tif = ida_typeinf.tinfo_t()
    result = self.get_func_type(tif)
    if not result:
        return
    return tif


cfunc_t.type = property(cfunc_type)
cfuncptr_t.type = property(lambda self: self.__deref__().type)
cfunc_t.arguments = property(lambda self: [self.lvars[i] for i in self.argidx])
cfuncptr_t.arguments = property(lambda self: self.__deref__().arguments)
cfunc_t.lvars = property(cfunc_t.get_lvars)
cfuncptr_t.lvars = property(lambda self: self.__deref__().lvars)
cfunc_t.warnings = property(cfunc_t.get_warnings)
cfuncptr_t.warnings = property(lambda self: self.__deref__().warnings)
cfunc_t.pseudocode = property(cfunc_t.get_pseudocode)
cfuncptr_t.pseudocode = property(lambda self: self.__deref__().get_pseudocode()
    )
cfunc_t.eamap = property(cfunc_t.get_eamap)
cfuncptr_t.eamap = property(lambda self: self.__deref__().get_eamap())
cfunc_t.boundaries = property(cfunc_t.get_boundaries)
cfuncptr_t.boundaries = property(lambda self: self.__deref__().get_boundaries()
    )


def _call_with_transferrable_ownership(fun, *args):
    e = args[0]
    was_owned = e.thisown
    res = fun(e, *args[1:])
    if was_owned:
        if res:
            e._maybe_disown_and_deregister()
            res._own_and_register()
    else:
        debug_hexrays_ctree(
            'NOTE: call_with_transferrable_ownership() called with non-IDAPython-owned object. Is this intentional?'
            )
    return res


def lnot(e):
    """Logically negate the specified expression. The specified expression will be logically negated. For example, "x == y" is converted into "x != y" by this function. 
        
:param e: expression to negate. After the call, e must not be used anymore because it can be changed by the function. The function return value must be used to refer to the expression.
:returns: logically negated expression."""
    return _call_with_transferrable_ownership(_ll_lnot, e)


def make_ref(e):
    """Create a reference. This function performs the following conversion: "obj" => "&obj". It can handle casts, annihilate "&*", and process other special cases. 
        """
    return _call_with_transferrable_ownership(_ll_make_ref, e)


def dereference(e, ptrsize, is_float=False):
    """Dereference a pointer. This function dereferences a pointer expression. It performs the following conversion: "ptr" => "*ptr" It can handle discrepancies in the pointer type and the access size. 
        
:param e: expression to deference
:param ptrsize: access size
:returns: dereferenced expression"""
    return _call_with_transferrable_ownership(_ll_dereference, e, ptrsize,
        is_float)


def call_helper(rettype, args, *rest):
    """Create a helper call.
"""
    res = _ll_call_helper(rettype, args, *rest)
    if res:
        res._own_and_register()
        if type(args) == carglist_t:
            args.thisown = False
    return res


def new_block():
    """Create a new block-statement.
"""
    res = _ll_new_block()
    if res:
        res._own_and_register()
    return res


def make_num(*args):
    """Create a number expression 
        
:param n: value
:param func: current function
:param ea: definition address of the number
:param opnum: operand number of the number (in the disassembly listing)
:param sign: number sign
:param size: size of number in bytes Please note that the type of the resulting expression can be anything because it can be inherited from the disassembly listing or taken from the user specified number representation in the pseudocode view."""
    res = _ll_make_num(*args)
    if res:
        res._own_and_register()
    return res


def create_helper(*args):
    """Create a helper object..
"""
    res = _ll_create_helper(*args)
    if res:
        res._own_and_register()
    return res


class __cbhooks_t(Hexrays_Hooks):
    instances = []

    def __init__(self, callback):
        self.callback = callback
        self.instances.append(self)
        Hexrays_Hooks.__init__(self)

    def mba_maturity(self, *args):
        return self.callback(hxe_mba_maturity, *args)

    def maturity(self, *args):
        return self.callback(hxe_maturity, *args)

    def interr(self, *args):
        return self.callback(hxe_interr, *args)

    def print_func(self, *args):
        return self.callback(hxe_print_func, *args)

    def func_printed(self, *args):
        return self.callback(hxe_func_printed, *args)

    def open_pseudocode(self, *args):
        return self.callback(hxe_open_pseudocode, *args)

    def switch_pseudocode(self, *args):
        return self.callback(hxe_switch_pseudocode, *args)

    def refresh_pseudocode(self, *args):
        return self.callback(hxe_refresh_pseudocode, *args)

    def close_pseudocode(self, *args):
        return self.callback(hxe_close_pseudocode, *args)

    def keyboard(self, *args):
        return self.callback(hxe_keyboard, *args)

    def right_click(self, *args):
        return self.callback(hxe_right_click, *args)

    def double_click(self, *args):
        return self.callback(hxe_double_click, *args)

    def curpos(self, *args):
        return self.callback(hxe_curpos, *args)

    def create_hint(self, *args):
        return self.callback(hxe_create_hint, *args)

    def text_ready(self, *args):
        return self.callback(hxe_text_ready, *args)

    def populating_popup(self, *args):
        return self.callback(hxe_populating_popup, *args)


def install_hexrays_callback(callback):
    """Install handler for decompiler events. 
        
:param callback: handler to install
:returns: false if failed"""
    h = __cbhooks_t(callback)
    h.hook()
    return True


def remove_hexrays_callback(callback):
    """Uninstall handler for decompiler events. 
        
:param callback: handler to uninstall
:returns: number of uninstalled handlers."""
    for inst in __cbhooks_t.instances:
        if inst.callback == callback:
            inst.unhook()
            __cbhooks_t.instances.remove(inst)
            return 1
    return 0
