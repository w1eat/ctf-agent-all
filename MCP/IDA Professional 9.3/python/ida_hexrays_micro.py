from __future__ import annotations
from sys import version_info as _swig_python_version_info
if __package__ or '.' in __name__:
    from . import _ida_hexrays_micro
else:
    import _ida_hexrays_micro
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
SWIG_PYTHON_LEGACY_BOOL = _ida_hexrays_micro.SWIG_PYTHON_LEGACY_BOOL
from typing import Tuple, List, Union
import ida_idaapi
import ida_pro
import ida_xref
import ida_typeinf
import ida_idp
import ida_gdl
from ida_hexrays_defs import MMAT_GLBOPT3
import ida_hexrays_defs


class array_of_bitsets(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.array_of_bitsets_swiginit(self,
            _ida_hexrays_micro.new_array_of_bitsets(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_array_of_bitsets

    def push_back(self, *args) ->'bitset_t &':
        return _ida_hexrays_micro.array_of_bitsets_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_micro.array_of_bitsets_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_micro.array_of_bitsets_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.array_of_bitsets_empty(self)

    def at(self, _idx: int) ->'bitset_t const &':
        return _ida_hexrays_micro.array_of_bitsets_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_micro.array_of_bitsets_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.array_of_bitsets_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_micro.array_of_bitsets_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_micro.array_of_bitsets_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_micro.array_of_bitsets_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_micro.array_of_bitsets_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_micro.array_of_bitsets_truncate(self)

    def swap(self, r: 'array_of_bitsets') ->None:
        return _ida_hexrays_micro.array_of_bitsets_swap(self, r)

    def extract(self) ->'bitset_t *':
        return _ida_hexrays_micro.array_of_bitsets_extract(self)

    def inject(self, s: 'bitset_t', len: int) ->None:
        return _ida_hexrays_micro.array_of_bitsets_inject(self, s, len)

    def __eq__(self, r: 'array_of_bitsets') ->bool:
        return _ida_hexrays_micro.array_of_bitsets___eq__(self, r)

    def __ne__(self, r: 'array_of_bitsets') ->bool:
        return _ida_hexrays_micro.array_of_bitsets___ne__(self, r)

    def begin(self, *args) ->'qvector< bitset_t >::const_iterator':
        return _ida_hexrays_micro.array_of_bitsets_begin(self, *args)

    def end(self, *args) ->'qvector< bitset_t >::const_iterator':
        return _ida_hexrays_micro.array_of_bitsets_end(self, *args)

    def insert(self, it: 'bitset_t', x: 'bitset_t'
        ) ->'qvector< bitset_t >::iterator':
        return _ida_hexrays_micro.array_of_bitsets_insert(self, it, x)

    def erase(self, *args) ->'qvector< bitset_t >::iterator':
        return _ida_hexrays_micro.array_of_bitsets_erase(self, *args)

    def find(self, *args) ->'qvector< bitset_t >::const_iterator':
        return _ida_hexrays_micro.array_of_bitsets_find(self, *args)

    def has(self, x: 'bitset_t') ->bool:
        return _ida_hexrays_micro.array_of_bitsets_has(self, x)

    def add_unique(self, x: 'bitset_t') ->bool:
        return _ida_hexrays_micro.array_of_bitsets_add_unique(self, x)

    def _del(self, x: 'bitset_t') ->bool:
        return _ida_hexrays_micro.array_of_bitsets__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_micro.array_of_bitsets___len__(self)

    def __getitem__(self, i: int) ->'bitset_t const &':
        return _ida_hexrays_micro.array_of_bitsets___getitem__(self, i)

    def __setitem__(self, i: int, v: 'bitset_t') ->None:
        return _ida_hexrays_micro.array_of_bitsets___setitem__(self, i, v)

    def append(self, x: 'bitset_t') ->None:
        return _ida_hexrays_micro.array_of_bitsets_append(self, x)

    def extend(self, x: 'array_of_bitsets') ->None:
        return _ida_hexrays_micro.array_of_bitsets_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_micro.array_of_bitsets_swigregister(array_of_bitsets)


class mopvec_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.mopvec_t_swiginit(self, _ida_hexrays_micro.
            new_mopvec_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_mopvec_t

    def push_back(self, *args) ->'mop_t &':
        return _ida_hexrays_micro.mopvec_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_micro.mopvec_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_micro.mopvec_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.mopvec_t_empty(self)

    def at(self, _idx: int) ->'mop_t const &':
        return _ida_hexrays_micro.mopvec_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_micro.mopvec_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.mopvec_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_micro.mopvec_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_micro.mopvec_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_micro.mopvec_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_micro.mopvec_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_micro.mopvec_t_truncate(self)

    def swap(self, r: 'mopvec_t') ->None:
        return _ida_hexrays_micro.mopvec_t_swap(self, r)

    def extract(self) ->'mop_t *':
        return _ida_hexrays_micro.mopvec_t_extract(self)

    def inject(self, s: 'mop_t', len: int) ->None:
        return _ida_hexrays_micro.mopvec_t_inject(self, s, len)

    def __eq__(self, r: 'mopvec_t') ->bool:
        return _ida_hexrays_micro.mopvec_t___eq__(self, r)

    def __ne__(self, r: 'mopvec_t') ->bool:
        return _ida_hexrays_micro.mopvec_t___ne__(self, r)

    def begin(self, *args) ->'qvector< mop_t >::const_iterator':
        return _ida_hexrays_micro.mopvec_t_begin(self, *args)

    def end(self, *args) ->'qvector< mop_t >::const_iterator':
        return _ida_hexrays_micro.mopvec_t_end(self, *args)

    def insert(self, it: 'mop_t', x: 'mop_t') ->'qvector< mop_t >::iterator':
        return _ida_hexrays_micro.mopvec_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< mop_t >::iterator':
        return _ida_hexrays_micro.mopvec_t_erase(self, *args)

    def find(self, *args) ->'qvector< mop_t >::const_iterator':
        return _ida_hexrays_micro.mopvec_t_find(self, *args)

    def has(self, x: 'mop_t') ->bool:
        return _ida_hexrays_micro.mopvec_t_has(self, x)

    def add_unique(self, x: 'mop_t') ->bool:
        return _ida_hexrays_micro.mopvec_t_add_unique(self, x)

    def _del(self, x: 'mop_t') ->bool:
        return _ida_hexrays_micro.mopvec_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_micro.mopvec_t___len__(self)

    def __getitem__(self, i: int) ->'mop_t const &':
        return _ida_hexrays_micro.mopvec_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'mop_t') ->None:
        return _ida_hexrays_micro.mopvec_t___setitem__(self, i, v)

    def append(self, x: 'mop_t') ->None:
        return _ida_hexrays_micro.mopvec_t_append(self, x)

    def extend(self, x: 'mopvec_t') ->None:
        return _ida_hexrays_micro.mopvec_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_micro.mopvec_t_swigregister(mopvec_t)


class mcallargs_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.mcallargs_t_swiginit(self, _ida_hexrays_micro.
            new_mcallargs_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_mcallargs_t

    def push_back(self, *args) ->'mcallarg_t &':
        return _ida_hexrays_micro.mcallargs_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_micro.mcallargs_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_micro.mcallargs_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.mcallargs_t_empty(self)

    def at(self, _idx: int) ->'mcallarg_t const &':
        return _ida_hexrays_micro.mcallargs_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_micro.mcallargs_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.mcallargs_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_micro.mcallargs_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_micro.mcallargs_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_micro.mcallargs_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_micro.mcallargs_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_micro.mcallargs_t_truncate(self)

    def swap(self, r: 'mcallargs_t') ->None:
        return _ida_hexrays_micro.mcallargs_t_swap(self, r)

    def extract(self) ->'mcallarg_t *':
        return _ida_hexrays_micro.mcallargs_t_extract(self)

    def inject(self, s: 'mcallarg_t', len: int) ->None:
        return _ida_hexrays_micro.mcallargs_t_inject(self, s, len)

    def __eq__(self, r: 'mcallargs_t') ->bool:
        return _ida_hexrays_micro.mcallargs_t___eq__(self, r)

    def __ne__(self, r: 'mcallargs_t') ->bool:
        return _ida_hexrays_micro.mcallargs_t___ne__(self, r)

    def begin(self, *args) ->'qvector< mcallarg_t >::const_iterator':
        return _ida_hexrays_micro.mcallargs_t_begin(self, *args)

    def end(self, *args) ->'qvector< mcallarg_t >::const_iterator':
        return _ida_hexrays_micro.mcallargs_t_end(self, *args)

    def insert(self, it: 'mcallarg_t', x: 'mcallarg_t'
        ) ->'qvector< mcallarg_t >::iterator':
        return _ida_hexrays_micro.mcallargs_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< mcallarg_t >::iterator':
        return _ida_hexrays_micro.mcallargs_t_erase(self, *args)

    def find(self, *args) ->'qvector< mcallarg_t >::const_iterator':
        return _ida_hexrays_micro.mcallargs_t_find(self, *args)

    def has(self, x: 'mcallarg_t') ->bool:
        return _ida_hexrays_micro.mcallargs_t_has(self, x)

    def add_unique(self, x: 'mcallarg_t') ->bool:
        return _ida_hexrays_micro.mcallargs_t_add_unique(self, x)

    def _del(self, x: 'mcallarg_t') ->bool:
        return _ida_hexrays_micro.mcallargs_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_micro.mcallargs_t___len__(self)

    def __getitem__(self, i: int) ->'mcallarg_t const &':
        return _ida_hexrays_micro.mcallargs_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'mcallarg_t') ->None:
        return _ida_hexrays_micro.mcallargs_t___setitem__(self, i, v)

    def append(self, x: 'mcallarg_t') ->None:
        return _ida_hexrays_micro.mcallargs_t_append(self, x)

    def extend(self, x: 'mcallargs_t') ->None:
        return _ida_hexrays_micro.mcallargs_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_micro.mcallargs_t_swigregister(mcallargs_t)


class block_chains_vec_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.block_chains_vec_t_swiginit(self,
            _ida_hexrays_micro.new_block_chains_vec_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_block_chains_vec_t

    def push_back(self, *args) ->'block_chains_t &':
        return _ida_hexrays_micro.block_chains_vec_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_micro.block_chains_vec_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_micro.block_chains_vec_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.block_chains_vec_t_empty(self)

    def at(self, _idx: int) ->'block_chains_t const &':
        return _ida_hexrays_micro.block_chains_vec_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_micro.block_chains_vec_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.block_chains_vec_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_micro.block_chains_vec_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_micro.block_chains_vec_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_micro.block_chains_vec_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_micro.block_chains_vec_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_micro.block_chains_vec_t_truncate(self)

    def swap(self, r: 'block_chains_vec_t') ->None:
        return _ida_hexrays_micro.block_chains_vec_t_swap(self, r)

    def extract(self) ->'block_chains_t *':
        return _ida_hexrays_micro.block_chains_vec_t_extract(self)

    def inject(self, s: 'block_chains_t', len: int) ->None:
        return _ida_hexrays_micro.block_chains_vec_t_inject(self, s, len)

    def begin(self, *args) ->'qvector< block_chains_t >::const_iterator':
        return _ida_hexrays_micro.block_chains_vec_t_begin(self, *args)

    def end(self, *args) ->'qvector< block_chains_t >::const_iterator':
        return _ida_hexrays_micro.block_chains_vec_t_end(self, *args)

    def insert(self, it: 'block_chains_t', x: 'block_chains_t'
        ) ->'qvector< block_chains_t >::iterator':
        return _ida_hexrays_micro.block_chains_vec_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< block_chains_t >::iterator':
        return _ida_hexrays_micro.block_chains_vec_t_erase(self, *args)

    def __len__(self) ->int:
        return _ida_hexrays_micro.block_chains_vec_t___len__(self)

    def __getitem__(self, i: int) ->'block_chains_t const &':
        return _ida_hexrays_micro.block_chains_vec_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'block_chains_t') ->None:
        return _ida_hexrays_micro.block_chains_vec_t___setitem__(self, i, v)

    def append(self, x: 'block_chains_t') ->None:
        return _ida_hexrays_micro.block_chains_vec_t_append(self, x)

    def extend(self, x: 'block_chains_vec_t') ->None:
        return _ida_hexrays_micro.block_chains_vec_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_micro.block_chains_vec_t_swigregister(block_chains_vec_t)


class lvar_mapping_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def at(self, _Keyval: 'lvar_locator_t') ->'lvar_locator_t &':
        return _ida_hexrays_micro.lvar_mapping_t_at(self, _Keyval)

    def size(self) ->int:
        return _ida_hexrays_micro.lvar_mapping_t_size(self)

    def __init__(self):
        _ida_hexrays_micro.lvar_mapping_t_swiginit(self, _ida_hexrays_micro
            .new_lvar_mapping_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_lvar_mapping_t


_ida_hexrays_micro.lvar_mapping_t_swigregister(lvar_mapping_t)


class qvector_lvar_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.qvector_lvar_t_swiginit(self, _ida_hexrays_micro
            .new_qvector_lvar_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_qvector_lvar_t

    def push_back(self, *args) ->'lvar_t &':
        return _ida_hexrays_micro.qvector_lvar_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_micro.qvector_lvar_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_micro.qvector_lvar_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.qvector_lvar_t_empty(self)

    def at(self, _idx: int) ->'lvar_t const &':
        return _ida_hexrays_micro.qvector_lvar_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_micro.qvector_lvar_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.qvector_lvar_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_micro.qvector_lvar_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_micro.qvector_lvar_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_micro.qvector_lvar_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_micro.qvector_lvar_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_micro.qvector_lvar_t_truncate(self)

    def swap(self, r: 'qvector_lvar_t') ->None:
        return _ida_hexrays_micro.qvector_lvar_t_swap(self, r)

    def extract(self) ->'lvar_t *':
        return _ida_hexrays_micro.qvector_lvar_t_extract(self)

    def inject(self, s: 'lvar_t', len: int) ->None:
        return _ida_hexrays_micro.qvector_lvar_t_inject(self, s, len)

    def __eq__(self, r: 'qvector_lvar_t') ->bool:
        return _ida_hexrays_micro.qvector_lvar_t___eq__(self, r)

    def __ne__(self, r: 'qvector_lvar_t') ->bool:
        return _ida_hexrays_micro.qvector_lvar_t___ne__(self, r)

    def begin(self, *args) ->'qvector< lvar_t >::const_iterator':
        return _ida_hexrays_micro.qvector_lvar_t_begin(self, *args)

    def end(self, *args) ->'qvector< lvar_t >::const_iterator':
        return _ida_hexrays_micro.qvector_lvar_t_end(self, *args)

    def insert(self, it: 'lvar_t', x: 'lvar_t'
        ) ->'qvector< lvar_t >::iterator':
        return _ida_hexrays_micro.qvector_lvar_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< lvar_t >::iterator':
        return _ida_hexrays_micro.qvector_lvar_t_erase(self, *args)

    def find(self, *args) ->'qvector< lvar_t >::const_iterator':
        return _ida_hexrays_micro.qvector_lvar_t_find(self, *args)

    def has(self, x: 'lvar_t') ->bool:
        return _ida_hexrays_micro.qvector_lvar_t_has(self, x)

    def add_unique(self, x: 'lvar_t') ->bool:
        return _ida_hexrays_micro.qvector_lvar_t_add_unique(self, x)

    def _del(self, x: 'lvar_t') ->bool:
        return _ida_hexrays_micro.qvector_lvar_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_micro.qvector_lvar_t___len__(self)

    def __getitem__(self, i: int) ->'lvar_t const &':
        return _ida_hexrays_micro.qvector_lvar_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'lvar_t') ->None:
        return _ida_hexrays_micro.qvector_lvar_t___setitem__(self, i, v)

    def append(self, x: 'lvar_t') ->None:
        return _ida_hexrays_micro.qvector_lvar_t_append(self, x)

    def extend(self, x: 'qvector_lvar_t') ->None:
        return _ida_hexrays_micro.qvector_lvar_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_micro.qvector_lvar_t_swigregister(qvector_lvar_t)


class lvar_saved_infos_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.lvar_saved_infos_t_swiginit(self,
            _ida_hexrays_micro.new_lvar_saved_infos_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_lvar_saved_infos_t

    def push_back(self, *args) ->'lvar_saved_info_t &':
        return _ida_hexrays_micro.lvar_saved_infos_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_micro.lvar_saved_infos_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.lvar_saved_infos_t_empty(self)

    def at(self, _idx: int) ->'lvar_saved_info_t const &':
        return _ida_hexrays_micro.lvar_saved_infos_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_micro.lvar_saved_infos_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_truncate(self)

    def swap(self, r: 'lvar_saved_infos_t') ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_swap(self, r)

    def extract(self) ->'lvar_saved_info_t *':
        return _ida_hexrays_micro.lvar_saved_infos_t_extract(self)

    def inject(self, s: 'lvar_saved_info_t', len: int) ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_inject(self, s, len)

    def __eq__(self, r: 'lvar_saved_infos_t') ->bool:
        return _ida_hexrays_micro.lvar_saved_infos_t___eq__(self, r)

    def __ne__(self, r: 'lvar_saved_infos_t') ->bool:
        return _ida_hexrays_micro.lvar_saved_infos_t___ne__(self, r)

    def begin(self, *args) ->'qvector< lvar_saved_info_t >::const_iterator':
        return _ida_hexrays_micro.lvar_saved_infos_t_begin(self, *args)

    def end(self, *args) ->'qvector< lvar_saved_info_t >::const_iterator':
        return _ida_hexrays_micro.lvar_saved_infos_t_end(self, *args)

    def insert(self, it: 'lvar_saved_info_t', x: 'lvar_saved_info_t'
        ) ->'qvector< lvar_saved_info_t >::iterator':
        return _ida_hexrays_micro.lvar_saved_infos_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< lvar_saved_info_t >::iterator':
        return _ida_hexrays_micro.lvar_saved_infos_t_erase(self, *args)

    def find(self, *args) ->'qvector< lvar_saved_info_t >::const_iterator':
        return _ida_hexrays_micro.lvar_saved_infos_t_find(self, *args)

    def has(self, x: 'lvar_saved_info_t') ->bool:
        return _ida_hexrays_micro.lvar_saved_infos_t_has(self, x)

    def add_unique(self, x: 'lvar_saved_info_t') ->bool:
        return _ida_hexrays_micro.lvar_saved_infos_t_add_unique(self, x)

    def _del(self, x: 'lvar_saved_info_t') ->bool:
        return _ida_hexrays_micro.lvar_saved_infos_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_micro.lvar_saved_infos_t___len__(self)

    def __getitem__(self, i: int) ->'lvar_saved_info_t const &':
        return _ida_hexrays_micro.lvar_saved_infos_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'lvar_saved_info_t') ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t___setitem__(self, i, v)

    def append(self, x: 'lvar_saved_info_t') ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_append(self, x)

    def extend(self, x: 'lvar_saved_infos_t') ->None:
        return _ida_hexrays_micro.lvar_saved_infos_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_micro.lvar_saved_infos_t_swigregister(lvar_saved_infos_t)
MAX_VLR_SIZE = _ida_hexrays_micro.MAX_VLR_SIZE


def max_vlr_value(size: int) ->'uvlr_t':
    return _ida_hexrays_micro.max_vlr_value(size)


def min_vlr_svalue(size: int) ->'uvlr_t':
    return _ida_hexrays_micro.min_vlr_svalue(size)


def max_vlr_svalue(size: int) ->'uvlr_t':
    return _ida_hexrays_micro.max_vlr_svalue(size)


CMP_NZ = _ida_hexrays_micro.CMP_NZ
CMP_Z = _ida_hexrays_micro.CMP_Z
CMP_AE = _ida_hexrays_micro.CMP_AE
CMP_B = _ida_hexrays_micro.CMP_B
CMP_A = _ida_hexrays_micro.CMP_A
CMP_BE = _ida_hexrays_micro.CMP_BE
CMP_GT = _ida_hexrays_micro.CMP_GT
CMP_GE = _ida_hexrays_micro.CMP_GE
CMP_LT = _ida_hexrays_micro.CMP_LT
CMP_LE = _ida_hexrays_micro.CMP_LE


def is_unsigned_cmpop(cmpop: 'cmpop_t') ->bool:
    return _ida_hexrays_micro.is_unsigned_cmpop(cmpop)


def is_signed_cmpop(cmpop: 'cmpop_t') ->bool:
    return _ida_hexrays_micro.is_signed_cmpop(cmpop)


def is_cmpop_with_eq(cmpop: 'cmpop_t') ->bool:
    return _ida_hexrays_micro.is_cmpop_with_eq(cmpop)


def is_cmpop_without_eq(cmpop: 'cmpop_t') ->bool:
    return _ida_hexrays_micro.is_cmpop_without_eq(cmpop)


class valrng_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.valrng_t_swiginit(self, _ida_hexrays_micro.
            new_valrng_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_valrng_t

    def swap(self, r: 'valrng_t') ->None:
        return _ida_hexrays_micro.valrng_t_swap(self, r)

    def __eq__(self, r: 'valrng_t') ->bool:
        return _ida_hexrays_micro.valrng_t___eq__(self, r)

    def __ne__(self, r: 'valrng_t') ->bool:
        return _ida_hexrays_micro.valrng_t___ne__(self, r)

    def __lt__(self, r: 'valrng_t') ->bool:
        return _ida_hexrays_micro.valrng_t___lt__(self, r)

    def __gt__(self, r: 'valrng_t') ->bool:
        return _ida_hexrays_micro.valrng_t___gt__(self, r)

    def __le__(self, r: 'valrng_t') ->bool:
        return _ida_hexrays_micro.valrng_t___le__(self, r)

    def __ge__(self, r: 'valrng_t') ->bool:
        return _ida_hexrays_micro.valrng_t___ge__(self, r)

    def compare(self, r: 'valrng_t') ->int:
        return _ida_hexrays_micro.valrng_t_compare(self, r)

    def set_none(self) ->None:
        return _ida_hexrays_micro.valrng_t_set_none(self)

    def set_all(self) ->None:
        return _ida_hexrays_micro.valrng_t_set_all(self)

    def set_unk(self) ->None:
        return _ida_hexrays_micro.valrng_t_set_unk(self)

    def set_eq(self, v: 'uvlr_t') ->None:
        return _ida_hexrays_micro.valrng_t_set_eq(self, v)

    def set_cmp(self, cmp: 'cmpop_t', _value: 'uvlr_t') ->None:
        return _ida_hexrays_micro.valrng_t_set_cmp(self, cmp, _value)

    def reduce_size(self, new_size: int) ->bool:
        return _ida_hexrays_micro.valrng_t_reduce_size(self, new_size)

    def intersect_with(self, r: 'valrng_t') ->bool:
        return _ida_hexrays_micro.valrng_t_intersect_with(self, r)

    def unite_with(self, r: 'valrng_t') ->bool:
        return _ida_hexrays_micro.valrng_t_unite_with(self, r)

    def inverse(self) ->None:
        return _ida_hexrays_micro.valrng_t_inverse(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.valrng_t_empty(self)

    def all_values(self) ->bool:
        return _ida_hexrays_micro.valrng_t_all_values(self)

    def is_unknown(self) ->bool:
        return _ida_hexrays_micro.valrng_t_is_unknown(self)

    def has(self, v: 'uvlr_t') ->bool:
        return _ida_hexrays_micro.valrng_t_has(self, v)

    def _print(self) ->None:
        return _ida_hexrays_micro.valrng_t__print(self)

    def dstr(self) ->str:
        return _ida_hexrays_micro.valrng_t_dstr(self)

    def cvt_to_single_value(self) ->bool:
        return _ida_hexrays_micro.valrng_t_cvt_to_single_value(self)

    def cvt_to_cmp(self) ->bool:
        return _ida_hexrays_micro.valrng_t_cvt_to_cmp(self)

    def get_size(self) ->int:
        return _ida_hexrays_micro.valrng_t_get_size(self)

    def max_value(self) ->'uvlr_t':
        return _ida_hexrays_micro.valrng_t_max_value(self)

    def min_svalue(self) ->'uvlr_t':
        return _ida_hexrays_micro.valrng_t_min_svalue(self)

    def max_svalue(self) ->'uvlr_t':
        return _ida_hexrays_micro.valrng_t_max_svalue(self)

    def _register(self) ->None:
        return _ida_hexrays_micro.valrng_t__register(self)

    def _deregister(self) ->None:
        return _ida_hexrays_micro.valrng_t__deregister(self)


_ida_hexrays_micro.valrng_t_swigregister(valrng_t)
cvar = _ida_hexrays_micro.cvar
MAX_VLR_VALUE = cvar.MAX_VLR_VALUE
MAX_VLR_SVALUE = cvar.MAX_VLR_SVALUE
MIN_VLR_SVALUE = cvar.MIN_VLR_SVALUE


def get_merror_desc(code: 'merror_t', mba: 'mba_t') ->str:
    """Get textual description of an error code 
        
:param code: Microcode error code
:param mba: the microcode array
:returns: the error address"""
    return _ida_hexrays_micro.get_merror_desc(code, mba)


class hexrays_failure_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    code: 'merror_t' = property(_ida_hexrays_micro.
        hexrays_failure_t_code_get, _ida_hexrays_micro.
        hexrays_failure_t_code_set)
    """Microcode error code
"""
    errea: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        hexrays_failure_t_errea_get, _ida_hexrays_micro.
        hexrays_failure_t_errea_set)
    """associated address
"""
    str: str = property(_ida_hexrays_micro.hexrays_failure_t_str_get,
        _ida_hexrays_micro.hexrays_failure_t_str_set)
    """string information
"""

    def __init__(self, *args):
        _ida_hexrays_micro.hexrays_failure_t_swiginit(self,
            _ida_hexrays_micro.new_hexrays_failure_t(*args))

    def desc(self) ->str:
        return _ida_hexrays_micro.hexrays_failure_t_desc(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_hexrays_failure_t


_ida_hexrays_micro.hexrays_failure_t_swigregister(hexrays_failure_t)


class vd_failure_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    hf: 'hexrays_failure_t' = property(_ida_hexrays_micro.
        vd_failure_t_hf_get, _ida_hexrays_micro.vd_failure_t_hf_set)

    def __init__(self, *args):
        _ida_hexrays_micro.vd_failure_t_swiginit(self, _ida_hexrays_micro.
            new_vd_failure_t(*args))

    def desc(self) ->str:
        return _ida_hexrays_micro.vd_failure_t_desc(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_vd_failure_t


_ida_hexrays_micro.vd_failure_t_swigregister(vd_failure_t)


class vd_interr_t(vd_failure_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, ea: ida_idaapi.ea_t, buf: str):
        _ida_hexrays_micro.vd_interr_t_swiginit(self, _ida_hexrays_micro.
            new_vd_interr_t(ea, buf))
    __swig_destroy__ = _ida_hexrays_micro.delete_vd_interr_t


_ida_hexrays_micro.vd_interr_t_swigregister(vd_interr_t)
m_nop = _ida_hexrays_micro.m_nop
m_stx = _ida_hexrays_micro.m_stx
m_ldx = _ida_hexrays_micro.m_ldx
m_ldc = _ida_hexrays_micro.m_ldc
m_mov = _ida_hexrays_micro.m_mov
m_neg = _ida_hexrays_micro.m_neg
m_lnot = _ida_hexrays_micro.m_lnot
m_bnot = _ida_hexrays_micro.m_bnot
m_xds = _ida_hexrays_micro.m_xds
m_xdu = _ida_hexrays_micro.m_xdu
m_low = _ida_hexrays_micro.m_low
m_high = _ida_hexrays_micro.m_high
m_add = _ida_hexrays_micro.m_add
m_sub = _ida_hexrays_micro.m_sub
m_mul = _ida_hexrays_micro.m_mul
m_udiv = _ida_hexrays_micro.m_udiv
m_sdiv = _ida_hexrays_micro.m_sdiv
m_umod = _ida_hexrays_micro.m_umod
m_smod = _ida_hexrays_micro.m_smod
m_or = _ida_hexrays_micro.m_or
m_and = _ida_hexrays_micro.m_and
m_xor = _ida_hexrays_micro.m_xor
m_shl = _ida_hexrays_micro.m_shl
m_shr = _ida_hexrays_micro.m_shr
m_sar = _ida_hexrays_micro.m_sar
m_cfadd = _ida_hexrays_micro.m_cfadd
m_ofadd = _ida_hexrays_micro.m_ofadd
m_cfshl = _ida_hexrays_micro.m_cfshl
m_cfshr = _ida_hexrays_micro.m_cfshr
m_sets = _ida_hexrays_micro.m_sets
m_seto = _ida_hexrays_micro.m_seto
m_setp = _ida_hexrays_micro.m_setp
m_setnz = _ida_hexrays_micro.m_setnz
m_setz = _ida_hexrays_micro.m_setz
m_setae = _ida_hexrays_micro.m_setae
m_setb = _ida_hexrays_micro.m_setb
m_seta = _ida_hexrays_micro.m_seta
m_setbe = _ida_hexrays_micro.m_setbe
m_setg = _ida_hexrays_micro.m_setg
m_setge = _ida_hexrays_micro.m_setge
m_setl = _ida_hexrays_micro.m_setl
m_setle = _ida_hexrays_micro.m_setle
m_jcnd = _ida_hexrays_micro.m_jcnd
m_jnz = _ida_hexrays_micro.m_jnz
m_jz = _ida_hexrays_micro.m_jz
m_jae = _ida_hexrays_micro.m_jae
m_jb = _ida_hexrays_micro.m_jb
m_ja = _ida_hexrays_micro.m_ja
m_jbe = _ida_hexrays_micro.m_jbe
m_jg = _ida_hexrays_micro.m_jg
m_jge = _ida_hexrays_micro.m_jge
m_jl = _ida_hexrays_micro.m_jl
m_jle = _ida_hexrays_micro.m_jle
m_jtbl = _ida_hexrays_micro.m_jtbl
m_ijmp = _ida_hexrays_micro.m_ijmp
m_goto = _ida_hexrays_micro.m_goto
m_call = _ida_hexrays_micro.m_call
m_icall = _ida_hexrays_micro.m_icall
m_ret = _ida_hexrays_micro.m_ret
m_push = _ida_hexrays_micro.m_push
m_pop = _ida_hexrays_micro.m_pop
m_und = _ida_hexrays_micro.m_und
m_ext = _ida_hexrays_micro.m_ext
m_f2i = _ida_hexrays_micro.m_f2i
m_f2u = _ida_hexrays_micro.m_f2u
m_i2f = _ida_hexrays_micro.m_i2f
m_u2f = _ida_hexrays_micro.m_u2f
m_f2f = _ida_hexrays_micro.m_f2f
m_fneg = _ida_hexrays_micro.m_fneg
m_fadd = _ida_hexrays_micro.m_fadd
m_fsub = _ida_hexrays_micro.m_fsub
m_fmul = _ida_hexrays_micro.m_fmul
m_fdiv = _ida_hexrays_micro.m_fdiv


def must_mcode_close_block(mcode: 'mcode_t', including_calls: bool) ->bool:
    """Must an instruction with the given opcode be the last one in a block? Such opcodes are called closing opcodes. 
        
:param mcode: instruction opcode
:param including_calls: should m_call/m_icall be considered as the closing opcodes? If this function returns true, the opcode cannot appear in the middle of a block. Calls are a special case: unknown calls (is_unknown_call) are considered as closing opcodes."""
    return _ida_hexrays_micro.must_mcode_close_block(mcode, including_calls)


def is_mcode_propagatable(mcode: 'mcode_t') ->bool:
    """May opcode be propagated? Such opcodes can be used in sub-instructions (nested instructions) There is a handful of non-propagatable opcodes, like jumps, ret, nop, etc All other regular opcodes are propagatable and may appear in a nested instruction. 
        """
    return _ida_hexrays_micro.is_mcode_propagatable(mcode)


def is_mcode_addsub(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_addsub(mcode)


def is_mcode_xdsu(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_xdsu(mcode)


def is_mcode_set(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_set(mcode)


def is_mcode_set1(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_set1(mcode)


def is_mcode_j1(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_j1(mcode)


def is_mcode_jcond(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_jcond(mcode)


def is_mcode_convertible_to_jmp(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_convertible_to_jmp(mcode)


def is_mcode_convertible_to_set(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_convertible_to_set(mcode)


def is_mcode_call(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_call(mcode)


def is_mcode_fpu(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_fpu(mcode)


def is_mcode_commutative(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_commutative(mcode)


def is_mcode_shift(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_shift(mcode)


def is_mcode_divmod(op: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_mcode_divmod(op)


def has_mcode_seloff(op: 'mcode_t') ->bool:
    return _ida_hexrays_micro.has_mcode_seloff(op)


def set2jcnd(code: 'mcode_t') ->'mcode_t':
    return _ida_hexrays_micro.set2jcnd(code)


def jcnd2set(code: 'mcode_t') ->'mcode_t':
    return _ida_hexrays_micro.jcnd2set(code)


def negate_mcode_relation(code: 'mcode_t') ->'mcode_t':
    return _ida_hexrays_micro.negate_mcode_relation(code)


def swap_mcode_relation(code: 'mcode_t') ->'mcode_t':
    return _ida_hexrays_micro.swap_mcode_relation(code)


def get_signed_mcode(code: 'mcode_t') ->'mcode_t':
    return _ida_hexrays_micro.get_signed_mcode(code)


def get_unsigned_mcode(code: 'mcode_t') ->'mcode_t':
    return _ida_hexrays_micro.get_unsigned_mcode(code)


def is_signed_mcode(code: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_signed_mcode(code)


def is_unsigned_mcode(code: 'mcode_t') ->bool:
    return _ida_hexrays_micro.is_unsigned_mcode(code)


def mcode_modifies_d(mcode: 'mcode_t') ->bool:
    return _ida_hexrays_micro.mcode_modifies_d(mcode)


def dstr(tif: 'tinfo_t') ->str:
    """Print the specified type info. This function can be used from a debugger by typing "tif->dstr()" 
        """
    return _ida_hexrays_micro.dstr(tif)


def is_type_correct(ptr: 'type_t const *') ->bool:
    """Verify a type string. 
        
:returns: true if type string is correct"""
    return _ida_hexrays_micro.is_type_correct(ptr)


def is_small_udt(tif: 'tinfo_t') ->bool:
    """Is a small structure or union? 
        
:returns: true if the type is a small UDT (user defined type). Small UDTs fit into a register (or pair or registers) as a rule."""
    return _ida_hexrays_micro.is_small_udt(tif)


def is_nonbool_type(type: 'tinfo_t') ->bool:
    """Is definitely a non-boolean type? 
        
:returns: true if the type is a non-boolean type (non bool and well defined)"""
    return _ida_hexrays_micro.is_nonbool_type(type)


def is_bool_type(type: 'tinfo_t') ->bool:
    """Is a boolean type? 
        
:returns: true if the type is a boolean type"""
    return _ida_hexrays_micro.is_bool_type(type)


def is_ptr_or_array(t: 'type_t') ->bool:
    """Is a pointer or array type?
"""
    return _ida_hexrays_micro.is_ptr_or_array(t)


def is_paf(t: 'type_t') ->bool:
    """Is a pointer, array, or function type?
"""
    return _ida_hexrays_micro.is_paf(t)


def is_inplace_def(type: 'tinfo_t') ->bool:
    """Is struct/union/enum definition (not declaration)?
"""
    return _ida_hexrays_micro.is_inplace_def(type)


def partial_type_num(type: 'tinfo_t') ->int:
    """Calculate number of partial subtypes. 
        
:returns: number of partial subtypes. The bigger is this number, the uglier is the type."""
    return _ida_hexrays_micro.partial_type_num(type)


def get_float_type(width: int) ->'tinfo_t':
    """Get a type of a floating point value with the specified width 
        
:param width: width of the desired type
:returns: type info object"""
    return _ida_hexrays_micro.get_float_type(width)


def get_int_type_by_width_and_sign(srcwidth: int, sign: 'type_sign_t'
    ) ->'tinfo_t':
    """Create a type info by width and sign. Returns a simple type (examples: int, short) with the given width and sign. 
        
:param srcwidth: size of the type in bytes
:param sign: sign of the type"""
    return _ida_hexrays_micro.get_int_type_by_width_and_sign(srcwidth, sign)


def get_unk_type(size: int) ->'tinfo_t':
    """Create a partial type info by width. Returns a partially defined type (examples: _DWORD, _BYTE) with the given width. 
        
:param size: size of the type in bytes"""
    return _ida_hexrays_micro.get_unk_type(size)


def dummy_ptrtype(ptrsize: int, isfp: bool) ->'tinfo_t':
    """Generate a dummy pointer type 
        
:param ptrsize: size of pointed object
:param isfp: is floating point object?"""
    return _ida_hexrays_micro.dummy_ptrtype(ptrsize, isfp)


def make_pointer(type: 'tinfo_t') ->'tinfo_t':
    """Create a pointer type. This function performs the following conversion: "type" -> "type*" 
        
:param type: object type.
:returns: "type*". for example, if 'char' is passed as the argument,"""
    return _ida_hexrays_micro.make_pointer(type)


def create_typedef(*args) ->'tinfo_t':
    """This function has the following signatures:

    0. create_typedef(name: str) -> tinfo_t
    1. create_typedef(n: int) -> tinfo_t

# 0: create_typedef(name: str) -> tinfo_t

Create a reference to a named type. 
        
:returns: type which refers to the specified name. For example, if name is "DWORD", the type info which refers to "DWORD" is created.

# 1: create_typedef(n: int) -> tinfo_t

Create a reference to an ordinal type. 
        
:returns: type which refers to the specified ordinal. For example, if n is 1, the type info which refers to ordinal type 1 is created.
"""
    return _ida_hexrays_micro.create_typedef(*args)


GUESSED_NONE = _ida_hexrays_micro.GUESSED_NONE
GUESSED_WEAK = _ida_hexrays_micro.GUESSED_WEAK
GUESSED_FUNC = _ida_hexrays_micro.GUESSED_FUNC
GUESSED_DATA = _ida_hexrays_micro.GUESSED_DATA
TS_NOELL = _ida_hexrays_micro.TS_NOELL
TS_SHRINK = _ida_hexrays_micro.TS_SHRINK
TS_DONTREF = _ida_hexrays_micro.TS_DONTREF
TS_MASK = _ida_hexrays_micro.TS_MASK


def get_type(id: int, tif: 'tinfo_t', guess: 'type_source_t') ->bool:
    """Get a global type. Global types are types of addressable objects and struct/union/enum types 
        
:param id: address or id of the object
:param tif: buffer for the answer
:param guess: what kind of types to consider
:returns: success"""
    return _ida_hexrays_micro.get_type(id, tif, guess)


def set_type(id: int, tif: 'tinfo_t', source: 'type_source_t', force: bool=
    False) ->bool:
    """Set a global type. 
        
:param id: address or id of the object
:param tif: new type info
:param source: where the type comes from
:param force: true means to set the type as is, false means to merge the new type with the possibly existing old type info.
:returns: success"""
    return _ida_hexrays_micro.set_type(id, tif, source, force)


class vdloc_t(ida_typeinf.argloc_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def reg1(self) ->int:
        return _ida_hexrays_micro.vdloc_t_reg1(self)

    def _set_reg1(self, r1: int) ->None:
        return _ida_hexrays_micro.vdloc_t__set_reg1(self, r1)

    def set_reg1(self, r1: int) ->None:
        return _ida_hexrays_micro.vdloc_t_set_reg1(self, r1)

    def __eq__(self, r: 'vdloc_t') ->bool:
        return _ida_hexrays_micro.vdloc_t___eq__(self, r)

    def __ne__(self, r: 'vdloc_t') ->bool:
        return _ida_hexrays_micro.vdloc_t___ne__(self, r)

    def __lt__(self, r: 'vdloc_t') ->bool:
        return _ida_hexrays_micro.vdloc_t___lt__(self, r)

    def __gt__(self, r: 'vdloc_t') ->bool:
        return _ida_hexrays_micro.vdloc_t___gt__(self, r)

    def __le__(self, r: 'vdloc_t') ->bool:
        return _ida_hexrays_micro.vdloc_t___le__(self, r)

    def __ge__(self, r: 'vdloc_t') ->bool:
        return _ida_hexrays_micro.vdloc_t___ge__(self, r)

    def compare(self, r: 'vdloc_t') ->int:
        return _ida_hexrays_micro.vdloc_t_compare(self, r)

    def is_aliasable(self, mb: 'mba_t', size: int) ->bool:
        return _ida_hexrays_micro.vdloc_t_is_aliasable(self, mb, size)

    def __init__(self):
        _ida_hexrays_micro.vdloc_t_swiginit(self, _ida_hexrays_micro.
            new_vdloc_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_vdloc_t


_ida_hexrays_micro.vdloc_t_swigregister(vdloc_t)
mr_none = cvar.mr_none
mr_cf = cvar.mr_cf
mr_zf = cvar.mr_zf
mr_sf = cvar.mr_sf
mr_of = cvar.mr_of
mr_pf = cvar.mr_pf
cc_count = cvar.cc_count
mr_cc = cvar.mr_cc
mr_first = cvar.mr_first


def print_vdloc(loc: 'vdloc_t', nbytes: int) ->str:
    """Print vdloc. Since vdloc does not always carry the size info, we pass it as NBYTES.. 
        """
    return _ida_hexrays_micro.print_vdloc(loc, nbytes)


def arglocs_overlap(loc1: 'vdloc_t', w1: int, loc2: 'vdloc_t', w2: int) ->bool:
    """Do two arglocs overlap?
"""
    return _ida_hexrays_micro.arglocs_overlap(loc1, w1, loc2, w2)


class lvar_locator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    location: 'vdloc_t' = property(_ida_hexrays_micro.
        lvar_locator_t_location_get, _ida_hexrays_micro.
        lvar_locator_t_location_set)
    """Variable location.
"""
    defea: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        lvar_locator_t_defea_get, _ida_hexrays_micro.lvar_locator_t_defea_set)
    """Definition address. Usually, this is the address of the instruction that initializes the variable. In some cases it can be a fictional address. 
        """

    def __init__(self, *args):
        _ida_hexrays_micro.lvar_locator_t_swiginit(self, _ida_hexrays_micro
            .new_lvar_locator_t(*args))

    def get_stkoff(self) ->int:
        """Get offset of the varialbe in the stack frame. 
        
:returns: a non-negative value for stack variables. The value is an offset from the bottom of the stack frame in terms of vd-offsets. negative values mean error (not a stack variable)"""
        return _ida_hexrays_micro.lvar_locator_t_get_stkoff(self)

    def is_reg1(self) ->bool:
        """Is variable located on one register?
"""
        return _ida_hexrays_micro.lvar_locator_t_is_reg1(self)

    def is_reg2(self) ->bool:
        """Is variable located on two registers?
"""
        return _ida_hexrays_micro.lvar_locator_t_is_reg2(self)

    def is_reg_var(self) ->bool:
        """Is variable located on register(s)?
"""
        return _ida_hexrays_micro.lvar_locator_t_is_reg_var(self)

    def is_stk_var(self) ->bool:
        """Is variable located on the stack?
"""
        return _ida_hexrays_micro.lvar_locator_t_is_stk_var(self)

    def is_scattered(self) ->bool:
        """Is variable scattered?
"""
        return _ida_hexrays_micro.lvar_locator_t_is_scattered(self)

    def get_reg1(self) ->'mreg_t':
        """Get the register number of the variable.
"""
        return _ida_hexrays_micro.lvar_locator_t_get_reg1(self)

    def get_reg2(self) ->'mreg_t':
        """Get the number of the second register (works only for ALOC_REG2 lvars)
"""
        return _ida_hexrays_micro.lvar_locator_t_get_reg2(self)

    def get_scattered(self) ->'scattered_aloc_t &':
        """Get information about scattered variable.
"""
        return _ida_hexrays_micro.lvar_locator_t_get_scattered(self)

    def __eq__(self, r: 'lvar_locator_t') ->bool:
        return _ida_hexrays_micro.lvar_locator_t___eq__(self, r)

    def __ne__(self, r: 'lvar_locator_t') ->bool:
        return _ida_hexrays_micro.lvar_locator_t___ne__(self, r)

    def __lt__(self, r: 'lvar_locator_t') ->bool:
        return _ida_hexrays_micro.lvar_locator_t___lt__(self, r)

    def __gt__(self, r: 'lvar_locator_t') ->bool:
        return _ida_hexrays_micro.lvar_locator_t___gt__(self, r)

    def __le__(self, r: 'lvar_locator_t') ->bool:
        return _ida_hexrays_micro.lvar_locator_t___le__(self, r)

    def __ge__(self, r: 'lvar_locator_t') ->bool:
        return _ida_hexrays_micro.lvar_locator_t___ge__(self, r)

    def compare(self, r: 'lvar_locator_t') ->int:
        return _ida_hexrays_micro.lvar_locator_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_micro.delete_lvar_locator_t


_ida_hexrays_micro.lvar_locator_t_swigregister(lvar_locator_t)


class lvar_t(lvar_locator_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined')
    __repr__ = _swig_repr
    name: str = property(_ida_hexrays_micro.lvar_t_name_get,
        _ida_hexrays_micro.lvar_t_name_set)
    """variable name. use mba_t::set_nice_lvar_name() and mba_t::set_user_lvar_name() to modify it 
        """
    cmt: str = property(_ida_hexrays_micro.lvar_t_cmt_get,
        _ida_hexrays_micro.lvar_t_cmt_set)
    """variable comment string
"""
    tif: 'tinfo_t' = property(_ida_hexrays_micro.lvar_t_tif_get,
        _ida_hexrays_micro.lvar_t_tif_set)
    """variable type
"""
    width: int = property(_ida_hexrays_micro.lvar_t_width_get,
        _ida_hexrays_micro.lvar_t_width_set)
    """variable size in bytes
"""
    defblk: int = property(_ida_hexrays_micro.lvar_t_defblk_get,
        _ida_hexrays_micro.lvar_t_defblk_set)
    """first block defining the variable. 0 for args, -1 if unknown 
        """
    divisor: 'uint64' = property(_ida_hexrays_micro.lvar_t_divisor_get,
        _ida_hexrays_micro.lvar_t_divisor_set)
    """max known divisor of the variable
"""

    def used(self) ->bool:
        """Is the variable used in the code?
"""
        return _ida_hexrays_micro.lvar_t_used(self)

    def typed(self) ->bool:
        """Has the variable a type?
"""
        return _ida_hexrays_micro.lvar_t_typed(self)

    def mreg_done(self) ->bool:
        """Have corresponding microregs been replaced by references to this variable?
"""
        return _ida_hexrays_micro.lvar_t_mreg_done(self)

    def has_nice_name(self) ->bool:
        """Does the variable have a nice name?
"""
        return _ida_hexrays_micro.lvar_t_has_nice_name(self)

    def is_unknown_width(self) ->bool:
        """Do we know the width of the variable?
"""
        return _ida_hexrays_micro.lvar_t_is_unknown_width(self)

    def has_user_info(self) ->bool:
        """Has any user-defined information?
"""
        return _ida_hexrays_micro.lvar_t_has_user_info(self)

    def has_user_name(self) ->bool:
        """Has user-defined name?
"""
        return _ida_hexrays_micro.lvar_t_has_user_name(self)

    def has_user_type(self) ->bool:
        """Has user-defined type?
"""
        return _ida_hexrays_micro.lvar_t_has_user_type(self)

    def is_result_var(self) ->bool:
        """Is the function result?
"""
        return _ida_hexrays_micro.lvar_t_is_result_var(self)

    def is_arg_var(self) ->bool:
        """Is the function argument?
"""
        return _ida_hexrays_micro.lvar_t_is_arg_var(self)

    def is_fake_var(self) ->bool:
        """Is fake return variable?
"""
        return _ida_hexrays_micro.lvar_t_is_fake_var(self)

    def is_overlapped_var(self) ->bool:
        """Is overlapped variable?
"""
        return _ida_hexrays_micro.lvar_t_is_overlapped_var(self)

    def is_floating_var(self) ->bool:
        """Used by a fpu insn?
"""
        return _ida_hexrays_micro.lvar_t_is_floating_var(self)

    def is_spoiled_var(self) ->bool:
        """Is spoiled var? (meaningful only during lvar allocation)
"""
        return _ida_hexrays_micro.lvar_t_is_spoiled_var(self)

    def is_noptr_var(self) ->bool:
        """Variable type should not be a pointer.
"""
        return _ida_hexrays_micro.lvar_t_is_noptr_var(self)

    def is_mapdst_var(self) ->bool:
        """Other variable(s) map to this var?
"""
        return _ida_hexrays_micro.lvar_t_is_mapdst_var(self)

    def is_thisarg(self) ->bool:
        """Is 'this' argument of a C++ member function?
"""
        return _ida_hexrays_micro.lvar_t_is_thisarg(self)

    def is_split_var(self) ->bool:
        """Is a split variable?
"""
        return _ida_hexrays_micro.lvar_t_is_split_var(self)

    def has_regname(self) ->bool:
        """Has a register name? (like _RAX)
"""
        return _ida_hexrays_micro.lvar_t_has_regname(self)

    def in_asm(self) ->bool:
        """Is variable used in an instruction translated into __asm?
"""
        return _ida_hexrays_micro.lvar_t_in_asm(self)

    def is_dummy_arg(self) ->bool:
        """Is a dummy argument (added to fill a hole in the argument list)
"""
        return _ida_hexrays_micro.lvar_t_is_dummy_arg(self)

    def is_notarg(self) ->bool:
        """Is a local variable? (local variable cannot be an input argument)
"""
        return _ida_hexrays_micro.lvar_t_is_notarg(self)

    def is_automapped(self) ->bool:
        """Was the variable automatically mapped to another variable?
"""
        return _ida_hexrays_micro.lvar_t_is_automapped(self)

    def is_used_byref(self) ->bool:
        """Was the address of the variable taken?
"""
        return _ida_hexrays_micro.lvar_t_is_used_byref(self)

    def is_decl_unused(self) ->bool:
        """Was declared as __unused by the user? See CVAR_UNUSED.
"""
        return _ida_hexrays_micro.lvar_t_is_decl_unused(self)

    def is_shared(self) ->bool:
        """Is lvar mapped to several chains.
"""
        return _ida_hexrays_micro.lvar_t_is_shared(self)

    def was_scattered_arg(self) ->bool:
        """Was lvar transformed from a scattered argument?
"""
        return _ida_hexrays_micro.lvar_t_was_scattered_arg(self)

    def is_noprop(self) ->bool:
        """Is it forbidden to propagate the variable?
"""
        return _ida_hexrays_micro.lvar_t_is_noprop(self)

    def set_used(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_used(self)

    def clear_used(self) ->None:
        return _ida_hexrays_micro.lvar_t_clear_used(self)

    def set_typed(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_typed(self)

    def set_non_typed(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_non_typed(self)

    def clr_user_info(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_user_info(self)

    def set_user_name(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_user_name(self)

    def set_user_type(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_user_type(self)

    def clr_user_type(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_user_type(self)

    def clr_user_name(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_user_name(self)

    def set_mreg_done(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_mreg_done(self)

    def clr_mreg_done(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_mreg_done(self)

    def set_unknown_width(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_unknown_width(self)

    def clr_unknown_width(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_unknown_width(self)

    def set_arg_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_arg_var(self)

    def clr_arg_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_arg_var(self)

    def set_fake_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_fake_var(self)

    def clr_fake_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_fake_var(self)

    def set_overlapped_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_overlapped_var(self)

    def clr_overlapped_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_overlapped_var(self)

    def set_floating_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_floating_var(self)

    def clr_floating_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_floating_var(self)

    def set_spoiled_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_spoiled_var(self)

    def clr_spoiled_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_spoiled_var(self)

    def set_mapdst_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_mapdst_var(self)

    def clr_mapdst_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_mapdst_var(self)

    def set_noptr_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_noptr_var(self)

    def clr_noptr_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_noptr_var(self)

    def set_thisarg(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_thisarg(self)

    def clr_thisarg(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_thisarg(self)

    def set_split_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_split_var(self)

    def clr_split_var(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_split_var(self)

    def set_dummy_arg(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_dummy_arg(self)

    def clr_dummy_arg(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_dummy_arg(self)

    def set_notarg(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_notarg(self)

    def clr_notarg(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_notarg(self)

    def set_automapped(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_automapped(self)

    def clr_automapped(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_automapped(self)

    def set_used_byref(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_used_byref(self)

    def clr_used_byref(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_used_byref(self)

    def set_decl_unused(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_decl_unused(self)

    def clr_decl_unused(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_decl_unused(self)

    def set_shared(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_shared(self)

    def clr_shared(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_shared(self)

    def set_scattered_arg(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_scattered_arg(self)

    def clr_scattered_arg(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_scattered_arg(self)

    def set_noprop(self) ->None:
        return _ida_hexrays_micro.lvar_t_set_noprop(self)

    def clr_noprop(self) ->None:
        return _ida_hexrays_micro.lvar_t_clr_noprop(self)

    def has_common(self, v: 'lvar_t') ->bool:
        """Do variables overlap?
"""
        return _ida_hexrays_micro.lvar_t_has_common(self, v)

    def has_common_bit(self, loc: 'vdloc_t', width2: 'asize_t') ->bool:
        """Does the variable overlap with the specified location?
"""
        return _ida_hexrays_micro.lvar_t_has_common_bit(self, loc, width2)

    def type(self) ->'tinfo_t &':
        """Get variable type.
"""
        return _ida_hexrays_micro.lvar_t_type(self)

    def accepts_type(self, t: 'tinfo_t', may_change_thisarg: bool=False
        ) ->bool:
        """Check if the variable accept the specified type. Some types are forbidden (void, function types, wrong arrays, etc) 
        """
        return _ida_hexrays_micro.lvar_t_accepts_type(self, t,
            may_change_thisarg)

    def set_lvar_type(self, t: 'tinfo_t', may_fail: bool=False) ->bool:
        """Set variable type Note: this function does not modify the idb, only the lvar instance in the memory. For permanent changes see modify_user_lvars() Also, the variable type is not considered as final by the decompiler and may be modified later by the type derivation. In some cases set_final_var_type() may work better, but it does not do persistent changes to the database neither. 
        
:param t: new type
:param may_fail: if false and type is bad, interr
:returns: success"""
        return _ida_hexrays_micro.lvar_t_set_lvar_type(self, t, may_fail)

    def set_final_lvar_type(self, t: 'tinfo_t') ->None:
        """Set final variable type.
"""
        return _ida_hexrays_micro.lvar_t_set_final_lvar_type(self, t)

    def set_width(self, w: int, svw_flags: int=0) ->bool:
        """Change the variable width. We call the variable size 'width', it is represents the number of bytes. This function may change the variable type using set_lvar_type(). 
        
:param w: new width
:param svw_flags: combination of SVW_... bits
:returns: success"""
        return _ida_hexrays_micro.lvar_t_set_width(self, w, svw_flags)

    def append_list(self, mba: 'mba_t', lst: 'mlist_t', pad_if_scattered:
        bool=False) ->None:
        """Append local variable to mlist. 
        
:param mba: ptr to the current mba_t
:param lst: list to append to
:param pad_if_scattered: if true, append padding bytes in case of scattered lvar"""
        return _ida_hexrays_micro.lvar_t_append_list(self, mba, lst,
            pad_if_scattered)

    def is_aliasable(self, mba: 'mba_t') ->bool:
        """Is the variable aliasable? 
        
:param mba: ptr to the current mba_t Aliasable variables may be modified indirectly (through a pointer)"""
        return _ida_hexrays_micro.lvar_t_is_aliasable(self, mba)
    __swig_destroy__ = _ida_hexrays_micro.delete_lvar_t


_ida_hexrays_micro.lvar_t_swigregister(lvar_t)
SVW_INT = _ida_hexrays_micro.SVW_INT
SVW_FLOAT = _ida_hexrays_micro.SVW_FLOAT
SVW_SOFT = _ida_hexrays_micro.SVW_SOFT


class lvars_t(qvector_lvar_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def find_input_lvar(self, argloc: 'vdloc_t', _size: int) ->int:
        """Find an input variable at the specified location. 
        
:param argloc: variable location
:param _size: variable size in bytes
:returns: -1 if failed, otherwise an index into 'vars'"""
        return _ida_hexrays_micro.lvars_t_find_input_lvar(self, argloc, _size)

    def find_input_reg(self, reg: int, _size: int=1) ->int:
        """Find an input register variable. 
        
:param reg: register to find
:param _size: variable size in bytes
:returns: -1 if failed, otherwise an index into 'vars'"""
        return _ida_hexrays_micro.lvars_t_find_input_reg(self, reg, _size)

    def find_stkvar(self, spoff: int, width: int) ->int:
        """Find a stack variable at the specified location. 
        
:param spoff: offset from the minimal sp
:param width: variable size in bytes
:returns: -1 if failed, otherwise an index into 'vars'"""
        return _ida_hexrays_micro.lvars_t_find_stkvar(self, spoff, width)

    def find(self, ll: 'lvar_locator_t') ->'lvar_t *':
        """Find a variable at the specified location. 
        
:param ll: variable location
:returns: pointer to variable or nullptr"""
        return _ida_hexrays_micro.lvars_t_find(self, ll)

    def find_lvar(self, location: 'vdloc_t', width: int, defblk: int=-1) ->int:
        """Find a variable at the specified location. 
        
:param location: variable location
:param width: variable size in bytes
:param defblk: definition block of the lvar. -1 means any block
:returns: -1 if failed, otherwise an index into 'vars'"""
        return _ida_hexrays_micro.lvars_t_find_lvar(self, location, width,
            defblk)

    def __init__(self):
        _ida_hexrays_micro.lvars_t_swiginit(self, _ida_hexrays_micro.
            new_lvars_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_lvars_t


_ida_hexrays_micro.lvars_t_swigregister(lvars_t)


class lvar_saved_info_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ll: 'lvar_locator_t' = property(_ida_hexrays_micro.
        lvar_saved_info_t_ll_get, _ida_hexrays_micro.lvar_saved_info_t_ll_set)
    """Variable locator.
"""
    name: str = property(_ida_hexrays_micro.lvar_saved_info_t_name_get,
        _ida_hexrays_micro.lvar_saved_info_t_name_set)
    """Name.
"""
    type: 'tinfo_t' = property(_ida_hexrays_micro.
        lvar_saved_info_t_type_get, _ida_hexrays_micro.
        lvar_saved_info_t_type_set)
    """Type.
"""
    cmt: str = property(_ida_hexrays_micro.lvar_saved_info_t_cmt_get,
        _ida_hexrays_micro.lvar_saved_info_t_cmt_set)
    """Comment.
"""
    size: 'ssize_t' = property(_ida_hexrays_micro.
        lvar_saved_info_t_size_get, _ida_hexrays_micro.
        lvar_saved_info_t_size_set)
    """Type size (if not initialized then -1)
"""
    flags: int = property(_ida_hexrays_micro.lvar_saved_info_t_flags_get,
        _ida_hexrays_micro.lvar_saved_info_t_flags_set)
    """saved user lvar info property bits 
        """

    def has_info(self) ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t_has_info(self)

    def __eq__(self, r: 'lvar_saved_info_t') ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t___eq__(self, r)

    def __ne__(self, r: 'lvar_saved_info_t') ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t___ne__(self, r)

    def is_kept(self) ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t_is_kept(self)

    def clear_keep(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_clear_keep(self)

    def set_keep(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_set_keep(self)

    def is_split_lvar(self) ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t_is_split_lvar(self)

    def set_split_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_set_split_lvar(self)

    def clr_split_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_clr_split_lvar(self)

    def is_noptr_lvar(self) ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t_is_noptr_lvar(self)

    def set_noptr_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_set_noptr_lvar(self)

    def clr_noptr_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_clr_noptr_lvar(self)

    def is_nomap_lvar(self) ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t_is_nomap_lvar(self)

    def set_nomap_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_set_nomap_lvar(self)

    def clr_nomap_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_clr_nomap_lvar(self)

    def is_unused_lvar(self) ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t_is_unused_lvar(self)

    def set_unused_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_set_unused_lvar(self)

    def clr_unused_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_clr_unused_lvar(self)

    def is_noprop_lvar(self) ->bool:
        return _ida_hexrays_micro.lvar_saved_info_t_is_noprop_lvar(self)

    def set_noprop_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_set_noprop_lvar(self)

    def clr_noprop_lvar(self) ->None:
        return _ida_hexrays_micro.lvar_saved_info_t_clr_noprop_lvar(self)

    def __init__(self):
        _ida_hexrays_micro.lvar_saved_info_t_swiginit(self,
            _ida_hexrays_micro.new_lvar_saved_info_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_lvar_saved_info_t


_ida_hexrays_micro.lvar_saved_info_t_swigregister(lvar_saved_info_t)
LVINF_KEEP = _ida_hexrays_micro.LVINF_KEEP
"""preserve saved user settings regardless of vars for example, if a var loses all its user-defined attributes or even gets destroyed, keep its lvar_saved_info_t. this is used for ephemeral variables that get destroyed by macro recognition. 
        """
LVINF_SPLIT = _ida_hexrays_micro.LVINF_SPLIT
"""split allocation of a new variable. forces the decompiler to create a new variable at ll.defea 
        """
LVINF_NOPTR = _ida_hexrays_micro.LVINF_NOPTR
"""variable type should not be a pointer
"""
LVINF_NOMAP = _ida_hexrays_micro.LVINF_NOMAP
"""forbid automatic mapping of the variable
"""
LVINF_UNUSED = _ida_hexrays_micro.LVINF_UNUSED
"""unused argument, corresponds to CVAR_UNUSED
"""
LVINF_NOPROP = _ida_hexrays_micro.LVINF_NOPROP
"""don't propagate assignments to this lvar (CVAR_NOPROP)
"""


class lvar_uservec_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    lvvec: 'lvar_saved_infos_t' = property(_ida_hexrays_micro.
        lvar_uservec_t_lvvec_get, _ida_hexrays_micro.lvar_uservec_t_lvvec_set)
    """User-specified names, types, comments for lvars. Variables without user-specified info are not present in this vector. 
        """
    lmaps: 'lvar_mapping_t' = property(_ida_hexrays_micro.
        lvar_uservec_t_lmaps_get, _ida_hexrays_micro.lvar_uservec_t_lmaps_set)
    """Local variable mapping (used for merging variables)
"""
    stkoff_delta: int = property(_ida_hexrays_micro.
        lvar_uservec_t_stkoff_delta_get, _ida_hexrays_micro.
        lvar_uservec_t_stkoff_delta_set)
    """Delta to add to IDA stack offset to calculate Hex-Rays stack offsets. Should be set by the caller before calling save_user_lvar_settings(); 
        """
    ulv_flags: int = property(_ida_hexrays_micro.
        lvar_uservec_t_ulv_flags_get, _ida_hexrays_micro.
        lvar_uservec_t_ulv_flags_set)
    """Various flags. Possible values are from lvar_uservec_t property bits.
"""

    def swap(self, r: 'lvar_uservec_t') ->None:
        return _ida_hexrays_micro.lvar_uservec_t_swap(self, r)

    def clear(self) ->None:
        return _ida_hexrays_micro.lvar_uservec_t_clear(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.lvar_uservec_t_empty(self)

    def find_info(self, vloc: 'lvar_locator_t') ->'lvar_saved_info_t *':
        """find saved user settings for given var
"""
        return _ida_hexrays_micro.lvar_uservec_t_find_info(self, vloc)

    def keep_info(self, v: 'lvar_t') ->None:
        """Preserve user settings for given var.
"""
        return _ida_hexrays_micro.lvar_uservec_t_keep_info(self, v)

    def __init__(self):
        _ida_hexrays_micro.lvar_uservec_t_swiginit(self, _ida_hexrays_micro
            .new_lvar_uservec_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_lvar_uservec_t


_ida_hexrays_micro.lvar_uservec_t_swigregister(lvar_uservec_t)
ULV_PRECISE_DEFEA = _ida_hexrays_micro.ULV_PRECISE_DEFEA
"""Use precise defea's for lvar locations.
"""


def restore_user_lvar_settings(lvinf: 'lvar_uservec_t', func_ea:
    ida_idaapi.ea_t) ->bool:
    """Restore user defined local variable settings in the database. 
        
:param lvinf: ptr to output buffer
:param func_ea: entry address of the function
:returns: success"""
    return _ida_hexrays_micro.restore_user_lvar_settings(lvinf, func_ea)


def save_user_lvar_settings(func_ea: ida_idaapi.ea_t, lvinf: 'lvar_uservec_t'
    ) ->None:
    """Save user defined local variable settings into the database. 
        
:param func_ea: entry address of the function
:param lvinf: user-specified info about local variables"""
    return _ida_hexrays_micro.save_user_lvar_settings(func_ea, lvinf)


class user_lvar_modifier_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    __swig_destroy__ = _ida_hexrays_micro.delete_user_lvar_modifier_t

    def modify_lvars(self, lvinf: 'lvar_uservec_t') ->bool:
        """Modify lvar settings. Returns: true-modified 
        """
        return _ida_hexrays_micro.user_lvar_modifier_t_modify_lvars(self, lvinf
            )

    def __init__(self):
        if self.__class__ == user_lvar_modifier_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.user_lvar_modifier_t_swiginit(self,
            _ida_hexrays_micro.new_user_lvar_modifier_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_user_lvar_modifier_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.user_lvar_modifier_t_swigregister(user_lvar_modifier_t)


def modify_user_lvars(entry_ea: ida_idaapi.ea_t, mlv: 'user_lvar_modifier_t'
    ) ->bool:
    """Modify saved local variable settings. 
        
:param entry_ea: function start address
:param mlv: local variable modifier
:returns: true if modified variables"""
    return _ida_hexrays_micro.modify_user_lvars(entry_ea, mlv)


def modify_user_lvar_info(func_ea: ida_idaapi.ea_t, mli_flags: 'uint', info:
    'lvar_saved_info_t') ->bool:
    """Modify saved local variable settings of one variable. 
        
:param func_ea: function start address
:param mli_flags: bits that specify which attrs defined by INFO are to be set
:param info: local variable info attrs
:returns: true if modified, false if invalid MLI_FLAGS passed"""
    return _ida_hexrays_micro.modify_user_lvar_info(func_ea, mli_flags, info)


MLI_NAME = _ida_hexrays_micro.MLI_NAME
"""apply lvar name
"""
MLI_TYPE = _ida_hexrays_micro.MLI_TYPE
"""apply lvar type
"""
MLI_CMT = _ida_hexrays_micro.MLI_CMT
"""apply lvar comment
"""
MLI_SET_FLAGS = _ida_hexrays_micro.MLI_SET_FLAGS
"""set LVINF_... bits
"""
MLI_CLR_FLAGS = _ida_hexrays_micro.MLI_CLR_FLAGS
"""clear LVINF_... bits
"""


def locate_lvar(out: 'lvar_locator_t', func_ea: ida_idaapi.ea_t, varname: str
    ) ->bool:
    """Find a variable by name. 
        
:param out: output buffer for the variable locator
:param func_ea: function start address
:param varname: variable name
:returns: success Since VARNAME is not always enough to find the variable, it may decompile the function."""
    return _ida_hexrays_micro.locate_lvar(out, func_ea, varname)


def rename_lvar(func_ea: ida_idaapi.ea_t, oldname: str, newname: str) ->bool:
    """Rename a local variable. 
        
:param func_ea: function start address
:param oldname: old name of the variable
:param newname: new name of the variable
:returns: success This is a convenience function. For bulk renaming consider using modify_user_lvars."""
    return _ida_hexrays_micro.rename_lvar(func_ea, oldname, newname)


class udcall_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    name: str = property(_ida_hexrays_micro.udcall_t_name_get,
        _ida_hexrays_micro.udcall_t_name_set)
    tif: 'tinfo_t' = property(_ida_hexrays_micro.udcall_t_tif_get,
        _ida_hexrays_micro.udcall_t_tif_set)

    def __eq__(self, r: 'udcall_t') ->bool:
        return _ida_hexrays_micro.udcall_t___eq__(self, r)

    def __ne__(self, r: 'udcall_t') ->bool:
        return _ida_hexrays_micro.udcall_t___ne__(self, r)

    def __lt__(self, r: 'udcall_t') ->bool:
        return _ida_hexrays_micro.udcall_t___lt__(self, r)

    def __gt__(self, r: 'udcall_t') ->bool:
        return _ida_hexrays_micro.udcall_t___gt__(self, r)

    def __le__(self, r: 'udcall_t') ->bool:
        return _ida_hexrays_micro.udcall_t___le__(self, r)

    def __ge__(self, r: 'udcall_t') ->bool:
        return _ida_hexrays_micro.udcall_t___ge__(self, r)

    def compare(self, r: 'udcall_t') ->int:
        return _ida_hexrays_micro.udcall_t_compare(self, r)

    def empty(self) ->bool:
        return _ida_hexrays_micro.udcall_t_empty(self)

    def __init__(self):
        _ida_hexrays_micro.udcall_t_swiginit(self, _ida_hexrays_micro.
            new_udcall_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_udcall_t


_ida_hexrays_micro.udcall_t_swigregister(udcall_t)


def restore_user_defined_calls(udcalls: 'udcall_map_t *', func_ea:
    ida_idaapi.ea_t) ->bool:
    """Restore user defined function calls from the database. 
        
:param udcalls: ptr to output buffer
:param func_ea: entry address of the function
:returns: success"""
    return _ida_hexrays_micro.restore_user_defined_calls(udcalls, func_ea)


def save_user_defined_calls(func_ea: ida_idaapi.ea_t, udcalls:
    'udcall_map_t const &') ->None:
    """Save user defined local function calls into the database. 
        
:param func_ea: entry address of the function
:param udcalls: user-specified info about user defined function calls"""
    return _ida_hexrays_micro.save_user_defined_calls(func_ea, udcalls)


def parse_user_call(udc: 'udcall_t', decl: str, silent: bool) ->bool:
    """Convert function type declaration into internal structure 
        
:param udc: - pointer to output structure
:param decl: - function type declaration
:param silent: - if TRUE: do not show warning in case of incorrect type
:returns: success"""
    return _ida_hexrays_micro.parse_user_call(udc, decl, silent)


def convert_to_user_call(udc: 'udcall_t', cdg: 'codegen_t') ->'merror_t':
    """try to generate user-defined call for an instruction 
        
:returns: Microcode error code code: MERR_OK - user-defined call generated else - error (MERR_INSN == inacceptable udc.tif)"""
    return _ida_hexrays_micro.convert_to_user_call(udc, cdg)


class microcode_filter_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    __swig_destroy__ = _ida_hexrays_micro.delete_microcode_filter_t

    def match(self, cdg: 'codegen_t') ->bool:
        """check if the filter object is to be applied 
        
:returns: success"""
        return _ida_hexrays_micro.microcode_filter_t_match(self, cdg)

    def apply(self, cdg: 'codegen_t') ->'merror_t':
        """generate microcode for an instruction 
        
:returns: MERR_... code: MERR_OK - user-defined microcode generated, go to the next instruction MERR_INSN - not generated - the caller should try the standard way else - error"""
        return _ida_hexrays_micro.microcode_filter_t_apply(self, cdg)

    def __init__(self):
        if self.__class__ == microcode_filter_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.microcode_filter_t_swiginit(self,
            _ida_hexrays_micro.new_microcode_filter_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_microcode_filter_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.microcode_filter_t_swigregister(microcode_filter_t)


def install_microcode_filter(filter: 'microcode_filter_t', install: bool=True
    ) ->bool:
    """register/unregister non-standard microcode generator 
        
:param filter: - microcode generator object
:param install: - TRUE - register the object, FALSE - unregister
:returns: success"""
    return _ida_hexrays_micro.install_microcode_filter(filter, install)


class udc_filter_t(microcode_filter_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def cleanup(self) ->None:
        """Cleanup the filter This function properly clears type information associated to this filter. 
        """
        return _ida_hexrays_micro.udc_filter_t_cleanup(self)

    def match(self, cdg: 'codegen_t') ->bool:
        """return true if the filter object should be applied to given instruction
"""
        return _ida_hexrays_micro.udc_filter_t_match(self, cdg)

    def apply(self, cdg: 'codegen_t') ->'merror_t':
        """generate microcode for an instruction 
        
:returns: MERR_... code: MERR_OK - user-defined microcode generated, go to the next instruction MERR_INSN - not generated - the caller should try the standard way else - error"""
        return _ida_hexrays_micro.udc_filter_t_apply(self, cdg)

    def empty(self) ->bool:
        return _ida_hexrays_micro.udc_filter_t_empty(self)

    def install(self) ->None:
        return _ida_hexrays_micro.udc_filter_t_install(self)

    def remove(self) ->bool:
        return _ida_hexrays_micro.udc_filter_t_remove(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_udc_filter_t

    def init(self, decl: str) ->bool:
        return _ida_hexrays_micro.udc_filter_t_init(self, decl)

    def __init__(self):
        if self.__class__ == udc_filter_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.udc_filter_t_swiginit(self, _ida_hexrays_micro.
            new_udc_filter_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_udc_filter_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.udc_filter_t_swigregister(udc_filter_t)


class bitset_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.bitset_t_swiginit(self, _ida_hexrays_micro.
            new_bitset_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_bitset_t

    def swap(self, r: 'bitset_t') ->None:
        return _ida_hexrays_micro.bitset_t_swap(self, r)

    def copy(self, m: 'bitset_t') ->'bitset_t &':
        return _ida_hexrays_micro.bitset_t_copy(self, m)

    def add(self, *args) ->bool:
        """This function has the following signatures:

    0. add(bit: int) -> bool
    1. add(bit: int, width: int) -> bool
    2. add(ml: const bitset_t &) -> bool

# 0: add(bit: int) -> bool


# 1: add(bit: int, width: int) -> bool


# 2: add(ml: const bitset_t &) -> bool

"""
        return _ida_hexrays_micro.bitset_t_add(self, *args)

    def sub(self, *args) ->bool:
        """This function has the following signatures:

    0. sub(bit: int) -> bool
    1. sub(bit: int, width: int) -> bool
    2. sub(ml: const bitset_t &) -> bool

# 0: sub(bit: int) -> bool


# 1: sub(bit: int, width: int) -> bool


# 2: sub(ml: const bitset_t &) -> bool

"""
        return _ida_hexrays_micro.bitset_t_sub(self, *args)

    def cut_at(self, maxbit: int) ->bool:
        return _ida_hexrays_micro.bitset_t_cut_at(self, maxbit)

    def shift_down(self, shift: int) ->None:
        return _ida_hexrays_micro.bitset_t_shift_down(self, shift)

    def has(self, bit: int) ->bool:
        return _ida_hexrays_micro.bitset_t_has(self, bit)

    def has_all(self, bit: int, width: int) ->bool:
        return _ida_hexrays_micro.bitset_t_has_all(self, bit, width)

    def has_any(self, bit: int, width: int) ->bool:
        return _ida_hexrays_micro.bitset_t_has_any(self, bit, width)

    def dstr(self) ->str:
        return _ida_hexrays_micro.bitset_t_dstr(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.bitset_t_empty(self)

    def count(self, *args) ->int:
        """This function has the following signatures:

    0. count() -> int
    1. count(bit: int) -> int

# 0: count() -> int


# 1: count(bit: int) -> int

"""
        return _ida_hexrays_micro.bitset_t_count(self, *args)

    def last(self) ->int:
        return _ida_hexrays_micro.bitset_t_last(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.bitset_t_clear(self)

    def fill_with_ones(self, maxbit: int) ->None:
        return _ida_hexrays_micro.bitset_t_fill_with_ones(self, maxbit)

    def has_common(self, ml: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t_has_common(self, ml)

    def intersect(self, ml: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t_intersect(self, ml)

    def is_subset_of(self, ml: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t_is_subset_of(self, ml)

    def includes(self, ml: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t_includes(self, ml)

    def __eq__(self, r: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t___eq__(self, r)

    def __ne__(self, r: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t___ne__(self, r)

    def __lt__(self, r: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t___lt__(self, r)

    def __gt__(self, r: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t___gt__(self, r)

    def __le__(self, r: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t___le__(self, r)

    def __ge__(self, r: 'bitset_t') ->bool:
        return _ida_hexrays_micro.bitset_t___ge__(self, r)

    def compare(self, r: 'bitset_t') ->int:
        return _ida_hexrays_micro.bitset_t_compare(self, r)

    def itat(self, n: int) ->'bitset_t::iterator':
        return _ida_hexrays_micro.bitset_t_itat(self, n)

    def begin(self) ->'bitset_t::iterator':
        return _ida_hexrays_micro.bitset_t_begin(self)

    def end(self) ->'bitset_t::iterator':
        return _ida_hexrays_micro.bitset_t_end(self)

    def front(self) ->int:
        return _ida_hexrays_micro.bitset_t_front(self)

    def back(self) ->int:
        return _ida_hexrays_micro.bitset_t_back(self)

    def inc(self, p: 'iterator', n: int=1) ->None:
        return _ida_hexrays_micro.bitset_t_inc(self, p, n)

    def itv(self, it: 'iterator') ->int:
        return _ida_hexrays_micro.bitset_t_itv(self, it)
    __len__ = count

    def __iter__(self):
        it = self.begin()
        for i in range(self.count()):
            yield self.itv(it)
            self.inc(it)


_ida_hexrays_micro.bitset_t_swigregister(bitset_t)
bitset_width = cvar.bitset_width
bitset_align = cvar.bitset_align
bitset_shift = cvar.bitset_shift


class iterator(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, n: int=-1):
        _ida_hexrays_micro.iterator_swiginit(self, _ida_hexrays_micro.
            new_iterator(n))

    def __eq__(self, n: 'iterator') ->bool:
        return _ida_hexrays_micro.iterator___eq__(self, n)

    def __ne__(self, n: 'iterator') ->bool:
        return _ida_hexrays_micro.iterator___ne__(self, n)

    def __ref__(self) ->int:
        return _ida_hexrays_micro.iterator___ref__(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_iterator


_ida_hexrays_micro.iterator_swigregister(iterator)


class node_bitset_t(bitset_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.node_bitset_t_swiginit(self, _ida_hexrays_micro.
            new_node_bitset_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_node_bitset_t


_ida_hexrays_micro.node_bitset_t_swigregister(node_bitset_t)


class array_of_node_bitset_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self):
        _ida_hexrays_micro.array_of_node_bitset_t_swiginit(self,
            _ida_hexrays_micro.new_array_of_node_bitset_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_array_of_node_bitset_t


_ida_hexrays_micro.array_of_node_bitset_t_swigregister(array_of_node_bitset_t)


class ivl_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    off: 'uint64' = property(_ida_hexrays_micro.ivl_t_off_get,
        _ida_hexrays_micro.ivl_t_off_set)
    size: 'uint64' = property(_ida_hexrays_micro.ivl_t_size_get,
        _ida_hexrays_micro.ivl_t_size_set)

    def __init__(self, _off: 'uint64'=0, _size: 'uint64'=0):
        _ida_hexrays_micro.ivl_t_swiginit(self, _ida_hexrays_micro.
            new_ivl_t(_off, _size))

    def empty(self) ->bool:
        return _ida_hexrays_micro.ivl_t_empty(self)

    def valid(self) ->bool:
        return _ida_hexrays_micro.ivl_t_valid(self)

    def end(self) ->'uint64':
        return _ida_hexrays_micro.ivl_t_end(self)

    def last(self) ->'uint64':
        return _ida_hexrays_micro.ivl_t_last(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.ivl_t_clear(self)

    def dstr(self) ->str:
        return _ida_hexrays_micro.ivl_t_dstr(self)

    def extend_to_cover(self, r: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t_extend_to_cover(self, r)

    def intersect(self, r: 'ivl_t') ->None:
        return _ida_hexrays_micro.ivl_t_intersect(self, r)

    def overlap(self, ivl: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t_overlap(self, ivl)

    def includes(self, ivl: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t_includes(self, ivl)

    def contains(self, off2: 'uint64') ->bool:
        return _ida_hexrays_micro.ivl_t_contains(self, off2)

    def __eq__(self, r: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t___eq__(self, r)

    def __ne__(self, r: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t___ne__(self, r)

    def __lt__(self, r: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t___lt__(self, r)

    def __gt__(self, r: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t___gt__(self, r)

    def __le__(self, r: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t___le__(self, r)

    def __ge__(self, r: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivl_t___ge__(self, r)

    def compare(self, r: 'ivl_t') ->int:
        return _ida_hexrays_micro.ivl_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_micro.delete_ivl_t


_ida_hexrays_micro.ivl_t_swigregister(ivl_t)


class ivl_with_name_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ivl: 'ivl_t' = property(_ida_hexrays_micro.ivl_with_name_t_ivl_get,
        _ida_hexrays_micro.ivl_with_name_t_ivl_set)
    whole: str = property(_ida_hexrays_micro.ivl_with_name_t_whole_get,
        _ida_hexrays_micro.ivl_with_name_t_whole_set)
    part: str = property(_ida_hexrays_micro.ivl_with_name_t_part_get,
        _ida_hexrays_micro.ivl_with_name_t_part_set)

    def __init__(self):
        _ida_hexrays_micro.ivl_with_name_t_swiginit(self,
            _ida_hexrays_micro.new_ivl_with_name_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_ivl_with_name_t


_ida_hexrays_micro.ivl_with_name_t_swigregister(ivl_with_name_t)


class ivlset_visitor_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def visit_ivl(self, ivl: 'ivl_t') ->int:
        return _ida_hexrays_micro.ivlset_visitor_t_visit_ivl(self, ivl)

    def __init__(self):
        if self.__class__ == ivlset_visitor_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.ivlset_visitor_t_swiginit(self,
            _ida_hexrays_micro.new_ivlset_visitor_t(_self))
    __swig_destroy__ = _ida_hexrays_micro.delete_ivlset_visitor_t

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_ivlset_visitor_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.ivlset_visitor_t_swigregister(ivlset_visitor_t)


class ivlset_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.ivlset_t_swiginit(self, _ida_hexrays_micro.
            new_ivlset_t(*args))

    def swap(self, r: 'ivlset_t') ->None:
        return _ida_hexrays_micro.ivlset_t_swap(self, r)

    def getivl(self, idx: int) ->'ivl_t const &':
        return _ida_hexrays_micro.ivlset_t_getivl(self, idx)

    def lastivl(self) ->'ivl_t const &':
        return _ida_hexrays_micro.ivlset_t_lastivl(self)

    def nivls(self) ->int:
        return _ida_hexrays_micro.ivlset_t_nivls(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.ivlset_t_empty(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.ivlset_t_clear(self)

    def qclear(self) ->None:
        return _ida_hexrays_micro.ivlset_t_qclear(self)

    def all_values(self) ->bool:
        return _ida_hexrays_micro.ivlset_t_all_values(self)

    def set_all_values(self) ->None:
        return _ida_hexrays_micro.ivlset_t_set_all_values(self)

    def single_value(self, *args) ->bool:
        """This function has the following signatures:

    0. single_value() -> bool
    1. single_value(v: uint64) -> bool

# 0: single_value() -> bool


# 1: single_value(v: uint64) -> bool

"""
        return _ida_hexrays_micro.ivlset_t_single_value(self, *args)

    def add(self, *args) ->bool:
        """This function has the following signatures:

    0. add(ivl: const ivl_t &) -> bool
    1. add(ea: ida_idaapi.ea_t, size: asize_t) -> bool
    2. add(ivs: const ivlset_t &) -> bool

# 0: add(ivl: const ivl_t &) -> bool


# 1: add(ea: ida_idaapi.ea_t, size: asize_t) -> bool


# 2: add(ivs: const ivlset_t &) -> bool

"""
        return _ida_hexrays_micro.ivlset_t_add(self, *args)

    def addmasked(self, ivs: 'ivlset_t', mask: 'ivl_t') ->bool:
        return _ida_hexrays_micro.ivlset_t_addmasked(self, ivs, mask)

    def sub(self, *args) ->bool:
        """This function has the following signatures:

    0. sub(ivl: const ivl_t &) -> bool
    1. sub(ea: ida_idaapi.ea_t, size: asize_t) -> bool
    2. sub(ivs: const ivlset_t &) -> bool

# 0: sub(ivl: const ivl_t &) -> bool


# 1: sub(ea: ida_idaapi.ea_t, size: asize_t) -> bool


# 2: sub(ivs: const ivlset_t &) -> bool

"""
        return _ida_hexrays_micro.ivlset_t_sub(self, *args)

    def count(self) ->'asize_t':
        return _ida_hexrays_micro.ivlset_t_count(self)

    def has_common(self, *args) ->bool:
        """This function has the following signatures:

    0. has_common(ivs: const ivlset_t &) -> bool
    1. has_common(ivl: const ivl_t &, strict: bool=false) -> bool

# 0: has_common(ivs: const ivlset_t &) -> bool


# 1: has_common(ivl: const ivl_t &, strict: bool=false) -> bool

"""
        return _ida_hexrays_micro.ivlset_t_has_common(self, *args)

    def contains(self, off: 'uint64') ->bool:
        return _ida_hexrays_micro.ivlset_t_contains(self, off)

    def includes(self, ivs: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.ivlset_t_includes(self, ivs)

    def intersect(self, ivs: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.ivlset_t_intersect(self, ivs)

    def is_subset_of(self, ivs: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.ivlset_t_is_subset_of(self, ivs)

    def __lt__(self, r: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.ivlset_t___lt__(self, r)

    def __gt__(self, r: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.ivlset_t___gt__(self, r)

    def __le__(self, r: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.ivlset_t___le__(self, r)

    def __ge__(self, r: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.ivlset_t___ge__(self, r)

    def compare(self, r: 'ivlset_t') ->int:
        return _ida_hexrays_micro.ivlset_t_compare(self, r)

    def __eq__(self, *args) ->bool:
        return _ida_hexrays_micro.ivlset_t___eq__(self, *args)

    def __ne__(self, *args) ->bool:
        return _ida_hexrays_micro.ivlset_t___ne__(self, *args)

    def begin(self, *args) ->'ivlset_t::iterator':
        """This function has the following signatures:

    0. begin() -> const_iterator
    1. begin() -> iterator

# 0: begin() -> const_iterator


# 1: begin() -> iterator

"""
        return _ida_hexrays_micro.ivlset_t_begin(self, *args)

    def end(self, *args) ->'ivlset_t::iterator':
        """This function has the following signatures:

    0. end() -> const_iterator
    1. end() -> iterator

# 0: end() -> const_iterator


# 1: end() -> iterator

"""
        return _ida_hexrays_micro.ivlset_t_end(self, *args)

    def _print(self) ->None:
        return _ida_hexrays_micro.ivlset_t__print(self)

    def dstr(self) ->str:
        return _ida_hexrays_micro.ivlset_t_dstr(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_ivlset_t


_ida_hexrays_micro.ivlset_t_swigregister(ivlset_t)


class rlist_t(bitset_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.rlist_t_swiginit(self, _ida_hexrays_micro.
            new_rlist_t(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_rlist_t

    def dstr(self) ->str:
        return _ida_hexrays_micro.rlist_t_dstr(self)


_ida_hexrays_micro.rlist_t_swigregister(rlist_t)


class mlist_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    reg: 'rlist_t' = property(_ida_hexrays_micro.mlist_t_reg_get,
        _ida_hexrays_micro.mlist_t_reg_set)
    mem: 'ivlset_t' = property(_ida_hexrays_micro.mlist_t_mem_get,
        _ida_hexrays_micro.mlist_t_mem_set)

    def __init__(self, *args):
        _ida_hexrays_micro.mlist_t_swiginit(self, _ida_hexrays_micro.
            new_mlist_t(*args))

    def swap(self, r: 'mlist_t') ->None:
        return _ida_hexrays_micro.mlist_t_swap(self, r)

    def addmem(self, ea: ida_idaapi.ea_t, size: 'asize_t') ->bool:
        return _ida_hexrays_micro.mlist_t_addmem(self, ea, size)

    def add(self, *args) ->bool:
        """This function has the following signatures:

    0. add(r: mreg_t, size: int) -> bool
    1. add(r: const rlist_t &) -> bool
    2. add(ivl: const ivl_t &) -> bool
    3. add(lst: const mlist_t &) -> bool

# 0: add(r: mreg_t, size: int) -> bool


# 1: add(r: const rlist_t &) -> bool


# 2: add(ivl: const ivl_t &) -> bool


# 3: add(lst: const mlist_t &) -> bool

"""
        return _ida_hexrays_micro.mlist_t_add(self, *args)

    def sub(self, *args) ->bool:
        """This function has the following signatures:

    0. sub(r: mreg_t, size: int) -> bool
    1. sub(ivl: const ivl_t &) -> bool
    2. sub(lst: const mlist_t &) -> bool

# 0: sub(r: mreg_t, size: int) -> bool


# 1: sub(ivl: const ivl_t &) -> bool


# 2: sub(lst: const mlist_t &) -> bool

"""
        return _ida_hexrays_micro.mlist_t_sub(self, *args)

    def count(self) ->'asize_t':
        return _ida_hexrays_micro.mlist_t_count(self)

    def _print(self) ->None:
        return _ida_hexrays_micro.mlist_t__print(self)

    def dstr(self) ->str:
        return _ida_hexrays_micro.mlist_t_dstr(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.mlist_t_empty(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.mlist_t_clear(self)

    def has(self, r: 'mreg_t') ->bool:
        return _ida_hexrays_micro.mlist_t_has(self, r)

    def has_all(self, r: 'mreg_t', size: int) ->bool:
        return _ida_hexrays_micro.mlist_t_has_all(self, r, size)

    def has_any(self, r: 'mreg_t', size: int) ->bool:
        return _ida_hexrays_micro.mlist_t_has_any(self, r, size)

    def has_memory(self) ->bool:
        return _ida_hexrays_micro.mlist_t_has_memory(self)

    def has_common(self, lst: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t_has_common(self, lst)

    def includes(self, lst: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t_includes(self, lst)

    def intersect(self, lst: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t_intersect(self, lst)

    def is_subset_of(self, lst: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t_is_subset_of(self, lst)

    def __eq__(self, r: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t___eq__(self, r)

    def __ne__(self, r: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t___ne__(self, r)

    def __lt__(self, r: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t___lt__(self, r)

    def __gt__(self, r: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t___gt__(self, r)

    def __le__(self, r: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t___le__(self, r)

    def __ge__(self, r: 'mlist_t') ->bool:
        return _ida_hexrays_micro.mlist_t___ge__(self, r)

    def compare(self, r: 'mlist_t') ->int:
        return _ida_hexrays_micro.mlist_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_micro.delete_mlist_t


_ida_hexrays_micro.mlist_t_swigregister(mlist_t)


def is_may_access(maymust: 'maymust_t') ->bool:
    return _ida_hexrays_micro.is_may_access(maymust)


def get_temp_regs() ->'mlist_t const &':
    """Get list of temporary registers. Tempregs are temporary registers that are used during code generation. They do not map to regular processor registers. They are used only to store temporary values during execution of one instruction. Tempregs may not be used to pass a value from one block to another. In other words, at the end of a block all tempregs must be dead. 
        """
    return _ida_hexrays_micro.get_temp_regs()


def is_kreg(r: 'mreg_t') ->bool:
    """Is a kernel register? Kernel registers are temporary registers that can be used freely. They may be used to store values that cross instruction or basic block boundaries. Kernel registers do not map to regular processor registers. See also mba_t::alloc_kreg() 
        """
    return _ida_hexrays_micro.is_kreg(r)


def reg2mreg(reg: int) ->'mreg_t':
    """Map a processor register to a microregister. 
        
:param reg: processor register number
:returns: microregister register id or mr_none"""
    return _ida_hexrays_micro.reg2mreg(reg)


def mreg2reg(reg: 'mreg_t', width: int) ->int:
    """Map a microregister to a processor register. 
        
:param reg: microregister number
:param width: size of microregister in bytes
:returns: processor register id or -1"""
    return _ida_hexrays_micro.mreg2reg(reg, width)


def get_mreg_name(reg: 'mreg_t', width: int, ud: 'void *'=None) ->str:
    """Get the microregister name. 
        
:param reg: microregister number
:param width: size of microregister in bytes. may be bigger than the real register size.
:param ud: reserved, must be nullptr
:returns: width of the printed register. this value may be less than the WIDTH argument."""
    return _ida_hexrays_micro.get_mreg_name(reg, width, ud)


class optinsn_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def func(self, blk: 'mblock_t', ins: 'minsn_t', optflags: int) ->int:
        """Optimize an instruction. 
        
:param blk: current basic block. maybe nullptr, which means that the instruction must be optimized without context
:param ins: instruction to optimize; it is always a top-level instruction. the callback may not delete the instruction but may convert it into nop (see mblock_t::make_nop). to optimize sub-instructions, visit them using minsn_visitor_t. sub-instructions may not be converted into nop but can be converted to "mov x,x". for example: add x,0,x => mov x,x this callback may change other instructions in the block, but should do this with care, e.g. to no break the propagation algorithm if called with OPTI_NO_LDXOPT.
:param optflags: combination of optimization flags bits
:returns: number of changes made to the instruction. if after this call the instruction's use/def lists have changed, you must mark the block level lists as dirty (see mark_lists_dirty)"""
        return _ida_hexrays_micro.optinsn_t_func(self, blk, ins, optflags)

    def install(self) ->None:
        return _ida_hexrays_micro.optinsn_t_install(self)

    def remove(self) ->bool:
        return _ida_hexrays_micro.optinsn_t_remove(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_optinsn_t

    def __init__(self):
        if self.__class__ == optinsn_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.optinsn_t_swiginit(self, _ida_hexrays_micro.
            new_optinsn_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_optinsn_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.optinsn_t_swigregister(optinsn_t)
MUST_ACCESS = cvar.MUST_ACCESS
MAY_ACCESS = cvar.MAY_ACCESS
MAYMUST_ACCESS_MASK = cvar.MAYMUST_ACCESS_MASK
ONE_ACCESS_TYPE = cvar.ONE_ACCESS_TYPE
INCLUDE_SPOILED_REGS = cvar.INCLUDE_SPOILED_REGS
EXCLUDE_PASS_REGS = cvar.EXCLUDE_PASS_REGS
FULL_XDSU = cvar.FULL_XDSU
WITH_ASSERTS = cvar.WITH_ASSERTS
EXCLUDE_VOLATILE = cvar.EXCLUDE_VOLATILE
INCLUDE_UNUSED_SRC = cvar.INCLUDE_UNUSED_SRC
INCLUDE_DEAD_RETREGS = cvar.INCLUDE_DEAD_RETREGS
INCLUDE_RESTRICTED = cvar.INCLUDE_RESTRICTED
CALL_SPOILS_ONLY_ARGS = cvar.CALL_SPOILS_ONLY_ARGS


class optblock_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def func(self, blk: 'mblock_t') ->int:
        """Optimize a block. This function usually performs the optimizations that require analyzing the entire block and/or its neighbors. For example it can recognize patterns and perform conversions like: b0: b0: ... ... jnz x, 0, @b2 => jnz x, 0, @b2 b1: b1: add x, 0, y mov x, y ... ... 
        
:param blk: Basic block to optimize as a whole.
:returns: number of changes made to the block. See also mark_lists_dirty."""
        return _ida_hexrays_micro.optblock_t_func(self, blk)

    def install(self) ->None:
        return _ida_hexrays_micro.optblock_t_install(self)

    def remove(self) ->bool:
        return _ida_hexrays_micro.optblock_t_remove(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_optblock_t

    def __init__(self):
        if self.__class__ == optblock_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.optblock_t_swiginit(self, _ida_hexrays_micro.
            new_optblock_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_optblock_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.optblock_t_swigregister(optblock_t)


class simple_graph_t(ida_gdl.gdl_graph_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined - class is abstract')
    __repr__ = _swig_repr
    title: str = property(_ida_hexrays_micro.simple_graph_t_title_get,
        _ida_hexrays_micro.simple_graph_t_title_set)
    colored_gdl_edges: bool = property(_ida_hexrays_micro.
        simple_graph_t_colored_gdl_edges_get, _ida_hexrays_micro.
        simple_graph_t_colored_gdl_edges_set)

    def compute_dominators(self, domin: 'array_of_node_bitset_t', post:
        bool=False) ->None:
        return _ida_hexrays_micro.simple_graph_t_compute_dominators(self,
            domin, post)

    def compute_immediate_dominators(self, domin: 'array_of_node_bitset_t',
        idomin: 'intvec_t', post: bool=False) ->None:
        return _ida_hexrays_micro.simple_graph_t_compute_immediate_dominators(
            self, domin, idomin, post)

    def depth_first_preorder(self, pre: 'node_ordering_t') ->int:
        return _ida_hexrays_micro.simple_graph_t_depth_first_preorder(self, pre
            )

    def depth_first_postorder(self, post: 'node_ordering_t') ->int:
        return _ida_hexrays_micro.simple_graph_t_depth_first_postorder(self,
            post)

    def begin(self) ->'simple_graph_t::iterator':
        return _ida_hexrays_micro.simple_graph_t_begin(self)

    def end(self) ->'simple_graph_t::iterator':
        return _ida_hexrays_micro.simple_graph_t_end(self)

    def front(self) ->int:
        return _ida_hexrays_micro.simple_graph_t_front(self)

    def inc(self, p: 'simple_graph_t::iterator &', n: int=1) ->None:
        return _ida_hexrays_micro.simple_graph_t_inc(self, p, n)

    def goup(self, node: int) ->int:
        return _ida_hexrays_micro.simple_graph_t_goup(self, node)


_ida_hexrays_micro.simple_graph_t_swigregister(simple_graph_t)


class op_parent_info_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    mba: 'mba_t *' = property(_ida_hexrays_micro.op_parent_info_t_mba_get,
        _ida_hexrays_micro.op_parent_info_t_mba_set)
    blk: 'mblock_t *' = property(_ida_hexrays_micro.
        op_parent_info_t_blk_get, _ida_hexrays_micro.op_parent_info_t_blk_set)
    topins: 'minsn_t *' = property(_ida_hexrays_micro.
        op_parent_info_t_topins_get, _ida_hexrays_micro.
        op_parent_info_t_topins_set)
    curins: 'minsn_t *' = property(_ida_hexrays_micro.
        op_parent_info_t_curins_get, _ida_hexrays_micro.
        op_parent_info_t_curins_set)

    def __init__(self, _mba: 'mba_t'=None, _blk: 'mblock_t'=None, _topins:
        'minsn_t'=None):
        if self.__class__ == op_parent_info_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.op_parent_info_t_swiginit(self,
            _ida_hexrays_micro.new_op_parent_info_t(_self, _mba, _blk, _topins)
            )
    __swig_destroy__ = _ida_hexrays_micro.delete_op_parent_info_t

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_op_parent_info_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.op_parent_info_t_swigregister(op_parent_info_t)


class minsn_visitor_t(op_parent_info_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, _mba: 'mba_t'=None, _blk: 'mblock_t'=None, _topins:
        'minsn_t'=None):
        if self.__class__ == minsn_visitor_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.minsn_visitor_t_swiginit(self,
            _ida_hexrays_micro.new_minsn_visitor_t(_self, _mba, _blk, _topins))

    def visit_minsn(self) ->int:
        return _ida_hexrays_micro.minsn_visitor_t_visit_minsn(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_minsn_visitor_t

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_minsn_visitor_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.minsn_visitor_t_swigregister(minsn_visitor_t)


class mop_visitor_t(op_parent_info_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    prune: bool = property(_ida_hexrays_micro.mop_visitor_t_prune_get,
        _ida_hexrays_micro.mop_visitor_t_prune_set)
    """Should skip sub-operands of the current operand? visit_mop() may set 'prune=true' for that. 
        """

    def __init__(self, _mba: 'mba_t'=None, _blk: 'mblock_t'=None, _topins:
        'minsn_t'=None):
        if self.__class__ == mop_visitor_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.mop_visitor_t_swiginit(self, _ida_hexrays_micro.
            new_mop_visitor_t(_self, _mba, _blk, _topins))

    def visit_mop(self, op: 'mop_t', type: 'tinfo_t', is_target: bool) ->int:
        return _ida_hexrays_micro.mop_visitor_t_visit_mop(self, op, type,
            is_target)
    __swig_destroy__ = _ida_hexrays_micro.delete_mop_visitor_t

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_mop_visitor_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.mop_visitor_t_swigregister(mop_visitor_t)


class scif_visitor_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    __swig_destroy__ = _ida_hexrays_micro.delete_scif_visitor_t

    def visit_scif_mop(self, r: 'mop_t', off: int) ->int:
        return _ida_hexrays_micro.scif_visitor_t_visit_scif_mop(self, r, off)

    def __init__(self):
        if self.__class__ == scif_visitor_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.scif_visitor_t_swiginit(self, _ida_hexrays_micro
            .new_scif_visitor_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_scif_visitor_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.scif_visitor_t_swigregister(scif_visitor_t)


class mlist_mop_visitor_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    topins: 'minsn_t *' = property(_ida_hexrays_micro.
        mlist_mop_visitor_t_topins_get, _ida_hexrays_micro.
        mlist_mop_visitor_t_topins_set)
    curins: 'minsn_t *' = property(_ida_hexrays_micro.
        mlist_mop_visitor_t_curins_get, _ida_hexrays_micro.
        mlist_mop_visitor_t_curins_set)
    changed: bool = property(_ida_hexrays_micro.
        mlist_mop_visitor_t_changed_get, _ida_hexrays_micro.
        mlist_mop_visitor_t_changed_set)
    list: 'mlist_t *' = property(_ida_hexrays_micro.
        mlist_mop_visitor_t_list_get, _ida_hexrays_micro.
        mlist_mop_visitor_t_list_set)
    prune: bool = property(_ida_hexrays_micro.mlist_mop_visitor_t_prune_get,
        _ida_hexrays_micro.mlist_mop_visitor_t_prune_set)
    """Should skip sub-operands of the current operand? visit_mop() may set 'prune=true' for that. 
        """
    __swig_destroy__ = _ida_hexrays_micro.delete_mlist_mop_visitor_t

    def visit_mop(self, op: 'mop_t') ->int:
        return _ida_hexrays_micro.mlist_mop_visitor_t_visit_mop(self, op)

    def __init__(self):
        if self.__class__ == mlist_mop_visitor_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.mlist_mop_visitor_t_swiginit(self,
            _ida_hexrays_micro.new_mlist_mop_visitor_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_mlist_mop_visitor_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.mlist_mop_visitor_t_swigregister(mlist_mop_visitor_t)


class lvar_ref_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    mba: 'mba_t *const' = property(_ida_hexrays_micro.lvar_ref_t_mba_get)
    """Pointer to the parent mba_t object. Since we need to access the 'mba->vars' array in order to retrieve the referenced variable, we keep a pointer to mba_t here. Note: this means this class and consequently mop_t, minsn_t, mblock_t are specific to a mba_t object and cannot migrate between them. fortunately this is not something we need to do. second, lvar_ref_t's appear only after MMAT_LVARS. 
        """
    off: int = property(_ida_hexrays_micro.lvar_ref_t_off_get,
        _ida_hexrays_micro.lvar_ref_t_off_set)
    """offset from the beginning of the variable
"""
    idx: int = property(_ida_hexrays_micro.lvar_ref_t_idx_get,
        _ida_hexrays_micro.lvar_ref_t_idx_set)
    """index into mba->vars
"""

    def __init__(self, *args):
        _ida_hexrays_micro.lvar_ref_t_swiginit(self, _ida_hexrays_micro.
            new_lvar_ref_t(*args))

    def __eq__(self, r: 'lvar_ref_t') ->bool:
        return _ida_hexrays_micro.lvar_ref_t___eq__(self, r)

    def __ne__(self, r: 'lvar_ref_t') ->bool:
        return _ida_hexrays_micro.lvar_ref_t___ne__(self, r)

    def __lt__(self, r: 'lvar_ref_t') ->bool:
        return _ida_hexrays_micro.lvar_ref_t___lt__(self, r)

    def __gt__(self, r: 'lvar_ref_t') ->bool:
        return _ida_hexrays_micro.lvar_ref_t___gt__(self, r)

    def __le__(self, r: 'lvar_ref_t') ->bool:
        return _ida_hexrays_micro.lvar_ref_t___le__(self, r)

    def __ge__(self, r: 'lvar_ref_t') ->bool:
        return _ida_hexrays_micro.lvar_ref_t___ge__(self, r)

    def compare(self, r: 'lvar_ref_t') ->int:
        return _ida_hexrays_micro.lvar_ref_t_compare(self, r)

    def swap(self, r: 'lvar_ref_t') ->None:
        return _ida_hexrays_micro.lvar_ref_t_swap(self, r)

    def var(self) ->'lvar_t &':
        """Retrieve the referenced variable.
"""
        return _ida_hexrays_micro.lvar_ref_t_var(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_lvar_ref_t


_ida_hexrays_micro.lvar_ref_t_swigregister(lvar_ref_t)
mop_z = cvar.mop_z
"""none
"""
mop_r = cvar.mop_r
"""register (they exist until MMAT_LVARS)
"""
mop_n = cvar.mop_n
"""immediate number constant
"""
mop_str = cvar.mop_str
"""immediate string constant (user representation)
"""
mop_d = cvar.mop_d
"""result of another instruction
"""
mop_S = cvar.mop_S
"""local stack variable (they exist until MMAT_LVARS)
"""
mop_v = cvar.mop_v
"""global variable
"""
mop_b = cvar.mop_b
"""micro basic block (mblock_t)
"""
mop_f = cvar.mop_f
"""list of arguments
"""
mop_l = cvar.mop_l
"""local variable
"""
mop_a = cvar.mop_a
"""mop_addr_t: address of operand (mop_l, mop_v, mop_S, mop_r)
"""
mop_h = cvar.mop_h
"""helper function
"""
mop_c = cvar.mop_c
"""mcases
"""
mop_fn = cvar.mop_fn
"""floating point constant
"""
mop_p = cvar.mop_p
"""operand pair
"""
mop_sc = cvar.mop_sc
"""scattered
"""
NOSIZE = cvar.NOSIZE
"""wrong or unexisting operand size
"""


class stkvar_ref_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    mba: 'mba_t *const' = property(_ida_hexrays_micro.stkvar_ref_t_mba_get)
    """Pointer to the parent mba_t object. We need it in order to retrieve the referenced stack variable. See notes for lvar_ref_t::mba. 
        """
    off: int = property(_ida_hexrays_micro.stkvar_ref_t_off_get,
        _ida_hexrays_micro.stkvar_ref_t_off_set)
    """Offset to the stack variable from the bottom of the stack frame. It is called 'decompiler stkoff' and it is different from IDA stkoff. See a note and a picture about 'decompiler stkoff' below. 
        """

    def __init__(self, m: 'mba_t', o: int):
        _ida_hexrays_micro.stkvar_ref_t_swiginit(self, _ida_hexrays_micro.
            new_stkvar_ref_t(m, o))

    def __eq__(self, r: 'stkvar_ref_t') ->bool:
        return _ida_hexrays_micro.stkvar_ref_t___eq__(self, r)

    def __ne__(self, r: 'stkvar_ref_t') ->bool:
        return _ida_hexrays_micro.stkvar_ref_t___ne__(self, r)

    def __lt__(self, r: 'stkvar_ref_t') ->bool:
        return _ida_hexrays_micro.stkvar_ref_t___lt__(self, r)

    def __gt__(self, r: 'stkvar_ref_t') ->bool:
        return _ida_hexrays_micro.stkvar_ref_t___gt__(self, r)

    def __le__(self, r: 'stkvar_ref_t') ->bool:
        return _ida_hexrays_micro.stkvar_ref_t___le__(self, r)

    def __ge__(self, r: 'stkvar_ref_t') ->bool:
        return _ida_hexrays_micro.stkvar_ref_t___ge__(self, r)

    def compare(self, r: 'stkvar_ref_t') ->int:
        return _ida_hexrays_micro.stkvar_ref_t_compare(self, r)

    def swap(self, r: 'stkvar_ref_t') ->None:
        return _ida_hexrays_micro.stkvar_ref_t_swap(self, r)

    def get_stkvar(self, udm: 'udm_t'=None, p_idaoff: 'uval_t *'=None
        ) ->'ssize_t':
        """Retrieve the referenced stack variable. 
        
:param udm: stkvar, may be nullptr
:param p_idaoff: if specified, will hold IDA stkoff after the call.
:returns: index of stkvar in the frame or -1"""
        return _ida_hexrays_micro.stkvar_ref_t_get_stkvar(self, udm, p_idaoff)
    __swig_destroy__ = _ida_hexrays_micro.delete_stkvar_ref_t


_ida_hexrays_micro.stkvar_ref_t_swigregister(stkvar_ref_t)


class scif_t(vdloc_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    mba: 'mba_t *' = property(_ida_hexrays_micro.scif_t_mba_get,
        _ida_hexrays_micro.scif_t_mba_set)
    """Pointer to the parent mba_t object. Some operations may convert a scattered operand into something simpler, (a stack operand, for example). We will need to create stkvar_ref_t at that moment, this is why we need this pointer. See notes for lvar_ref_t::mba. 
        """
    name: str = property(_ida_hexrays_micro.scif_t_name_get,
        _ida_hexrays_micro.scif_t_name_set)
    """Usually scattered operands are created from a function prototype, which has the name information. We preserve it and use it to name the corresponding local variable. 
        """
    type: 'tinfo_t' = property(_ida_hexrays_micro.scif_t_type_get,
        _ida_hexrays_micro.scif_t_type_set)
    """Scattered operands always have type info assigned to them because without it we won't be able to manipulte them. 
        """

    def __init__(self, _mba: 'mba_t', tif: 'tinfo_t', n: str=None):
        _ida_hexrays_micro.scif_t_swiginit(self, _ida_hexrays_micro.
            new_scif_t(_mba, tif, n))
    __swig_destroy__ = _ida_hexrays_micro.delete_scif_t


_ida_hexrays_micro.scif_t_swigregister(scif_t)


class mnumber_t(ida_hexrays_defs.operand_locator_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    value: 'uint64' = property(_ida_hexrays_micro.mnumber_t_value_get,
        _ida_hexrays_micro.mnumber_t_value_set)
    org_value: 'uint64' = property(_ida_hexrays_micro.
        mnumber_t_org_value_get, _ida_hexrays_micro.mnumber_t_org_value_set)

    def __init__(self, *args):
        _ida_hexrays_micro.mnumber_t_swiginit(self, _ida_hexrays_micro.
            new_mnumber_t(*args))

    def __eq__(self, r: 'mnumber_t') ->bool:
        return _ida_hexrays_micro.mnumber_t___eq__(self, r)

    def __ne__(self, r: 'mnumber_t') ->bool:
        return _ida_hexrays_micro.mnumber_t___ne__(self, r)

    def __lt__(self, r: 'mnumber_t') ->bool:
        return _ida_hexrays_micro.mnumber_t___lt__(self, r)

    def __gt__(self, r: 'mnumber_t') ->bool:
        return _ida_hexrays_micro.mnumber_t___gt__(self, r)

    def __le__(self, r: 'mnumber_t') ->bool:
        return _ida_hexrays_micro.mnumber_t___le__(self, r)

    def __ge__(self, r: 'mnumber_t') ->bool:
        return _ida_hexrays_micro.mnumber_t___ge__(self, r)

    def compare(self, r: 'mnumber_t') ->int:
        return _ida_hexrays_micro.mnumber_t_compare(self, r)

    def update_value(self, val64: 'uint64') ->None:
        return _ida_hexrays_micro.mnumber_t_update_value(self, val64)
    __swig_destroy__ = _ida_hexrays_micro.delete_mnumber_t


_ida_hexrays_micro.mnumber_t_swigregister(mnumber_t)


class fnumber_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    fnum: 'fpvalue_t' = property(_ida_hexrays_micro.fnumber_t_fnum_get,
        _ida_hexrays_micro.fnumber_t_fnum_set)
    """Internal representation of the number.
"""
    nbytes: int = property(_ida_hexrays_micro.fnumber_t_nbytes_get,
        _ida_hexrays_micro.fnumber_t_nbytes_set)
    """Original size of the constant in bytes.
"""

    def dereference_uint16(self) ->'uint16 *':
        return _ida_hexrays_micro.fnumber_t_dereference_uint16(self)

    def dereference_const_uint16(self) ->'uint16 const *':
        return _ida_hexrays_micro.fnumber_t_dereference_const_uint16(self)

    def _print(self) ->None:
        return _ida_hexrays_micro.fnumber_t__print(self)

    def __eq__(self, r: 'fnumber_t') ->bool:
        return _ida_hexrays_micro.fnumber_t___eq__(self, r)

    def __ne__(self, r: 'fnumber_t') ->bool:
        return _ida_hexrays_micro.fnumber_t___ne__(self, r)

    def __lt__(self, r: 'fnumber_t') ->bool:
        return _ida_hexrays_micro.fnumber_t___lt__(self, r)

    def __gt__(self, r: 'fnumber_t') ->bool:
        return _ida_hexrays_micro.fnumber_t___gt__(self, r)

    def __le__(self, r: 'fnumber_t') ->bool:
        return _ida_hexrays_micro.fnumber_t___le__(self, r)

    def __ge__(self, r: 'fnumber_t') ->bool:
        return _ida_hexrays_micro.fnumber_t___ge__(self, r)

    def compare(self, r: 'fnumber_t') ->int:
        return _ida_hexrays_micro.fnumber_t_compare(self, r)

    def calc_max_exp(self) ->int:
        return _ida_hexrays_micro.fnumber_t_calc_max_exp(self)

    def is_nan(self) ->bool:
        return _ida_hexrays_micro.fnumber_t_is_nan(self)

    def __init__(self):
        _ida_hexrays_micro.fnumber_t_swiginit(self, _ida_hexrays_micro.
            new_fnumber_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_fnumber_t


_ida_hexrays_micro.fnumber_t_swigregister(fnumber_t)
SHINS_NUMADDR = _ida_hexrays_micro.SHINS_NUMADDR
"""display definition addresses for numbers
"""
SHINS_VALNUM = _ida_hexrays_micro.SHINS_VALNUM
"""display value numbers
"""
SHINS_SHORT = _ida_hexrays_micro.SHINS_SHORT
"""do not display use-def chains and other attrs
"""
SHINS_LDXEA = _ida_hexrays_micro.SHINS_LDXEA
"""display address of ldx expressions (not used)
"""
NO_SIDEFF = _ida_hexrays_micro.NO_SIDEFF
"""change operand size but ignore side effects if you decide to keep the changed operand, handle_new_size() must be called 
          """
WITH_SIDEFF = _ida_hexrays_micro.WITH_SIDEFF
"""change operand size and handle side effects
"""
ONLY_SIDEFF = _ida_hexrays_micro.ONLY_SIDEFF
"""only handle side effects
"""
ANY_REGSIZE = _ida_hexrays_micro.ANY_REGSIZE
"""any register size is permitted
"""
ANY_FPSIZE = _ida_hexrays_micro.ANY_FPSIZE
"""any size of floating operand is permitted
"""


class mop_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    t: 'mopt_t' = property(_ida_hexrays_micro.mop_t_t_get,
        _ida_hexrays_micro.mop_t_t_set)
    """Operand type.
"""
    oprops: 'uint8' = property(_ida_hexrays_micro.mop_t_oprops_get,
        _ida_hexrays_micro.mop_t_oprops_set)
    """Operand properties.
"""
    valnum: 'uint16' = property(_ida_hexrays_micro.mop_t_valnum_get,
        _ida_hexrays_micro.mop_t_valnum_set)
    """Value number. Zero means unknown. Operands with the same value number are equal. 
        """
    size: int = property(_ida_hexrays_micro.mop_t_size_get,
        _ida_hexrays_micro.mop_t_size_set)
    """Operand size. Usually it is 1,2,4,8 or NOSIZE but for UDTs other sizes are permitted 
        """

    def set_impptr_done(self) ->None:
        return _ida_hexrays_micro.mop_t_set_impptr_done(self)

    def set_udt(self) ->None:
        return _ida_hexrays_micro.mop_t_set_udt(self)

    def set_undef_val(self) ->None:
        return _ida_hexrays_micro.mop_t_set_undef_val(self)

    def set_lowaddr(self) ->None:
        return _ida_hexrays_micro.mop_t_set_lowaddr(self)

    def set_for_abi(self) ->None:
        return _ida_hexrays_micro.mop_t_set_for_abi(self)

    def is_impptr_done(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_impptr_done(self)

    def is_udt(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_udt(self)

    def probably_floating(self) ->bool:
        return _ida_hexrays_micro.mop_t_probably_floating(self)

    def is_undef_val(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_undef_val(self)

    def is_lowaddr(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_lowaddr(self)

    def is_for_abi(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_for_abi(self)

    def is_ccflags(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_ccflags(self)

    def is_pcval(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_pcval(self)

    def is_glbaddr_from_fixup(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_glbaddr_from_fixup(self)

    def __init__(self, *args):
        _ida_hexrays_micro.mop_t_swiginit(self, _ida_hexrays_micro.
            new_mop_t(*args))

    def assign(self, rop: 'mop_t') ->'mop_t &':
        return _ida_hexrays_micro.mop_t_assign(self, rop)
    __swig_destroy__ = _ida_hexrays_micro.delete_mop_t

    def zero(self) ->None:
        return _ida_hexrays_micro.mop_t_zero(self)

    def swap(self, rop: 'mop_t') ->None:
        return _ida_hexrays_micro.mop_t_swap(self, rop)

    def erase(self) ->None:
        return _ida_hexrays_micro.mop_t_erase(self)

    def erase_but_keep_size(self) ->None:
        return _ida_hexrays_micro.mop_t_erase_but_keep_size(self)

    def _print(self, *args) ->None:
        return _ida_hexrays_micro.mop_t__print(self, *args)

    def dstr(self) ->str:
        return _ida_hexrays_micro.mop_t_dstr(self)

    def create_from_mlist(self, mba: 'mba_t', lst: 'mlist_t', fullsize: int
        ) ->bool:
        """Create operand from mlist_t. Example: if LST contains 4 bits for R0.4, our operand will be (t=mop_r, r=R0, size=4) 
        
:param mba: pointer to microcode
:param lst: list of locations
:param fullsize: mba->fullsize
:returns: success"""
        return _ida_hexrays_micro.mop_t_create_from_mlist(self, mba, lst,
            fullsize)

    def create_from_ivlset(self, mba: 'mba_t', ivs: 'ivlset_t', fullsize: int
        ) ->bool:
        """Create operand from ivlset_t. Example: if IVS contains [glbvar..glbvar+4), our operand will be (t=mop_v, g=&glbvar, size=4) 
        
:param mba: pointer to microcode
:param ivs: set of memory intervals
:param fullsize: mba->fullsize
:returns: success"""
        return _ida_hexrays_micro.mop_t_create_from_ivlset(self, mba, ivs,
            fullsize)

    def create_from_vdloc(self, mba: 'mba_t', loc: 'vdloc_t', _size: int
        ) ->None:
        """Create operand from vdloc_t. Example: if LOC contains (type=ALOC_REG1, r=R0), our operand will be (t=mop_r, r=R0, size=_SIZE) 
        
:param mba: pointer to microcode
:param loc: location
:param _size: operand size Note: this function cannot handle scattered locations.
:returns: success"""
        return _ida_hexrays_micro.mop_t_create_from_vdloc(self, mba, loc, _size
            )

    def create_from_scattered_vdloc(self, mba: 'mba_t', name: str, type:
        'tinfo_t', loc: 'vdloc_t') ->None:
        """Create operand from scattered vdloc_t. Example: if LOC is (ALOC_DIST, {EAX.4, EDX.4}) and TYPE is _LARGE_INTEGER, our operand will be (t=mop_sc, scif={EAX.4, EDX.4}) 
        
:param mba: pointer to microcode
:param name: name of the operand, if available
:param type: type of the operand, must be present
:param loc: a scattered location
:returns: success"""
        return _ida_hexrays_micro.mop_t_create_from_scattered_vdloc(self,
            mba, name, type, loc)

    def create_from_insn(self, m: 'minsn_t') ->None:
        """Create operand from an instruction. This function creates a nested instruction that can be used as an operand. Example: if m="add x,y,z", our operand will be (t=mop_d,d=m). The destination operand of 'add' (z) is lost. 
        
:param m: instruction to embed into operand. may not be nullptr."""
        return _ida_hexrays_micro.mop_t_create_from_insn(self, m)

    def make_number(self, *args) ->None:
        """Create an integer constant operand. 
        
:param _value: value to store in the operand
:param _size: size of the value in bytes (1,2,4,8)
:param _ea: address of the processor instruction that made the value
:param opnum: operand number of the processor instruction"""
        return _ida_hexrays_micro.mop_t_make_number(self, *args)

    def make_fpnum(self, bytes: 'void const *') ->bool:
        """Create a floating point constant operand. 
        
:param bytes: pointer to the floating point value as used by the current processor (e.g. for x86 it must be in IEEE 754)
:returns: success"""
        return _ida_hexrays_micro.mop_t_make_fpnum(self, bytes)

    def _make_reg(self, *args) ->None:
        """This function has the following signatures:

    0. _make_reg(reg: mreg_t) -> None
    1. _make_reg(reg: mreg_t, _size: int) -> None

# 0: _make_reg(reg: mreg_t) -> None

Create a register operand without erasing previous data. 
        

# 1: _make_reg(reg: mreg_t, _size: int) -> None

"""
        return _ida_hexrays_micro.mop_t__make_reg(self, *args)

    def make_reg(self, *args) ->None:
        """This function has the following signatures:

    0. make_reg(reg: mreg_t) -> None
    1. make_reg(reg: mreg_t, _size: int) -> None

# 0: make_reg(reg: mreg_t) -> None

Create a register operand.


# 1: make_reg(reg: mreg_t, _size: int) -> None

"""
        return _ida_hexrays_micro.mop_t_make_reg(self, *args)

    def _make_lvar(self, mba: 'mba_t', idx: int, off: int=0) ->None:
        """Create a local variable operand. 
        
:param mba: pointer to microcode
:param idx: index into mba->vars
:param off: offset from the beginning of the variable Note: this function does not erase the previous contents of the operand; call erase() if necessary"""
        return _ida_hexrays_micro.mop_t__make_lvar(self, mba, idx, off)

    def _make_gvar(self, ea: ida_idaapi.ea_t) ->None:
        """Create a global variable operand without erasing previous data. 
        
:param ea: address of the variable Note: this function does not erase the previous contents of the operand; call erase() if necessary"""
        return _ida_hexrays_micro.mop_t__make_gvar(self, ea)

    def make_gvar(self, ea: ida_idaapi.ea_t) ->None:
        """Create a global variable operand.
"""
        return _ida_hexrays_micro.mop_t_make_gvar(self, ea)

    def _make_stkvar(self, mba: 'mba_t', off: int) ->None:
        """Create a stack variable operand. 
        
:param mba: pointer to microcode
:param off: decompiler stkoff Note: this function does not erase the previous contents of the operand; call erase() if necessary"""
        return _ida_hexrays_micro.mop_t__make_stkvar(self, mba, off)

    def make_stkvar(self, mba: 'mba_t', off: int) ->None:
        return _ida_hexrays_micro.mop_t_make_stkvar(self, mba, off)

    def make_reg_pair(self, loreg: int, hireg: int, halfsize: int) ->None:
        """Create pair of registers. 
        
:param loreg: register holding the low part of the value
:param hireg: register holding the high part of the value
:param halfsize: the size of each of loreg/hireg"""
        return _ida_hexrays_micro.mop_t_make_reg_pair(self, loreg, hireg,
            halfsize)

    def _make_insn(self, ins: 'minsn_t') ->None:
        """Create a nested instruction without erasing previous data. 
        
:param ins: pointer to the instruction to encapsulate into the operand Note: this function does not erase the previous contents of the operand; call erase() if necessary See also create_from_insn, which is higher level"""
        o = ins
        self._ensure_cond(self.t == mop_z, 'self.t == mop_z')
        val = _ida_hexrays_micro.mop_t__make_insn(self, ins)
        self._acquire_ownership(o, True)
        return val

    def make_insn(self, ins: 'minsn_t') ->None:
        """Create a nested instruction.
"""
        o = ins
        self._ensure_cond(self.t == mop_z, 'self.t == mop_z')
        val = _ida_hexrays_micro.mop_t_make_insn(self, ins)
        self._acquire_ownership(o, True)
        return val

    def _make_blkref(self, blknum: int) ->None:
        """Create a block reference operand without erasing previous data. 
        
:param blknum: block number Note: this function does not erase the previous contents of the operand; call erase() if necessary"""
        return _ida_hexrays_micro.mop_t__make_blkref(self, blknum)

    def make_blkref(self, blknum: int) ->None:
        """Create a global variable operand.
"""
        return _ida_hexrays_micro.mop_t_make_blkref(self, blknum)

    def make_helper(self, name: str) ->None:
        """Create a helper operand. A helper operand usually keeps a built-in function name like "va_start" It is essentially just an arbitrary identifier without any additional info. 
        """
        return _ida_hexrays_micro.mop_t_make_helper(self, name)

    def _make_strlit(self, str: str) ->None:
        """Create a constant string operand.
"""
        return _ida_hexrays_micro.mop_t__make_strlit(self, str)

    def _make_callinfo(self, fi: 'mcallinfo_t') ->None:
        """Create a call info operand without erasing previous data. 
        
:param fi: callinfo Note: this function does not erase the previous contents of the operand; call erase() if necessary"""
        o = fi
        self._ensure_cond(self.t == mop_z, 'self.t == mop_z')
        val = _ida_hexrays_micro.mop_t__make_callinfo(self, fi)
        self._acquire_ownership(o, True)
        return val

    def _make_cases(self, _cases: 'mcases_t') ->None:
        """Create a 'switch cases' operand without erasing previous data. Note: this function does not erase the previous contents of the operand; call erase() if necessary 
        """
        o = _cases
        self._ensure_cond(self.t == mop_z, 'self.t == mop_z')
        val = _ida_hexrays_micro.mop_t__make_cases(self, _cases)
        self._acquire_ownership(o, True)
        return val

    def _make_pair(self, _pair: 'mop_pair_t') ->None:
        """Create a pair operand without erasing previous data. Note: this function does not erase the previous contents of the operand; call erase() if necessary 
        """
        o = _pair
        self._ensure_cond(self.t == mop_z, 'self.t == mop_z')
        val = _ida_hexrays_micro.mop_t__make_pair(self, _pair)
        self._acquire_ownership(o, True)
        return val

    def empty(self) ->bool:
        return _ida_hexrays_micro.mop_t_empty(self)

    def is_glbvar(self) ->bool:
        """Is a global variable?
"""
        return _ida_hexrays_micro.mop_t_is_glbvar(self)

    def is_stkvar(self) ->bool:
        """Is a stack variable?
"""
        return _ida_hexrays_micro.mop_t_is_stkvar(self)

    def is_reg(self, *args) ->bool:
        """This function has the following signatures:

    0. is_reg() -> bool
    1. is_reg(_r: mreg_t) -> bool
    2. is_reg(_r: mreg_t, _size: int) -> bool

# 0: is_reg() -> bool

Is a register operand? See also get_mreg_name() 
        

# 1: is_reg(_r: mreg_t) -> bool

Is the specified register?


# 2: is_reg(_r: mreg_t, _size: int) -> bool

Is the specified register of the specified size?

"""
        return _ida_hexrays_micro.mop_t_is_reg(self, *args)

    def is_arglist(self) ->bool:
        """Is a list of arguments?
"""
        return _ida_hexrays_micro.mop_t_is_arglist(self)

    def is_cc(self) ->bool:
        """Is a condition code?
"""
        return _ida_hexrays_micro.mop_t_is_cc(self)

    def is_bit_reg(self, *args) ->bool:
        """This function has the following signatures:

    0. is_bit_reg() -> bool
    1. is_bit_reg(reg: mreg_t) -> bool

# 0: is_bit_reg() -> bool


# 1: is_bit_reg(reg: mreg_t) -> bool

Is a bit register? This includes condition codes and eventually other bit registers 
        
"""
        return _ida_hexrays_micro.mop_t_is_bit_reg(self, *args)

    def is_kreg(self) ->bool:
        """Is a kernel register?
"""
        return _ida_hexrays_micro.mop_t_is_kreg(self)

    def is_mblock(self, *args) ->bool:
        """This function has the following signatures:

    0. is_mblock() -> bool
    1. is_mblock(serial: int) -> bool

# 0: is_mblock() -> bool

Is a block reference?


# 1: is_mblock(serial: int) -> bool

Is a block reference to the specified block?

"""
        return _ida_hexrays_micro.mop_t_is_mblock(self, *args)

    def is_scattered(self) ->bool:
        """Is a scattered operand?
"""
        return _ida_hexrays_micro.mop_t_is_scattered(self)

    def is_glbaddr(self, *args) ->bool:
        """This function has the following signatures:

    0. is_glbaddr() -> bool
    1. is_glbaddr(ea: ida_idaapi.ea_t) -> bool

# 0: is_glbaddr() -> bool

Is address of a global memory cell?


# 1: is_glbaddr(ea: ida_idaapi.ea_t) -> bool

Is address of the specified global memory cell?

"""
        return _ida_hexrays_micro.mop_t_is_glbaddr(self, *args)

    def is_stkaddr(self) ->bool:
        """Is address of a stack variable?
"""
        return _ida_hexrays_micro.mop_t_is_stkaddr(self)

    def is_insn(self, *args) ->bool:
        """This function has the following signatures:

    0. is_insn() -> bool
    1. is_insn(code: mcode_t) -> bool

# 0: is_insn() -> bool

Is a sub-instruction?


# 1: is_insn(code: mcode_t) -> bool

Is a sub-instruction with the specified opcode?

"""
        return _ida_hexrays_micro.mop_t_is_insn(self, *args)

    def has_side_effects(self, include_ldx_and_divs: bool=False) ->bool:
        """Has any side effects? 
        
:param include_ldx_and_divs: consider ldx/div/mod as having side effects?"""
        return _ida_hexrays_micro.mop_t_has_side_effects(self,
            include_ldx_and_divs)

    def may_use_aliased_memory(self) ->bool:
        """Is it possible for the operand to use aliased memory?
"""
        return _ida_hexrays_micro.mop_t_may_use_aliased_memory(self)

    def is01(self) ->bool:
        """Are the possible values of the operand only 0 and 1? This function returns true for 0/1 constants, bit registers, the result of 'set' insns, etc. 
        """
        return _ida_hexrays_micro.mop_t_is01(self)

    def is_sign_extended_from(self, nbytes: int) ->bool:
        """Does the high part of the operand consist of the sign bytes? 
        
:param nbytes: number of bytes that were sign extended. the remaining size-nbytes high bytes must be sign bytes Example: is_sign_extended_from(xds.4(op.1), 1) -> true because the high 3 bytes are certainly sign bits"""
        return _ida_hexrays_micro.mop_t_is_sign_extended_from(self, nbytes)

    def is_zero_extended_from(self, nbytes: int) ->bool:
        """Does the high part of the operand consist of zero bytes? 
        
:param nbytes: number of bytes that were zero extended. the remaining size-nbytes high bytes must be zero Example: is_zero_extended_from(xdu.8(op.1), 2) -> true because the high 6 bytes are certainly zero"""
        return _ida_hexrays_micro.mop_t_is_zero_extended_from(self, nbytes)

    def is_extended_from(self, nbytes: int, is_signed: bool) ->bool:
        """Does the high part of the operand consist of zero or sign bytes?
"""
        return _ida_hexrays_micro.mop_t_is_extended_from(self, nbytes,
            is_signed)

    def equal_mops(self, rop: 'mop_t', eqflags: int) ->bool:
        """Compare operands. This is the main comparison function for operands. 
        
:param rop: operand to compare with
:param eqflags: combination of comparison bits bits"""
        return _ida_hexrays_micro.mop_t_equal_mops(self, rop, eqflags)

    def __eq__(self, rop: 'mop_t') ->bool:
        return _ida_hexrays_micro.mop_t___eq__(self, rop)

    def __ne__(self, rop: 'mop_t') ->bool:
        return _ida_hexrays_micro.mop_t___ne__(self, rop)

    def __lt__(self, rop: 'mop_t') ->bool:
        return _ida_hexrays_micro.mop_t___lt__(self, rop)

    def lexcompare(self, rop: 'mop_t') ->int:
        return _ida_hexrays_micro.mop_t_lexcompare(self, rop)

    def for_all_ops(self, mv: 'mop_visitor_t', type: 'tinfo_t'=None,
        is_target: bool=False) ->int:
        """Visit the operand and all its sub-operands. This function visits the current operand as well. 
        
:param mv: visitor object
:param type: operand type
:param is_target: is a destination operand?"""
        return _ida_hexrays_micro.mop_t_for_all_ops(self, mv, type, is_target)

    def for_all_scattered_submops(self, sv: 'scif_visitor_t') ->int:
        """Visit all sub-operands of a scattered operand. This function does not visit the current operand, only its sub-operands. All sub-operands are synthetic and are destroyed after the visitor. This function works only with scattered operands. 
        
:param sv: visitor object"""
        return _ida_hexrays_micro.mop_t_for_all_scattered_submops(self, sv)

    def value(self, is_signed: bool) ->'uint64':
        """Retrieve value of a constant integer operand. These functions can be called only for mop_n operands. See is_constant() that can be called on any operand. 
        """
        return _ida_hexrays_micro.mop_t_value(self, is_signed)

    def signed_value(self) ->'int64':
        return _ida_hexrays_micro.mop_t_signed_value(self)

    def unsigned_value(self) ->'uint64':
        return _ida_hexrays_micro.mop_t_unsigned_value(self)

    def update_numop_value(self, val: 'uint64') ->None:
        return _ida_hexrays_micro.mop_t_update_numop_value(self, val)

    def is_constant(self, is_signed: bool=True) ->bool:
        """Retrieve value of a constant integer operand. 
        
:param is_signed: should treat the value as signed
:returns: true if the operand is mop_n"""
        return _ida_hexrays_micro.mop_t_is_constant(self, is_signed)

    def is_equal_to(self, n: 'uint64', is_signed: bool=True) ->bool:
        return _ida_hexrays_micro.mop_t_is_equal_to(self, n, is_signed)

    def is_zero(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_zero(self)

    def is_one(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_one(self)

    def is_positive_constant(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_positive_constant(self)

    def is_negative_constant(self) ->bool:
        return _ida_hexrays_micro.mop_t_is_negative_constant(self)

    def get_stkvar(self, udm: 'udm_t'=None, p_idaoff: 'uval_t *'=None
        ) ->'ssize_t':
        """Retrieve the referenced stack variable. 
        
:param udm: stkvar, may be nullptr
:param p_idaoff: if specified, will hold IDA stkoff after the call.
:returns: index of stkvar in the frame or -1"""
        return _ida_hexrays_micro.mop_t_get_stkvar(self, udm, p_idaoff)

    def get_stkoff(self, p_vdoff: 'sval_t *') ->bool:
        """Get the referenced stack offset. This function can also handle mop_sc if it is entirely mapped into a continuous stack region. 
        
:param p_vdoff: the output buffer
:returns: success"""
        return _ida_hexrays_micro.mop_t_get_stkoff(self, p_vdoff)

    def get_insn(self, code: 'mcode_t') ->'minsn_t *':
        """Get subinstruction of the operand. If the operand has a subinstruction with the specified opcode, return it. 
        
:param code: desired opcode
:returns: pointer to the instruction or nullptr"""
        return _ida_hexrays_micro.mop_t_get_insn(self, code)

    def make_low_half(self, width: int) ->bool:
        """Make the low part of the operand. This function takes into account the memory endianness (byte sex) 
        
:param width: the desired size of the operand part in bytes
:returns: success"""
        return _ida_hexrays_micro.mop_t_make_low_half(self, width)

    def make_high_half(self, width: int) ->bool:
        """Make the high part of the operand. This function takes into account the memory endianness (byte sex) 
        
:param width: the desired size of the operand part in bytes
:returns: success"""
        return _ida_hexrays_micro.mop_t_make_high_half(self, width)

    def make_first_half(self, width: int) ->bool:
        """Make the first part of the operand. This function does not care about the memory endianness 
        
:param width: the desired size of the operand part in bytes
:returns: success"""
        return _ida_hexrays_micro.mop_t_make_first_half(self, width)

    def make_second_half(self, width: int) ->bool:
        """Make the second part of the operand. This function does not care about the memory endianness 
        
:param width: the desired size of the operand part in bytes
:returns: success"""
        return _ida_hexrays_micro.mop_t_make_second_half(self, width)

    def shift_mop(self, offset: int) ->bool:
        """Shift the operand. This function shifts only the beginning of the operand. The operand size will be changed. Examples: shift_mop(AH.1, -1) -> AX.2 shift_mop(qword_00000008.8, 4) -> dword_0000000C.4 shift_mop(xdu.8(op.4), 4) -> #0.4 shift_mop(#0x12345678.4, 3) -> #12.1 
        
:param offset: shift count (the number of bytes to shift)
:returns: success"""
        return _ida_hexrays_micro.mop_t_shift_mop(self, offset)

    def change_size(self, nsize: int, sideff: 'side_effect_t'=WITH_SIDEFF
        ) ->bool:
        """Change the operand size. Examples: change_size(AL.1, 2) -> AX.2 change_size(qword_00000008.8, 4) -> dword_00000008.4 change_size(xdu.8(op.4), 4) -> op.4 change_size(#0x12345678.4, 1) -> #0x78.1 
        
:param nsize: new operand size
:param sideff: may modify the database because of the size change?
:returns: success"""
        return _ida_hexrays_micro.mop_t_change_size(self, nsize, sideff)

    def double_size(self, sideff: 'side_effect_t'=WITH_SIDEFF) ->bool:
        return _ida_hexrays_micro.mop_t_double_size(self, sideff)

    def preserve_side_effects(self, blk: 'mblock_t', top: 'minsn_t',
        moved_calls: 'bool *'=None) ->bool:
        """Move subinstructions with side effects out of the operand. If we decide to delete an instruction operand, it is a good idea to call this function. Alternatively we should skip such operands by calling mop_t::has_side_effects() For example, if we transform: jnz x, x, @blk => goto @blk then we must call this function before deleting the X operands. 
        
:param blk: current block
:param top: top level instruction that contains our operand
:param moved_calls: pointer to the boolean that will track if all side effects get handled correctly. must be false initially.
:returns: false failed to preserve a side effect, it is not safe to delete the operand true no side effects or successfully preserved them"""
        return _ida_hexrays_micro.mop_t_preserve_side_effects(self, blk,
            top, moved_calls)

    def apply_ld_mcode(self, mcode: 'mcode_t', ea: ida_idaapi.ea_t, newsize:
        int) ->None:
        """Apply a unary opcode to the operand. 
        
:param mcode: opcode to apply. it must accept 'l' and 'd' operands but not 'r'. examples: m_low/m_high/m_xds/m_xdu
:param ea: value of minsn_t::ea for the newly created insruction
:param newsize: new operand size Example: apply_ld_mcode(m_low) will convert op => low(op)"""
        return _ida_hexrays_micro.mop_t_apply_ld_mcode(self, mcode, ea, newsize
            )

    def apply_xdu(self, ea: ida_idaapi.ea_t, newsize: int) ->None:
        return _ida_hexrays_micro.mop_t_apply_xdu(self, ea, newsize)

    def apply_xds(self, ea: ida_idaapi.ea_t, newsize: int) ->None:
        return _ida_hexrays_micro.mop_t_apply_xds(self, ea, newsize)

    def _register(self) ->None:
        return _ida_hexrays_micro.mop_t__register(self)

    def _deregister(self) ->None:
        return _ida_hexrays_micro.mop_t__deregister(self)

    def _get_t(self) ->'mopt_t':
        return _ida_hexrays_micro.mop_t__get_t(self)

    def _set_t(self, v: 'mopt_t') ->None:
        return _ida_hexrays_micro.mop_t__set_t(self, v)

    def _ensure_no_t(self):
        if self.t not in [mop_z]:
            raise Exception('%s has type %s; cannot be modified' % (self,
                self.t))
        return True
    t = property(_get_t, lambda self, v: self._ensure_no_t() and self._set_t(v)
        )
    """Operand type.
"""

    def __dbg_get_meminfo(self) ->str:
        return _ida_hexrays_micro.mop_t___dbg_get_meminfo(self)

    def __dbg_get_registered_kind(self) ->int:
        return _ida_hexrays_micro.mop_t___dbg_get_registered_kind(self)

    def _obj_id(self) ->'PyObject *':
        return _ida_hexrays_micro.mop_t__obj_id(self)
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

    def _get_nnn(self) ->'mnumber_t *':
        return _ida_hexrays_micro.mop_t__get_nnn(self)

    def _set_nnn(self, _v: 'mnumber_t') ->None:
        return _ida_hexrays_micro.mop_t__set_nnn(self, _v)

    @property
    def nnn(self):
        return self._get_nnn() if self.t == mop_n else None

    @nnn.setter
    def nnn(self, value):
        return self._ensure_cond(self.t == mop_n, 'self.t == mop_n'
            ) and self._ensure_no_obj(self._get_nnn(), 'nnn', True
            ) and self._acquire_ownership(value, True) and self._set_nnn(value)

    def _get_d(self) ->'minsn_t *':
        return _ida_hexrays_micro.mop_t__get_d(self)

    def _set_d(self, _v: 'minsn_t') ->None:
        return _ida_hexrays_micro.mop_t__set_d(self, _v)

    @property
    def d(self):
        return self._get_d() if self.t == mop_d else None

    @d.setter
    def d(self, value):
        return self._ensure_cond(self.t == mop_d, 'self.t == mop_d'
            ) and self._ensure_no_obj(self._get_d(), 'd', True
            ) and self._acquire_ownership(value, True) and self._set_d(value)

    def _get_s(self) ->'stkvar_ref_t *':
        return _ida_hexrays_micro.mop_t__get_s(self)

    def _set_s(self, _v: 'stkvar_ref_t') ->None:
        return _ida_hexrays_micro.mop_t__set_s(self, _v)

    @property
    def s(self):
        return self._get_s() if self.t == mop_S else None

    @s.setter
    def s(self, value):
        return self._ensure_cond(self.t == mop_S, 'self.t == mop_S'
            ) and self._ensure_no_obj(self._get_s(), 's', True
            ) and self._acquire_ownership(value, True) and self._set_s(value)

    def _get_f(self) ->'mcallinfo_t *':
        return _ida_hexrays_micro.mop_t__get_f(self)

    def _set_f(self, _v: 'mcallinfo_t') ->None:
        return _ida_hexrays_micro.mop_t__set_f(self, _v)

    @property
    def f(self):
        return self._get_f() if self.t == mop_f else None

    @f.setter
    def f(self, value):
        return self._ensure_cond(self.t == mop_f, 'self.t == mop_f'
            ) and self._ensure_no_obj(self._get_f(), 'f', True
            ) and self._acquire_ownership(value, True) and self._set_f(value)

    def _get_l(self) ->'lvar_ref_t *':
        return _ida_hexrays_micro.mop_t__get_l(self)

    def _set_l(self, _v: 'lvar_ref_t') ->None:
        return _ida_hexrays_micro.mop_t__set_l(self, _v)

    @property
    def l(self):
        return self._get_l() if self.t == mop_l else None

    @l.setter
    def l(self, value):
        return self._ensure_cond(self.t == mop_l, 'self.t == mop_l'
            ) and self._ensure_no_obj(self._get_l(), 'l', True
            ) and self._acquire_ownership(value, True) and self._set_l(value)

    def _get_a(self) ->'mop_addr_t *':
        return _ida_hexrays_micro.mop_t__get_a(self)

    def _set_a(self, _v: 'mop_addr_t') ->None:
        return _ida_hexrays_micro.mop_t__set_a(self, _v)

    @property
    def a(self):
        return self._get_a() if self.t == mop_a else None

    @a.setter
    def a(self, value):
        return self._ensure_cond(self.t == mop_a, 'self.t == mop_a'
            ) and self._ensure_no_obj(self._get_a(), 'a', True
            ) and self._acquire_ownership(value, True) and self._set_a(value)

    def _get_c(self) ->'mcases_t *':
        return _ida_hexrays_micro.mop_t__get_c(self)

    def _set_c(self, _v: 'mcases_t') ->None:
        return _ida_hexrays_micro.mop_t__set_c(self, _v)

    @property
    def c(self):
        return self._get_c() if self.t == mop_c else None

    @c.setter
    def c(self, value):
        return self._ensure_cond(self.t == mop_c, 'self.t == mop_c'
            ) and self._ensure_no_obj(self._get_c(), 'c', True
            ) and self._acquire_ownership(value, True) and self._set_c(value)

    def _get_fpc(self) ->'fnumber_t *':
        return _ida_hexrays_micro.mop_t__get_fpc(self)

    def _set_fpc(self, _v: 'fnumber_t') ->None:
        return _ida_hexrays_micro.mop_t__set_fpc(self, _v)

    @property
    def fpc(self):
        return self._get_fpc() if self.t == mop_fn else None

    @fpc.setter
    def fpc(self, value):
        return self._ensure_cond(self.t == mop_fn, 'self.t == mop_fn'
            ) and self._ensure_no_obj(self._get_fpc(), 'fpc', True
            ) and self._acquire_ownership(value, True) and self._set_fpc(value)

    def _get_pair(self) ->'mop_pair_t *':
        return _ida_hexrays_micro.mop_t__get_pair(self)

    def _set_pair(self, _v: 'mop_pair_t') ->None:
        return _ida_hexrays_micro.mop_t__set_pair(self, _v)

    @property
    def pair(self):
        return self._get_pair() if self.t == mop_p else None

    @pair.setter
    def pair(self, value):
        return self._ensure_cond(self.t == mop_p, 'self.t == mop_p'
            ) and self._ensure_no_obj(self._get_pair(), 'pair', True
            ) and self._acquire_ownership(value, True) and self._set_pair(value
            )

    def _get_scif(self) ->'scif_t *':
        return _ida_hexrays_micro.mop_t__get_scif(self)

    def _set_scif(self, _v: 'scif_t') ->None:
        return _ida_hexrays_micro.mop_t__set_scif(self, _v)

    @property
    def scif(self):
        return self._get_scif() if self.t == mop_sc else None

    @scif.setter
    def scif(self, value):
        return self._ensure_cond(self.t == mop_sc, 'self.t == mop_sc'
            ) and self._ensure_no_obj(self._get_scif(), 'scif', True
            ) and self._acquire_ownership(value, True) and self._set_scif(value
            )

    @property
    def scif(self):
        return self._get_scif() if self.t == mop_sc else None

    @scif.setter
    def scif(self, value):
        return self._ensure_cond(self.t == mop_sc, 'self.t == mop_sc'
            ) and self._ensure_no_obj(self._get_scif(), 'scif', True
            ) and self._acquire_ownership(value, True) and self._set_scif(value
            )

    def _get_r(self) ->'mreg_t':
        return _ida_hexrays_micro.mop_t__get_r(self)

    def _set_r(self, _v: 'mreg_t') ->None:
        return _ida_hexrays_micro.mop_t__set_r(self, _v)

    @property
    def r(self):
        return self._get_r() if self.t == mop_r else None

    @r.setter
    def r(self, value):
        return self._ensure_cond(self.t == mop_r, 'self.t == mop_r'
            ) and self._set_r(value)

    def _get_g(self) ->ida_idaapi.ea_t:
        return _ida_hexrays_micro.mop_t__get_g(self)

    def _set_g(self, _v: ida_idaapi.ea_t) ->None:
        return _ida_hexrays_micro.mop_t__set_g(self, _v)

    @property
    def g(self):
        return self._get_g() if self.t == mop_v else None

    @g.setter
    def g(self, value):
        return self._ensure_cond(self.t == mop_v, 'self.t == mop_v'
            ) and self._set_g(value)

    def _get_b(self) ->int:
        return _ida_hexrays_micro.mop_t__get_b(self)

    def _set_b(self, _v: int) ->None:
        return _ida_hexrays_micro.mop_t__set_b(self, _v)

    @property
    def b(self):
        return self._get_b() if self.t == mop_b else None

    @b.setter
    def b(self, value):
        return self._ensure_cond(self.t == mop_b, 'self.t == mop_b'
            ) and self._set_b(value)

    def _get_cstr(self) ->str:
        return _ida_hexrays_micro.mop_t__get_cstr(self)

    def _set_cstr(self, _v: str) ->None:
        return _ida_hexrays_micro.mop_t__set_cstr(self, _v)

    @property
    def cstr(self):
        return self._get_cstr() if self.t == mop_str else None

    @cstr.setter
    def cstr(self, value):
        return self._ensure_cond(self.t == mop_str, 'self.t == mop_str'
            ) and self._ensure_no_obj(self._get_cstr(), 'cstr', False
            ) and self._acquire_ownership(value, False) and self._set_cstr(
            value)

    def _get_helper(self) ->str:
        return _ida_hexrays_micro.mop_t__get_helper(self)

    def _set_helper(self, _v: str) ->None:
        return _ida_hexrays_micro.mop_t__set_helper(self, _v)

    @property
    def helper(self):
        return self._get_helper() if self.t == mop_h else None

    @helper.setter
    def helper(self, value):
        return self._ensure_cond(self.t == mop_h, 'self.t == mop_h'
            ) and self._ensure_no_obj(self._get_helper(), 'helper', False
            ) and self._acquire_ownership(value, False) and self._set_helper(
            value)


_ida_hexrays_micro.mop_t_swigregister(mop_t)
OPROP_IMPDONE = _ida_hexrays_micro.OPROP_IMPDONE
"""imported operand (a pointer) has been dereferenced
"""
OPROP_UDT = _ida_hexrays_micro.OPROP_UDT
"""a struct or union
"""
OPROP_FLOAT = _ida_hexrays_micro.OPROP_FLOAT
"""possibly floating value
"""
OPROP_CCFLAGS = _ida_hexrays_micro.OPROP_CCFLAGS
"""mop_n: a pc-relative value mop_a: an address obtained from a relocation else: value of a condition code register (like mr_cc) 
        """
OPROP_UDEFVAL = _ida_hexrays_micro.OPROP_UDEFVAL
"""uses undefined value
"""
OPROP_LOWADDR = _ida_hexrays_micro.OPROP_LOWADDR
"""a low address offset
"""
OPROP_ABI = _ida_hexrays_micro.OPROP_ABI
"""is used to organize arg/retval of a call such operands should be combined more carefully than others at least on BE platforms 
        """


def lexcompare(a: 'mop_t', b: 'mop_t') ->int:
    return _ida_hexrays_micro.lexcompare(a, b)


class mop_pair_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    lop: 'mop_t' = property(_ida_hexrays_micro.mop_pair_t_lop_get,
        _ida_hexrays_micro.mop_pair_t_lop_set)
    """low operand
"""
    hop: 'mop_t' = property(_ida_hexrays_micro.mop_pair_t_hop_get,
        _ida_hexrays_micro.mop_pair_t_hop_set)
    """high operand
"""

    def __init__(self):
        _ida_hexrays_micro.mop_pair_t_swiginit(self, _ida_hexrays_micro.
            new_mop_pair_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_mop_pair_t


_ida_hexrays_micro.mop_pair_t_swigregister(mop_pair_t)


class mop_addr_t(mop_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    insize: int = property(_ida_hexrays_micro.mop_addr_t_insize_get,
        _ida_hexrays_micro.mop_addr_t_insize_set)
    outsize: int = property(_ida_hexrays_micro.mop_addr_t_outsize_get,
        _ida_hexrays_micro.mop_addr_t_outsize_set)

    def __init__(self, *args):
        _ida_hexrays_micro.mop_addr_t_swiginit(self, _ida_hexrays_micro.
            new_mop_addr_t(*args))

    def lexcompare(self, ra: 'mop_addr_t') ->int:
        return _ida_hexrays_micro.mop_addr_t_lexcompare(self, ra)
    __swig_destroy__ = _ida_hexrays_micro.delete_mop_addr_t


_ida_hexrays_micro.mop_addr_t_swigregister(mop_addr_t)


class mcallarg_t(mop_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ea: ida_idaapi.ea_t = property(_ida_hexrays_micro.mcallarg_t_ea_get,
        _ida_hexrays_micro.mcallarg_t_ea_set)
    """address where the argument was initialized. BADADDR means unknown. 
        """
    type: 'tinfo_t' = property(_ida_hexrays_micro.mcallarg_t_type_get,
        _ida_hexrays_micro.mcallarg_t_type_set)
    """formal argument type
"""
    name: str = property(_ida_hexrays_micro.mcallarg_t_name_get,
        _ida_hexrays_micro.mcallarg_t_name_set)
    """formal argument name
"""
    argloc: 'argloc_t' = property(_ida_hexrays_micro.mcallarg_t_argloc_get,
        _ida_hexrays_micro.mcallarg_t_argloc_set)
    """ida argloc
"""
    flags: int = property(_ida_hexrays_micro.mcallarg_t_flags_get,
        _ida_hexrays_micro.mcallarg_t_flags_set)
    """FAI_...
"""

    def __init__(self, *args):
        _ida_hexrays_micro.mcallarg_t_swiginit(self, _ida_hexrays_micro.
            new_mcallarg_t(*args))

    def copy_mop(self, op: 'mop_t') ->None:
        return _ida_hexrays_micro.mcallarg_t_copy_mop(self, op)

    def _print(self, *args) ->None:
        return _ida_hexrays_micro.mcallarg_t__print(self, *args)

    def dstr(self) ->str:
        return _ida_hexrays_micro.mcallarg_t_dstr(self)

    def set_regarg(self, *args) ->None:
        """This function has the following signatures:

    0. set_regarg(mr: mreg_t, sz: int, tif: const tinfo_t &) -> None
    1. set_regarg(mr: mreg_t, tif: const tinfo_t &) -> None
    2. set_regarg(mr: mreg_t, dt: char, sign: type_sign_t=type_unsigned) -> None

# 0: set_regarg(mr: mreg_t, sz: int, tif: const tinfo_t &) -> None


# 1: set_regarg(mr: mreg_t, tif: const tinfo_t &) -> None


# 2: set_regarg(mr: mreg_t, dt: char, sign: type_sign_t=type_unsigned) -> None

"""
        return _ida_hexrays_micro.mcallarg_t_set_regarg(self, *args)

    def make_int(self, val: int, val_ea: ida_idaapi.ea_t, opno: int=0) ->None:
        return _ida_hexrays_micro.mcallarg_t_make_int(self, val, val_ea, opno)

    def make_uint(self, val: int, val_ea: ida_idaapi.ea_t, opno: int=0) ->None:
        return _ida_hexrays_micro.mcallarg_t_make_uint(self, val, val_ea, opno)
    __swig_destroy__ = _ida_hexrays_micro.delete_mcallarg_t


_ida_hexrays_micro.mcallarg_t_swigregister(mcallarg_t)
ROLE_UNK = _ida_hexrays_micro.ROLE_UNK
"""unknown function role
"""
ROLE_EMPTY = _ida_hexrays_micro.ROLE_EMPTY
"""empty, does not do anything (maybe spoils regs)
"""
ROLE_MEMSET = _ida_hexrays_micro.ROLE_MEMSET
"""memset(void *dst, uchar value, size_t count);
"""
ROLE_MEMSET32 = _ida_hexrays_micro.ROLE_MEMSET32
"""memset32(void *dst, uint32 value, size_t count);
"""
ROLE_MEMSET64 = _ida_hexrays_micro.ROLE_MEMSET64
"""memset64(void *dst, uint64 value, size_t count);
"""
ROLE_MEMCPY = _ida_hexrays_micro.ROLE_MEMCPY
"""memcpy(void *dst, const void *src, size_t count);
"""
ROLE_STRCPY = _ida_hexrays_micro.ROLE_STRCPY
"""strcpy(char *dst, const char *src);
"""
ROLE_STRLEN = _ida_hexrays_micro.ROLE_STRLEN
"""strlen(const char *src);
"""
ROLE_STRCAT = _ida_hexrays_micro.ROLE_STRCAT
"""strcat(char *dst, const char *src);
"""
ROLE_TAIL = _ida_hexrays_micro.ROLE_TAIL
"""char *tail(const char *str);
"""
ROLE_BUG = _ida_hexrays_micro.ROLE_BUG
"""BUG() helper macro: never returns, causes exception.
"""
ROLE_ALLOCA = _ida_hexrays_micro.ROLE_ALLOCA
"""alloca() function
"""
ROLE_BSWAP = _ida_hexrays_micro.ROLE_BSWAP
"""bswap() function (any size)
"""
ROLE_PRESENT = _ida_hexrays_micro.ROLE_PRESENT
"""present() function (used in patterns)
"""
ROLE_CONTAINING_RECORD = _ida_hexrays_micro.ROLE_CONTAINING_RECORD
"""CONTAINING_RECORD() macro.
"""
ROLE_FASTFAIL = _ida_hexrays_micro.ROLE_FASTFAIL
"""__fastfail()
"""
ROLE_READFLAGS = _ida_hexrays_micro.ROLE_READFLAGS
"""__readeflags, __readcallersflags
"""
ROLE_IS_MUL_OK = _ida_hexrays_micro.ROLE_IS_MUL_OK
"""is_mul_ok
"""
ROLE_SATURATED_MUL = _ida_hexrays_micro.ROLE_SATURATED_MUL
"""saturated_mul
"""
ROLE_BITTEST = _ida_hexrays_micro.ROLE_BITTEST
"""[lock] bt
"""
ROLE_BITTESTANDSET = _ida_hexrays_micro.ROLE_BITTESTANDSET
"""[lock] bts
"""
ROLE_BITTESTANDRESET = _ida_hexrays_micro.ROLE_BITTESTANDRESET
"""[lock] btr
"""
ROLE_BITTESTANDCOMPLEMENT = _ida_hexrays_micro.ROLE_BITTESTANDCOMPLEMENT
"""[lock] btc
"""
ROLE_VA_ARG = _ida_hexrays_micro.ROLE_VA_ARG
"""va_arg() macro
"""
ROLE_VA_COPY = _ida_hexrays_micro.ROLE_VA_COPY
"""va_copy() function
"""
ROLE_VA_START = _ida_hexrays_micro.ROLE_VA_START
"""va_start() function
"""
ROLE_VA_END = _ida_hexrays_micro.ROLE_VA_END
"""va_end() function
"""
ROLE_ROL = _ida_hexrays_micro.ROLE_ROL
"""rotate left
"""
ROLE_ROR = _ida_hexrays_micro.ROLE_ROR
"""rotate right
"""
ROLE_CFSUB3 = _ida_hexrays_micro.ROLE_CFSUB3
"""carry flag after subtract with carry
"""
ROLE_OFSUB3 = _ida_hexrays_micro.ROLE_OFSUB3
"""overflow flag after subtract with carry
"""
ROLE_ABS = _ida_hexrays_micro.ROLE_ABS
"""integer absolute value
"""
ROLE_3WAYCMP0 = _ida_hexrays_micro.ROLE_3WAYCMP0
"""3-way compare helper, returns -1/0/1
"""
ROLE_3WAYCMP1 = _ida_hexrays_micro.ROLE_3WAYCMP1
"""3-way compare helper, returns 0/1/2
"""
ROLE_WMEMCPY = _ida_hexrays_micro.ROLE_WMEMCPY
"""wchar_t *wmemcpy(wchar_t *dst, const wchar_t *src, size_t n)
"""
ROLE_WMEMSET = _ida_hexrays_micro.ROLE_WMEMSET
"""wchar_t *wmemset(wchar_t *dst, wchar_t wc, size_t n)
"""
ROLE_WCSCPY = _ida_hexrays_micro.ROLE_WCSCPY
"""wchar_t *wcscpy(wchar_t *dst, const wchar_t *src);
"""
ROLE_WCSLEN = _ida_hexrays_micro.ROLE_WCSLEN
"""size_t wcslen(const wchar_t *s)
"""
ROLE_WCSCAT = _ida_hexrays_micro.ROLE_WCSCAT
"""wchar_t *wcscat(wchar_t *dst, const wchar_t *src)
"""
ROLE_SSE_CMP4 = _ida_hexrays_micro.ROLE_SSE_CMP4
"""e.g. _mm_cmpgt_ss
"""
ROLE_SSE_CMP8 = _ida_hexrays_micro.ROLE_SSE_CMP8
"""e.g. _mm_cmpgt_sd
"""
FUNC_NAME_MEMCPY = _ida_hexrays_micro.FUNC_NAME_MEMCPY
FUNC_NAME_WMEMCPY = _ida_hexrays_micro.FUNC_NAME_WMEMCPY
FUNC_NAME_MEMSET = _ida_hexrays_micro.FUNC_NAME_MEMSET
FUNC_NAME_WMEMSET = _ida_hexrays_micro.FUNC_NAME_WMEMSET
FUNC_NAME_MEMSET32 = _ida_hexrays_micro.FUNC_NAME_MEMSET32
FUNC_NAME_MEMSET64 = _ida_hexrays_micro.FUNC_NAME_MEMSET64
FUNC_NAME_STRCPY = _ida_hexrays_micro.FUNC_NAME_STRCPY
FUNC_NAME_WCSCPY = _ida_hexrays_micro.FUNC_NAME_WCSCPY
FUNC_NAME_STRLEN = _ida_hexrays_micro.FUNC_NAME_STRLEN
FUNC_NAME_WCSLEN = _ida_hexrays_micro.FUNC_NAME_WCSLEN
FUNC_NAME_STRCAT = _ida_hexrays_micro.FUNC_NAME_STRCAT
FUNC_NAME_WCSCAT = _ida_hexrays_micro.FUNC_NAME_WCSCAT
FUNC_NAME_TAIL = _ida_hexrays_micro.FUNC_NAME_TAIL
FUNC_NAME_VA_ARG = _ida_hexrays_micro.FUNC_NAME_VA_ARG
FUNC_NAME_EMPTY = _ida_hexrays_micro.FUNC_NAME_EMPTY
FUNC_NAME_PRESENT = _ida_hexrays_micro.FUNC_NAME_PRESENT
FUNC_NAME_CONTAINING_RECORD = _ida_hexrays_micro.FUNC_NAME_CONTAINING_RECORD
FUNC_NAME_MORESTACK = _ida_hexrays_micro.FUNC_NAME_MORESTACK


class mcallinfo_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    callee: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        mcallinfo_t_callee_get, _ida_hexrays_micro.mcallinfo_t_callee_set)
    """address of the called function, if known
"""
    solid_args: int = property(_ida_hexrays_micro.
        mcallinfo_t_solid_args_get, _ida_hexrays_micro.
        mcallinfo_t_solid_args_set)
    """number of solid args. there may be variadic args in addtion 
        """
    call_spd: int = property(_ida_hexrays_micro.mcallinfo_t_call_spd_get,
        _ida_hexrays_micro.mcallinfo_t_call_spd_set)
    """sp value at call insn
"""
    stkargs_top: int = property(_ida_hexrays_micro.
        mcallinfo_t_stkargs_top_get, _ida_hexrays_micro.
        mcallinfo_t_stkargs_top_set)
    """first offset past stack arguments
"""
    cc: 'callcnv_t' = property(_ida_hexrays_micro.mcallinfo_t_cc_get,
        _ida_hexrays_micro.mcallinfo_t_cc_set)
    """calling convention
"""
    args: 'mcallargs_t' = property(_ida_hexrays_micro.mcallinfo_t_args_get,
        _ida_hexrays_micro.mcallinfo_t_args_set)
    """call arguments
"""
    retregs: 'mopvec_t' = property(_ida_hexrays_micro.
        mcallinfo_t_retregs_get, _ida_hexrays_micro.mcallinfo_t_retregs_set)
    """return register(s) (e.g., AX, AX:DX, etc.) this vector is built from return_regs 
        """
    return_type: 'tinfo_t' = property(_ida_hexrays_micro.
        mcallinfo_t_return_type_get, _ida_hexrays_micro.
        mcallinfo_t_return_type_set)
    """type of the returned value
"""
    return_argloc: 'argloc_t' = property(_ida_hexrays_micro.
        mcallinfo_t_return_argloc_get, _ida_hexrays_micro.
        mcallinfo_t_return_argloc_set)
    """location of the returned value
"""
    return_regs: 'mlist_t' = property(_ida_hexrays_micro.
        mcallinfo_t_return_regs_get, _ida_hexrays_micro.
        mcallinfo_t_return_regs_set)
    """list of values returned by the function
"""
    spoiled: 'mlist_t' = property(_ida_hexrays_micro.
        mcallinfo_t_spoiled_get, _ida_hexrays_micro.mcallinfo_t_spoiled_set)
    """list of spoiled locations (includes return_regs)
"""
    pass_regs: 'mlist_t' = property(_ida_hexrays_micro.
        mcallinfo_t_pass_regs_get, _ida_hexrays_micro.mcallinfo_t_pass_regs_set
        )
    """passthrough registers: registers that depend on input values (subset of spoiled) 
        """
    visible_memory: 'ivlset_t' = property(_ida_hexrays_micro.
        mcallinfo_t_visible_memory_get, _ida_hexrays_micro.
        mcallinfo_t_visible_memory_set)
    """what memory is visible to the call?
"""
    dead_regs: 'mlist_t' = property(_ida_hexrays_micro.
        mcallinfo_t_dead_regs_get, _ida_hexrays_micro.mcallinfo_t_dead_regs_set
        )
    """registers defined by the function but never used. upon propagation we do the following:
* dead_regs += return_regs
* retregs.clear() since the call is propagated 


        """
    flags: int = property(_ida_hexrays_micro.mcallinfo_t_flags_get,
        _ida_hexrays_micro.mcallinfo_t_flags_set)
    """combination of Call properties... bits 
        """
    role: 'funcrole_t' = property(_ida_hexrays_micro.mcallinfo_t_role_get,
        _ida_hexrays_micro.mcallinfo_t_role_set)
    """function role
"""
    fti_attrs: 'type_attrs_t' = property(_ida_hexrays_micro.
        mcallinfo_t_fti_attrs_get, _ida_hexrays_micro.mcallinfo_t_fti_attrs_set
        )
    """extended function attributes
"""

    def __init__(self, *args):
        _ida_hexrays_micro.mcallinfo_t_swiginit(self, _ida_hexrays_micro.
            new_mcallinfo_t(*args))

    def lexcompare(self, f: 'mcallinfo_t') ->int:
        return _ida_hexrays_micro.mcallinfo_t_lexcompare(self, f)

    def set_type(self, type: 'tinfo_t') ->bool:
        return _ida_hexrays_micro.mcallinfo_t_set_type(self, type)

    def get_type(self) ->'tinfo_t':
        return _ida_hexrays_micro.mcallinfo_t_get_type(self)

    def is_vararg(self) ->bool:
        return _ida_hexrays_micro.mcallinfo_t_is_vararg(self)

    def _print(self, *args) ->None:
        return _ida_hexrays_micro.mcallinfo_t__print(self, *args)

    def dstr(self) ->str:
        return _ida_hexrays_micro.mcallinfo_t_dstr(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_mcallinfo_t


_ida_hexrays_micro.mcallinfo_t_swigregister(mcallinfo_t)
FCI_PROP = _ida_hexrays_micro.FCI_PROP
"""call has been propagated
"""
FCI_DEAD = _ida_hexrays_micro.FCI_DEAD
"""some return registers were determined dead
"""
FCI_FINAL = _ida_hexrays_micro.FCI_FINAL
"""call type is final, should not be changed
"""
FCI_NORET = _ida_hexrays_micro.FCI_NORET
"""call does not return
"""
FCI_PURE = _ida_hexrays_micro.FCI_PURE
"""pure function
"""
FCI_NOSIDE = _ida_hexrays_micro.FCI_NOSIDE
"""call does not have side effects
"""
FCI_SPLOK = _ida_hexrays_micro.FCI_SPLOK
"""spoiled/visible_memory lists have been optimized. for some functions we can reduce them as soon as information about the arguments becomes available. in order not to try optimize them again we use this bit. 
        """
FCI_HASCALL = _ida_hexrays_micro.FCI_HASCALL
"""A function is an synthetic helper combined from several instructions and at least one of them was a call to a real functions 
        """
FCI_HASFMT = _ida_hexrays_micro.FCI_HASFMT
"""A variadic function with recognized printf- or scanf-style format string 
        """
FCI_EXPLOCS = _ida_hexrays_micro.FCI_EXPLOCS
"""all arglocs are specified explicitly
"""


class mcases_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    values: 'casevec_t' = property(_ida_hexrays_micro.mcases_t_values_get,
        _ida_hexrays_micro.mcases_t_values_set)
    """expression values for each target
"""
    targets: 'intvec_t' = property(_ida_hexrays_micro.mcases_t_targets_get,
        _ida_hexrays_micro.mcases_t_targets_set)
    """target block numbers
"""

    def swap(self, r: 'mcases_t') ->None:
        return _ida_hexrays_micro.mcases_t_swap(self, r)

    def __eq__(self, r: 'mcases_t') ->bool:
        return _ida_hexrays_micro.mcases_t___eq__(self, r)

    def __ne__(self, r: 'mcases_t') ->bool:
        return _ida_hexrays_micro.mcases_t___ne__(self, r)

    def __lt__(self, r: 'mcases_t') ->bool:
        return _ida_hexrays_micro.mcases_t___lt__(self, r)

    def __gt__(self, r: 'mcases_t') ->bool:
        return _ida_hexrays_micro.mcases_t___gt__(self, r)

    def __le__(self, r: 'mcases_t') ->bool:
        return _ida_hexrays_micro.mcases_t___le__(self, r)

    def __ge__(self, r: 'mcases_t') ->bool:
        return _ida_hexrays_micro.mcases_t___ge__(self, r)

    def compare(self, r: 'mcases_t') ->int:
        return _ida_hexrays_micro.mcases_t_compare(self, r)

    def empty(self) ->bool:
        return _ida_hexrays_micro.mcases_t_empty(self)

    def size(self) ->int:
        return _ida_hexrays_micro.mcases_t_size(self)

    def resize(self, s: int) ->None:
        return _ida_hexrays_micro.mcases_t_resize(self, s)

    def _print(self) ->None:
        return _ida_hexrays_micro.mcases_t__print(self)

    def dstr(self) ->str:
        return _ida_hexrays_micro.mcases_t_dstr(self)

    def __init__(self):
        _ida_hexrays_micro.mcases_t_swiginit(self, _ida_hexrays_micro.
            new_mcases_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_mcases_t


_ida_hexrays_micro.mcases_t_swigregister(mcases_t)


class voff_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    off: int = property(_ida_hexrays_micro.voff_t_off_get,
        _ida_hexrays_micro.voff_t_off_set)
    """register number or stack offset
"""
    type: 'mopt_t' = property(_ida_hexrays_micro.voff_t_type_get,
        _ida_hexrays_micro.voff_t_type_set)
    """mop_r - register, mop_S - stack, mop_z - undefined
"""

    def __init__(self, *args):
        _ida_hexrays_micro.voff_t_swiginit(self, _ida_hexrays_micro.
            new_voff_t(*args))

    def set(self, _type: 'mopt_t', _off: int) ->None:
        return _ida_hexrays_micro.voff_t_set(self, _type, _off)

    def set_stkoff(self, stkoff: int) ->None:
        return _ida_hexrays_micro.voff_t_set_stkoff(self, stkoff)

    def set_reg(self, mreg: 'mreg_t') ->None:
        return _ida_hexrays_micro.voff_t_set_reg(self, mreg)

    def undef(self) ->None:
        return _ida_hexrays_micro.voff_t_undef(self)

    def defined(self) ->bool:
        return _ida_hexrays_micro.voff_t_defined(self)

    def is_reg(self) ->bool:
        return _ida_hexrays_micro.voff_t_is_reg(self)

    def is_stkoff(self) ->bool:
        return _ida_hexrays_micro.voff_t_is_stkoff(self)

    def get_reg(self) ->'mreg_t':
        return _ida_hexrays_micro.voff_t_get_reg(self)

    def get_stkoff(self) ->int:
        return _ida_hexrays_micro.voff_t_get_stkoff(self)

    def inc(self, delta: int) ->None:
        return _ida_hexrays_micro.voff_t_inc(self, delta)

    def add(self, width: int) ->'voff_t':
        return _ida_hexrays_micro.voff_t_add(self, width)

    def diff(self, r: 'voff_t') ->int:
        return _ida_hexrays_micro.voff_t_diff(self, r)

    def __eq__(self, r: 'voff_t') ->bool:
        return _ida_hexrays_micro.voff_t___eq__(self, r)

    def __ne__(self, r: 'voff_t') ->bool:
        return _ida_hexrays_micro.voff_t___ne__(self, r)

    def __lt__(self, r: 'voff_t') ->bool:
        return _ida_hexrays_micro.voff_t___lt__(self, r)

    def __gt__(self, r: 'voff_t') ->bool:
        return _ida_hexrays_micro.voff_t___gt__(self, r)

    def __le__(self, r: 'voff_t') ->bool:
        return _ida_hexrays_micro.voff_t___le__(self, r)

    def __ge__(self, r: 'voff_t') ->bool:
        return _ida_hexrays_micro.voff_t___ge__(self, r)

    def compare(self, r: 'voff_t') ->int:
        return _ida_hexrays_micro.voff_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_micro.delete_voff_t


_ida_hexrays_micro.voff_t_swigregister(voff_t)


class vivl_t(voff_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    size: int = property(_ida_hexrays_micro.vivl_t_size_get,
        _ida_hexrays_micro.vivl_t_size_set)
    """Interval size in bytes.
"""

    def __init__(self, *args):
        _ida_hexrays_micro.vivl_t_swiginit(self, _ida_hexrays_micro.
            new_vivl_t(*args))

    def set(self, *args) ->None:
        """This function has the following signatures:

    0. set(_type: mopt_t, _off: int, _size: int=0) -> None
    1. set(voff: const voff_t &, _size: int) -> None

# 0: set(_type: mopt_t, _off: int, _size: int=0) -> None


# 1: set(voff: const voff_t &, _size: int) -> None

"""
        return _ida_hexrays_micro.vivl_t_set(self, *args)

    def set_stkoff(self, stkoff: int, sz: int=0) ->None:
        return _ida_hexrays_micro.vivl_t_set_stkoff(self, stkoff, sz)

    def set_reg(self, mreg: 'mreg_t', sz: int=0) ->None:
        return _ida_hexrays_micro.vivl_t_set_reg(self, mreg, sz)

    def extend_to_cover(self, r: 'vivl_t') ->bool:
        """Extend a value interval using another value interval of the same type 
        
:returns: success"""
        return _ida_hexrays_micro.vivl_t_extend_to_cover(self, r)

    def intersect(self, r: 'vivl_t') ->int:
        """Intersect value intervals the same type 
        
:returns: size of the resulting intersection"""
        return _ida_hexrays_micro.vivl_t_intersect(self, r)

    def overlap(self, r: 'vivl_t') ->bool:
        """Do two value intervals overlap?
"""
        return _ida_hexrays_micro.vivl_t_overlap(self, r)

    def includes(self, r: 'vivl_t') ->bool:
        """Does our value interval include another?
"""
        return _ida_hexrays_micro.vivl_t_includes(self, r)

    def contains(self, voff2: 'voff_t') ->bool:
        """Does our value interval contain the specified value offset?
"""
        return _ida_hexrays_micro.vivl_t_contains(self, voff2)

    def __ne__(self, r: 'vivl_t') ->bool:
        return _ida_hexrays_micro.vivl_t___ne__(self, r)

    def __lt__(self, r: 'vivl_t') ->bool:
        return _ida_hexrays_micro.vivl_t___lt__(self, r)

    def __gt__(self, r: 'vivl_t') ->bool:
        return _ida_hexrays_micro.vivl_t___gt__(self, r)

    def __le__(self, r: 'vivl_t') ->bool:
        return _ida_hexrays_micro.vivl_t___le__(self, r)

    def __ge__(self, r: 'vivl_t') ->bool:
        return _ida_hexrays_micro.vivl_t___ge__(self, r)

    def compare(self, r: 'vivl_t') ->int:
        return _ida_hexrays_micro.vivl_t_compare(self, r)

    def __eq__(self, *args) ->bool:
        return _ida_hexrays_micro.vivl_t___eq__(self, *args)

    def _print(self) ->None:
        return _ida_hexrays_micro.vivl_t__print(self)

    def dstr(self) ->str:
        return _ida_hexrays_micro.vivl_t_dstr(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_vivl_t


_ida_hexrays_micro.vivl_t_swigregister(vivl_t)


class chain_t(ida_pro.intvec_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    width: int = property(_ida_hexrays_micro.chain_t_width_get,
        _ida_hexrays_micro.chain_t_width_set)
    """size of the value in bytes
"""
    varnum: int = property(_ida_hexrays_micro.chain_t_varnum_get,
        _ida_hexrays_micro.chain_t_varnum_set)
    """allocated variable index (-1 - not allocated yet)
"""
    flags: 'uchar' = property(_ida_hexrays_micro.chain_t_flags_get,
        _ida_hexrays_micro.chain_t_flags_set)
    """combination Chain properties bits 
        """

    def __init__(self, *args):
        _ida_hexrays_micro.chain_t_swiginit(self, _ida_hexrays_micro.
            new_chain_t(*args))

    def set_value(self, r: 'chain_t') ->None:
        return _ida_hexrays_micro.chain_t_set_value(self, r)

    def key(self) ->'voff_t const &':
        return _ida_hexrays_micro.chain_t_key(self)

    def is_inited(self) ->bool:
        return _ida_hexrays_micro.chain_t_is_inited(self)

    def is_reg(self) ->bool:
        return _ida_hexrays_micro.chain_t_is_reg(self)

    def is_stkoff(self) ->bool:
        return _ida_hexrays_micro.chain_t_is_stkoff(self)

    def is_replaced(self) ->bool:
        return _ida_hexrays_micro.chain_t_is_replaced(self)

    def is_overlapped(self) ->bool:
        return _ida_hexrays_micro.chain_t_is_overlapped(self)

    def is_fake(self) ->bool:
        return _ida_hexrays_micro.chain_t_is_fake(self)

    def is_passreg(self) ->bool:
        return _ida_hexrays_micro.chain_t_is_passreg(self)

    def is_term(self) ->bool:
        return _ida_hexrays_micro.chain_t_is_term(self)

    def set_inited(self, b: bool) ->None:
        return _ida_hexrays_micro.chain_t_set_inited(self, b)

    def set_replaced(self, b: bool) ->None:
        return _ida_hexrays_micro.chain_t_set_replaced(self, b)

    def set_overlapped(self, b: bool) ->None:
        return _ida_hexrays_micro.chain_t_set_overlapped(self, b)

    def set_term(self, b: bool) ->None:
        return _ida_hexrays_micro.chain_t_set_term(self, b)

    def get_reg(self) ->'mreg_t':
        return _ida_hexrays_micro.chain_t_get_reg(self)

    def get_stkoff(self) ->int:
        return _ida_hexrays_micro.chain_t_get_stkoff(self)

    def overlap(self, r: 'chain_t') ->bool:
        return _ida_hexrays_micro.chain_t_overlap(self, r)

    def includes(self, r: 'chain_t') ->bool:
        return _ida_hexrays_micro.chain_t_includes(self, r)

    def endoff(self) ->'voff_t const':
        return _ida_hexrays_micro.chain_t_endoff(self)

    def __lt__(self, r: 'chain_t') ->bool:
        return _ida_hexrays_micro.chain_t___lt__(self, r)

    def _print(self) ->None:
        return _ida_hexrays_micro.chain_t__print(self)

    def dstr(self) ->str:
        return _ida_hexrays_micro.chain_t_dstr(self)

    def append_list(self, mba: 'mba_t', list: 'mlist_t') ->None:
        """Append the contents of the chain to the specified list of locations.
"""
        return _ida_hexrays_micro.chain_t_append_list(self, mba, list)

    def clear_varnum(self) ->None:
        return _ida_hexrays_micro.chain_t_clear_varnum(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_chain_t


_ida_hexrays_micro.chain_t_swigregister(chain_t)
CHF_INITED = _ida_hexrays_micro.CHF_INITED
"""is chain initialized? (valid only after lvar allocation)
"""
CHF_REPLACED = _ida_hexrays_micro.CHF_REPLACED
"""chain operands have been replaced?
"""
CHF_OVER = _ida_hexrays_micro.CHF_OVER
"""overlapped chain
"""
CHF_FAKE = _ida_hexrays_micro.CHF_FAKE
"""fake chain created by widen_chains()
"""
CHF_PASSTHRU = _ida_hexrays_micro.CHF_PASSTHRU
"""pass-thru chain, must use the input variable to the block
"""
CHF_TERM = _ida_hexrays_micro.CHF_TERM
"""terminating chain; the variable does not survive across the block
"""


class block_chains_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def get_reg_chain(self, reg: 'mreg_t', width: int=1) ->'chain_t *':
        """Get chain for the specified register 
        
:param reg: register number
:param width: size of register in bytes"""
        return _ida_hexrays_micro.block_chains_t_get_reg_chain(self, reg, width
            )

    def get_stk_chain(self, off: int, width: int=1) ->'chain_t *':
        """Get chain for the specified stack offset 
        
:param off: stack offset
:param width: size of stack value in bytes"""
        return _ida_hexrays_micro.block_chains_t_get_stk_chain(self, off, width
            )

    def get_chain(self, *args) ->'chain_t *':
        """This function has the following signatures:

    0. get_chain(k: const voff_t &, width: int=1) -> const chain_t *
    1. get_chain(k: const voff_t &, width: int=1) -> chain_t *
    2. get_chain(ch: const chain_t &) -> const chain_t *
    3. get_chain(ch: const chain_t &) -> chain_t *

# 0: get_chain(k: const voff_t &, width: int=1) -> const chain_t *

Get chain for the specified value offset. 
        

# 1: get_chain(k: const voff_t &, width: int=1) -> chain_t *


# 2: get_chain(ch: const chain_t &) -> const chain_t *

Get chain similar to the specified chain 
        

# 3: get_chain(ch: const chain_t &) -> chain_t *

"""
        return _ida_hexrays_micro.block_chains_t_get_chain(self, *args)

    def _print(self) ->None:
        return _ida_hexrays_micro.block_chains_t__print(self)

    def dstr(self) ->str:
        return _ida_hexrays_micro.block_chains_t_dstr(self)

    def __init__(self):
        _ida_hexrays_micro.block_chains_t_swiginit(self, _ida_hexrays_micro
            .new_block_chains_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_block_chains_t


_ida_hexrays_micro.block_chains_t_swigregister(block_chains_t)


class chain_visitor_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    parent: 'block_chains_t *' = property(_ida_hexrays_micro.
        chain_visitor_t_parent_get, _ida_hexrays_micro.
        chain_visitor_t_parent_set)
    """parent of the current chain
"""
    __swig_destroy__ = _ida_hexrays_micro.delete_chain_visitor_t

    def visit_chain(self, nblock: int, ch: 'chain_t') ->int:
        return _ida_hexrays_micro.chain_visitor_t_visit_chain(self, nblock, ch)

    def __init__(self):
        if self.__class__ == chain_visitor_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.chain_visitor_t_swiginit(self,
            _ida_hexrays_micro.new_chain_visitor_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_chain_visitor_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.chain_visitor_t_swigregister(chain_visitor_t)


class graph_chains_t(block_chains_vec_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    __swig_destroy__ = _ida_hexrays_micro.delete_graph_chains_t

    def for_all_chains(self, cv: 'chain_visitor_t', gca_flags: int) ->int:
        """Visit all chains 
        
:param cv: chain visitor
:param gca_flags: combination of GCA_ bits"""
        return _ida_hexrays_micro.graph_chains_t_for_all_chains(self, cv,
            gca_flags)

    def is_locked(self) ->bool:
        """Are the chains locked? It is a good idea to lock the chains before using them. This ensures that they won't be recalculated and reallocated during the use. See the chain_keeper_t class for that. 
        """
        return _ida_hexrays_micro.graph_chains_t_is_locked(self)

    def acquire(self) ->None:
        """Lock the chains.
"""
        return _ida_hexrays_micro.graph_chains_t_acquire(self)

    def release(self) ->None:
        """Unlock the chains.
"""
        return _ida_hexrays_micro.graph_chains_t_release(self)

    def swap(self, r: 'graph_chains_t') ->None:
        return _ida_hexrays_micro.graph_chains_t_swap(self, r)

    def __init__(self):
        _ida_hexrays_micro.graph_chains_t_swiginit(self, _ida_hexrays_micro
            .new_graph_chains_t())


_ida_hexrays_micro.graph_chains_t_swigregister(graph_chains_t)
GCA_EMPTY = _ida_hexrays_micro.GCA_EMPTY
"""include empty chains
"""
GCA_SPEC = _ida_hexrays_micro.GCA_SPEC
"""include chains for special registers
"""
GCA_ALLOC = _ida_hexrays_micro.GCA_ALLOC
"""enumerate only allocated chains
"""
GCA_NALLOC = _ida_hexrays_micro.GCA_NALLOC
"""enumerate only non-allocated chains
"""
GCA_OFIRST = _ida_hexrays_micro.GCA_OFIRST
"""consider only chains of the first block
"""
GCA_OLAST = _ida_hexrays_micro.GCA_OLAST
"""consider only chains of the last block
"""


class minsn_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    opcode: 'mcode_t' = property(_ida_hexrays_micro.minsn_t_opcode_get,
        _ida_hexrays_micro.minsn_t_opcode_set)
    """instruction opcode
"""
    iprops: int = property(_ida_hexrays_micro.minsn_t_iprops_get,
        _ida_hexrays_micro.minsn_t_iprops_set)
    """combination of instruction property bits bits
"""
    next: 'minsn_t *' = property(_ida_hexrays_micro.minsn_t_next_get,
        _ida_hexrays_micro.minsn_t_next_set)
    """next insn in doubly linked list. check also nexti()
"""
    prev: 'minsn_t *' = property(_ida_hexrays_micro.minsn_t_prev_get,
        _ida_hexrays_micro.minsn_t_prev_set)
    """prev insn in doubly linked list. check also previ()
"""
    ea: ida_idaapi.ea_t = property(_ida_hexrays_micro.minsn_t_ea_get,
        _ida_hexrays_micro.minsn_t_ea_set)
    """instruction address
"""
    l: 'mop_t' = property(_ida_hexrays_micro.minsn_t_l_get,
        _ida_hexrays_micro.minsn_t_l_set)
    """left operand
"""
    r: 'mop_t' = property(_ida_hexrays_micro.minsn_t_r_get,
        _ida_hexrays_micro.minsn_t_r_set)
    """right operand
"""
    d: 'mop_t' = property(_ida_hexrays_micro.minsn_t_d_get,
        _ida_hexrays_micro.minsn_t_d_set)
    """destination operand
"""

    def is_optional(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_optional(self)

    def is_combined(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_combined(self)

    def is_farcall(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_farcall(self)

    def is_cleaning_pop(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_cleaning_pop(self)

    def is_extstx(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_extstx(self)

    def is_tailcall(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_tailcall(self)

    def is_fpinsn(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_fpinsn(self)

    def is_assert(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_assert(self)

    def is_persistent(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_persistent(self)

    def is_wild_match(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_wild_match(self)

    def is_propagatable(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_propagatable(self)

    def is_ignlowsrc(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_ignlowsrc(self)

    def is_inverted_jx(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_inverted_jx(self)

    def was_noret_icall(self) ->bool:
        return _ida_hexrays_micro.minsn_t_was_noret_icall(self)

    def is_multimov(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_multimov(self)

    def is_combinable(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_combinable(self)

    def was_split(self) ->bool:
        return _ida_hexrays_micro.minsn_t_was_split(self)

    def is_mbarrier(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_mbarrier(self)

    def was_unmerged(self) ->bool:
        return _ida_hexrays_micro.minsn_t_was_unmerged(self)

    def was_unpaired(self) ->bool:
        return _ida_hexrays_micro.minsn_t_was_unpaired(self)

    def set_optional(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_optional(self)

    def clr_combined(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_combined(self)

    def set_farcall(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_farcall(self)

    def set_cleaning_pop(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_cleaning_pop(self)

    def set_extstx(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_extstx(self)

    def set_tailcall(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_tailcall(self)

    def clr_tailcall(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_tailcall(self)

    def set_fpinsn(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_fpinsn(self)

    def clr_fpinsn(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_fpinsn(self)

    def set_assert(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_assert(self)

    def clr_assert(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_assert(self)

    def set_persistent(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_persistent(self)

    def set_wild_match(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_wild_match(self)

    def clr_propagatable(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_propagatable(self)

    def set_ignlowsrc(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_ignlowsrc(self)

    def clr_ignlowsrc(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_ignlowsrc(self)

    def set_inverted_jx(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_inverted_jx(self)

    def set_noret_icall(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_noret_icall(self)

    def clr_noret_icall(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_noret_icall(self)

    def set_multimov(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_multimov(self)

    def clr_multimov(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_multimov(self)

    def set_combinable(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_combinable(self)

    def clr_combinable(self) ->None:
        return _ida_hexrays_micro.minsn_t_clr_combinable(self)

    def set_mbarrier(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_mbarrier(self)

    def set_unmerged(self) ->None:
        return _ida_hexrays_micro.minsn_t_set_unmerged(self)

    def set_split_size(self, s: int) ->None:
        return _ida_hexrays_micro.minsn_t_set_split_size(self, s)

    def get_split_size(self) ->int:
        return _ida_hexrays_micro.minsn_t_get_split_size(self)

    def __init__(self, *args):
        _ida_hexrays_micro.minsn_t_swiginit(self, _ida_hexrays_micro.
            new_minsn_t(*args))

    def swap(self, m: 'minsn_t') ->None:
        """Swap two instructions. The prev/next fields are not modified by this function because it would corrupt the doubly linked list. 
        """
        return _ida_hexrays_micro.minsn_t_swap(self, m)

    def _print(self, *args) ->None:
        return _ida_hexrays_micro.minsn_t__print(self, *args)

    def dstr(self) ->str:
        """Get displayable text without tags in a static buffer.
"""
        return _ida_hexrays_micro.minsn_t_dstr(self)

    def setaddr(self, new_ea: ida_idaapi.ea_t) ->None:
        """Change the instruction address. This function modifies subinstructions as well. 
        """
        return _ida_hexrays_micro.minsn_t_setaddr(self, new_ea)

    def optimize_solo(self, optflags: int=0) ->int:
        """Optimize one instruction without context. This function does not have access to the instruction context (the previous and next instructions in the list, the block number, etc). It performs only basic optimizations that are available without this info. 
        
:param optflags: combination of optimization flags bits
:returns: number of changes, 0-unchanged See also mblock_t::optimize_insn()"""
        return _ida_hexrays_micro.minsn_t_optimize_solo(self, optflags)

    def optimize_subtree(self, blk: 'mblock_t', top: 'minsn_t', parent:
        'minsn_t', converted_call: 'ea_t *', optflags: int=2) ->int:
        """Optimize instruction in its context. Do not use this function, use mblock_t::optimize() 
        """
        return _ida_hexrays_micro.minsn_t_optimize_subtree(self, blk, top,
            parent, converted_call, optflags)

    def for_all_ops(self, mv: 'mop_visitor_t') ->int:
        """Visit all instruction operands. This function visits subinstruction operands as well. 
        
:param mv: operand visitor
:returns: non-zero value returned by mv.visit_mop() or zero"""
        return _ida_hexrays_micro.minsn_t_for_all_ops(self, mv)

    def for_all_insns(self, mv: 'minsn_visitor_t') ->int:
        """Visit all instructions. This function visits the instruction itself and all its subinstructions. 
        
:param mv: instruction visitor
:returns: non-zero value returned by mv.visit_mop() or zero"""
        return _ida_hexrays_micro.minsn_t_for_all_insns(self, mv)

    def _make_nop(self) ->None:
        """Convert instruction to nop. This function erases all info but the prev/next fields. In most cases it is better to use mblock_t::make_nop(), which also marks the block lists as dirty. 
        """
        return _ida_hexrays_micro.minsn_t__make_nop(self)

    def equal_insns(self, m: 'minsn_t', eqflags: int) ->bool:
        """Compare instructions. This is the main comparison function for instructions. 
        
:param m: instruction to compare with
:param eqflags: combination of comparison bits bits"""
        return _ida_hexrays_micro.minsn_t_equal_insns(self, m, eqflags)

    def __lt__(self, ri: 'minsn_t') ->bool:
        return _ida_hexrays_micro.minsn_t___lt__(self, ri)

    def lexcompare(self, ri: 'minsn_t') ->int:
        return _ida_hexrays_micro.minsn_t_lexcompare(self, ri)

    def is_noret_call(self, flags: int=0) ->bool:
        """Is a non-returing call? 
        
:param flags: combination of NORET_... bits"""
        return _ida_hexrays_micro.minsn_t_is_noret_call(self, flags)

    def is_unknown_call(self) ->bool:
        """Is an unknown call? Unknown calls are calls without the argument list (mcallinfo_t). Usually the argument lists are determined by mba_t::analyze_calls(). Unknown calls exist until the MMAT_CALLS maturity level. See also mblock_t::is_call_block 
        """
        return _ida_hexrays_micro.minsn_t_is_unknown_call(self)

    def is_helper(self, name: str) ->bool:
        """Is a helper call with the specified name? Helper calls usually have well-known function names (see Well known function names) but they may have any other name. The decompiler does not assume any special meaning for non-well-known names. 
        """
        return _ida_hexrays_micro.minsn_t_is_helper(self, name)

    def find_call(self, with_helpers: bool=False) ->'minsn_t *':
        """Find a call instruction. Check for the current instruction and its subinstructions. 
        
:param with_helpers: consider helper calls as well?"""
        return _ida_hexrays_micro.minsn_t_find_call(self, with_helpers)

    def contains_call(self, with_helpers: bool=False) ->bool:
        """Does the instruction contain a call?
"""
        return _ida_hexrays_micro.minsn_t_contains_call(self, with_helpers)

    def has_side_effects(self, include_ldx_and_divs: bool=False) ->bool:
        """Does the instruction have a side effect? 
        
:param include_ldx_and_divs: consider ldx/div/mod as having side effects? stx is always considered as having side effects. Apart from ldx/std only call may have side effects."""
        return _ida_hexrays_micro.minsn_t_has_side_effects(self,
            include_ldx_and_divs)

    def get_role(self) ->'funcrole_t':
        """Get the function role of a call.
"""
        return _ida_hexrays_micro.minsn_t_get_role(self)

    def is_memcpy(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_memcpy(self)

    def is_memset(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_memset(self)

    def is_alloca(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_alloca(self)

    def is_bswap(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_bswap(self)

    def is_readflags(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_readflags(self)

    def contains_opcode(self, mcode: 'mcode_t') ->bool:
        """Does the instruction have the specified opcode? This function searches subinstructions as well. 
        
:param mcode: opcode to search for."""
        return _ida_hexrays_micro.minsn_t_contains_opcode(self, mcode)

    def find_opcode(self, mcode: 'mcode_t') ->'minsn_t *':
        """Find a (sub)insruction with the specified opcode. 
        
:param mcode: opcode to search for."""
        return _ida_hexrays_micro.minsn_t_find_opcode(self, mcode)

    def find_ins_op(self, op: 'mcode_t'=m_nop) ->'minsn_t *':
        """Find an operand that is a subinsruction with the specified opcode. This function checks only the 'l' and 'r' operands of the current insn. 
        
:param op: opcode to search for
:returns: &l or &r or nullptr"""
        return _ida_hexrays_micro.minsn_t_find_ins_op(self, op)

    def find_num_op(self) ->'mop_t *':
        """Find a numeric operand of the current instruction. This function checks only the 'l' and 'r' operands of the current insn. 
        
:returns: &l or &r or nullptr"""
        return _ida_hexrays_micro.minsn_t_find_num_op(self)

    def is_mov(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_mov(self)

    def is_like_move(self) ->bool:
        return _ida_hexrays_micro.minsn_t_is_like_move(self)

    def modifies_d(self) ->bool:
        """Does the instruction modify its 'd' operand? Some instructions (e.g. m_stx) do not modify the 'd' operand. 
        """
        return _ida_hexrays_micro.minsn_t_modifies_d(self)

    def modifies_pair_mop(self) ->bool:
        return _ida_hexrays_micro.minsn_t_modifies_pair_mop(self)

    def is_between(self, m1: 'minsn_t', m2: 'minsn_t') ->bool:
        """Is the instruction in the specified range of instructions? 
        
:param m1: beginning of the range in the doubly linked list
:param m2: end of the range in the doubly linked list (excluded, may be nullptr) This function assumes that m1 and m2 belong to the same basic block and they are top level instructions."""
        return _ida_hexrays_micro.minsn_t_is_between(self, m1, m2)

    def is_after(self, m: 'minsn_t') ->bool:
        """Is the instruction after the specified one? 
        
:param m: the instruction to compare against in the list"""
        return _ida_hexrays_micro.minsn_t_is_after(self, m)

    def may_use_aliased_memory(self) ->bool:
        """Is it possible for the instruction to use aliased memory?
"""
        return _ida_hexrays_micro.minsn_t_may_use_aliased_memory(self)

    def serialize(self, b: 'bytevec_t *') ->int:
        """Serialize an instruction 
        
:param b: the output buffer
:returns: the serialization format that was used to store info"""
        return _ida_hexrays_micro.minsn_t_serialize(self, b)

    def deserialize(self, bytes: 'uchar const *', format_version: int) ->bool:
        """Deserialize an instruction 
        
:param bytes: pointer to serialized data
:param format_version: serialization format version. this value is returned by minsn_t::serialize()
:returns: success"""
        return _ida_hexrays_micro.minsn_t_deserialize(self, bytes,
            format_version)

    def _register(self) ->None:
        return _ida_hexrays_micro.minsn_t__register(self)

    def _deregister(self) ->None:
        return _ida_hexrays_micro.minsn_t__deregister(self)

    def __dbg_get_meminfo(self) ->str:
        return _ida_hexrays_micro.minsn_t___dbg_get_meminfo(self)

    def __dbg_get_registered_kind(self) ->int:
        return _ida_hexrays_micro.minsn_t___dbg_get_registered_kind(self)

    def _obj_id(self) ->'PyObject *':
        return _ida_hexrays_micro.minsn_t__obj_id(self)
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
    __swig_destroy__ = _ida_hexrays_micro.delete_minsn_t


_ida_hexrays_micro.minsn_t_swigregister(minsn_t)
IPROP_OPTIONAL = _ida_hexrays_micro.IPROP_OPTIONAL
"""optional instruction
"""
IPROP_PERSIST = _ida_hexrays_micro.IPROP_PERSIST
"""persistent insn; they are not destroyed
"""
IPROP_WILDMATCH = _ida_hexrays_micro.IPROP_WILDMATCH
"""match multiple insns
"""
IPROP_CLNPOP = _ida_hexrays_micro.IPROP_CLNPOP
"""the purpose of the instruction is to clean stack (e.g. "pop ecx" is often used for that) 
        """
IPROP_FPINSN = _ida_hexrays_micro.IPROP_FPINSN
"""floating point insn
"""
IPROP_FARCALL = _ida_hexrays_micro.IPROP_FARCALL
"""call of a far function using push cs/call sequence
"""
IPROP_TAILCALL = _ida_hexrays_micro.IPROP_TAILCALL
"""tail call
"""
IPROP_ASSERT = _ida_hexrays_micro.IPROP_ASSERT
"""assertion: usually mov #val, op. assertions are used to help the optimizer. assertions are ignored when generating ctree 
        """
IPROP_SPLIT = _ida_hexrays_micro.IPROP_SPLIT
"""the instruction has been split:
"""
IPROP_SPLIT1 = _ida_hexrays_micro.IPROP_SPLIT1
"""into 1 byte
"""
IPROP_SPLIT2 = _ida_hexrays_micro.IPROP_SPLIT2
"""into 2 bytes
"""
IPROP_SPLIT4 = _ida_hexrays_micro.IPROP_SPLIT4
"""into 4 bytes
"""
IPROP_SPLIT8 = _ida_hexrays_micro.IPROP_SPLIT8
"""into 8 bytes
"""
IPROP_COMBINED = _ida_hexrays_micro.IPROP_COMBINED
"""insn has been modified because of a partial reference
"""
IPROP_EXTSTX = _ida_hexrays_micro.IPROP_EXTSTX
"""this is m_ext propagated into m_stx
"""
IPROP_IGNLOWSRC = _ida_hexrays_micro.IPROP_IGNLOWSRC
"""low part of the instruction source operand has been created artificially (this bit is used only for 'and x, 80...') 
        """
IPROP_INV_JX = _ida_hexrays_micro.IPROP_INV_JX
"""inverted conditional jump
"""
IPROP_WAS_NORET = _ida_hexrays_micro.IPROP_WAS_NORET
"""was noret icall
"""
IPROP_MULTI_MOV = _ida_hexrays_micro.IPROP_MULTI_MOV
"""bits that can be set by plugins:

the minsn was generated as part of insn that moves multiple registers (example: STM on ARM may transfer multiple registers) 
        """
IPROP_DONT_PROP = _ida_hexrays_micro.IPROP_DONT_PROP
"""may not propagate
"""
IPROP_DONT_COMB = _ida_hexrays_micro.IPROP_DONT_COMB
"""may not combine this instruction with others
"""
IPROP_MBARRIER = _ida_hexrays_micro.IPROP_MBARRIER
"""this instruction acts as a memory barrier (instructions accessing memory may not be reordered past it) 
        """
IPROP_UNMERGED = _ida_hexrays_micro.IPROP_UNMERGED
"""'goto' instruction was transformed info 'call'
"""
IPROP_UNPAIRED = _ida_hexrays_micro.IPROP_UNPAIRED
"""instruction is a result of del_dest_pairs() transformation
"""
OPTI_ADDREXPRS = _ida_hexrays_micro.OPTI_ADDREXPRS
"""optimize all address expressions (&x+N; &x-&y)
"""
OPTI_MINSTKREF = _ida_hexrays_micro.OPTI_MINSTKREF
"""may update minstkref
"""
OPTI_COMBINSNS = _ida_hexrays_micro.OPTI_COMBINSNS
"""may combine insns (only for optimize_insn)
"""
OPTI_NO_LDXOPT = _ida_hexrays_micro.OPTI_NO_LDXOPT
"""the function is called after the propagation attempt, we do not optimize low/high(ldx) in this case 
        """
OPTI_NO_VALRNG = _ida_hexrays_micro.OPTI_NO_VALRNG
"""forbid using valranges
"""
EQ_IGNSIZE = _ida_hexrays_micro.EQ_IGNSIZE
"""ignore source operand sizes
"""
EQ_IGNCODE = _ida_hexrays_micro.EQ_IGNCODE
"""ignore instruction opcodes
"""
EQ_CMPDEST = _ida_hexrays_micro.EQ_CMPDEST
"""compare instruction destinations
"""
EQ_OPTINSN = _ida_hexrays_micro.EQ_OPTINSN
"""optimize mop_d operands
"""
NORET_IGNORE_WAS_NORET_ICALL = _ida_hexrays_micro.NORET_IGNORE_WAS_NORET_ICALL
NORET_FORBID_ANALYSIS = _ida_hexrays_micro.NORET_FORBID_ANALYSIS


def getf_reginsn(ins: 'minsn_t') ->'minsn_t *':
    """Skip assertions forward.
"""
    return _ida_hexrays_micro.getf_reginsn(ins)


def getb_reginsn(ins: 'minsn_t') ->'minsn_t *':
    """Skip assertions backward.
"""
    return _ida_hexrays_micro.getb_reginsn(ins)


class intval64_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    val: 'uint64' = property(_ida_hexrays_micro.intval64_t_val_get,
        _ida_hexrays_micro.intval64_t_val_set)
    size: int = property(_ida_hexrays_micro.intval64_t_size_get,
        _ida_hexrays_micro.intval64_t_size_set)

    def __init__(self, v: 'uint64'=0, _s: int=1):
        _ida_hexrays_micro.intval64_t_swiginit(self, _ida_hexrays_micro.
            new_intval64_t(v, _s))

    def sval(self) ->'int64':
        return _ida_hexrays_micro.intval64_t_sval(self)

    def uval(self) ->'uint64':
        return _ida_hexrays_micro.intval64_t_uval(self)

    def _print(self) ->None:
        return _ida_hexrays_micro.intval64_t__print(self)

    def __eq__(self, o: 'intval64_t') ->bool:
        return _ida_hexrays_micro.intval64_t___eq__(self, o)

    def __ne__(self, o: 'intval64_t') ->bool:
        return _ida_hexrays_micro.intval64_t___ne__(self, o)

    def __lt__(self, o: 'intval64_t') ->bool:
        return _ida_hexrays_micro.intval64_t___lt__(self, o)

    def sext(self, target_sz: int) ->'intval64_t':
        return _ida_hexrays_micro.intval64_t_sext(self, target_sz)

    def zext(self, target_sz: int) ->'intval64_t':
        return _ida_hexrays_micro.intval64_t_zext(self, target_sz)

    def low(self, target_sz: int) ->'intval64_t':
        return _ida_hexrays_micro.intval64_t_low(self, target_sz)

    def high(self, target_sz: int) ->'intval64_t':
        return _ida_hexrays_micro.intval64_t_high(self, target_sz)

    def __add__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___add__(self, o)

    def __sub__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___sub__(self, o)

    def __mul__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___mul__(self, o)

    def __truediv__(self, *args):
        return _ida_hexrays_micro.intval64_t___truediv__(self, *args)
    __div__ = __truediv__

    def sdiv(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t_sdiv(self, o)

    def __mod__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___mod__(self, o)

    def smod(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t_smod(self, o)

    def __lshift__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___lshift__(self, o)

    def __rshift__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___rshift__(self, o)

    def sar(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t_sar(self, o)

    def __or__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___or__(self, o)

    def __and__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___and__(self, o)

    def __xor__(self, o: 'intval64_t') ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___xor__(self, o)

    def __neg__(self) ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___neg__(self)

    def __invert__(self) ->'intval64_t':
        return _ida_hexrays_micro.intval64_t___invert__(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_intval64_t


_ida_hexrays_micro.intval64_t_swigregister(intval64_t)


class int64_emulator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    __swig_destroy__ = _ida_hexrays_micro.delete_int64_emulator_t

    def get_mop_value(self, mop: 'mop_t') ->'intval64_t':
        return _ida_hexrays_micro.int64_emulator_t_get_mop_value(self, mop)

    def _mop_value(self, out: 'intval64_t', mop: 'mop_t', vf:
        'vd_failure_t'=None) ->bool:
        return _ida_hexrays_micro.int64_emulator_t__mop_value(self, out,
            mop, vf)

    def mop_value(self, mop: 'mop_t') ->'intval64_t':
        return _ida_hexrays_micro.int64_emulator_t_mop_value(self, mop)

    def _minsn_value(self, out: 'intval64_t', insn: 'minsn_t', vf:
        'vd_failure_t'=None) ->bool:
        return _ida_hexrays_micro.int64_emulator_t__minsn_value(self, out,
            insn, vf)

    def minsn_value(self, insn: 'minsn_t') ->'intval64_t':
        return _ida_hexrays_micro.int64_emulator_t_minsn_value(self, insn)

    def __init__(self):
        if self.__class__ == int64_emulator_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_micro.int64_emulator_t_swiginit(self,
            _ida_hexrays_micro.new_int64_emulator_t(_self))

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_micro.disown_int64_emulator_t(self)
        return weakref.proxy(self)


_ida_hexrays_micro.int64_emulator_t_swigregister(int64_emulator_t)
BLT_NONE = _ida_hexrays_micro.BLT_NONE
"""unknown block type
"""
BLT_STOP = _ida_hexrays_micro.BLT_STOP
"""stops execution regularly (must be the last block)
"""
BLT_0WAY = _ida_hexrays_micro.BLT_0WAY
"""does not have successors (tail is a noret function)
"""
BLT_1WAY = _ida_hexrays_micro.BLT_1WAY
"""passes execution to one block (regular or goto block)
"""
BLT_2WAY = _ida_hexrays_micro.BLT_2WAY
"""passes execution to two blocks (conditional jump)
"""
BLT_NWAY = _ida_hexrays_micro.BLT_NWAY
"""passes execution to many blocks (switch idiom)
"""
BLT_XTRN = _ida_hexrays_micro.BLT_XTRN
"""external block (out of function address)
"""


class mblock_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined')
    __repr__ = _swig_repr
    nextb: 'mblock_t *' = property(_ida_hexrays_micro.mblock_t_nextb_get,
        _ida_hexrays_micro.mblock_t_nextb_set)
    """next block in the doubly linked list
"""
    prevb: 'mblock_t *' = property(_ida_hexrays_micro.mblock_t_prevb_get,
        _ida_hexrays_micro.mblock_t_prevb_set)
    """previous block in the doubly linked list
"""
    flags: int = property(_ida_hexrays_micro.mblock_t_flags_get,
        _ida_hexrays_micro.mblock_t_flags_set)
    """combination of Basic block properties bits 
        """
    start: ida_idaapi.ea_t = property(_ida_hexrays_micro.mblock_t_start_get,
        _ida_hexrays_micro.mblock_t_start_set)
    """start address
"""
    end: ida_idaapi.ea_t = property(_ida_hexrays_micro.mblock_t_end_get,
        _ida_hexrays_micro.mblock_t_end_set)
    """end address note: we cannot rely on start/end addresses very much because instructions are propagated between blocks 
        """
    head: 'minsn_t *' = property(_ida_hexrays_micro.mblock_t_head_get,
        _ida_hexrays_micro.mblock_t_head_set)
    """pointer to the first instruction of the block
"""
    tail: 'minsn_t *' = property(_ida_hexrays_micro.mblock_t_tail_get,
        _ida_hexrays_micro.mblock_t_tail_set)
    """pointer to the last instruction of the block
"""
    mba: 'mba_t *' = property(_ida_hexrays_micro.mblock_t_mba_get,
        _ida_hexrays_micro.mblock_t_mba_set)
    """the parent micro block array
"""
    serial: int = property(_ida_hexrays_micro.mblock_t_serial_get,
        _ida_hexrays_micro.mblock_t_serial_set)
    """block number
"""
    type: 'mblock_type_t' = property(_ida_hexrays_micro.mblock_t_type_get,
        _ida_hexrays_micro.mblock_t_type_set)
    """block type (BLT_NONE - not computed yet)
"""
    dead_at_start: 'mlist_t' = property(_ida_hexrays_micro.
        mblock_t_dead_at_start_get, _ida_hexrays_micro.
        mblock_t_dead_at_start_set)
    """data that is dead at the block entry
"""
    mustbuse: 'mlist_t' = property(_ida_hexrays_micro.mblock_t_mustbuse_get,
        _ida_hexrays_micro.mblock_t_mustbuse_set)
    """data that must be used by the block
"""
    maybuse: 'mlist_t' = property(_ida_hexrays_micro.mblock_t_maybuse_get,
        _ida_hexrays_micro.mblock_t_maybuse_set)
    """data that may be used by the block
"""
    mustbdef: 'mlist_t' = property(_ida_hexrays_micro.mblock_t_mustbdef_get,
        _ida_hexrays_micro.mblock_t_mustbdef_set)
    """data that must be defined by the block
"""
    maybdef: 'mlist_t' = property(_ida_hexrays_micro.mblock_t_maybdef_get,
        _ida_hexrays_micro.mblock_t_maybdef_set)
    """data that may be defined by the block
"""
    dnu: 'mlist_t' = property(_ida_hexrays_micro.mblock_t_dnu_get,
        _ida_hexrays_micro.mblock_t_dnu_set)
    """data that is defined but not used in the block
"""
    maxbsp: int = property(_ida_hexrays_micro.mblock_t_maxbsp_get,
        _ida_hexrays_micro.mblock_t_maxbsp_set)
    """maximal sp value in the block (0...stacksize)
"""
    minbstkref: int = property(_ida_hexrays_micro.mblock_t_minbstkref_get,
        _ida_hexrays_micro.mblock_t_minbstkref_set)
    """lowest stack location accessible with indirect addressing (offset from the stack bottom) initially it is 0 (not computed) 
        """
    minbargref: int = property(_ida_hexrays_micro.mblock_t_minbargref_get,
        _ida_hexrays_micro.mblock_t_minbargref_set)
    """the same for arguments
"""
    predset: 'intvec_t' = property(_ida_hexrays_micro.mblock_t_predset_get,
        _ida_hexrays_micro.mblock_t_predset_set)
    """control flow graph: list of our predecessors use npred() and pred() to access it 
        """
    succset: 'intvec_t' = property(_ida_hexrays_micro.mblock_t_succset_get,
        _ida_hexrays_micro.mblock_t_succset_set)
    """control flow graph: list of our successors use nsucc() and succ() to access it 
        """

    def mark_lists_dirty(self) ->None:
        return _ida_hexrays_micro.mblock_t_mark_lists_dirty(self)

    def request_propagation(self) ->None:
        return _ida_hexrays_micro.mblock_t_request_propagation(self)

    def needs_propagation(self) ->bool:
        return _ida_hexrays_micro.mblock_t_needs_propagation(self)

    def request_demote64(self) ->None:
        return _ida_hexrays_micro.mblock_t_request_demote64(self)

    def lists_dirty(self) ->bool:
        return _ida_hexrays_micro.mblock_t_lists_dirty(self)

    def lists_ready(self) ->bool:
        return _ida_hexrays_micro.mblock_t_lists_ready(self)

    def make_lists_ready(self) ->int:
        return _ida_hexrays_micro.mblock_t_make_lists_ready(self)

    def npred(self) ->int:
        """Get number of block predecessors.
"""
        return _ida_hexrays_micro.mblock_t_npred(self)

    def nsucc(self) ->int:
        """Get number of block successors.
"""
        return _ida_hexrays_micro.mblock_t_nsucc(self)

    def pred(self, n: int) ->int:
        return _ida_hexrays_micro.mblock_t_pred(self, n)

    def succ(self, n: int) ->int:
        return _ida_hexrays_micro.mblock_t_succ(self, n)
    __swig_destroy__ = _ida_hexrays_micro.delete_mblock_t

    def empty(self) ->bool:
        return _ida_hexrays_micro.mblock_t_empty(self)

    def _print(self, vp: 'vd_printer_t') ->None:
        return _ida_hexrays_micro.mblock_t__print(self, vp)

    def dump(self) ->None:
        """Dump block info. This function is useful for debugging, see mba_t::dump for info 
        """
        return _ida_hexrays_micro.mblock_t_dump(self)

    def dump_block(self, title: str) ->None:
        return _ida_hexrays_micro.mblock_t_dump_block(self, title)

    def verify_insn(self, m: 'minsn_t') ->None:
        """Verify an instruction. This function will generate an internal error if something is wrong with the instruction. 
        """
        return _ida_hexrays_micro.mblock_t_verify_insn(self, m)

    def insert_into_block(self, nm: 'minsn_t', om: 'minsn_t') ->'minsn_t *':
        """Insert instruction into the doubly linked list 
        
:param nm: new instruction
:param om: existing instruction, part of the doubly linked list if nullptr, then the instruction will be inserted at the beginning of the list NM will be inserted immediately after OM
:returns: pointer to NM"""
        val = _ida_hexrays_micro.mblock_t_insert_into_block(self, nm, om)
        mn = nm
        mn._maybe_disown_and_deregister()
        return val

    def remove_from_block(self, m: 'minsn_t') ->'minsn_t *':
        """Remove instruction from the doubly linked list 
        
:param m: instruction to remove The removed instruction is not deleted, the caller gets its ownership
:returns: pointer to the next instruction"""
        mn = m
        val = _ida_hexrays_micro.mblock_t_remove_from_block(self, m)
        if mn:
            mn._own_and_register()
        return val

    def for_all_insns(self, mv: 'minsn_visitor_t') ->int:
        """Visit all instructions. This function visits subinstructions too. 
        
:param mv: instruction visitor
:returns: zero or the value returned by mv.visit_insn() See also mba_t::for_all_topinsns()"""
        return _ida_hexrays_micro.mblock_t_for_all_insns(self, mv)

    def for_all_ops(self, mv: 'mop_visitor_t') ->int:
        """Visit all operands. This function visit subinstruction operands too. 
        
:param mv: operand visitor
:returns: zero or the value returned by mv.visit_mop()"""
        return _ida_hexrays_micro.mblock_t_for_all_ops(self, mv)

    def for_all_uses(self, list: 'mlist_t', i1: 'minsn_t', i2: 'minsn_t',
        mmv: 'mlist_mop_visitor_t') ->int:
        """Visit all operands that use LIST. 
        
:param list: ptr to the list of locations. it may be modified: parts that get redefined by the instructions in [i1,i2) will be deleted.
:param i1: starting instruction. must be a top level insn.
:param i2: ending instruction (excluded). must be a top level insn.
:param mmv: operand visitor
:returns: zero or the value returned by mmv.visit_mop()"""
        return _ida_hexrays_micro.mblock_t_for_all_uses(self, list, i1, i2, mmv
            )

    def optimize_insn(self, *args) ->int:
        """Optimize one instruction in the context of the block. 
        
:param m: pointer to a top level instruction
:param optflags: combination of optimization flags bits
:returns: number of changes made to the block This function may change other instructions in the block too. However, it will not destroy top level instructions (it may convert them to nop's). This function performs only intrablock modifications. See also minsn_t::optimize_solo()"""
        return _ida_hexrays_micro.mblock_t_optimize_insn(self, *args)

    def optimize_block(self) ->int:
        """Optimize a basic block. Usually there is no need to call this function explicitly because the decompiler will call it itself if optinsn_t::func or optblock_t::func return non-zero. 
        
:returns: number of changes made to the block"""
        return _ida_hexrays_micro.mblock_t_optimize_block(self)

    def build_lists(self, kill_deads: bool) ->int:
        """Build def-use lists and eliminate deads. 
        
:param kill_deads: do delete dead instructions?
:returns: the number of eliminated instructions Better mblock_t::call make_lists_ready() rather than this function."""
        return _ida_hexrays_micro.mblock_t_build_lists(self, kill_deads)

    def optimize_useless_jump(self) ->int:
        """Remove a jump at the end of the block if it is useless. This function preserves any side effects when removing a useless jump. Both conditional and unconditional jumps are handled (and jtbl too). This function deletes useless jumps, not only replaces them with a nop. (please note that \\optimize_insn does not handle useless jumps). 
        
:returns: number of changes made to the block"""
        return _ida_hexrays_micro.mblock_t_optimize_useless_jump(self)

    def append_use_list(self, *args) ->None:
        """Append use-list of an operand. This function calculates list of locations that may or must be used by the operand and appends it to LIST. 
        
:param list: ptr to the output buffer. we will append to it.
:param op: operand to calculate the use list of
:param maymust: should we calculate 'may-use' or 'must-use' list? see maymust_t for more details.
:param mask: if only part of the operand should be considered, a bitmask can be used to specify which part. example: op=AX,mask=0xFF means that we will consider only AL."""
        return _ida_hexrays_micro.mblock_t_append_use_list(self, *args)

    def append_def_list(self, list: 'mlist_t', op: 'mop_t', maymust:
        'maymust_t') ->None:
        """Append def-list of an operand. This function calculates list of locations that may or must be modified by the operand and appends it to LIST. 
        
:param list: ptr to the output buffer. we will append to it.
:param op: operand to calculate the def list of
:param maymust: should we calculate 'may-def' or 'must-def' list? see maymust_t for more details."""
        return _ida_hexrays_micro.mblock_t_append_def_list(self, list, op,
            maymust)

    def build_use_list(self, ins: 'minsn_t', maymust: 'maymust_t') ->'mlist_t':
        """Build use-list of an instruction. This function calculates list of locations that may or must be used by the instruction. Examples: "ldx ds.2, eax.4, ebx.4", may-list: all aliasable memory "ldx ds.2, eax.4, ebx.4", must-list: empty Since LDX uses EAX for indirect access, it may access any aliasable memory. On the other hand, we cannot tell for sure which memory cells will be accessed, this is why the must-list is empty. 
        
:param ins: instruction to calculate the use list of
:param maymust: should we calculate 'may-use' or 'must-use' list? see maymust_t for more details.
:returns: the calculated use-list"""
        return _ida_hexrays_micro.mblock_t_build_use_list(self, ins, maymust)

    def build_def_list(self, ins: 'minsn_t', maymust: 'maymust_t') ->'mlist_t':
        """Build def-list of an instruction. This function calculates list of locations that may or must be modified by the instruction. Examples: "stx ebx.4, ds.2, eax.4", may-list: all aliasable memory "stx ebx.4, ds.2, eax.4", must-list: empty Since STX uses EAX for indirect access, it may modify any aliasable memory. On the other hand, we cannot tell for sure which memory cells will be modified, this is why the must-list is empty. 
        
:param ins: instruction to calculate the def list of
:param maymust: should we calculate 'may-def' or 'must-def' list? see maymust_t for more details.
:returns: the calculated def-list"""
        return _ida_hexrays_micro.mblock_t_build_def_list(self, ins, maymust)

    def is_used(self, *args) ->bool:
        """Is the list used by the specified instruction range? 
        
:param list: list of locations. LIST may be modified by the function: redefined locations will be removed from it.
:param i1: starting instruction of the range (must be a top level insn)
:param i2: end instruction of the range (must be a top level insn) i2 is excluded from the range. it can be specified as nullptr. i1 and i2 must belong to the same block.
:param maymust: should we search in 'may-access' or 'must-access' mode?"""
        return _ida_hexrays_micro.mblock_t_is_used(self, *args)

    def find_first_use(self, *args) ->'minsn_t *':
        """This function has the following signatures:

    0. find_first_use(list: mlist_t *, i1: const minsn_t *, i2: const minsn_t *, maymust: maymust_t=MAY_ACCESS) -> const minsn_t *
    1. find_first_use(list: mlist_t *, i1: minsn_t *, i2: const minsn_t *, maymust: maymust_t=MAY_ACCESS) -> minsn_t *

# 0: find_first_use(list: mlist_t *, i1: const minsn_t *, i2: const minsn_t *, maymust: maymust_t=MAY_ACCESS) -> const minsn_t *

Find the first insn that uses the specified list in the insn range. 
        
:returns: pointer to such instruction or nullptr. Upon return LIST will contain only locations not redefined by insns [i1..result]

# 1: find_first_use(list: mlist_t *, i1: minsn_t *, i2: const minsn_t *, maymust: maymust_t=MAY_ACCESS) -> minsn_t *

"""
        return _ida_hexrays_micro.mblock_t_find_first_use(self, *args)

    def is_redefined(self, *args) ->bool:
        """Is the list redefined by the specified instructions? 
        
:param list: list of locations to check.
:param i1: starting instruction of the range (must be a top level insn)
:param i2: end instruction of the range (must be a top level insn) i2 is excluded from the range. it can be specified as nullptr. i1 and i2 must belong to the same block.
:param maymust: should we search in 'may-access' or 'must-access' mode?"""
        return _ida_hexrays_micro.mblock_t_is_redefined(self, *args)

    def find_redefinition(self, *args) ->'minsn_t *':
        """This function has the following signatures:

    0. find_redefinition(list: const mlist_t &, i1: const minsn_t *, i2: const minsn_t *, maymust: maymust_t=MAY_ACCESS) -> const minsn_t *
    1. find_redefinition(list: const mlist_t &, i1: minsn_t *, i2: const minsn_t *, maymust: maymust_t=MAY_ACCESS) -> minsn_t *

# 0: find_redefinition(list: const mlist_t &, i1: const minsn_t *, i2: const minsn_t *, maymust: maymust_t=MAY_ACCESS) -> const minsn_t *

Find the first insn that redefines any part of the list in the insn range. 
        
:returns: pointer to such instruction or nullptr.

# 1: find_redefinition(list: const mlist_t &, i1: minsn_t *, i2: const minsn_t *, maymust: maymust_t=MAY_ACCESS) -> minsn_t *

"""
        return _ida_hexrays_micro.mblock_t_find_redefinition(self, *args)

    def is_rhs_redefined(self, ins: 'minsn_t', i1: 'minsn_t', i2: 'minsn_t'
        ) ->bool:
        """Is the right hand side of the instruction redefined the insn range? "right hand side" corresponds to the source operands of the instruction. 
        
:param ins: instruction to consider
:param i1: starting instruction of the range (must be a top level insn)
:param i2: end instruction of the range (must be a top level insn) i2 is excluded from the range. it can be specified as nullptr. i1 and i2 must belong to the same block."""
        return _ida_hexrays_micro.mblock_t_is_rhs_redefined(self, ins, i1, i2)

    def find_access(self, op: 'mop_t', parent: 'minsn_t **', mend:
        'minsn_t', fdflags: int) ->'minsn_t *':
        """Find the instruction that accesses the specified operand. This function search inside one block. 
        
:param op: operand to search for
:param parent: ptr to ptr to a top level instruction. in: denotes the beginning of the search range. out: denotes the parent of the found instruction.
:param mend: end instruction of the range (must be a top level insn) mend is excluded from the range. it can be specified as nullptr. parent and mend must belong to the same block.
:param fdflags: combination of bits for mblock_t::find_access bits
:returns: the instruction that accesses the operand. this instruction may be a sub-instruction. to find out the top level instruction, check out *parent. nullptr means 'not found'."""
        return _ida_hexrays_micro.mblock_t_find_access(self, op, parent,
            mend, fdflags)

    def find_def(self, op: 'mop_t', p_i1: 'minsn_t **', i2: 'minsn_t',
        fdflags: int) ->'minsn_t *':
        return _ida_hexrays_micro.mblock_t_find_def(self, op, p_i1, i2, fdflags
            )

    def find_use(self, op: 'mop_t', p_i1: 'minsn_t **', i2: 'minsn_t',
        fdflags: int) ->'minsn_t *':
        return _ida_hexrays_micro.mblock_t_find_use(self, op, p_i1, i2, fdflags
            )

    def get_valranges(self, *args) ->bool:
        """This function has the following signatures:

    0. get_valranges(res: valrng_t *, vivl: const vivl_t &, vrflags: int) -> bool
    1. get_valranges(res: valrng_t *, vivl: const vivl_t &, m: const minsn_t *, vrflags: int) -> bool

# 0: get_valranges(res: valrng_t *, vivl: const vivl_t &, vrflags: int) -> bool

Find possible values for a block. 
        

# 1: get_valranges(res: valrng_t *, vivl: const vivl_t &, m: const minsn_t *, vrflags: int) -> bool

Find possible values for an instruction. 
        
"""
        return _ida_hexrays_micro.mblock_t_get_valranges(self, *args)

    def make_nop(self, m: 'minsn_t') ->None:
        """Erase the instruction (convert it to nop) and mark the lists dirty. This is the recommended function to use because it also marks the block use-def lists dirty. 
        """
        return _ida_hexrays_micro.mblock_t_make_nop(self, m)

    def get_reginsn_qty(self) ->int:
        """Calculate number of regular instructions in the block. Assertions are skipped by this function. 
        
:returns: Number of non-assertion instructions in the block."""
        return _ida_hexrays_micro.mblock_t_get_reginsn_qty(self)

    def is_call_block(self) ->bool:
        return _ida_hexrays_micro.mblock_t_is_call_block(self)

    def is_unknown_call(self) ->bool:
        return _ida_hexrays_micro.mblock_t_is_unknown_call(self)

    def is_nway(self) ->bool:
        return _ida_hexrays_micro.mblock_t_is_nway(self)

    def is_branch(self) ->bool:
        return _ida_hexrays_micro.mblock_t_is_branch(self)

    def is_simple_goto_block(self) ->bool:
        return _ida_hexrays_micro.mblock_t_is_simple_goto_block(self)

    def is_simple_jcnd_block(self) ->bool:
        return _ida_hexrays_micro.mblock_t_is_simple_jcnd_block(self)

    def preds(self):
        """
        Iterates the list of predecessor blocks
        """
        for ser in self.predset:
            yield self.mba.get_mblock(ser)

    def succs(self):
        """
        Iterates the list of successor blocks
        """
        for ser in self.succset:
            yield self.mba.get_mblock(ser)


_ida_hexrays_micro.mblock_t_swigregister(mblock_t)
MBL_PRIV = _ida_hexrays_micro.MBL_PRIV
"""private block - no instructions except the specified are accepted (used in patterns) 
        """
MBL_NONFAKE = _ida_hexrays_micro.MBL_NONFAKE
"""regular block
"""
MBL_FAKE = _ida_hexrays_micro.MBL_FAKE
"""fake block
"""
MBL_GOTO = _ida_hexrays_micro.MBL_GOTO
"""this block is a goto target
"""
MBL_TCAL = _ida_hexrays_micro.MBL_TCAL
"""aritifical call block for tail calls
"""
MBL_PUSH = _ida_hexrays_micro.MBL_PUSH
"""needs "convert push/pop instructions\"
"""
MBL_DMT64 = _ida_hexrays_micro.MBL_DMT64
"""needs "demote 64bits\"
"""
MBL_COMB = _ida_hexrays_micro.MBL_COMB
"""needs "combine" pass
"""
MBL_PROP = _ida_hexrays_micro.MBL_PROP
"""needs 'propagation' pass
"""
MBL_DEAD = _ida_hexrays_micro.MBL_DEAD
"""needs "eliminate deads" pass
"""
MBL_LIST = _ida_hexrays_micro.MBL_LIST
"""use/def lists are ready (not dirty)
"""
MBL_INCONST = _ida_hexrays_micro.MBL_INCONST
"""inconsistent lists: we are building them
"""
MBL_CALL = _ida_hexrays_micro.MBL_CALL
"""call information has been built
"""
MBL_BACKPROP = _ida_hexrays_micro.MBL_BACKPROP
"""performed backprop_cc
"""
MBL_NORET = _ida_hexrays_micro.MBL_NORET
"""dead end block: doesn't return execution control
"""
MBL_DSLOT = _ida_hexrays_micro.MBL_DSLOT
"""block for delay slot
"""
MBL_VALRANGES = _ida_hexrays_micro.MBL_VALRANGES
"""should optimize using value ranges
"""
MBL_KEEP = _ida_hexrays_micro.MBL_KEEP
"""do not remove even if unreachable
"""
MBL_INLINED = _ida_hexrays_micro.MBL_INLINED
"""block was inlined, not originally part of mbr
"""
MBL_EXTFRAME = _ida_hexrays_micro.MBL_EXTFRAME
"""an inlined block with an external frame
"""
FD_BACKWARD = _ida_hexrays_micro.FD_BACKWARD
"""search direction
"""
FD_FORWARD = _ida_hexrays_micro.FD_FORWARD
"""search direction
"""
FD_USE = _ida_hexrays_micro.FD_USE
"""look for use
"""
FD_DEF = _ida_hexrays_micro.FD_DEF
"""look for definition
"""
FD_DIRTY = _ida_hexrays_micro.FD_DIRTY
"""ignore possible implicit definitions by function calls and indirect memory access 
        """
VR_AT_START = _ida_hexrays_micro.VR_AT_START
"""get value ranges before the instruction or at the block start (if M is nullptr) 
        """
VR_AT_END = _ida_hexrays_micro.VR_AT_END
"""get value ranges after the instruction or at the block end, just after the last instruction (if M is nullptr) 
        """
VR_EXACT = _ida_hexrays_micro.VR_EXACT
"""find exact match. if not set, the returned valrng size will be >= vivl.size 
        """
MMIDX_GLBLOW = _ida_hexrays_micro.MMIDX_GLBLOW
"""global memory: low part
"""
MMIDX_LVARS = _ida_hexrays_micro.MMIDX_LVARS
"""stack: local variables
"""
MMIDX_RETADDR = _ida_hexrays_micro.MMIDX_RETADDR
"""stack: return address
"""
MMIDX_SHADOW = _ida_hexrays_micro.MMIDX_SHADOW
"""stack: shadow arguments
"""
MMIDX_ARGS = _ida_hexrays_micro.MMIDX_ARGS
"""stack: regular stack arguments
"""
MMIDX_GLBHIGH = _ida_hexrays_micro.MMIDX_GLBHIGH
"""global memory: high part
"""


class mba_range_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    rii: 'range_chunk_iterator_t' = property(_ida_hexrays_micro.
        mba_range_iterator_t_rii_get, _ida_hexrays_micro.
        mba_range_iterator_t_rii_set)
    fii: 'func_tail_iterator_t' = property(_ida_hexrays_micro.
        mba_range_iterator_t_fii_get, _ida_hexrays_micro.
        mba_range_iterator_t_fii_set)

    def is_snippet(self) ->bool:
        return _ida_hexrays_micro.mba_range_iterator_t_is_snippet(self)

    def set(self, mbr: 'mba_ranges_t') ->bool:
        return _ida_hexrays_micro.mba_range_iterator_t_set(self, mbr)

    def next(self) ->bool:
        return _ida_hexrays_micro.mba_range_iterator_t_next(self)

    def chunk(self) ->'range_t const &':
        return _ida_hexrays_micro.mba_range_iterator_t_chunk(self)

    def __init__(self):
        _ida_hexrays_micro.mba_range_iterator_t_swiginit(self,
            _ida_hexrays_micro.new_mba_range_iterator_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_mba_range_iterator_t


_ida_hexrays_micro.mba_range_iterator_t_swigregister(mba_range_iterator_t)


class mba_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined')
    __repr__ = _swig_repr

    def precise_defeas(self) ->bool:
        return _ida_hexrays_micro.mba_t_precise_defeas(self)

    def optimized(self) ->bool:
        return _ida_hexrays_micro.mba_t_optimized(self)

    def short_display(self) ->bool:
        return _ida_hexrays_micro.mba_t_short_display(self)

    def show_reduction(self) ->bool:
        return _ida_hexrays_micro.mba_t_show_reduction(self)

    def graph_insns(self) ->bool:
        return _ida_hexrays_micro.mba_t_graph_insns(self)

    def loaded_gdl(self) ->bool:
        return _ida_hexrays_micro.mba_t_loaded_gdl(self)

    def should_beautify(self) ->bool:
        return _ida_hexrays_micro.mba_t_should_beautify(self)

    def rtype_refined(self) ->bool:
        return _ida_hexrays_micro.mba_t_rtype_refined(self)

    def may_refine_rettype(self) ->bool:
        return _ida_hexrays_micro.mba_t_may_refine_rettype(self)

    def use_wingraph32(self) ->bool:
        return _ida_hexrays_micro.mba_t_use_wingraph32(self)

    def display_numaddrs(self) ->bool:
        return _ida_hexrays_micro.mba_t_display_numaddrs(self)

    def display_valnums(self) ->bool:
        return _ida_hexrays_micro.mba_t_display_valnums(self)

    def is_pattern(self) ->bool:
        return _ida_hexrays_micro.mba_t_is_pattern(self)

    def is_thunk(self) ->bool:
        return _ida_hexrays_micro.mba_t_is_thunk(self)

    def saverest_done(self) ->bool:
        return _ida_hexrays_micro.mba_t_saverest_done(self)

    def callinfo_built(self) ->bool:
        return _ida_hexrays_micro.mba_t_callinfo_built(self)

    def really_alloc(self) ->bool:
        return _ida_hexrays_micro.mba_t_really_alloc(self)

    def lvars_allocated(self) ->bool:
        return _ida_hexrays_micro.mba_t_lvars_allocated(self)

    def chain_varnums_ok(self) ->bool:
        return _ida_hexrays_micro.mba_t_chain_varnums_ok(self)

    def returns_fpval(self) ->bool:
        return _ida_hexrays_micro.mba_t_returns_fpval(self)

    def has_passregs(self) ->bool:
        return _ida_hexrays_micro.mba_t_has_passregs(self)

    def generated_asserts(self) ->bool:
        return _ida_hexrays_micro.mba_t_generated_asserts(self)

    def propagated_asserts(self) ->bool:
        return _ida_hexrays_micro.mba_t_propagated_asserts(self)

    def deleted_pairs(self) ->bool:
        return _ida_hexrays_micro.mba_t_deleted_pairs(self)

    def common_stkvars_stkargs(self) ->bool:
        return _ida_hexrays_micro.mba_t_common_stkvars_stkargs(self)

    def lvar_names_ok(self) ->bool:
        return _ida_hexrays_micro.mba_t_lvar_names_ok(self)

    def lvars_renamed(self) ->bool:
        return _ida_hexrays_micro.mba_t_lvars_renamed(self)

    def has_over_chains(self) ->bool:
        return _ida_hexrays_micro.mba_t_has_over_chains(self)

    def valranges_done(self) ->bool:
        return _ida_hexrays_micro.mba_t_valranges_done(self)

    def argidx_ok(self) ->bool:
        return _ida_hexrays_micro.mba_t_argidx_ok(self)

    def argidx_sorted(self) ->bool:
        return _ida_hexrays_micro.mba_t_argidx_sorted(self)

    def code16_bit_removed(self) ->bool:
        return _ida_hexrays_micro.mba_t_code16_bit_removed(self)

    def has_stack_retval(self) ->bool:
        return _ida_hexrays_micro.mba_t_has_stack_retval(self)

    def has_outlines(self) ->bool:
        return _ida_hexrays_micro.mba_t_has_outlines(self)

    def is_ctr(self) ->bool:
        return _ida_hexrays_micro.mba_t_is_ctr(self)

    def is_dtr(self) ->bool:
        return _ida_hexrays_micro.mba_t_is_dtr(self)

    def is_cdtr(self) ->bool:
        return _ida_hexrays_micro.mba_t_is_cdtr(self)

    def prop_complex(self) ->bool:
        return _ida_hexrays_micro.mba_t_prop_complex(self)

    def get_mba_flags(self) ->int:
        return _ida_hexrays_micro.mba_t_get_mba_flags(self)

    def get_mba_flags2(self) ->int:
        return _ida_hexrays_micro.mba_t_get_mba_flags2(self)

    def set_mba_flags(self, f: int) ->None:
        return _ida_hexrays_micro.mba_t_set_mba_flags(self, f)

    def clr_mba_flags(self, f: int) ->None:
        return _ida_hexrays_micro.mba_t_clr_mba_flags(self, f)

    def set_mba_flags2(self, f: int) ->None:
        return _ida_hexrays_micro.mba_t_set_mba_flags2(self, f)

    def clr_mba_flags2(self, f: int) ->None:
        return _ida_hexrays_micro.mba_t_clr_mba_flags2(self, f)

    def clr_cdtr(self) ->None:
        return _ida_hexrays_micro.mba_t_clr_cdtr(self)

    def calc_shins_flags(self) ->int:
        return _ida_hexrays_micro.mba_t_calc_shins_flags(self)

    def stkoff_vd2ida(self, off: int) ->int:
        return _ida_hexrays_micro.mba_t_stkoff_vd2ida(self, off)

    def stkoff_ida2vd(self, off: int) ->int:
        return _ida_hexrays_micro.mba_t_stkoff_ida2vd(self, off)

    def argbase(self) ->int:
        return _ida_hexrays_micro.mba_t_argbase(self)

    def idaloc2vd(self, loc: 'argloc_t', width: int) ->'vdloc_t':
        return _ida_hexrays_micro.mba_t_idaloc2vd(self, loc, width)

    def vd2idaloc(self, *args) ->'argloc_t':
        """This function has the following signatures:

    0. vd2idaloc(loc: const vdloc_t &, width: int) -> argloc_t
    1. vd2idaloc(loc: const vdloc_t &, width: int, spd: int) -> argloc_t

# 0: vd2idaloc(loc: const vdloc_t &, width: int) -> argloc_t


# 1: vd2idaloc(loc: const vdloc_t &, width: int, spd: int) -> argloc_t

"""
        return _ida_hexrays_micro.mba_t_vd2idaloc(self, *args)

    def is_stkarg(self, v: 'lvar_t') ->bool:
        return _ida_hexrays_micro.mba_t_is_stkarg(self, v)

    def get_ida_argloc(self, v: 'lvar_t') ->'argloc_t':
        return _ida_hexrays_micro.mba_t_get_ida_argloc(self, v)
    mbr: 'mba_ranges_t' = property(_ida_hexrays_micro.mba_t_mbr_get,
        _ida_hexrays_micro.mba_t_mbr_set)
    entry_ea: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        mba_t_entry_ea_get, _ida_hexrays_micro.mba_t_entry_ea_set)
    last_prolog_ea: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        mba_t_last_prolog_ea_get, _ida_hexrays_micro.mba_t_last_prolog_ea_set)
    first_epilog_ea: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        mba_t_first_epilog_ea_get, _ida_hexrays_micro.mba_t_first_epilog_ea_set
        )
    qty: int = property(_ida_hexrays_micro.mba_t_qty_get,
        _ida_hexrays_micro.mba_t_qty_set)
    """number of basic blocks
"""
    npurged: int = property(_ida_hexrays_micro.mba_t_npurged_get,
        _ida_hexrays_micro.mba_t_npurged_set)
    """-1 - unknown
"""
    cc: 'callcnv_t' = property(_ida_hexrays_micro.mba_t_cc_get,
        _ida_hexrays_micro.mba_t_cc_set)
    """calling convention
"""
    tmpstk_size: int = property(_ida_hexrays_micro.mba_t_tmpstk_size_get,
        _ida_hexrays_micro.mba_t_tmpstk_size_set)
    """size of the temporary stack part (which dynamically changes with push/pops) 
        """
    frsize: int = property(_ida_hexrays_micro.mba_t_frsize_get,
        _ida_hexrays_micro.mba_t_frsize_set)
    """size of local stkvars range in the stack frame
"""
    frregs: int = property(_ida_hexrays_micro.mba_t_frregs_get,
        _ida_hexrays_micro.mba_t_frregs_set)
    """size of saved registers range in the stack frame
"""
    fpd: int = property(_ida_hexrays_micro.mba_t_fpd_get,
        _ida_hexrays_micro.mba_t_fpd_set)
    """frame pointer delta
"""
    pfn_flags: int = property(_ida_hexrays_micro.mba_t_pfn_flags_get,
        _ida_hexrays_micro.mba_t_pfn_flags_set)
    """copy of func_t::flags
"""
    retsize: int = property(_ida_hexrays_micro.mba_t_retsize_get,
        _ida_hexrays_micro.mba_t_retsize_set)
    """size of return address in the stack frame
"""
    shadow_args: int = property(_ida_hexrays_micro.mba_t_shadow_args_get,
        _ida_hexrays_micro.mba_t_shadow_args_set)
    """size of shadow argument area
"""
    fullsize: int = property(_ida_hexrays_micro.mba_t_fullsize_get,
        _ida_hexrays_micro.mba_t_fullsize_set)
    """Full stack size including incoming args.
"""
    stacksize: int = property(_ida_hexrays_micro.mba_t_stacksize_get,
        _ida_hexrays_micro.mba_t_stacksize_set)
    """The maximal size of the function stack including bytes allocated for outgoing call arguments (up to retaddr) 
        """
    inargoff: int = property(_ida_hexrays_micro.mba_t_inargoff_get,
        _ida_hexrays_micro.mba_t_inargoff_set)
    """offset of the first stack argument; after fix_scattered_movs() INARGOFF may be less than STACKSIZE 
        """
    minstkref: int = property(_ida_hexrays_micro.mba_t_minstkref_get,
        _ida_hexrays_micro.mba_t_minstkref_set)
    """The lowest stack location whose address was taken.
"""
    minstkref_ea: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        mba_t_minstkref_ea_get, _ida_hexrays_micro.mba_t_minstkref_ea_set)
    """address with lowest minstkref (for debugging)
"""
    minargref: int = property(_ida_hexrays_micro.mba_t_minargref_get,
        _ida_hexrays_micro.mba_t_minargref_set)
    """The lowest stack argument location whose address was taken This location and locations above it can be aliased It controls locations >= inargoff-shadow_args 
        """
    spd_adjust: int = property(_ida_hexrays_micro.mba_t_spd_adjust_get,
        _ida_hexrays_micro.mba_t_spd_adjust_set)
    """If sp>0, the max positive sp value.
"""
    gotoff_stkvars: 'ivlset_t' = property(_ida_hexrays_micro.
        mba_t_gotoff_stkvars_get, _ida_hexrays_micro.mba_t_gotoff_stkvars_set)
    """stkvars that hold .got offsets. considered to be unaliasable
"""
    restricted_memory: 'ivlset_t' = property(_ida_hexrays_micro.
        mba_t_restricted_memory_get, _ida_hexrays_micro.
        mba_t_restricted_memory_set)
    aliased_memory: 'ivlset_t' = property(_ida_hexrays_micro.
        mba_t_aliased_memory_get, _ida_hexrays_micro.mba_t_aliased_memory_set)
    """aliased_memory+restricted_memory=ALLMEM
"""
    nodel_memory: 'mlist_t' = property(_ida_hexrays_micro.
        mba_t_nodel_memory_get, _ida_hexrays_micro.mba_t_nodel_memory_set)
    """global dead elimination may not delete references to this area
"""
    consumed_argregs: 'rlist_t' = property(_ida_hexrays_micro.
        mba_t_consumed_argregs_get, _ida_hexrays_micro.
        mba_t_consumed_argregs_set)
    """registers converted into stack arguments, should not be used as arguments
"""
    maturity: 'mba_maturity_t' = property(_ida_hexrays_micro.
        mba_t_maturity_get, _ida_hexrays_micro.mba_t_maturity_set)
    """current maturity level
"""
    reqmat: 'mba_maturity_t' = property(_ida_hexrays_micro.mba_t_reqmat_get,
        _ida_hexrays_micro.mba_t_reqmat_set)
    """required maturity level
"""
    final_type: bool = property(_ida_hexrays_micro.mba_t_final_type_get,
        _ida_hexrays_micro.mba_t_final_type_set)
    """is the function type final? (specified by the user)
"""
    idb_type: 'tinfo_t' = property(_ida_hexrays_micro.mba_t_idb_type_get,
        _ida_hexrays_micro.mba_t_idb_type_set)
    """function type as retrieved from the database
"""
    idb_spoiled: 'reginfovec_t' = property(_ida_hexrays_micro.
        mba_t_idb_spoiled_get, _ida_hexrays_micro.mba_t_idb_spoiled_set)
    """MBA_SPLINFO && final_type: info in ida format.
"""
    spoiled_list: 'mlist_t' = property(_ida_hexrays_micro.
        mba_t_spoiled_list_get, _ida_hexrays_micro.mba_t_spoiled_list_set)
    """MBA_SPLINFO && !final_type: info in vd format.
"""
    fti_flags: int = property(_ida_hexrays_micro.mba_t_fti_flags_get,
        _ida_hexrays_micro.mba_t_fti_flags_set)
    """FTI_... constants for the current function.
"""
    label: str = property(_ida_hexrays_micro.mba_t_label_get,
        _ida_hexrays_micro.mba_t_label_set)
    """name of the function or pattern (colored)
"""
    vars: 'lvars_t' = property(_ida_hexrays_micro.mba_t_vars_get,
        _ida_hexrays_micro.mba_t_vars_set)
    """local variables
"""
    argidx: 'intvec_t' = property(_ida_hexrays_micro.mba_t_argidx_get,
        _ida_hexrays_micro.mba_t_argidx_set)
    """input arguments (indexes into 'vars')
"""
    retvaridx: int = property(_ida_hexrays_micro.mba_t_retvaridx_get,
        _ida_hexrays_micro.mba_t_retvaridx_set)
    """index of variable holding the return value -1 means none 
        """
    error_ea: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        mba_t_error_ea_get, _ida_hexrays_micro.mba_t_error_ea_set)
    """during microcode generation holds ins.ea
"""
    error_strarg: str = property(_ida_hexrays_micro.mba_t_error_strarg_get,
        _ida_hexrays_micro.mba_t_error_strarg_set)
    blocks: 'mblock_t *' = property(_ida_hexrays_micro.mba_t_blocks_get,
        _ida_hexrays_micro.mba_t_blocks_set)
    """double linked list of blocks
"""
    natural: 'mblock_t **' = property(_ida_hexrays_micro.mba_t_natural_get,
        _ida_hexrays_micro.mba_t_natural_set)
    """natural order of blocks
"""
    std_ivls: 'ivl_with_name_t [6]' = property(_ida_hexrays_micro.
        mba_t_std_ivls_get, _ida_hexrays_micro.mba_t_std_ivls_set)
    """we treat memory as consisting of 6 parts see memreg_index_t 
        """
    notes: 'hexwarns_t' = property(_ida_hexrays_micro.mba_t_notes_get,
        _ida_hexrays_micro.mba_t_notes_set)
    occurred_warns: 'uchar [32]' = property(_ida_hexrays_micro.
        mba_t_occurred_warns_get, _ida_hexrays_micro.mba_t_occurred_warns_set)

    def write_to_const_detected(self) ->bool:
        return _ida_hexrays_micro.mba_t_write_to_const_detected(self)

    def bad_call_sp_detected(self) ->bool:
        return _ida_hexrays_micro.mba_t_bad_call_sp_detected(self)

    def regargs_is_not_aligned(self) ->bool:
        return _ida_hexrays_micro.mba_t_regargs_is_not_aligned(self)

    def has_bad_sp(self) ->bool:
        return _ida_hexrays_micro.mba_t_has_bad_sp(self)
    __swig_destroy__ = _ida_hexrays_micro.delete_mba_t

    def term(self) ->None:
        return _ida_hexrays_micro.mba_t_term(self)

    def get_curfunc(self) ->'func_t *':
        return _ida_hexrays_micro.mba_t_get_curfunc(self)

    def use_frame(self) ->bool:
        return _ida_hexrays_micro.mba_t_use_frame(self)

    def is_snippet(self) ->bool:
        return _ida_hexrays_micro.mba_t_is_snippet(self)

    def set_maturity(self, mat: 'mba_maturity_t') ->'merror_t':
        """Set maturity level. 
        
:param mat: new maturity level
:returns: error code Plugins may use this function to skip some parts of the analysis. The maturity level cannot be decreased."""
        return _ida_hexrays_micro.mba_t_set_maturity(self, mat)

    def optimize_local(self, locopt_bits: int) ->int:
        """Optimize each basic block locally 
        
:param locopt_bits: combination of Bits for optimize_local() bits
:returns: number of changes. 0 means nothing changed This function is called by the decompiler, usually there is no need to call it explicitly."""
        return _ida_hexrays_micro.mba_t_optimize_local(self, locopt_bits)

    def build_graph(self) ->'merror_t':
        """Build control flow graph. This function may be called only once. It calculates the type of each basic block and the adjacency list. optimize_local() calls this function if necessary. You need to call this function only before MMAT_LOCOPT. 
        
:returns: error code"""
        return _ida_hexrays_micro.mba_t_build_graph(self)

    def get_graph(self) ->'mbl_graph_t *':
        """Get control graph. Call build_graph() if you need the graph before MMAT_LOCOPT. 
        """
        return _ida_hexrays_micro.mba_t_get_graph(self)

    def analyze_calls(self, acflags: int) ->int:
        """Analyze calls and determine calling conventions. 
        
:param acflags: permitted actions that are necessary for successful detection of calling conventions. See Bits for analyze_calls()
:returns: number of calls. -1 means error."""
        return _ida_hexrays_micro.mba_t_analyze_calls(self, acflags)

    def optimize_global(self) ->'merror_t':
        """Optimize microcode globally. This function applies various optimization methods until we reach the fixed point. After that it preallocates lvars unless reqmat forbids it. 
        
:returns: error code"""
        return _ida_hexrays_micro.mba_t_optimize_global(self)

    def alloc_lvars(self) ->None:
        """Allocate local variables. Must be called only immediately after optimize_global(), with no modifications to the microcode. Converts registers, stack variables, and similar operands into mop_l. This call will not fail because all necessary checks were performed in optimize_global(). After this call the microcode reaches its final state. 
        """
        return _ida_hexrays_micro.mba_t_alloc_lvars(self)

    def dump(self) ->None:
        """Dump microcode to a file. The file will be created in the directory pointed by IDA_DUMPDIR envvar. Dump will be created only if IDA is run under debugger. 
        """
        return _ida_hexrays_micro.mba_t_dump(self)

    def dump_mba(self, _verify: bool, title: str) ->None:
        return _ida_hexrays_micro.mba_t_dump_mba(self, _verify, title)

    def _print(self, vp: 'vd_printer_t') ->None:
        return _ida_hexrays_micro.mba_t__print(self, vp)

    def verify(self, always: bool) ->None:
        """Verify microcode consistency. 
        
:param always: if false, the check will be performed only if ida runs under debugger If any inconsistency is discovered, an internal error will be generated. We strongly recommend you to call this function before returing control to the decompiler from your callbacks, in the case if you modified the microcode. If the microcode is inconsistent, this function will generate an internal error. We provide the source code of this function in the plugins/hexrays_sdk/verifier directory for your reference."""
        return _ida_hexrays_micro.mba_t_verify(self, always)

    def mark_chains_dirty(self) ->None:
        """Mark the microcode use-def chains dirty. Call this function is any inter-block data dependencies got changed because of your modifications to the microcode. Failing to do so may cause an internal error. 
        """
        return _ida_hexrays_micro.mba_t_mark_chains_dirty(self)

    def get_mblock(self, n: 'uint') ->'mblock_t *':
        """Get basic block by its serial number.
"""
        return _ida_hexrays_micro.mba_t_get_mblock(self, n)

    def insert_block(self, bblk: int) ->'mblock_t *':
        """Insert a block in the middle of the mbl array. The very first block of microcode must be empty, it is the entry block. The very last block of microcode must be BLT_STOP, it is the exit block. Therefore inserting a new block before the entry point or after the exit block is not a good idea. 
        
:param bblk: the new block will be inserted before BBLK
:returns: ptr to the new block"""
        return _ida_hexrays_micro.mba_t_insert_block(self, bblk)

    def split_block(self, blk: 'mblock_t', start_insn: 'minsn_t'
        ) ->'mblock_t *':
        """Split a block: insert a new one after the block, move some instructions to new block 
        
:param blk: block to be split
:param start_insn: all instructions to be moved to new block: starting with this one up to the end
:returns: ptr to the new block"""
        return _ida_hexrays_micro.mba_t_split_block(self, blk, start_insn)

    def remove_block(self, blk: 'mblock_t') ->bool:
        """Delete a block. 
        
:param blk: block to delete
:returns: true if at least one of the other blocks became empty or unreachable"""
        return _ida_hexrays_micro.mba_t_remove_block(self, blk)

    def remove_blocks(self, start_blk: int, end_blk: int) ->bool:
        return _ida_hexrays_micro.mba_t_remove_blocks(self, start_blk, end_blk)

    def copy_block(self, blk: 'mblock_t', new_serial: int, cpblk_flags: int=3
        ) ->'mblock_t *':
        """Make a copy of a block. This function makes a simple copy of the block. It does not fix the predecessor and successor lists, they must be fixed if necessary. 
        
:param blk: block to copy
:param new_serial: position of the copied block
:param cpblk_flags: combination of Batch decompilation bits... bits
:returns: pointer to the new copy"""
        return _ida_hexrays_micro.mba_t_copy_block(self, blk, new_serial,
            cpblk_flags)

    def remove_empty_and_unreachable_blocks(self) ->bool:
        """Delete all empty and unreachable blocks. Blocks marked with MBL_KEEP won't be deleted. 
        """
        return _ida_hexrays_micro.mba_t_remove_empty_and_unreachable_blocks(
            self)

    def merge_blocks(self) ->bool:
        """Merge blocks. This function merges blocks constituting linear flow. It calls remove_empty_and_unreachable_blocks() as well. 
        
:returns: true if changed any blocks"""
        return _ida_hexrays_micro.mba_t_merge_blocks(self)

    def for_all_ops(self, mv: 'mop_visitor_t') ->int:
        """Visit all operands of all instructions. 
        
:param mv: operand visitor
:returns: non-zero value returned by mv.visit_mop() or zero"""
        return _ida_hexrays_micro.mba_t_for_all_ops(self, mv)

    def for_all_insns(self, mv: 'minsn_visitor_t') ->int:
        """Visit all instructions. This function visits all instruction and subinstructions. 
        
:param mv: instruction visitor
:returns: non-zero value returned by mv.visit_mop() or zero"""
        return _ida_hexrays_micro.mba_t_for_all_insns(self, mv)

    def for_all_topinsns(self, mv: 'minsn_visitor_t') ->int:
        """Visit all top level instructions. 
        
:param mv: instruction visitor
:returns: non-zero value returned by mv.visit_mop() or zero"""
        return _ida_hexrays_micro.mba_t_for_all_topinsns(self, mv)

    def find_mop(self, ctx: 'op_parent_info_t', ea: ida_idaapi.ea_t,
        is_dest: bool, list: 'mlist_t') ->'mop_t *':
        """Find an operand in the microcode. This function tries to find the operand that matches LIST. Any operand that overlaps with LIST is considered as a match. 
        
:param ctx: context information for the result
:param ea: desired address of the operand. BADADDR means to accept any address.
:param is_dest: search for destination operand? this argument may be ignored if the exact match could not be found
:param list: list of locations the correspond to the operand
:returns: pointer to the operand or nullptr."""
        return _ida_hexrays_micro.mba_t_find_mop(self, ctx, ea, is_dest, list)

    def create_helper_call(self, ea: ida_idaapi.ea_t, helper: str, rettype:
        'tinfo_t'=None, callargs: 'mcallargs_t'=None, out: 'mop_t'=None
        ) ->'minsn_t *':
        """Create a call of a helper function. 
        
:param ea: The desired address of the instruction
:param helper: The helper name
:param rettype: The return type (nullptr or empty type means 'void')
:param callargs: The helper arguments (nullptr-no arguments)
:param out: The operand where the call result should be stored. If this argument is not nullptr, "mov helper_call(), out" will be generated. Otherwise "call helper()" will be generated. Note: the size of this operand must be equal to the RETTYPE size
:returns: pointer to the created instruction or nullptr if error"""
        return _ida_hexrays_micro.mba_t_create_helper_call(self, ea, helper,
            rettype, callargs, out)

    def get_func_output_lists(self, *args) ->None:
        """Prepare the lists of registers & memory that are defined/killed by a function 
        
:param return_regs: defined regs to return (eax,edx)
:param spoiled: spoiled regs (flags,ecx,mem)
:param type: the function type
:param call_ea: the call insn address (if known)
:param tail_call: is it the tail call?"""
        return _ida_hexrays_micro.mba_t_get_func_output_lists(self, *args)

    def arg(self, n: int) ->'lvar_t &':
        """Get input argument of the decompiled function. 
        
:param n: argument number (0..nargs-1)"""
        return _ida_hexrays_micro.mba_t_arg(self, n)

    def alloc_fict_ea(self, real_ea: ida_idaapi.ea_t) ->ida_idaapi.ea_t:
        """Allocate a fictional address. This function can be used to allocate a new unique address for a new instruction, if re-using any existing address leads to conflicts. For example, if the last instruction of the function modifies R0 and falls through to the next function, it will be a tail call: LDM R0!, {R4,R7} end of the function start of another function In this case R0 generates two different lvars at the same address:
* one modified by LDM
* another that represents the return value from the tail call


Another example: a third-party plugin makes a copy of an instruction. This may lead to the generation of two variables at the same address. Example 3: fictional addresses can be used for new instructions created while modifying the microcode. This function can be used to allocate a new unique address for a new instruction or a variable. The fictional address is selected from an unallocated address range. 
        
:param real_ea: real instruction address (BADADDR is ok too)
:returns: a unique fictional address"""
        return _ida_hexrays_micro.mba_t_alloc_fict_ea(self, real_ea)

    def map_fict_ea(self, fict_ea: ida_idaapi.ea_t) ->ida_idaapi.ea_t:
        """Resolve a fictional address. This function provides a reverse of the mapping made by alloc_fict_ea(). 
        
:param fict_ea: fictional definition address
:returns: the real instruction address"""
        return _ida_hexrays_micro.mba_t_map_fict_ea(self, fict_ea)

    def get_std_region(self, idx: 'memreg_index_t') ->'ivl_t const &':
        """Get information about various memory regions. We map the stack frame to the global memory, to some unused range. 
        """
        return _ida_hexrays_micro.mba_t_get_std_region(self, idx)

    def get_lvars_region(self) ->'ivl_t const &':
        return _ida_hexrays_micro.mba_t_get_lvars_region(self)

    def get_shadow_region(self) ->'ivl_t const &':
        return _ida_hexrays_micro.mba_t_get_shadow_region(self)

    def get_args_region(self) ->'ivl_t const &':
        return _ida_hexrays_micro.mba_t_get_args_region(self)

    def get_stack_region(self) ->'ivl_t':
        return _ida_hexrays_micro.mba_t_get_stack_region(self)

    def serialize(self) ->None:
        """Serialize mbl array into a sequence of bytes.
"""
        return _ida_hexrays_micro.mba_t_serialize(self)

    @staticmethod
    def deserialize(bytes: 'uchar const *') ->'mba_t *':
        """Deserialize a byte sequence into mbl array. 
        
:param bytes: pointer to the beginning of the byte sequence.
:returns: new mbl array"""
        return _ida_hexrays_micro.mba_t_deserialize(bytes)

    def save_snapshot(self, description: str) ->None:
        """Create and save microcode snapshot.
"""
        return _ida_hexrays_micro.mba_t_save_snapshot(self, description)

    def alloc_kreg(self, size: int, check_size: bool=True) ->'mreg_t':
        """Allocate a kernel register. 
        
:param size: size of the register in bytes
:param check_size: if true, only the sizes that correspond to a size of a basic type will be accepted.
:returns: allocated register. mr_none means failure."""
        return _ida_hexrays_micro.mba_t_alloc_kreg(self, size, check_size)

    def free_kreg(self, reg: 'mreg_t', size: int) ->None:
        """Free a kernel register. If wrong arguments are passed, this function will generate an internal error. 
        
:param reg: a previously allocated kernel register
:param size: size of the register in bytes"""
        return _ida_hexrays_micro.mba_t_free_kreg(self, reg, size)

    def inline_func(self, cdg: 'codegen_t', blknum: int, ranges:
        'mba_ranges_t', decomp_flags: int=0, inline_flags: int=0) ->'merror_t':
        """Inline a range. This function may be called only during the initial microcode generation phase. 
        
:param cdg: the codegenerator object
:param blknum: the block contaning the call/jump instruction to inline
:param ranges: the set of ranges to inline. in the case of multiple calls to inline_func(), ranges will be compared using their start addresses. if two ranges have the same address, they will be considered the same.
:param decomp_flags: combination of decompile() flags bits
:param inline_flags: combination of inline_func() flags bits
:returns: error code"""
        return _ida_hexrays_micro.mba_t_inline_func(self, cdg, blknum,
            ranges, decomp_flags, inline_flags)

    def locate_stkpnt(self, ea: ida_idaapi.ea_t) ->'stkpnt_t const *':
        return _ida_hexrays_micro.mba_t_locate_stkpnt(self, ea)

    def set_lvar_name(self, v: 'lvar_t', name: str, flagbits: int) ->bool:
        return _ida_hexrays_micro.mba_t_set_lvar_name(self, v, name, flagbits)

    def set_nice_lvar_name(self, v: 'lvar_t', name: str) ->bool:
        return _ida_hexrays_micro.mba_t_set_nice_lvar_name(self, v, name)

    def set_user_lvar_name(self, v: 'lvar_t', name: str) ->bool:
        return _ida_hexrays_micro.mba_t_set_user_lvar_name(self, v, name)
    """
    Deprecated. Please do not use.
    """
    idb_node = property(lambda self: self.deprecated_idb_node)

    def _register(self) ->None:
        return _ida_hexrays_micro.mba_t__register(self)

    def _deregister(self) ->None:
        return _ida_hexrays_micro.mba_t__deregister(self)


_ida_hexrays_micro.mba_t_swigregister(mba_t)
MBA_PRCDEFS = _ida_hexrays_micro.MBA_PRCDEFS
"""use precise defeas for chain-allocated lvars
"""
MBA_NOFUNC = _ida_hexrays_micro.MBA_NOFUNC
"""function is not present, addresses might be wrong
"""
MBA_PATTERN = _ida_hexrays_micro.MBA_PATTERN
"""microcode pattern, callinfo is present
"""
MBA_LOADED = _ida_hexrays_micro.MBA_LOADED
"""loaded gdl, no instructions (debugging)
"""
MBA_RETFP = _ida_hexrays_micro.MBA_RETFP
"""function returns floating point value
"""
MBA_SPLINFO = _ida_hexrays_micro.MBA_SPLINFO
"""(final_type ? idb_spoiled : spoiled_regs) is valid
"""
MBA_PASSREGS = _ida_hexrays_micro.MBA_PASSREGS
"""has mcallinfo_t::pass_regs
"""
MBA_THUNK = _ida_hexrays_micro.MBA_THUNK
"""thunk function
"""
MBA_CMNSTK = _ida_hexrays_micro.MBA_CMNSTK
"""stkvars+stkargs should be considered as one area
"""
MBA_PREOPT = _ida_hexrays_micro.MBA_PREOPT
"""preoptimization stage complete
"""
MBA_CMBBLK = _ida_hexrays_micro.MBA_CMBBLK
"""request to combine blocks
"""
MBA_ASRTOK = _ida_hexrays_micro.MBA_ASRTOK
"""assertions have been generated
"""
MBA_CALLS = _ida_hexrays_micro.MBA_CALLS
"""callinfo has been built
"""
MBA_ASRPROP = _ida_hexrays_micro.MBA_ASRPROP
"""assertion have been propagated
"""
MBA_SAVRST = _ida_hexrays_micro.MBA_SAVRST
"""save-restore analysis has been performed
"""
MBA_RETREF = _ida_hexrays_micro.MBA_RETREF
"""return type has been refined
"""
MBA_GLBOPT = _ida_hexrays_micro.MBA_GLBOPT
"""microcode has been optimized globally
"""
MBA_LVARS0 = _ida_hexrays_micro.MBA_LVARS0
"""lvar pre-allocation has been performed
"""
MBA_LVARS1 = _ida_hexrays_micro.MBA_LVARS1
"""lvar real allocation has been performed
"""
MBA_DELPAIRS = _ida_hexrays_micro.MBA_DELPAIRS
"""pairs have been deleted once
"""
MBA_CHVARS = _ida_hexrays_micro.MBA_CHVARS
"""can verify chain varnums
"""
MBA_SHORT = _ida_hexrays_micro.MBA_SHORT
"""use short display
"""
MBA_COLGDL = _ida_hexrays_micro.MBA_COLGDL
"""display graph after each reduction
"""
MBA_INSGDL = _ida_hexrays_micro.MBA_INSGDL
"""display instruction in graphs
"""
MBA_NICE = _ida_hexrays_micro.MBA_NICE
"""apply transformations to c code
"""
MBA_REFINE = _ida_hexrays_micro.MBA_REFINE
"""may refine return value size
"""
MBA_WINGR32 = _ida_hexrays_micro.MBA_WINGR32
"""use wingraph32
"""
MBA_NUMADDR = _ida_hexrays_micro.MBA_NUMADDR
"""display definition addresses for numbers
"""
MBA_VALNUM = _ida_hexrays_micro.MBA_VALNUM
"""display value numbers
"""
MBA_INITIAL_FLAGS = _ida_hexrays_micro.MBA_INITIAL_FLAGS
MBA2_LVARNAMES_OK = _ida_hexrays_micro.MBA2_LVARNAMES_OK
"""may verify lvar_names?
"""
MBA2_LVARS_RENAMED = _ida_hexrays_micro.MBA2_LVARS_RENAMED
"""accept empty names now?
"""
MBA2_OVER_CHAINS = _ida_hexrays_micro.MBA2_OVER_CHAINS
"""has overlapped chains?
"""
MBA2_VALRNG_DONE = _ida_hexrays_micro.MBA2_VALRNG_DONE
"""calculated valranges?
"""
MBA2_IS_CTR = _ida_hexrays_micro.MBA2_IS_CTR
"""is constructor?
"""
MBA2_IS_DTR = _ida_hexrays_micro.MBA2_IS_DTR
"""is destructor?
"""
MBA2_ARGIDX_OK = _ida_hexrays_micro.MBA2_ARGIDX_OK
"""may verify input argument list?
"""
MBA2_NO_DUP_CALLS = _ida_hexrays_micro.MBA2_NO_DUP_CALLS
"""forbid multiple calls with the same ea
"""
MBA2_NO_DUP_LVARS = _ida_hexrays_micro.MBA2_NO_DUP_LVARS
"""forbid multiple lvars with the same ea
"""
MBA2_UNDEF_RETVAR = _ida_hexrays_micro.MBA2_UNDEF_RETVAR
"""return value is undefined
"""
MBA2_ARGIDX_SORTED = _ida_hexrays_micro.MBA2_ARGIDX_SORTED
"""args finally sorted according to ABI (e.g. reverse stkarg order in Borland) 
        """
MBA2_CODE16_BIT = _ida_hexrays_micro.MBA2_CODE16_BIT
"""the code16 bit got removed
"""
MBA2_STACK_RETVAL = _ida_hexrays_micro.MBA2_STACK_RETVAL
"""the return value (or its part) is on the stack
"""
MBA2_HAS_OUTLINES = _ida_hexrays_micro.MBA2_HAS_OUTLINES
"""calls to outlined code have been inlined
"""
MBA2_NO_FRAME = _ida_hexrays_micro.MBA2_NO_FRAME
"""do not use function frame info (only snippet mode)
"""
MBA2_PROP_COMPLEX = _ida_hexrays_micro.MBA2_PROP_COMPLEX
"""allow propagation of more complex variable definitions
"""
MBA2_DONT_VERIFY = _ida_hexrays_micro.MBA2_DONT_VERIFY
"""Do not verify microcode. This flag is recomended to be set only when debugging decompiler plugins 
        """
MBA2_INITIAL_FLAGS = _ida_hexrays_micro.MBA2_INITIAL_FLAGS
MBA2_ALL_FLAGS = _ida_hexrays_micro.MBA2_ALL_FLAGS
NALT_VD = _ida_hexrays_micro.NALT_VD
"""this index is not used by ida
"""
LOCOPT_ALL = _ida_hexrays_micro.LOCOPT_ALL
"""redo optimization for all blocks. if this bit is not set, only dirty blocks will be optimized 
        """
LOCOPT_REFINE = _ida_hexrays_micro.LOCOPT_REFINE
"""refine return type, ok to fail
"""
LOCOPT_REFINE2 = _ida_hexrays_micro.LOCOPT_REFINE2
"""refine return type, try harder
"""
ACFL_LOCOPT = _ida_hexrays_micro.ACFL_LOCOPT
"""perform local propagation (requires ACFL_BLKOPT)
"""
ACFL_BLKOPT = _ida_hexrays_micro.ACFL_BLKOPT
"""perform interblock transformations
"""
ACFL_GLBPROP = _ida_hexrays_micro.ACFL_GLBPROP
"""perform global propagation
"""
ACFL_GLBDEL = _ida_hexrays_micro.ACFL_GLBDEL
"""perform dead code eliminition
"""
ACFL_GUESS = _ida_hexrays_micro.ACFL_GUESS
"""may guess calling conventions
"""
CPBLK_FAST = _ida_hexrays_micro.CPBLK_FAST
"""do not update minbstkref and minbargref
"""
CPBLK_MINREF = _ida_hexrays_micro.CPBLK_MINREF
"""update minbstkref and minbargref
"""
CPBLK_OPTJMP = _ida_hexrays_micro.CPBLK_OPTJMP
"""del the jump insn at the end of the block if it becomes useless 
        """
INLINE_EXTFRAME = _ida_hexrays_micro.INLINE_EXTFRAME
"""Inlined function has its own (external) frame.
"""
INLINE_DONTCOPY = _ida_hexrays_micro.INLINE_DONTCOPY
"""Do not reuse old inlined copy even if it exists.
"""


def gen_microcode(mbr: 'mba_ranges_t', hf: 'hexrays_failure_t'=None,
    retlist: 'mlist_t'=None, decomp_flags: int=0, reqmat: 'mba_maturity_t'=
    MMAT_GLBOPT3) ->'mba_t *':
    """Generate microcode of an arbitrary code snippet 
        
:param mbr: snippet ranges
:param hf: extended error information (if failed)
:param retlist: list of registers the snippet returns
:param decomp_flags: bitwise combination of decompile() flags... bits
:param reqmat: required microcode maturity
:returns: pointer to the microcode, nullptr if failed."""
    return _ida_hexrays_micro.gen_microcode(mbr, hf, retlist, decomp_flags,
        reqmat)


def create_empty_mba(mbr: 'mba_ranges_t', hf: 'hexrays_failure_t'=None
    ) ->'mba_t *':
    """Create an empty microcode object.
"""
    return _ida_hexrays_micro.create_empty_mba(mbr, hf)


class chain_keeper_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, _gc: 'graph_chains_t'):
        _ida_hexrays_micro.chain_keeper_t_swiginit(self, _ida_hexrays_micro
            .new_chain_keeper_t(_gc))
    __swig_destroy__ = _ida_hexrays_micro.delete_chain_keeper_t

    def front(self) ->'block_chains_t &':
        return _ida_hexrays_micro.chain_keeper_t_front(self)

    def back(self) ->'block_chains_t &':
        return _ida_hexrays_micro.chain_keeper_t_back(self)

    def for_all_chains(self, cv: 'chain_visitor_t', gca: int) ->int:
        return _ida_hexrays_micro.chain_keeper_t_for_all_chains(self, cv, gca)


_ida_hexrays_micro.chain_keeper_t_swigregister(chain_keeper_t)
GC_REGS_AND_STKVARS = _ida_hexrays_micro.GC_REGS_AND_STKVARS
"""registers and stkvars (restricted memory only)
"""
GC_ASR = _ida_hexrays_micro.GC_ASR
"""all the above and assertions
"""
GC_XDSU = _ida_hexrays_micro.GC_XDSU
"""only registers calculated with FULL_XDSU
"""
GC_END = _ida_hexrays_micro.GC_END
"""number of chain types
"""
GC_DIRTY_ALL = _ida_hexrays_micro.GC_DIRTY_ALL
"""bitmask to represent all chains
"""


class mbl_graph_t(simple_graph_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined - class is abstract')
    __repr__ = _swig_repr

    def is_ud_chain_dirty(self, gctype: 'gctype_t') ->bool:
        """Is the use-def chain of the specified kind dirty?
"""
        return _ida_hexrays_micro.mbl_graph_t_is_ud_chain_dirty(self, gctype)

    def is_du_chain_dirty(self, gctype: 'gctype_t') ->bool:
        """Is the def-use chain of the specified kind dirty?
"""
        return _ida_hexrays_micro.mbl_graph_t_is_du_chain_dirty(self, gctype)

    def get_chain_stamp(self) ->int:
        return _ida_hexrays_micro.mbl_graph_t_get_chain_stamp(self)

    def get_ud(self, gctype: 'gctype_t') ->'graph_chains_t *':
        """Get use-def chains.
"""
        return _ida_hexrays_micro.mbl_graph_t_get_ud(self, gctype)

    def get_du(self, gctype: 'gctype_t') ->'graph_chains_t *':
        """Get def-use chains.
"""
        return _ida_hexrays_micro.mbl_graph_t_get_du(self, gctype)

    def is_redefined_globally(self, *args) ->bool:
        """Is LIST redefined in the graph?
"""
        return _ida_hexrays_micro.mbl_graph_t_is_redefined_globally(self, *args
            )

    def is_used_globally(self, *args) ->bool:
        """Is LIST used in the graph?
"""
        return _ida_hexrays_micro.mbl_graph_t_is_used_globally(self, *args)

    def get_mblock(self, n: int) ->'mblock_t *':
        return _ida_hexrays_micro.mbl_graph_t_get_mblock(self, n)


_ida_hexrays_micro.mbl_graph_t_swigregister(mbl_graph_t)


class cdg_insn_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    mba: 'mba_t const *' = property(_ida_hexrays_micro.
        cdg_insn_iterator_t_mba_get, _ida_hexrays_micro.
        cdg_insn_iterator_t_mba_set)
    ea: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        cdg_insn_iterator_t_ea_get, _ida_hexrays_micro.
        cdg_insn_iterator_t_ea_set)
    end: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        cdg_insn_iterator_t_end_get, _ida_hexrays_micro.
        cdg_insn_iterator_t_end_set)
    dslot: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        cdg_insn_iterator_t_dslot_get, _ida_hexrays_micro.
        cdg_insn_iterator_t_dslot_set)
    dslot_insn: 'insn_t' = property(_ida_hexrays_micro.
        cdg_insn_iterator_t_dslot_insn_get, _ida_hexrays_micro.
        cdg_insn_iterator_t_dslot_insn_set)
    severed_branch: ida_idaapi.ea_t = property(_ida_hexrays_micro.
        cdg_insn_iterator_t_severed_branch_get, _ida_hexrays_micro.
        cdg_insn_iterator_t_severed_branch_set)
    is_likely_dslot: bool = property(_ida_hexrays_micro.
        cdg_insn_iterator_t_is_likely_dslot_get, _ida_hexrays_micro.
        cdg_insn_iterator_t_is_likely_dslot_set)

    def __init__(self, *args):
        _ida_hexrays_micro.cdg_insn_iterator_t_swiginit(self,
            _ida_hexrays_micro.new_cdg_insn_iterator_t(*args))

    def ok(self) ->bool:
        return _ida_hexrays_micro.cdg_insn_iterator_t_ok(self)

    def has_dslot(self) ->bool:
        return _ida_hexrays_micro.cdg_insn_iterator_t_has_dslot(self)

    def dslot_with_xrefs(self) ->bool:
        return _ida_hexrays_micro.cdg_insn_iterator_t_dslot_with_xrefs(self)

    def is_severed_dslot(self) ->bool:
        return _ida_hexrays_micro.cdg_insn_iterator_t_is_severed_dslot(self)

    def start(self, rng: 'range_t') ->None:
        return _ida_hexrays_micro.cdg_insn_iterator_t_start(self, rng)

    def next(self, ins: 'insn_t *') ->'merror_t':
        return _ida_hexrays_micro.cdg_insn_iterator_t_next(self, ins)
    __swig_destroy__ = _ida_hexrays_micro.delete_cdg_insn_iterator_t


_ida_hexrays_micro.cdg_insn_iterator_t_swigregister(cdg_insn_iterator_t)


class codegen_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError('No constructor defined - class is abstract')
    __repr__ = _swig_repr
    mba: 'mba_t *' = property(_ida_hexrays_micro.codegen_t_mba_get,
        _ida_hexrays_micro.codegen_t_mba_set)
    mb: 'mblock_t *' = property(_ida_hexrays_micro.codegen_t_mb_get,
        _ida_hexrays_micro.codegen_t_mb_set)
    insn: 'insn_t' = property(_ida_hexrays_micro.codegen_t_insn_get,
        _ida_hexrays_micro.codegen_t_insn_set)
    ignore_micro: 'char' = property(_ida_hexrays_micro.
        codegen_t_ignore_micro_get, _ida_hexrays_micro.
        codegen_t_ignore_micro_set)
    ii: 'cdg_insn_iterator_t' = property(_ida_hexrays_micro.
        codegen_t_ii_get, _ida_hexrays_micro.codegen_t_ii_set)
    __swig_destroy__ = _ida_hexrays_micro.delete_codegen_t

    def clear(self) ->None:
        return _ida_hexrays_micro.codegen_t_clear(self)

    def analyze_prolog(self, fc: 'qflow_chart_t', reachable: 'bitset_t'
        ) ->'merror_t':
        """Analyze prolog/epilog of the function to decompile. If prolog is found, allocate and fill 'mba->pi' structure. 
        
:param fc: flow chart
:param reachable: bitmap of reachable blocks
:returns: error code"""
        return _ida_hexrays_micro.codegen_t_analyze_prolog(self, fc, reachable)

    def gen_micro(self) ->'merror_t':
        """Generate microcode for one instruction. The instruction is in INSN 
        
:returns: MERR_OK - all ok MERR_BLOCK - all ok, need to switch to new block MERR_BADBLK - delete current block and continue other error codes are fatal"""
        return _ida_hexrays_micro.codegen_t_gen_micro(self)

    def load_operand(self, opnum: int, flags: int=0) ->'mreg_t':
        """Generate microcode to load one operand. 
        
:param opnum: number of INSN operand
:param flags: reserved for future use
:returns: register containing the operand."""
        return _ida_hexrays_micro.codegen_t_load_operand(self, opnum, flags)

    def microgen_completed(self) ->None:
        """This method is called when the microcode generation is done.
"""
        return _ida_hexrays_micro.codegen_t_microgen_completed(self)

    def prepare_gen_micro(self) ->'merror_t':
        """Setup internal data to handle new instruction. This method should be called before calling gen_micro(). Usually gen_micro() is called by the decompiler. You have to call this function explicitly only if you yourself call gen_micro(). The instruction is in INSN 
        
:returns: MERR_OK - all ok other error codes are fatal"""
        return _ida_hexrays_micro.codegen_t_prepare_gen_micro(self)

    def load_effective_address(self, n: int, flags: int=0) ->'mreg_t':
        """Generate microcode to calculate the address of a memory operand. 
        
:param n: - number of INSN operand
:param flags: - reserved for future use
:returns: register containing the operand address. mr_none - failed (not a memory operand)"""
        return _ida_hexrays_micro.codegen_t_load_effective_address(self, n,
            flags)

    def store_operand(self, n: int, mop: 'mop_t', flags: int=0, outins:
        'minsn_t **'=None) ->bool:
        """Generate microcode to store an operand. In case of success an arbitrary number of instructions can be generated (and even no instruction if the source and target are the same) 
        
:param n: - number of target INSN operand
:param mop: - operand to be stored
:param flags: - reserved for future use
:param outins: - (OUT) the last generated instruction
:returns: success"""
        return _ida_hexrays_micro.codegen_t_store_operand(self, n, mop,
            flags, outins)

    def emit_micro_mvm(self, code: 'mcode_t', dtype: 'op_dtype_t', l: int,
        r: int, d: int, offsize: int) ->'minsn_t *':
        """Emit one microinstruction. This variant takes a data type not a size. 
        """
        return _ida_hexrays_micro.codegen_t_emit_micro_mvm(self, code,
            dtype, l, r, d, offsize)

    def emit(self, *args) ->'minsn_t *':
        """This function has the following signatures:

    0. emit(code: mcode_t, width: int, l: int, r: int, d: int, offsize: int) -> minsn_t *
    1. emit(code: mcode_t, l: const mop_t *, r: const mop_t *, d: const mop_t *) -> minsn_t *

# 0: emit(code: mcode_t, width: int, l: int, r: int, d: int, offsize: int) -> minsn_t *

Emit one microinstruction. The L, R, D arguments usually mean the register number. However, they depend on CODE. For example:
* for m_goto and m_jcnd L is the target address
* for m_ldc L is the constant value to load



:returns: created microinstruction. can be nullptr if the instruction got immediately optimized away.

# 1: emit(code: mcode_t, l: const mop_t *, r: const mop_t *, d: const mop_t *) -> minsn_t *

Emit one microinstruction. This variant accepts pointers to operands. It is more difficult to use but permits to create virtually any instruction. Operands may be nullptr when it makes sense. The ownership of the operands is not transferred to the decompiler, so it is ok to destroy them after this call. 
        
"""
        return _ida_hexrays_micro.codegen_t_emit(self, *args)


_ida_hexrays_micro.codegen_t_swigregister(codegen_t)


def change_hexrays_config(directive: str) ->bool:
    """Parse DIRECTIVE and update the current configuration variables. For the syntax see hexrays.cfg 
        """
    return _ida_hexrays_micro.change_hexrays_config(directive)


def get_hexrays_version() ->str:
    """Get decompiler version. The returned string is of the form <major>.<minor>.<revision>.<build-date> 
        
:returns: pointer to version string. For example: "2.0.0.140605\""""
    return _ida_hexrays_micro.get_hexrays_version()


OPF_REUSE = _ida_hexrays_micro.OPF_REUSE
"""reuse existing window
"""
OPF_NEW_WINDOW = _ida_hexrays_micro.OPF_NEW_WINDOW
"""open new window
"""
OPF_REUSE_ACTIVE = _ida_hexrays_micro.OPF_REUSE_ACTIVE
"""reuse existing window, only if the currently active widget is a pseudocode view 
        """
OPF_NO_WAIT = _ida_hexrays_micro.OPF_NO_WAIT
"""do not display waitbox if decompilation happens
"""
OPF_WINDOW_MGMT_MASK = _ida_hexrays_micro.OPF_WINDOW_MGMT_MASK


def open_pseudocode(ea: ida_idaapi.ea_t, flags: int) ->'vdui_t *':
    """Open pseudocode window. The specified function is decompiled and the pseudocode window is opened. 
        
:param ea: function to decompile
:param flags: a combination of OPF_ flags
:returns: false if failed"""
    return _ida_hexrays_micro.open_pseudocode(ea, flags)


def close_pseudocode(f: 'TWidget *') ->bool:
    """Close pseudocode window. 
        
:param f: pointer to window
:returns: false if failed"""
    return _ida_hexrays_micro.close_pseudocode(f)


def get_widget_vdui(f: 'TWidget *') ->'vdui_t *':
    """Get the vdui_t instance associated to the TWidget 
        
:param f: pointer to window
:returns: a vdui_t *, or nullptr"""
    return _ida_hexrays_micro.get_widget_vdui(f)


VDRUN_NEWFILE = _ida_hexrays_micro.VDRUN_NEWFILE
"""Create a new file or overwrite existing file.
"""
VDRUN_APPEND = _ida_hexrays_micro.VDRUN_APPEND
"""Create a new file or append to existing file.
"""
VDRUN_ONLYNEW = _ida_hexrays_micro.VDRUN_ONLYNEW
"""Fail if output file already exists.
"""
VDRUN_SILENT = _ida_hexrays_micro.VDRUN_SILENT
"""Silent decompilation.
"""
VDRUN_SENDIDB = _ida_hexrays_micro.VDRUN_SENDIDB
"""Send problematic databases to hex-rays.com.
"""
VDRUN_MAYSTOP = _ida_hexrays_micro.VDRUN_MAYSTOP
"""The user can cancel decompilation.
"""
VDRUN_CMDLINE = _ida_hexrays_micro.VDRUN_CMDLINE
"""Called from ida's command line.
"""
VDRUN_STATS = _ida_hexrays_micro.VDRUN_STATS
"""Print statistics into vd_stats.txt.
"""
VDRUN_LUMINA = _ida_hexrays_micro.VDRUN_LUMINA
"""Use lumina server.
"""
VDRUN_PERF = _ida_hexrays_micro.VDRUN_PERF
"""Print performance stats to ida.log.
"""


def decompile_many(outfile: str, funcaddrs: 'uint64vec_t', flags: int) ->bool:
    """Batch decompilation. Decompile all or the specified functions 
        
:param outfile: name of the output file
:param funcaddrs: list of functions to decompile. If nullptr or empty, then decompile all nonlib functions
:param flags: Batch decompilation bits
:returns: true if no internal error occurred and the user has not cancelled decompilation"""
    return _ida_hexrays_micro.decompile_many(outfile, funcaddrs, flags)


def send_database(err: 'hexrays_failure_t', silent: bool) ->None:
    """Send the database to Hex-Rays. This function sends the current database to the Hex-Rays server. The database is sent in the compressed form over an encrypted (SSL) connection. 
        
:param err: failure description object. Empty hexrays_failure_t object can be used if error information is not available.
:param silent: if false, a dialog box will be displayed before sending the database."""
    return _ida_hexrays_micro.send_database(err, silent)


class gco_info_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    name: str = property(_ida_hexrays_micro.gco_info_t_name_get,
        _ida_hexrays_micro.gco_info_t_name_set)
    """register or stkvar name
"""
    stkoff: int = property(_ida_hexrays_micro.gco_info_t_stkoff_get,
        _ida_hexrays_micro.gco_info_t_stkoff_set)
    """if stkvar, stack offset
"""
    regnum: int = property(_ida_hexrays_micro.gco_info_t_regnum_get,
        _ida_hexrays_micro.gco_info_t_regnum_set)
    """if register, the register id
"""
    size: int = property(_ida_hexrays_micro.gco_info_t_size_get,
        _ida_hexrays_micro.gco_info_t_size_set)
    """operand size
"""
    flags: int = property(_ida_hexrays_micro.gco_info_t_flags_get,
        _ida_hexrays_micro.gco_info_t_flags_set)

    def is_reg(self) ->bool:
        return _ida_hexrays_micro.gco_info_t_is_reg(self)

    def is_use(self) ->bool:
        return _ida_hexrays_micro.gco_info_t_is_use(self)

    def is_def(self) ->bool:
        return _ida_hexrays_micro.gco_info_t_is_def(self)

    def append_to_list(self, list: 'mlist_t', mba: 'mba_t') ->bool:
        """Append operand info to LIST. This function converts IDA register number or stack offset to a decompiler list. 
        
:param list: list to append to
:param mba: microcode object"""
        return _ida_hexrays_micro.gco_info_t_append_to_list(self, list, mba)

    def cvt_to_ivl(self) ->'vivl_t':
        """Convert operand info to VIVL. The returned VIVL can be used, for example, in a call of get_valranges(). 
        """
        return _ida_hexrays_micro.gco_info_t_cvt_to_ivl(self)

    def __init__(self):
        _ida_hexrays_micro.gco_info_t_swiginit(self, _ida_hexrays_micro.
            new_gco_info_t())
    __swig_destroy__ = _ida_hexrays_micro.delete_gco_info_t


_ida_hexrays_micro.gco_info_t_swigregister(gco_info_t)
GCO_STK = _ida_hexrays_micro.GCO_STK
"""a stack variable
"""
GCO_REG = _ida_hexrays_micro.GCO_REG
"""is register? otherwise a stack variable
"""
GCO_USE = _ida_hexrays_micro.GCO_USE
"""is source operand?
"""
GCO_DEF = _ida_hexrays_micro.GCO_DEF
"""is destination operand?
"""


def get_current_operand(out: 'gco_info_t') ->bool:
    """Get the instruction operand under the cursor. This function determines the operand that is under the cursor in the active disassembly listing. If the operand refers to a register or stack variable, it returns true. 
        """
    return _ida_hexrays_micro.get_current_operand(out)


class array_of_ivlsets(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_micro.array_of_ivlsets_swiginit(self,
            _ida_hexrays_micro.new_array_of_ivlsets(*args))
    __swig_destroy__ = _ida_hexrays_micro.delete_array_of_ivlsets

    def push_back(self, *args) ->'ivlset_t &':
        return _ida_hexrays_micro.array_of_ivlsets_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_micro.array_of_ivlsets_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_micro.array_of_ivlsets_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_micro.array_of_ivlsets_empty(self)

    def at(self, _idx: int) ->'ivlset_t const &':
        return _ida_hexrays_micro.array_of_ivlsets_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_micro.array_of_ivlsets_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_micro.array_of_ivlsets_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_micro.array_of_ivlsets_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_micro.array_of_ivlsets_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_micro.array_of_ivlsets_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_micro.array_of_ivlsets_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_micro.array_of_ivlsets_truncate(self)

    def swap(self, r: 'array_of_ivlsets') ->None:
        return _ida_hexrays_micro.array_of_ivlsets_swap(self, r)

    def extract(self) ->'ivlset_t *':
        return _ida_hexrays_micro.array_of_ivlsets_extract(self)

    def inject(self, s: 'ivlset_t', len: int) ->None:
        return _ida_hexrays_micro.array_of_ivlsets_inject(self, s, len)

    def __eq__(self, r: 'array_of_ivlsets') ->bool:
        return _ida_hexrays_micro.array_of_ivlsets___eq__(self, r)

    def __ne__(self, r: 'array_of_ivlsets') ->bool:
        return _ida_hexrays_micro.array_of_ivlsets___ne__(self, r)

    def begin(self, *args) ->'qvector< ivlset_t >::const_iterator':
        return _ida_hexrays_micro.array_of_ivlsets_begin(self, *args)

    def end(self, *args) ->'qvector< ivlset_t >::const_iterator':
        return _ida_hexrays_micro.array_of_ivlsets_end(self, *args)

    def insert(self, it: 'ivlset_t', x: 'ivlset_t'
        ) ->'qvector< ivlset_t >::iterator':
        return _ida_hexrays_micro.array_of_ivlsets_insert(self, it, x)

    def erase(self, *args) ->'qvector< ivlset_t >::iterator':
        return _ida_hexrays_micro.array_of_ivlsets_erase(self, *args)

    def find(self, *args) ->'qvector< ivlset_t >::const_iterator':
        return _ida_hexrays_micro.array_of_ivlsets_find(self, *args)

    def has(self, x: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.array_of_ivlsets_has(self, x)

    def add_unique(self, x: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.array_of_ivlsets_add_unique(self, x)

    def _del(self, x: 'ivlset_t') ->bool:
        return _ida_hexrays_micro.array_of_ivlsets__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_micro.array_of_ivlsets___len__(self)

    def __getitem__(self, i: int) ->'ivlset_t const &':
        return _ida_hexrays_micro.array_of_ivlsets___getitem__(self, i)

    def __setitem__(self, i: int, v: 'ivlset_t') ->None:
        return _ida_hexrays_micro.array_of_ivlsets___setitem__(self, i, v)

    def append(self, x: 'ivlset_t') ->None:
        return _ida_hexrays_micro.array_of_ivlsets_append(self, x)

    def extend(self, x: 'array_of_ivlsets') ->None:
        return _ida_hexrays_micro.array_of_ivlsets_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_micro.array_of_ivlsets_swigregister(array_of_ivlsets)
hexrays_failure_t.__repr__ = lambda self: str('%x: %s' % (self.errea, self.
    desc()))
is_small_struni = is_small_udt
mbl_array_t = mba_t
import ida_idaapi
ida_idaapi._listify_types(qvector_lvar_t, lvar_saved_infos_t)
lvar_t.used = property(lvar_t.used)
lvar_t.typed = property(lvar_t.typed)
lvar_t.mreg_done = property(lvar_t.mreg_done)
lvar_t.has_nice_name = property(lvar_t.has_nice_name)
lvar_t.is_unknown_width = property(lvar_t.is_unknown_width)
lvar_t.has_user_info = property(lvar_t.has_user_info)
lvar_t.has_user_name = property(lvar_t.has_user_name)
lvar_t.has_user_type = property(lvar_t.has_user_type)
lvar_t.is_result_var = property(lvar_t.is_result_var)
lvar_t.is_arg_var = property(lvar_t.is_arg_var)
lvar_t.is_fake_var = property(lvar_t.is_fake_var)
lvar_t.is_overlapped_var = property(lvar_t.is_overlapped_var)
lvar_t.is_floating_var = property(lvar_t.is_floating_var)
lvar_t.is_spoiled_var = property(lvar_t.is_spoiled_var)
lvar_t.is_mapdst_var = property(lvar_t.is_mapdst_var)
