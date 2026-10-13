"""There are 2 representations of the binary code in the decompiler:

Hex-Rays Decompiler project Copyright (c) 1990-2025 Hex-Rays ALL RIGHTS RESERVED.

* microcode: processor instructions are translated into it and then the decompiler optimizes and transforms it
* ctree: ctree is built from the optimized microcode and represents AST-like tree with C statements and expressions. It can be printed as C code.


Microcode is represented by the following classes:
* mba_t keeps general info about the decompiled code and array of basic blocks. usually mba_t is named 'mba'
* mblock_t a basic block. includes list of instructions
* minsn_t an instruction. contains 3 operands: left, right, and destination
* mop_t an operand. depending on its type may hold various info like a number, register, stack variable, etc.
* mlist_t list of memory or register locations; can hold vast areas of memory and multiple registers. this class is used very extensively in the decompiler. it may represent list of locations accessed by an instruction or even an entire basic block. it is also used as argument of many functions. for example, there is a function that searches for an instruction that refers to a mlist_t.


See [https://hex-rays.com/blog/microcode-in-pictures](https://hex-rays.com/blog/microcode-in-pictures) for a few pictures.
Ctree is represented by:
* cfunc_t keeps general info about the decompiled code, including a pointer to mba_t. deleting cfunc_t will delete mba_t too (however, decompiler returns cfuncptr_t, which is a reference counting object and deletes the underlying function as soon as all references to it go out of scope). cfunc_t has 'body', which represents the decompiled function body as cinsn_t.
* cinsn_t a C statement. can be a compound statement or any other legal C statements (like if, for, while, return, expression-statement, etc). depending on the statement type has pointers to additional info. for example, the 'if' statement has poiner to cif_t, which holds the 'if' condition, 'then' branch, and optionally 'else' branch. Please note that despite of the name cinsn_t we say "statements", not "instructions". For us instructions are part of microcode, not ctree.
* cexpr_t a C expression. is used as part of a C statement, when necessary. cexpr_t has 'type' field, which keeps the expression type.
* citem_t a base class for cinsn_t and cexpr_t, holds common info like the address, label, and opcode.
* cnumber_t a constant 64-bit number. in addition to its value also holds information how to represent it: decimal, hex, or as a symbolic constant (enum member). please note that numbers are represented by another class (mnumber_t) in microcode.


See [https://hex-rays.com/blog/hex-rays-decompiler-primer](https://hex-rays.com/blog/hex-rays-decompiler-primer) for more pictures and more details.
Both microcode and ctree use the following class:
* lvar_t a local variable. may represent a stack or register variable. a variable has a name, type, location, etc. the list of variables is stored in mba->vars.
* lvar_locator_t holds a variable location (vdloc_t) and its definition address.
* vdloc_t describes a variable location, like a register number, a stack offset, or, in complex cases, can be a mix of register and stack locations. very similar to argloc_t, which is used in ida. the differences between argloc_t and vdloc_t are:
* vdloc_t never uses ARGLOC_REG2
* vdloc_t uses micro register numbers instead of processor register numbers
* the stack offsets are never negative in vdloc_t, while in argloc_t there can be negative offsets




The above are the most important classes in this header file. There are many auxiliary classes, please see their definitions in the header file.
See also the description of Virtual Machine used by Microcode. 
    """
from __future__ import annotations
from sys import version_info as _swig_python_version_info
if __package__ or '.' in __name__:
    from . import _ida_hexrays
else:
    import _ida_hexrays
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
SWIG_PYTHON_LEGACY_BOOL = _ida_hexrays.SWIG_PYTHON_LEGACY_BOOL
from typing import Tuple, List, Union
import ida_idaapi


def _kludge_force_declare_TPopupMenu(arg1: 'TPopupMenu const *') ->None:
    return _ida_hexrays._kludge_force_declare_TPopupMenu(arg1)


def get_widget_vdui(f: 'TWidget *') ->'vdui_t *':
    """Get the vdui_t instance associated to the TWidget 
        
:param f: pointer to window
:returns: a vdui_t *, or nullptr"""
    return _ida_hexrays.get_widget_vdui(f)


def init_hexrays_plugin(flags: int=0) ->bool:
    """Check that your plugin is compatible with hex-rays decompiler. This function must be called before calling any other decompiler function. 
        
:param flags: reserved, must be 0
:returns: true if the decompiler exists and is compatible with your plugin"""
    return _ida_hexrays.init_hexrays_plugin(flags)


def boundaries_find(map: 'boundaries_t', key: 'cinsn_t'
    ) ->'boundaries_iterator_t':
    """Find the specified key in boundaries_t.
"""
    return _ida_hexrays.boundaries_find(map, key)


def boundaries_insert(map: 'boundaries_t', key: 'cinsn_t', val: 'rangeset_t'
    ) ->'boundaries_iterator_t':
    """Insert new (cinsn_t *, rangeset_t) pair into boundaries_t.
"""
    return _ida_hexrays.boundaries_insert(map, key, val)


def term_hexrays_plugin() ->None:
    """Stop working with hex-rays decompiler.
"""
    return _ida_hexrays.term_hexrays_plugin()


import ida_pro
import ida_range
from ida_hexrays_defs import *
from ida_hexrays_micro import *
from ida_hexrays_ctree import *


def _map_as_dict(_ida_module, maptype, name, keytype, valuetype):
    maptype.keytype = keytype
    maptype.valuetype = valuetype
    for fctname in ['begin', 'end', 'first', 'second', 'next', 'find',
        'insert', 'erase', 'clear', 'size']:
        fct = getattr(_ida_module, name + '_' + fctname)
        setattr(maptype, '__' + fctname, fct)
    maptype.__len__ = maptype.size
    maptype.__getitem__ = maptype.at
    maptype.begin = lambda self, *args: self.__begin(self, *args)
    maptype.end = lambda self, *args: self.__end(self, *args)
    maptype.first = lambda self, *args: self.__first(*args)
    maptype.second = lambda self, *args: self.__second(*args)
    maptype.next = lambda self, *args: self.__next(*args)
    maptype.find = lambda self, *args: self.__find(self, *args)
    maptype.insert = lambda self, *args: self.__insert(self, *args)
    maptype.erase = lambda self, *args: self.__erase(self, *args)
    maptype.clear = lambda self, *args: self.__clear(self, *args)
    maptype.size = lambda self, *args: self.__size(self, *args)

    def _map___iter__(self):
        """ Iterate over dictionary keys. """
        return self.iterkeys()
    maptype.__iter__ = _map___iter__

    def _map___getitem__(self, key):
        """ Returns the value associated with the provided key. """
        if not isinstance(key, self.keytype):
            raise KeyError('type of key should be ' + repr(self.keytype) +
                ' but got ' + repr(type(key)))
        if key not in self:
            raise KeyError('key not found')
        return self.second(self.find(key))
    maptype.__getitem__ = _map___getitem__

    def _map___setitem__(self, key, value):
        """ Returns the value associated with the provided key. """
        if not isinstance(key, self.keytype):
            raise KeyError('type of `key` should be ' + repr(self.keytype) +
                ' but got ' + repr(type(key)))
        if not isinstance(value, self.valuetype):
            raise KeyError('type of `value` should be ' + repr(self.
                valuetype) + ' but got ' + type(value))
        self.insert(key, value)
        return
    maptype.__setitem__ = _map___setitem__

    def _map___delitem__(self, key):
        """ Removes the value associated with the provided key. """
        if not isinstance(key, self.keytype):
            raise KeyError('type of `key` should be ' + repr(self.keytype) +
                ' but got ' + repr(type(key)))
        if key not in self:
            raise KeyError('key not found')
        self.erase(self.find(key))
        return
    maptype.__delitem__ = _map___delitem__

    def _map___contains__(self, key):
        """ Returns true if the specified key exists in the . """
        if not isinstance(key, self.keytype):
            raise KeyError('type of `key` should be ' + repr(self.keytype) +
                ' but got ' + repr(type(key)))
        if self.find(key) != self.end():
            return True
        return False
    maptype.__contains__ = _map___contains__

    def _map_clear(self):
        self.clear()
        return
    maptype.clear = _map_clear

    def _map_copy(self):
        ret = {}
        for k in self.iterkeys():
            ret[k] = self[k]
        return ret
    maptype.copy = _map_copy

    def _map_get(self, key, default=None):
        if key in self:
            return self[key]
        return default
    maptype.get = _map_get

    def _map_iterkeys(self):
        iter = self.begin()
        while iter != self.end():
            yield self.first(iter)
            iter = self.next(iter)
        return
    maptype.iterkeys = _map_iterkeys

    def _map_itervalues(self):
        iter = self.begin()
        while iter != self.end():
            yield self.second(iter)
            iter = self.next(iter)
        return
    maptype.itervalues = _map_itervalues

    def _map_iteritems(self):
        iter = self.begin()
        while iter != self.end():
            yield self.first(iter), self.second(iter)
            iter = self.next(iter)
        return
    maptype.iteritems = _map_iteritems

    def _map_keys(self):
        return list(self.iterkeys())
    maptype.keys = _map_keys

    def _map_values(self):
        return list(self.itervalues())
    maptype.values = _map_values

    def _map_items(self):
        return list(self.iteritems())
    maptype.items = _map_items

    def _map_has_key(self, key):
        return key in self
    maptype.has_key = _map_has_key

    def _map_pop(self, key):
        """ Sets the value associated with the provided key. """
        if not isinstance(key, self.keytype):
            raise KeyError('type of `key` should be ' + repr(self.keytype) +
                ' but got ' + repr(type(key)))
        if key not in self:
            raise KeyError('key not found')
        ret = self[key]
        del self[key]
        return ret
    maptype.pop = _map_pop

    def _map_popitem(self):
        """ Sets the value associated with the provided key. """
        if len(self) == 0:
            raise KeyError('key not found')
        key = self.keys()[0]
        return key, self.pop(key)
    maptype.popitem = _map_popitem

    def _map_setdefault(self, key, default=None):
        """ Sets the value associated with the provided key. """
        if not isinstance(key, self.keytype):
            raise KeyError('type of `key` should be ' + repr(self.keytype) +
                ' but got ' + repr(type(key)))
        if key in self:
            return self[key]
        self[key] = default
        return default
    maptype.setdefault = _map_setdefault


_map_as_dict(_ida_hexrays, user_numforms_t, 'user_numforms',
    operand_locator_t, number_format_t)
_map_as_dict(_ida_hexrays, user_cmts_t, 'user_cmts', treeloc_t, citem_cmt_t)
_map_as_dict(_ida_hexrays, user_iflags_t, 'user_iflags', citem_locator_t, int)
_map_as_dict(_ida_hexrays, user_unions_t, 'user_unions', ida_idaapi.
    integer_types, ida_pro.intvec_t)
_map_as_dict(_ida_hexrays, eamap_t, 'eamap', ida_idaapi.long_type,
    cinsnptrvec_t)
_map_as_dict(_ida_hexrays, boundaries_t, 'boundaries', cinsn_t, ida_range.
    rangeset_t)
import ida_hexrays_defs
import ida_hexrays_ctree
import ida_hexrays_micro
hx_user_numforms_begin = _ida_hexrays.hx_user_numforms_begin
hx_user_numforms_end = _ida_hexrays.hx_user_numforms_end
hx_user_numforms_next = _ida_hexrays.hx_user_numforms_next
hx_user_numforms_prev = _ida_hexrays.hx_user_numforms_prev
hx_user_numforms_first = _ida_hexrays.hx_user_numforms_first
hx_user_numforms_second = _ida_hexrays.hx_user_numforms_second
hx_user_numforms_find = _ida_hexrays.hx_user_numforms_find
hx_user_numforms_insert = _ida_hexrays.hx_user_numforms_insert
hx_user_numforms_erase = _ida_hexrays.hx_user_numforms_erase
hx_user_numforms_clear = _ida_hexrays.hx_user_numforms_clear
hx_user_numforms_size = _ida_hexrays.hx_user_numforms_size
hx_user_numforms_free = _ida_hexrays.hx_user_numforms_free
hx_user_numforms_new = _ida_hexrays.hx_user_numforms_new
hx_lvar_mapping_begin = _ida_hexrays.hx_lvar_mapping_begin
hx_lvar_mapping_end = _ida_hexrays.hx_lvar_mapping_end
hx_lvar_mapping_next = _ida_hexrays.hx_lvar_mapping_next
hx_lvar_mapping_prev = _ida_hexrays.hx_lvar_mapping_prev
hx_lvar_mapping_first = _ida_hexrays.hx_lvar_mapping_first
hx_lvar_mapping_second = _ida_hexrays.hx_lvar_mapping_second
hx_lvar_mapping_find = _ida_hexrays.hx_lvar_mapping_find
hx_lvar_mapping_insert = _ida_hexrays.hx_lvar_mapping_insert
hx_lvar_mapping_erase = _ida_hexrays.hx_lvar_mapping_erase
hx_lvar_mapping_clear = _ida_hexrays.hx_lvar_mapping_clear
hx_lvar_mapping_size = _ida_hexrays.hx_lvar_mapping_size
hx_lvar_mapping_free = _ida_hexrays.hx_lvar_mapping_free
hx_lvar_mapping_new = _ida_hexrays.hx_lvar_mapping_new
hx_udcall_map_begin = _ida_hexrays.hx_udcall_map_begin
hx_udcall_map_end = _ida_hexrays.hx_udcall_map_end
hx_udcall_map_next = _ida_hexrays.hx_udcall_map_next
hx_udcall_map_prev = _ida_hexrays.hx_udcall_map_prev
hx_udcall_map_first = _ida_hexrays.hx_udcall_map_first
hx_udcall_map_second = _ida_hexrays.hx_udcall_map_second
hx_udcall_map_find = _ida_hexrays.hx_udcall_map_find
hx_udcall_map_insert = _ida_hexrays.hx_udcall_map_insert
hx_udcall_map_erase = _ida_hexrays.hx_udcall_map_erase
hx_udcall_map_clear = _ida_hexrays.hx_udcall_map_clear
hx_udcall_map_size = _ida_hexrays.hx_udcall_map_size
hx_udcall_map_free = _ida_hexrays.hx_udcall_map_free
hx_udcall_map_new = _ida_hexrays.hx_udcall_map_new
hx_user_cmts_begin = _ida_hexrays.hx_user_cmts_begin
hx_user_cmts_end = _ida_hexrays.hx_user_cmts_end
hx_user_cmts_next = _ida_hexrays.hx_user_cmts_next
hx_user_cmts_prev = _ida_hexrays.hx_user_cmts_prev
hx_user_cmts_first = _ida_hexrays.hx_user_cmts_first
hx_user_cmts_second = _ida_hexrays.hx_user_cmts_second
hx_user_cmts_find = _ida_hexrays.hx_user_cmts_find
hx_user_cmts_insert = _ida_hexrays.hx_user_cmts_insert
hx_user_cmts_erase = _ida_hexrays.hx_user_cmts_erase
hx_user_cmts_clear = _ida_hexrays.hx_user_cmts_clear
hx_user_cmts_size = _ida_hexrays.hx_user_cmts_size
hx_user_cmts_free = _ida_hexrays.hx_user_cmts_free
hx_user_cmts_new = _ida_hexrays.hx_user_cmts_new
hx_user_iflags_begin = _ida_hexrays.hx_user_iflags_begin
hx_user_iflags_end = _ida_hexrays.hx_user_iflags_end
hx_user_iflags_next = _ida_hexrays.hx_user_iflags_next
hx_user_iflags_prev = _ida_hexrays.hx_user_iflags_prev
hx_user_iflags_first = _ida_hexrays.hx_user_iflags_first
hx_user_iflags_second = _ida_hexrays.hx_user_iflags_second
hx_user_iflags_find = _ida_hexrays.hx_user_iflags_find
hx_user_iflags_insert = _ida_hexrays.hx_user_iflags_insert
hx_user_iflags_erase = _ida_hexrays.hx_user_iflags_erase
hx_user_iflags_clear = _ida_hexrays.hx_user_iflags_clear
hx_user_iflags_size = _ida_hexrays.hx_user_iflags_size
hx_user_iflags_free = _ida_hexrays.hx_user_iflags_free
hx_user_iflags_new = _ida_hexrays.hx_user_iflags_new
hx_user_unions_begin = _ida_hexrays.hx_user_unions_begin
hx_user_unions_end = _ida_hexrays.hx_user_unions_end
hx_user_unions_next = _ida_hexrays.hx_user_unions_next
hx_user_unions_prev = _ida_hexrays.hx_user_unions_prev
hx_user_unions_first = _ida_hexrays.hx_user_unions_first
hx_user_unions_second = _ida_hexrays.hx_user_unions_second
hx_user_unions_find = _ida_hexrays.hx_user_unions_find
hx_user_unions_insert = _ida_hexrays.hx_user_unions_insert
hx_user_unions_erase = _ida_hexrays.hx_user_unions_erase
hx_user_unions_clear = _ida_hexrays.hx_user_unions_clear
hx_user_unions_size = _ida_hexrays.hx_user_unions_size
hx_user_unions_free = _ida_hexrays.hx_user_unions_free
hx_user_unions_new = _ida_hexrays.hx_user_unions_new
hx_user_labels_begin = _ida_hexrays.hx_user_labels_begin
hx_user_labels_end = _ida_hexrays.hx_user_labels_end
hx_user_labels_next = _ida_hexrays.hx_user_labels_next
hx_user_labels_prev = _ida_hexrays.hx_user_labels_prev
hx_user_labels_first = _ida_hexrays.hx_user_labels_first
hx_user_labels_second = _ida_hexrays.hx_user_labels_second
hx_user_labels_find = _ida_hexrays.hx_user_labels_find
hx_user_labels_insert = _ida_hexrays.hx_user_labels_insert
hx_user_labels_erase = _ida_hexrays.hx_user_labels_erase
hx_user_labels_clear = _ida_hexrays.hx_user_labels_clear
hx_user_labels_size = _ida_hexrays.hx_user_labels_size
hx_user_labels_free = _ida_hexrays.hx_user_labels_free
hx_user_labels_new = _ida_hexrays.hx_user_labels_new
hx_eamap_begin = _ida_hexrays.hx_eamap_begin
hx_eamap_end = _ida_hexrays.hx_eamap_end
hx_eamap_next = _ida_hexrays.hx_eamap_next
hx_eamap_prev = _ida_hexrays.hx_eamap_prev
hx_eamap_first = _ida_hexrays.hx_eamap_first
hx_eamap_second = _ida_hexrays.hx_eamap_second
hx_eamap_find = _ida_hexrays.hx_eamap_find
hx_eamap_insert = _ida_hexrays.hx_eamap_insert
hx_eamap_erase = _ida_hexrays.hx_eamap_erase
hx_eamap_clear = _ida_hexrays.hx_eamap_clear
hx_eamap_size = _ida_hexrays.hx_eamap_size
hx_eamap_free = _ida_hexrays.hx_eamap_free
hx_eamap_new = _ida_hexrays.hx_eamap_new
hx_boundaries_begin = _ida_hexrays.hx_boundaries_begin
hx_boundaries_end = _ida_hexrays.hx_boundaries_end
hx_boundaries_next = _ida_hexrays.hx_boundaries_next
hx_boundaries_prev = _ida_hexrays.hx_boundaries_prev
hx_boundaries_first = _ida_hexrays.hx_boundaries_first
hx_boundaries_second = _ida_hexrays.hx_boundaries_second
hx_boundaries_find = _ida_hexrays.hx_boundaries_find
hx_boundaries_insert = _ida_hexrays.hx_boundaries_insert
hx_boundaries_erase = _ida_hexrays.hx_boundaries_erase
hx_boundaries_clear = _ida_hexrays.hx_boundaries_clear
hx_boundaries_size = _ida_hexrays.hx_boundaries_size
hx_boundaries_free = _ida_hexrays.hx_boundaries_free
hx_boundaries_new = _ida_hexrays.hx_boundaries_new
hx_block_chains_begin = _ida_hexrays.hx_block_chains_begin
hx_block_chains_end = _ida_hexrays.hx_block_chains_end
hx_block_chains_next = _ida_hexrays.hx_block_chains_next
hx_block_chains_prev = _ida_hexrays.hx_block_chains_prev
hx_block_chains_get = _ida_hexrays.hx_block_chains_get
hx_block_chains_find = _ida_hexrays.hx_block_chains_find
hx_block_chains_insert = _ida_hexrays.hx_block_chains_insert
hx_block_chains_erase = _ida_hexrays.hx_block_chains_erase
hx_block_chains_clear = _ida_hexrays.hx_block_chains_clear
hx_block_chains_size = _ida_hexrays.hx_block_chains_size
hx_block_chains_free = _ida_hexrays.hx_block_chains_free
hx_block_chains_new = _ida_hexrays.hx_block_chains_new
hx_hexrays_alloc = _ida_hexrays.hx_hexrays_alloc
hx_hexrays_free = _ida_hexrays.hx_hexrays_free
hx_valrng_t_clear = _ida_hexrays.hx_valrng_t_clear
hx_valrng_t_copy = _ida_hexrays.hx_valrng_t_copy
hx_valrng_t_assign = _ida_hexrays.hx_valrng_t_assign
hx_valrng_t_compare = _ida_hexrays.hx_valrng_t_compare
hx_valrng_t_set_eq = _ida_hexrays.hx_valrng_t_set_eq
hx_valrng_t_set_cmp = _ida_hexrays.hx_valrng_t_set_cmp
hx_valrng_t_reduce_size = _ida_hexrays.hx_valrng_t_reduce_size
hx_valrng_t_intersect_with = _ida_hexrays.hx_valrng_t_intersect_with
hx_valrng_t_unite_with = _ida_hexrays.hx_valrng_t_unite_with
hx_valrng_t_inverse = _ida_hexrays.hx_valrng_t_inverse
hx_valrng_t_has = _ida_hexrays.hx_valrng_t_has
hx_valrng_t_print = _ida_hexrays.hx_valrng_t_print
hx_valrng_t_dstr = _ida_hexrays.hx_valrng_t_dstr
hx_valrng_t_cvt_to_single_value = _ida_hexrays.hx_valrng_t_cvt_to_single_value
hx_valrng_t_cvt_to_cmp = _ida_hexrays.hx_valrng_t_cvt_to_cmp
hx_get_merror_desc = _ida_hexrays.hx_get_merror_desc
hx_must_mcode_close_block = _ida_hexrays.hx_must_mcode_close_block
hx_is_mcode_propagatable = _ida_hexrays.hx_is_mcode_propagatable
hx_negate_mcode_relation = _ida_hexrays.hx_negate_mcode_relation
hx_swap_mcode_relation = _ida_hexrays.hx_swap_mcode_relation
hx_get_signed_mcode = _ida_hexrays.hx_get_signed_mcode
hx_get_unsigned_mcode = _ida_hexrays.hx_get_unsigned_mcode
hx_mcode_modifies_d = _ida_hexrays.hx_mcode_modifies_d
hx_operand_locator_t_compare = _ida_hexrays.hx_operand_locator_t_compare
hx_vd_printer_t_print = _ida_hexrays.hx_vd_printer_t_print
hx_file_printer_t_print = _ida_hexrays.hx_file_printer_t_print
hx_qstring_printer_t_print = _ida_hexrays.hx_qstring_printer_t_print
hx_dstr = _ida_hexrays.hx_dstr
hx_is_type_correct = _ida_hexrays.hx_is_type_correct
hx_is_small_udt = _ida_hexrays.hx_is_small_udt
hx_is_nonbool_type = _ida_hexrays.hx_is_nonbool_type
hx_is_bool_type = _ida_hexrays.hx_is_bool_type
hx_partial_type_num = _ida_hexrays.hx_partial_type_num
hx_get_float_type = _ida_hexrays.hx_get_float_type
hx_get_int_type_by_width_and_sign = (_ida_hexrays.
    hx_get_int_type_by_width_and_sign)
hx_get_unk_type = _ida_hexrays.hx_get_unk_type
hx_dummy_ptrtype = _ida_hexrays.hx_dummy_ptrtype
hx_get_member_type = _ida_hexrays.hx_get_member_type
hx_make_pointer = _ida_hexrays.hx_make_pointer
hx_create_typedef = _ida_hexrays.hx_create_typedef
hx_get_type = _ida_hexrays.hx_get_type
hx_set_type = _ida_hexrays.hx_set_type
hx_vdloc_t_dstr = _ida_hexrays.hx_vdloc_t_dstr
hx_vdloc_t_compare = _ida_hexrays.hx_vdloc_t_compare
hx_vdloc_t_is_aliasable = _ida_hexrays.hx_vdloc_t_is_aliasable
hx_print_vdloc = _ida_hexrays.hx_print_vdloc
hx_arglocs_overlap = _ida_hexrays.hx_arglocs_overlap
hx_lvar_locator_t_compare = _ida_hexrays.hx_lvar_locator_t_compare
hx_lvar_locator_t_dstr = _ida_hexrays.hx_lvar_locator_t_dstr
hx_lvar_t_dstr = _ida_hexrays.hx_lvar_t_dstr
hx_lvar_t_is_promoted_arg = _ida_hexrays.hx_lvar_t_is_promoted_arg
hx_lvar_t_accepts_type = _ida_hexrays.hx_lvar_t_accepts_type
hx_lvar_t_set_lvar_type = _ida_hexrays.hx_lvar_t_set_lvar_type
hx_lvar_t_set_width = _ida_hexrays.hx_lvar_t_set_width
hx_lvar_t_append_list = _ida_hexrays.hx_lvar_t_append_list
hx_lvar_t_append_list_ = _ida_hexrays.hx_lvar_t_append_list_
hx_lvars_t_find_stkvar = _ida_hexrays.hx_lvars_t_find_stkvar
hx_lvars_t_find = _ida_hexrays.hx_lvars_t_find
hx_lvars_t_find_lvar = _ida_hexrays.hx_lvars_t_find_lvar
hx_restore_user_lvar_settings = _ida_hexrays.hx_restore_user_lvar_settings
hx_save_user_lvar_settings = _ida_hexrays.hx_save_user_lvar_settings
hx_modify_user_lvars = _ida_hexrays.hx_modify_user_lvars
hx_modify_user_lvar_info = _ida_hexrays.hx_modify_user_lvar_info
hx_locate_lvar = _ida_hexrays.hx_locate_lvar
hx_restore_user_defined_calls = _ida_hexrays.hx_restore_user_defined_calls
hx_save_user_defined_calls = _ida_hexrays.hx_save_user_defined_calls
hx_parse_user_call = _ida_hexrays.hx_parse_user_call
hx_convert_to_user_call = _ida_hexrays.hx_convert_to_user_call
hx_install_microcode_filter = _ida_hexrays.hx_install_microcode_filter
hx_udc_filter_t_cleanup = _ida_hexrays.hx_udc_filter_t_cleanup
hx_udc_filter_t_init = _ida_hexrays.hx_udc_filter_t_init
hx_udc_filter_t_apply = _ida_hexrays.hx_udc_filter_t_apply
hx_bitset_t_bitset_t = _ida_hexrays.hx_bitset_t_bitset_t
hx_bitset_t_copy = _ida_hexrays.hx_bitset_t_copy
hx_bitset_t_add = _ida_hexrays.hx_bitset_t_add
hx_bitset_t_add_ = _ida_hexrays.hx_bitset_t_add_
hx_bitset_t_add__ = _ida_hexrays.hx_bitset_t_add__
hx_bitset_t_sub = _ida_hexrays.hx_bitset_t_sub
hx_bitset_t_sub_ = _ida_hexrays.hx_bitset_t_sub_
hx_bitset_t_sub__ = _ida_hexrays.hx_bitset_t_sub__
hx_bitset_t_cut_at = _ida_hexrays.hx_bitset_t_cut_at
hx_bitset_t_shift_down = _ida_hexrays.hx_bitset_t_shift_down
hx_bitset_t_has = _ida_hexrays.hx_bitset_t_has
hx_bitset_t_has_all = _ida_hexrays.hx_bitset_t_has_all
hx_bitset_t_has_any = _ida_hexrays.hx_bitset_t_has_any
hx_bitset_t_dstr = _ida_hexrays.hx_bitset_t_dstr
hx_bitset_t_empty = _ida_hexrays.hx_bitset_t_empty
hx_bitset_t_count = _ida_hexrays.hx_bitset_t_count
hx_bitset_t_count_ = _ida_hexrays.hx_bitset_t_count_
hx_bitset_t_last = _ida_hexrays.hx_bitset_t_last
hx_bitset_t_fill_with_ones = _ida_hexrays.hx_bitset_t_fill_with_ones
hx_bitset_t_fill_gaps = _ida_hexrays.hx_bitset_t_fill_gaps
hx_bitset_t_has_common = _ida_hexrays.hx_bitset_t_has_common
hx_bitset_t_intersect = _ida_hexrays.hx_bitset_t_intersect
hx_bitset_t_is_subset_of = _ida_hexrays.hx_bitset_t_is_subset_of
hx_bitset_t_compare = _ida_hexrays.hx_bitset_t_compare
hx_bitset_t_goup = _ida_hexrays.hx_bitset_t_goup
hx_ivl_t_dstr = _ida_hexrays.hx_ivl_t_dstr
hx_ivl_t_compare = _ida_hexrays.hx_ivl_t_compare
hx_ivlset_t_add = _ida_hexrays.hx_ivlset_t_add
hx_ivlset_t_add_ = _ida_hexrays.hx_ivlset_t_add_
hx_ivlset_t_addmasked = _ida_hexrays.hx_ivlset_t_addmasked
hx_ivlset_t_sub = _ida_hexrays.hx_ivlset_t_sub
hx_ivlset_t_sub_ = _ida_hexrays.hx_ivlset_t_sub_
hx_ivlset_t_has_common = _ida_hexrays.hx_ivlset_t_has_common
hx_ivlset_t_print = _ida_hexrays.hx_ivlset_t_print
hx_ivlset_t_dstr = _ida_hexrays.hx_ivlset_t_dstr
hx_ivlset_t_count = _ida_hexrays.hx_ivlset_t_count
hx_ivlset_t_has_common_ = _ida_hexrays.hx_ivlset_t_has_common_
hx_ivlset_t_contains = _ida_hexrays.hx_ivlset_t_contains
hx_ivlset_t_includes = _ida_hexrays.hx_ivlset_t_includes
hx_ivlset_t_intersect = _ida_hexrays.hx_ivlset_t_intersect
hx_ivlset_t_compare = _ida_hexrays.hx_ivlset_t_compare
hx_rlist_t_print = _ida_hexrays.hx_rlist_t_print
hx_rlist_t_dstr = _ida_hexrays.hx_rlist_t_dstr
hx_mlist_t_addmem = _ida_hexrays.hx_mlist_t_addmem
hx_mlist_t_print = _ida_hexrays.hx_mlist_t_print
hx_mlist_t_dstr = _ida_hexrays.hx_mlist_t_dstr
hx_mlist_t_compare = _ida_hexrays.hx_mlist_t_compare
hx_get_temp_regs = _ida_hexrays.hx_get_temp_regs
hx_is_kreg = _ida_hexrays.hx_is_kreg
hx_reg2mreg = _ida_hexrays.hx_reg2mreg
hx_mreg2reg = _ida_hexrays.hx_mreg2reg
hx_get_mreg_name = _ida_hexrays.hx_get_mreg_name
hx_install_optinsn_handler = _ida_hexrays.hx_install_optinsn_handler
hx_remove_optinsn_handler = _ida_hexrays.hx_remove_optinsn_handler
hx_install_optblock_handler = _ida_hexrays.hx_install_optblock_handler
hx_remove_optblock_handler = _ida_hexrays.hx_remove_optblock_handler
hx_simple_graph_t_compute_dominators = (_ida_hexrays.
    hx_simple_graph_t_compute_dominators)
hx_simple_graph_t_compute_immediate_dominators = (_ida_hexrays.
    hx_simple_graph_t_compute_immediate_dominators)
hx_simple_graph_t_depth_first_preorder = (_ida_hexrays.
    hx_simple_graph_t_depth_first_preorder)
hx_simple_graph_t_depth_first_postorder = (_ida_hexrays.
    hx_simple_graph_t_depth_first_postorder)
hx_simple_graph_t_goup = _ida_hexrays.hx_simple_graph_t_goup
hx_mutable_graph_t_resize = _ida_hexrays.hx_mutable_graph_t_resize
hx_mutable_graph_t_goup = _ida_hexrays.hx_mutable_graph_t_goup
hx_mutable_graph_t_del_edge = _ida_hexrays.hx_mutable_graph_t_del_edge
hx_lvar_ref_t_compare = _ida_hexrays.hx_lvar_ref_t_compare
hx_lvar_ref_t_var = _ida_hexrays.hx_lvar_ref_t_var
hx_stkvar_ref_t_compare = _ida_hexrays.hx_stkvar_ref_t_compare
hx_stkvar_ref_t_get_stkvar = _ida_hexrays.hx_stkvar_ref_t_get_stkvar
hx_fnumber_t_print = _ida_hexrays.hx_fnumber_t_print
hx_fnumber_t_dstr = _ida_hexrays.hx_fnumber_t_dstr
hx_mop_t_copy = _ida_hexrays.hx_mop_t_copy
hx_mop_t_assign = _ida_hexrays.hx_mop_t_assign
hx_mop_t_swap = _ida_hexrays.hx_mop_t_swap
hx_mop_t_erase = _ida_hexrays.hx_mop_t_erase
hx_mop_t_print = _ida_hexrays.hx_mop_t_print
hx_mop_t_dstr = _ida_hexrays.hx_mop_t_dstr
hx_mop_t_create_from_mlist = _ida_hexrays.hx_mop_t_create_from_mlist
hx_mop_t_create_from_ivlset = _ida_hexrays.hx_mop_t_create_from_ivlset
hx_mop_t_create_from_vdloc = _ida_hexrays.hx_mop_t_create_from_vdloc
hx_mop_t_create_from_scattered_vdloc = (_ida_hexrays.
    hx_mop_t_create_from_scattered_vdloc)
hx_mop_t_create_from_insn = _ida_hexrays.hx_mop_t_create_from_insn
hx_mop_t_make_number = _ida_hexrays.hx_mop_t_make_number
hx_mop_t_make_fpnum = _ida_hexrays.hx_mop_t_make_fpnum
hx_mop_t__make_gvar = _ida_hexrays.hx_mop_t__make_gvar
hx_mop_t_make_gvar = _ida_hexrays.hx_mop_t_make_gvar
hx_mop_t_make_reg_pair = _ida_hexrays.hx_mop_t_make_reg_pair
hx_mop_t_make_helper = _ida_hexrays.hx_mop_t_make_helper
hx_mop_t_is_bit_reg = _ida_hexrays.hx_mop_t_is_bit_reg
hx_mop_t_may_use_aliased_memory = _ida_hexrays.hx_mop_t_may_use_aliased_memory
hx_mop_t_is01 = _ida_hexrays.hx_mop_t_is01
hx_mop_t_is_sign_extended_from = _ida_hexrays.hx_mop_t_is_sign_extended_from
hx_mop_t_is_zero_extended_from = _ida_hexrays.hx_mop_t_is_zero_extended_from
hx_mop_t_equal_mops = _ida_hexrays.hx_mop_t_equal_mops
hx_mop_t_lexcompare = _ida_hexrays.hx_mop_t_lexcompare
hx_mop_t_for_all_ops = _ida_hexrays.hx_mop_t_for_all_ops
hx_mop_t_for_all_scattered_submops = (_ida_hexrays.
    hx_mop_t_for_all_scattered_submops)
hx_mop_t_is_constant = _ida_hexrays.hx_mop_t_is_constant
hx_mop_t_get_stkoff = _ida_hexrays.hx_mop_t_get_stkoff
hx_mop_t_make_low_half = _ida_hexrays.hx_mop_t_make_low_half
hx_mop_t_make_high_half = _ida_hexrays.hx_mop_t_make_high_half
hx_mop_t_make_first_half = _ida_hexrays.hx_mop_t_make_first_half
hx_mop_t_make_second_half = _ida_hexrays.hx_mop_t_make_second_half
hx_mop_t_shift_mop = _ida_hexrays.hx_mop_t_shift_mop
hx_mop_t_change_size = _ida_hexrays.hx_mop_t_change_size
hx_mop_t_preserve_side_effects = _ida_hexrays.hx_mop_t_preserve_side_effects
hx_mop_t_apply_ld_mcode = _ida_hexrays.hx_mop_t_apply_ld_mcode
hx_mcallarg_t_print = _ida_hexrays.hx_mcallarg_t_print
hx_mcallarg_t_dstr = _ida_hexrays.hx_mcallarg_t_dstr
hx_mcallarg_t_set_regarg = _ida_hexrays.hx_mcallarg_t_set_regarg
hx_mcallinfo_t_lexcompare = _ida_hexrays.hx_mcallinfo_t_lexcompare
hx_mcallinfo_t_set_type = _ida_hexrays.hx_mcallinfo_t_set_type
hx_mcallinfo_t_get_type = _ida_hexrays.hx_mcallinfo_t_get_type
hx_mcallinfo_t_print = _ida_hexrays.hx_mcallinfo_t_print
hx_mcallinfo_t_dstr = _ida_hexrays.hx_mcallinfo_t_dstr
hx_mcases_t_compare = _ida_hexrays.hx_mcases_t_compare
hx_mcases_t_print = _ida_hexrays.hx_mcases_t_print
hx_mcases_t_dstr = _ida_hexrays.hx_mcases_t_dstr
hx_vivl_t_extend_to_cover = _ida_hexrays.hx_vivl_t_extend_to_cover
hx_vivl_t_intersect = _ida_hexrays.hx_vivl_t_intersect
hx_vivl_t_print = _ida_hexrays.hx_vivl_t_print
hx_vivl_t_dstr = _ida_hexrays.hx_vivl_t_dstr
hx_chain_t_print = _ida_hexrays.hx_chain_t_print
hx_chain_t_dstr = _ida_hexrays.hx_chain_t_dstr
hx_chain_t_append_list = _ida_hexrays.hx_chain_t_append_list
hx_chain_t_append_list_ = _ida_hexrays.hx_chain_t_append_list_
hx_block_chains_t_get_chain = _ida_hexrays.hx_block_chains_t_get_chain
hx_block_chains_t_print = _ida_hexrays.hx_block_chains_t_print
hx_block_chains_t_dstr = _ida_hexrays.hx_block_chains_t_dstr
hx_graph_chains_t_for_all_chains = (_ida_hexrays.
    hx_graph_chains_t_for_all_chains)
hx_graph_chains_t_release = _ida_hexrays.hx_graph_chains_t_release
hx_minsn_t_init = _ida_hexrays.hx_minsn_t_init
hx_minsn_t_copy = _ida_hexrays.hx_minsn_t_copy
hx_minsn_t_set_combined = _ida_hexrays.hx_minsn_t_set_combined
hx_minsn_t_swap = _ida_hexrays.hx_minsn_t_swap
hx_minsn_t_print = _ida_hexrays.hx_minsn_t_print
hx_minsn_t_dstr = _ida_hexrays.hx_minsn_t_dstr
hx_minsn_t_setaddr = _ida_hexrays.hx_minsn_t_setaddr
hx_minsn_t_optimize_subtree = _ida_hexrays.hx_minsn_t_optimize_subtree
hx_minsn_t_for_all_ops = _ida_hexrays.hx_minsn_t_for_all_ops
hx_minsn_t_for_all_insns = _ida_hexrays.hx_minsn_t_for_all_insns
hx_minsn_t__make_nop = _ida_hexrays.hx_minsn_t__make_nop
hx_minsn_t_equal_insns = _ida_hexrays.hx_minsn_t_equal_insns
hx_minsn_t_lexcompare = _ida_hexrays.hx_minsn_t_lexcompare
hx_minsn_t_is_noret_call = _ida_hexrays.hx_minsn_t_is_noret_call
hx_minsn_t_is_helper = _ida_hexrays.hx_minsn_t_is_helper
hx_minsn_t_find_call = _ida_hexrays.hx_minsn_t_find_call
hx_minsn_t_has_side_effects = _ida_hexrays.hx_minsn_t_has_side_effects
hx_minsn_t_find_opcode = _ida_hexrays.hx_minsn_t_find_opcode
hx_minsn_t_find_ins_op = _ida_hexrays.hx_minsn_t_find_ins_op
hx_minsn_t_find_num_op = _ida_hexrays.hx_minsn_t_find_num_op
hx_minsn_t_modifies_d = _ida_hexrays.hx_minsn_t_modifies_d
hx_minsn_t_is_between = _ida_hexrays.hx_minsn_t_is_between
hx_minsn_t_may_use_aliased_memory = (_ida_hexrays.
    hx_minsn_t_may_use_aliased_memory)
hx_minsn_t_serialize = _ida_hexrays.hx_minsn_t_serialize
hx_minsn_t_deserialize = _ida_hexrays.hx_minsn_t_deserialize
hx_getf_reginsn = _ida_hexrays.hx_getf_reginsn
hx_getb_reginsn = _ida_hexrays.hx_getb_reginsn
hx_mblock_t_init = _ida_hexrays.hx_mblock_t_init
hx_mblock_t_print = _ida_hexrays.hx_mblock_t_print
hx_mblock_t_dump = _ida_hexrays.hx_mblock_t_dump
hx_mblock_t_vdump_block = _ida_hexrays.hx_mblock_t_vdump_block
hx_mblock_t_insert_into_block = _ida_hexrays.hx_mblock_t_insert_into_block
hx_mblock_t_remove_from_block = _ida_hexrays.hx_mblock_t_remove_from_block
hx_mblock_t_for_all_insns = _ida_hexrays.hx_mblock_t_for_all_insns
hx_mblock_t_for_all_ops = _ida_hexrays.hx_mblock_t_for_all_ops
hx_mblock_t_for_all_uses = _ida_hexrays.hx_mblock_t_for_all_uses
hx_mblock_t_optimize_insn = _ida_hexrays.hx_mblock_t_optimize_insn
hx_mblock_t_optimize_block = _ida_hexrays.hx_mblock_t_optimize_block
hx_mblock_t_build_lists = _ida_hexrays.hx_mblock_t_build_lists
hx_mblock_t_optimize_useless_jump = (_ida_hexrays.
    hx_mblock_t_optimize_useless_jump)
hx_mblock_t_append_use_list = _ida_hexrays.hx_mblock_t_append_use_list
hx_mblock_t_append_def_list = _ida_hexrays.hx_mblock_t_append_def_list
hx_mblock_t_build_use_list = _ida_hexrays.hx_mblock_t_build_use_list
hx_mblock_t_build_def_list = _ida_hexrays.hx_mblock_t_build_def_list
hx_mblock_t_find_first_use = _ida_hexrays.hx_mblock_t_find_first_use
hx_mblock_t_find_redefinition = _ida_hexrays.hx_mblock_t_find_redefinition
hx_mblock_t_is_rhs_redefined = _ida_hexrays.hx_mblock_t_is_rhs_redefined
hx_mblock_t_find_access = _ida_hexrays.hx_mblock_t_find_access
hx_mblock_t_get_valranges = _ida_hexrays.hx_mblock_t_get_valranges
hx_mblock_t_get_valranges_ = _ida_hexrays.hx_mblock_t_get_valranges_
hx_mblock_t_get_reginsn_qty = _ida_hexrays.hx_mblock_t_get_reginsn_qty
hx_mba_ranges_t_range_contains = _ida_hexrays.hx_mba_ranges_t_range_contains
hx_mba_t_stkoff_vd2ida = _ida_hexrays.hx_mba_t_stkoff_vd2ida
hx_mba_t_stkoff_ida2vd = _ida_hexrays.hx_mba_t_stkoff_ida2vd
hx_mba_t_idaloc2vd = _ida_hexrays.hx_mba_t_idaloc2vd
hx_mba_t_idaloc2vd_ = _ida_hexrays.hx_mba_t_idaloc2vd_
hx_mba_t_vd2idaloc = _ida_hexrays.hx_mba_t_vd2idaloc
hx_mba_t_vd2idaloc_ = _ida_hexrays.hx_mba_t_vd2idaloc_
hx_mba_t_term = _ida_hexrays.hx_mba_t_term
hx_mba_t_get_curfunc = _ida_hexrays.hx_mba_t_get_curfunc
hx_mba_t_set_maturity = _ida_hexrays.hx_mba_t_set_maturity
hx_mba_t_optimize_local = _ida_hexrays.hx_mba_t_optimize_local
hx_mba_t_build_graph = _ida_hexrays.hx_mba_t_build_graph
hx_mba_t_get_graph = _ida_hexrays.hx_mba_t_get_graph
hx_mba_t_analyze_calls = _ida_hexrays.hx_mba_t_analyze_calls
hx_mba_t_optimize_global = _ida_hexrays.hx_mba_t_optimize_global
hx_mba_t_alloc_lvars = _ida_hexrays.hx_mba_t_alloc_lvars
hx_mba_t_dump = _ida_hexrays.hx_mba_t_dump
hx_mba_t_vdump_mba = _ida_hexrays.hx_mba_t_vdump_mba
hx_mba_t_print = _ida_hexrays.hx_mba_t_print
hx_mba_t_verify = _ida_hexrays.hx_mba_t_verify
hx_mba_t_mark_chains_dirty = _ida_hexrays.hx_mba_t_mark_chains_dirty
hx_mba_t_insert_block = _ida_hexrays.hx_mba_t_insert_block
hx_mba_t_remove_block = _ida_hexrays.hx_mba_t_remove_block
hx_mba_t_copy_block = _ida_hexrays.hx_mba_t_copy_block
hx_mba_t_remove_empty_and_unreachable_blocks = (_ida_hexrays.
    hx_mba_t_remove_empty_and_unreachable_blocks)
hx_mba_t_merge_blocks = _ida_hexrays.hx_mba_t_merge_blocks
hx_mba_t_for_all_ops = _ida_hexrays.hx_mba_t_for_all_ops
hx_mba_t_for_all_insns = _ida_hexrays.hx_mba_t_for_all_insns
hx_mba_t_for_all_topinsns = _ida_hexrays.hx_mba_t_for_all_topinsns
hx_mba_t_find_mop = _ida_hexrays.hx_mba_t_find_mop
hx_mba_t_create_helper_call = _ida_hexrays.hx_mba_t_create_helper_call
hx_mba_t_get_func_output_lists = _ida_hexrays.hx_mba_t_get_func_output_lists
hx_mba_t_arg = _ida_hexrays.hx_mba_t_arg
hx_mba_t_alloc_fict_ea = _ida_hexrays.hx_mba_t_alloc_fict_ea
hx_mba_t_map_fict_ea = _ida_hexrays.hx_mba_t_map_fict_ea
hx_mba_t_serialize = _ida_hexrays.hx_mba_t_serialize
hx_mba_t_deserialize = _ida_hexrays.hx_mba_t_deserialize
hx_mba_t_save_snapshot = _ida_hexrays.hx_mba_t_save_snapshot
hx_mba_t_alloc_kreg = _ida_hexrays.hx_mba_t_alloc_kreg
hx_mba_t_free_kreg = _ida_hexrays.hx_mba_t_free_kreg
hx_mba_t_inline_func = _ida_hexrays.hx_mba_t_inline_func
hx_mba_t_locate_stkpnt = _ida_hexrays.hx_mba_t_locate_stkpnt
hx_mba_t_set_lvar_name = _ida_hexrays.hx_mba_t_set_lvar_name
hx_mbl_graph_t_is_accessed_globally = (_ida_hexrays.
    hx_mbl_graph_t_is_accessed_globally)
hx_mbl_graph_t_get_ud = _ida_hexrays.hx_mbl_graph_t_get_ud
hx_mbl_graph_t_get_du = _ida_hexrays.hx_mbl_graph_t_get_du
hx_cdg_insn_iterator_t_next = _ida_hexrays.hx_cdg_insn_iterator_t_next
hx_codegen_t_clear = _ida_hexrays.hx_codegen_t_clear
hx_codegen_t_emit = _ida_hexrays.hx_codegen_t_emit
hx_codegen_t_emit_ = _ida_hexrays.hx_codegen_t_emit_
hx_change_hexrays_config = _ida_hexrays.hx_change_hexrays_config
hx_get_hexrays_version = _ida_hexrays.hx_get_hexrays_version
hx_open_pseudocode = _ida_hexrays.hx_open_pseudocode
hx_close_pseudocode = _ida_hexrays.hx_close_pseudocode
hx_get_widget_vdui = _ida_hexrays.hx_get_widget_vdui
hx_decompile_many = _ida_hexrays.hx_decompile_many
hx_hexrays_failure_t_desc = _ida_hexrays.hx_hexrays_failure_t_desc
hx_send_database = _ida_hexrays.hx_send_database
hx_gco_info_t_append_to_list = _ida_hexrays.hx_gco_info_t_append_to_list
hx_get_current_operand = _ida_hexrays.hx_get_current_operand
hx_remitem = _ida_hexrays.hx_remitem
hx_negated_relation = _ida_hexrays.hx_negated_relation
hx_swapped_relation = _ida_hexrays.hx_swapped_relation
hx_get_op_signness = _ida_hexrays.hx_get_op_signness
hx_asgop = _ida_hexrays.hx_asgop
hx_asgop_revert = _ida_hexrays.hx_asgop_revert
hx_cnumber_t_print = _ida_hexrays.hx_cnumber_t_print
hx_cnumber_t_value = _ida_hexrays.hx_cnumber_t_value
hx_cnumber_t_assign = _ida_hexrays.hx_cnumber_t_assign
hx_cnumber_t_compare = _ida_hexrays.hx_cnumber_t_compare
hx_var_ref_t_compare = _ida_hexrays.hx_var_ref_t_compare
hx_ctree_visitor_t_apply_to = _ida_hexrays.hx_ctree_visitor_t_apply_to
hx_ctree_visitor_t_apply_to_exprs = (_ida_hexrays.
    hx_ctree_visitor_t_apply_to_exprs)
hx_ctree_parentee_t_recalc_parent_types = (_ida_hexrays.
    hx_ctree_parentee_t_recalc_parent_types)
hx_cfunc_parentee_t_calc_rvalue_type = (_ida_hexrays.
    hx_cfunc_parentee_t_calc_rvalue_type)
hx_citem_locator_t_compare = _ida_hexrays.hx_citem_locator_t_compare
hx_citem_t_contains_expr = _ida_hexrays.hx_citem_t_contains_expr
hx_citem_t_contains_label = _ida_hexrays.hx_citem_t_contains_label
hx_citem_t_find_parent_of = _ida_hexrays.hx_citem_t_find_parent_of
hx_citem_t_find_closest_addr = _ida_hexrays.hx_citem_t_find_closest_addr
hx_cexpr_t_assign = _ida_hexrays.hx_cexpr_t_assign
hx_cexpr_t_compare = _ida_hexrays.hx_cexpr_t_compare
hx_cexpr_t_replace_by = _ida_hexrays.hx_cexpr_t_replace_by
hx_cexpr_t_cleanup = _ida_hexrays.hx_cexpr_t_cleanup
hx_cexpr_t_put_number = _ida_hexrays.hx_cexpr_t_put_number
hx_cexpr_t_print1 = _ida_hexrays.hx_cexpr_t_print1
hx_cexpr_t_calc_type = _ida_hexrays.hx_cexpr_t_calc_type
hx_cexpr_t_equal_effect = _ida_hexrays.hx_cexpr_t_equal_effect
hx_cexpr_t_is_child_of = _ida_hexrays.hx_cexpr_t_is_child_of
hx_cexpr_t_contains_operator = _ida_hexrays.hx_cexpr_t_contains_operator
hx_cexpr_t_get_high_nbit_bound = _ida_hexrays.hx_cexpr_t_get_high_nbit_bound
hx_cexpr_t_get_low_nbit_bound = _ida_hexrays.hx_cexpr_t_get_low_nbit_bound
hx_cexpr_t_requires_lvalue = _ida_hexrays.hx_cexpr_t_requires_lvalue
hx_cexpr_t_has_side_effects = _ida_hexrays.hx_cexpr_t_has_side_effects
hx_cexpr_t_maybe_ptr = _ida_hexrays.hx_cexpr_t_maybe_ptr
hx_cexpr_t_dstr = _ida_hexrays.hx_cexpr_t_dstr
hx_cif_t_assign = _ida_hexrays.hx_cif_t_assign
hx_cif_t_compare = _ida_hexrays.hx_cif_t_compare
hx_cloop_t_assign = _ida_hexrays.hx_cloop_t_assign
hx_cfor_t_compare = _ida_hexrays.hx_cfor_t_compare
hx_cwhile_t_compare = _ida_hexrays.hx_cwhile_t_compare
hx_cdo_t_compare = _ida_hexrays.hx_cdo_t_compare
hx_creturn_t_compare = _ida_hexrays.hx_creturn_t_compare
hx_cthrow_t_compare = _ida_hexrays.hx_cthrow_t_compare
hx_cgoto_t_compare = _ida_hexrays.hx_cgoto_t_compare
hx_casm_t_compare = _ida_hexrays.hx_casm_t_compare
hx_cinsn_t_assign = _ida_hexrays.hx_cinsn_t_assign
hx_cinsn_t_compare = _ida_hexrays.hx_cinsn_t_compare
hx_cinsn_t_replace_by = _ida_hexrays.hx_cinsn_t_replace_by
hx_cinsn_t_cleanup = _ida_hexrays.hx_cinsn_t_cleanup
hx_cinsn_t_new_insn = _ida_hexrays.hx_cinsn_t_new_insn
hx_cinsn_t_create_if = _ida_hexrays.hx_cinsn_t_create_if
hx_cinsn_t_print = _ida_hexrays.hx_cinsn_t_print
hx_cinsn_t_print1 = _ida_hexrays.hx_cinsn_t_print1
hx_cinsn_t_is_ordinary_flow = _ida_hexrays.hx_cinsn_t_is_ordinary_flow
hx_cinsn_t_contains_insn = _ida_hexrays.hx_cinsn_t_contains_insn
hx_cinsn_t_collect_free_breaks = _ida_hexrays.hx_cinsn_t_collect_free_breaks
hx_cinsn_t_collect_free_continues = (_ida_hexrays.
    hx_cinsn_t_collect_free_continues)
hx_cinsn_t_dstr = _ida_hexrays.hx_cinsn_t_dstr
hx_cblock_t_compare = _ida_hexrays.hx_cblock_t_compare
hx_carglist_t_compare = _ida_hexrays.hx_carglist_t_compare
hx_ccase_t_compare = _ida_hexrays.hx_ccase_t_compare
hx_ccases_t_compare = _ida_hexrays.hx_ccases_t_compare
hx_cswitch_t_compare = _ida_hexrays.hx_cswitch_t_compare
hx_ccatch_t_compare = _ida_hexrays.hx_ccatch_t_compare
hx_ctry_t_compare = _ida_hexrays.hx_ctry_t_compare
hx_ctree_item_t_get_udm = _ida_hexrays.hx_ctree_item_t_get_udm
hx_ctree_item_t_get_edm = _ida_hexrays.hx_ctree_item_t_get_edm
hx_ctree_item_t_get_lvar = _ida_hexrays.hx_ctree_item_t_get_lvar
hx_ctree_item_t_get_ea = _ida_hexrays.hx_ctree_item_t_get_ea
hx_ctree_item_t_get_label_num = _ida_hexrays.hx_ctree_item_t_get_label_num
hx_ctree_item_t_print = _ida_hexrays.hx_ctree_item_t_print
hx_ctree_item_t_dstr = _ida_hexrays.hx_ctree_item_t_dstr
hx_lnot = _ida_hexrays.hx_lnot
hx_new_block = _ida_hexrays.hx_new_block
hx_vcreate_helper = _ida_hexrays.hx_vcreate_helper
hx_vcall_helper = _ida_hexrays.hx_vcall_helper
hx_make_num = _ida_hexrays.hx_make_num
hx_make_ref = _ida_hexrays.hx_make_ref
hx_dereference = _ida_hexrays.hx_dereference
hx_save_user_labels = _ida_hexrays.hx_save_user_labels
hx_save_user_cmts = _ida_hexrays.hx_save_user_cmts
hx_save_user_numforms = _ida_hexrays.hx_save_user_numforms
hx_save_user_iflags = _ida_hexrays.hx_save_user_iflags
hx_save_user_unions = _ida_hexrays.hx_save_user_unions
hx_restore_user_labels = _ida_hexrays.hx_restore_user_labels
hx_restore_user_cmts = _ida_hexrays.hx_restore_user_cmts
hx_restore_user_numforms = _ida_hexrays.hx_restore_user_numforms
hx_restore_user_iflags = _ida_hexrays.hx_restore_user_iflags
hx_restore_user_unions = _ida_hexrays.hx_restore_user_unions
hx_cfunc_t_build_c_tree = _ida_hexrays.hx_cfunc_t_build_c_tree
hx_cfunc_t_verify = _ida_hexrays.hx_cfunc_t_verify
hx_cfunc_t_print_dcl = _ida_hexrays.hx_cfunc_t_print_dcl
hx_cfunc_t_print_func = _ida_hexrays.hx_cfunc_t_print_func
hx_cfunc_t_get_func_type = _ida_hexrays.hx_cfunc_t_get_func_type
hx_cfunc_t_get_lvars = _ida_hexrays.hx_cfunc_t_get_lvars
hx_cfunc_t_get_stkoff_delta = _ida_hexrays.hx_cfunc_t_get_stkoff_delta
hx_cfunc_t_find_label = _ida_hexrays.hx_cfunc_t_find_label
hx_cfunc_t_remove_unused_labels = _ida_hexrays.hx_cfunc_t_remove_unused_labels
hx_cfunc_t_get_user_cmt = _ida_hexrays.hx_cfunc_t_get_user_cmt
hx_cfunc_t_set_user_cmt = _ida_hexrays.hx_cfunc_t_set_user_cmt
hx_cfunc_t_get_user_iflags = _ida_hexrays.hx_cfunc_t_get_user_iflags
hx_cfunc_t_set_user_iflags = _ida_hexrays.hx_cfunc_t_set_user_iflags
hx_cfunc_t_has_orphan_cmts = _ida_hexrays.hx_cfunc_t_has_orphan_cmts
hx_cfunc_t_del_orphan_cmts = _ida_hexrays.hx_cfunc_t_del_orphan_cmts
hx_cfunc_t_get_user_union_selection = (_ida_hexrays.
    hx_cfunc_t_get_user_union_selection)
hx_cfunc_t_set_user_union_selection = (_ida_hexrays.
    hx_cfunc_t_set_user_union_selection)
hx_cfunc_t_save_user_labels = _ida_hexrays.hx_cfunc_t_save_user_labels
hx_cfunc_t_save_user_cmts = _ida_hexrays.hx_cfunc_t_save_user_cmts
hx_cfunc_t_save_user_numforms = _ida_hexrays.hx_cfunc_t_save_user_numforms
hx_cfunc_t_save_user_iflags = _ida_hexrays.hx_cfunc_t_save_user_iflags
hx_cfunc_t_save_user_unions = _ida_hexrays.hx_cfunc_t_save_user_unions
hx_cfunc_t_get_line_item = _ida_hexrays.hx_cfunc_t_get_line_item
hx_cfunc_t_get_warnings = _ida_hexrays.hx_cfunc_t_get_warnings
hx_cfunc_t_get_eamap = _ida_hexrays.hx_cfunc_t_get_eamap
hx_cfunc_t_get_boundaries = _ida_hexrays.hx_cfunc_t_get_boundaries
hx_cfunc_t_get_pseudocode = _ida_hexrays.hx_cfunc_t_get_pseudocode
hx_cfunc_t_refresh_func_ctext = _ida_hexrays.hx_cfunc_t_refresh_func_ctext
hx_cfunc_t_gather_derefs = _ida_hexrays.hx_cfunc_t_gather_derefs
hx_cfunc_t_find_item_coords = _ida_hexrays.hx_cfunc_t_find_item_coords
hx_cfunc_t_cleanup = _ida_hexrays.hx_cfunc_t_cleanup
hx_close_hexrays_waitbox = _ida_hexrays.hx_close_hexrays_waitbox
hx_decompile = _ida_hexrays.hx_decompile
hx_gen_microcode = _ida_hexrays.hx_gen_microcode
hx_create_cfunc = _ida_hexrays.hx_create_cfunc
hx_mark_cfunc_dirty = _ida_hexrays.hx_mark_cfunc_dirty
hx_clear_cached_cfuncs = _ida_hexrays.hx_clear_cached_cfuncs
hx_has_cached_cfunc = _ida_hexrays.hx_has_cached_cfunc
hx_get_ctype_name = _ida_hexrays.hx_get_ctype_name
hx_create_field_name = _ida_hexrays.hx_create_field_name
hx_install_hexrays_callback = _ida_hexrays.hx_install_hexrays_callback
hx_remove_hexrays_callback = _ida_hexrays.hx_remove_hexrays_callback
hx_vdui_t_set_locked = _ida_hexrays.hx_vdui_t_set_locked
hx_vdui_t_refresh_view = _ida_hexrays.hx_vdui_t_refresh_view
hx_vdui_t_refresh_ctext = _ida_hexrays.hx_vdui_t_refresh_ctext
hx_vdui_t_switch_to = _ida_hexrays.hx_vdui_t_switch_to
hx_vdui_t_get_number = _ida_hexrays.hx_vdui_t_get_number
hx_vdui_t_get_current_label = _ida_hexrays.hx_vdui_t_get_current_label
hx_vdui_t_clear = _ida_hexrays.hx_vdui_t_clear
hx_vdui_t_refresh_cpos = _ida_hexrays.hx_vdui_t_refresh_cpos
hx_vdui_t_get_current_item = _ida_hexrays.hx_vdui_t_get_current_item
hx_vdui_t_ui_rename_lvar = _ida_hexrays.hx_vdui_t_ui_rename_lvar
hx_vdui_t_rename_lvar = _ida_hexrays.hx_vdui_t_rename_lvar
hx_vdui_t_ui_set_call_type = _ida_hexrays.hx_vdui_t_ui_set_call_type
hx_vdui_t_ui_set_lvar_type = _ida_hexrays.hx_vdui_t_ui_set_lvar_type
hx_vdui_t_set_lvar_type = _ida_hexrays.hx_vdui_t_set_lvar_type
hx_vdui_t_set_noptr_lvar = _ida_hexrays.hx_vdui_t_set_noptr_lvar
hx_vdui_t_ui_edit_lvar_cmt = _ida_hexrays.hx_vdui_t_ui_edit_lvar_cmt
hx_vdui_t_set_lvar_cmt = _ida_hexrays.hx_vdui_t_set_lvar_cmt
hx_vdui_t_ui_map_lvar = _ida_hexrays.hx_vdui_t_ui_map_lvar
hx_vdui_t_ui_unmap_lvar = _ida_hexrays.hx_vdui_t_ui_unmap_lvar
hx_vdui_t_map_lvar = _ida_hexrays.hx_vdui_t_map_lvar
hx_vdui_t_set_udm_type = _ida_hexrays.hx_vdui_t_set_udm_type
hx_vdui_t_rename_udm = _ida_hexrays.hx_vdui_t_rename_udm
hx_vdui_t_set_global_type = _ida_hexrays.hx_vdui_t_set_global_type
hx_vdui_t_rename_global = _ida_hexrays.hx_vdui_t_rename_global
hx_vdui_t_rename_label = _ida_hexrays.hx_vdui_t_rename_label
hx_vdui_t_jump_enter = _ida_hexrays.hx_vdui_t_jump_enter
hx_vdui_t_ctree_to_disasm = _ida_hexrays.hx_vdui_t_ctree_to_disasm
hx_vdui_t_calc_cmt_type = _ida_hexrays.hx_vdui_t_calc_cmt_type
hx_vdui_t_edit_cmt = _ida_hexrays.hx_vdui_t_edit_cmt
hx_vdui_t_edit_func_cmt = _ida_hexrays.hx_vdui_t_edit_func_cmt
hx_vdui_t_del_orphan_cmts = _ida_hexrays.hx_vdui_t_del_orphan_cmts
hx_vdui_t_set_num_radix = _ida_hexrays.hx_vdui_t_set_num_radix
hx_vdui_t_set_num_enum = _ida_hexrays.hx_vdui_t_set_num_enum
hx_vdui_t_set_num_stroff = _ida_hexrays.hx_vdui_t_set_num_stroff
hx_vdui_t_invert_sign = _ida_hexrays.hx_vdui_t_invert_sign
hx_vdui_t_invert_bits = _ida_hexrays.hx_vdui_t_invert_bits
hx_vdui_t_collapse_item = _ida_hexrays.hx_vdui_t_collapse_item
hx_vdui_t_collapse_lvars = _ida_hexrays.hx_vdui_t_collapse_lvars
hx_vdui_t_split_item = _ida_hexrays.hx_vdui_t_split_item
hx_select_udt_by_offset = _ida_hexrays.hx_select_udt_by_offset
hx_catchexpr_t_compare = _ida_hexrays.hx_catchexpr_t_compare
hx_mba_t_split_block = _ida_hexrays.hx_mba_t_split_block
hx_mba_t_remove_blocks = _ida_hexrays.hx_mba_t_remove_blocks
hx_cfunc_t_recalc_item_addresses = (_ida_hexrays.
    hx_cfunc_t_recalc_item_addresses)
hx_obsolete_int64_emulator_t_mop_value = (_ida_hexrays.
    hx_obsolete_int64_emulator_t_mop_value)
hx_obsolete_int64_emulator_t_minsn_value = (_ida_hexrays.
    hx_obsolete_int64_emulator_t_minsn_value)
hx_int64_emulator_t__mop_value = _ida_hexrays.hx_int64_emulator_t__mop_value
hx_int64_emulator_t__minsn_value = (_ida_hexrays.
    hx_int64_emulator_t__minsn_value)
hx_cfunc_t_serialize = _ida_hexrays.hx_cfunc_t_serialize
hx_cfunc_t_deserialize = _ida_hexrays.hx_cfunc_t_deserialize
hx_mblock_t_verify_insn = _ida_hexrays.hx_mblock_t_verify_insn
hx_vdui_t_ui_noprop_lvar = _ida_hexrays.hx_vdui_t_ui_noprop_lvar


class user_numforms_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.
        user_numforms_iterator_t_x_get, _ida_hexrays.
        user_numforms_iterator_t_x_set)

    def __eq__(self, p: 'user_numforms_iterator_t') ->bool:
        return _ida_hexrays.user_numforms_iterator_t___eq__(self, p)

    def __ne__(self, p: 'user_numforms_iterator_t') ->bool:
        return _ida_hexrays.user_numforms_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.user_numforms_iterator_t_swiginit(self, _ida_hexrays.
            new_user_numforms_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_user_numforms_iterator_t


_ida_hexrays.user_numforms_iterator_t_swigregister(user_numforms_iterator_t)


def user_numforms_first(p: 'user_numforms_iterator_t'
    ) ->'operand_locator_t const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.user_numforms_first(p)


def user_numforms_second(p: 'user_numforms_iterator_t') ->'number_format_t &':
    """Get reference to the current map value.
"""
    return _ida_hexrays.user_numforms_second(p)


def user_numforms_find(map: 'user_numforms_t', key: 'operand_locator_t'
    ) ->'user_numforms_iterator_t':
    """Find the specified key in user_numforms_t.
"""
    return _ida_hexrays.user_numforms_find(map, key)


def user_numforms_insert(map: 'user_numforms_t', key: 'operand_locator_t',
    val: 'number_format_t') ->'user_numforms_iterator_t':
    """Insert new (operand_locator_t, number_format_t) pair into user_numforms_t.
"""
    return _ida_hexrays.user_numforms_insert(map, key, val)


def user_numforms_begin(map: 'user_numforms_t') ->'user_numforms_iterator_t':
    """Get iterator pointing to the beginning of user_numforms_t.
"""
    return _ida_hexrays.user_numforms_begin(map)


def user_numforms_end(map: 'user_numforms_t') ->'user_numforms_iterator_t':
    """Get iterator pointing to the end of user_numforms_t.
"""
    return _ida_hexrays.user_numforms_end(map)


def user_numforms_next(p: 'user_numforms_iterator_t'
    ) ->'user_numforms_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.user_numforms_next(p)


def user_numforms_prev(p: 'user_numforms_iterator_t'
    ) ->'user_numforms_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.user_numforms_prev(p)


def user_numforms_erase(map: 'user_numforms_t', p: 'user_numforms_iterator_t'
    ) ->None:
    """Erase current element from user_numforms_t.
"""
    return _ida_hexrays.user_numforms_erase(map, p)


def user_numforms_clear(map: 'user_numforms_t') ->None:
    """Clear user_numforms_t.
"""
    return _ida_hexrays.user_numforms_clear(map)


def user_numforms_size(map: 'user_numforms_t') ->int:
    """Get size of user_numforms_t.
"""
    return _ida_hexrays.user_numforms_size(map)


def user_numforms_free(map: 'user_numforms_t') ->None:
    """Delete user_numforms_t instance.
"""
    return _ida_hexrays.user_numforms_free(map)


def user_numforms_new() ->'user_numforms_t *':
    """Create a new user_numforms_t instance.
"""
    return _ida_hexrays.user_numforms_new()


class user_cmts_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.user_cmts_iterator_t_x_get,
        _ida_hexrays.user_cmts_iterator_t_x_set)

    def __eq__(self, p: 'user_cmts_iterator_t') ->bool:
        return _ida_hexrays.user_cmts_iterator_t___eq__(self, p)

    def __ne__(self, p: 'user_cmts_iterator_t') ->bool:
        return _ida_hexrays.user_cmts_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.user_cmts_iterator_t_swiginit(self, _ida_hexrays.
            new_user_cmts_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_user_cmts_iterator_t


_ida_hexrays.user_cmts_iterator_t_swigregister(user_cmts_iterator_t)


def user_cmts_first(p: 'user_cmts_iterator_t') ->'treeloc_t const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.user_cmts_first(p)


def user_cmts_second(p: 'user_cmts_iterator_t') ->'citem_cmt_t &':
    """Get reference to the current map value.
"""
    return _ida_hexrays.user_cmts_second(p)


def user_cmts_find(map: 'user_cmts_t', key: 'treeloc_t'
    ) ->'user_cmts_iterator_t':
    """Find the specified key in user_cmts_t.
"""
    return _ida_hexrays.user_cmts_find(map, key)


def user_cmts_insert(map: 'user_cmts_t', key: 'treeloc_t', val: 'citem_cmt_t'
    ) ->'user_cmts_iterator_t':
    """Insert new (treeloc_t, citem_cmt_t) pair into user_cmts_t.
"""
    return _ida_hexrays.user_cmts_insert(map, key, val)


def user_cmts_begin(map: 'user_cmts_t') ->'user_cmts_iterator_t':
    """Get iterator pointing to the beginning of user_cmts_t.
"""
    return _ida_hexrays.user_cmts_begin(map)


def user_cmts_end(map: 'user_cmts_t') ->'user_cmts_iterator_t':
    """Get iterator pointing to the end of user_cmts_t.
"""
    return _ida_hexrays.user_cmts_end(map)


def user_cmts_next(p: 'user_cmts_iterator_t') ->'user_cmts_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.user_cmts_next(p)


def user_cmts_prev(p: 'user_cmts_iterator_t') ->'user_cmts_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.user_cmts_prev(p)


def user_cmts_erase(map: 'user_cmts_t', p: 'user_cmts_iterator_t') ->None:
    """Erase current element from user_cmts_t.
"""
    return _ida_hexrays.user_cmts_erase(map, p)


def user_cmts_clear(map: 'user_cmts_t') ->None:
    """Clear user_cmts_t.
"""
    return _ida_hexrays.user_cmts_clear(map)


def user_cmts_size(map: 'user_cmts_t') ->int:
    """Get size of user_cmts_t.
"""
    return _ida_hexrays.user_cmts_size(map)


def user_cmts_free(map: 'user_cmts_t') ->None:
    """Delete user_cmts_t instance.
"""
    return _ida_hexrays.user_cmts_free(map)


def user_cmts_new() ->'user_cmts_t *':
    """Create a new user_cmts_t instance.
"""
    return _ida_hexrays.user_cmts_new()


class user_iflags_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.user_iflags_iterator_t_x_get,
        _ida_hexrays.user_iflags_iterator_t_x_set)

    def __eq__(self, p: 'user_iflags_iterator_t') ->bool:
        return _ida_hexrays.user_iflags_iterator_t___eq__(self, p)

    def __ne__(self, p: 'user_iflags_iterator_t') ->bool:
        return _ida_hexrays.user_iflags_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.user_iflags_iterator_t_swiginit(self, _ida_hexrays.
            new_user_iflags_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_user_iflags_iterator_t


_ida_hexrays.user_iflags_iterator_t_swigregister(user_iflags_iterator_t)


def user_iflags_first(p: 'user_iflags_iterator_t') ->'citem_locator_t const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.user_iflags_first(p)


def user_iflags_second(p: 'user_iflags_iterator_t') ->'int32 &':
    """Get reference to the current map value.
"""
    return _ida_hexrays.user_iflags_second(p)


def user_iflags_find(map: 'user_iflags_t', key: 'citem_locator_t'
    ) ->'user_iflags_iterator_t':
    """Find the specified key in user_iflags_t.
"""
    return _ida_hexrays.user_iflags_find(map, key)


def user_iflags_insert(map: 'user_iflags_t', key: 'citem_locator_t', val:
    'int32 const &') ->'user_iflags_iterator_t':
    """Insert new (citem_locator_t, int32) pair into user_iflags_t.
"""
    return _ida_hexrays.user_iflags_insert(map, key, val)


def user_iflags_begin(map: 'user_iflags_t') ->'user_iflags_iterator_t':
    """Get iterator pointing to the beginning of user_iflags_t.
"""
    return _ida_hexrays.user_iflags_begin(map)


def user_iflags_end(map: 'user_iflags_t') ->'user_iflags_iterator_t':
    """Get iterator pointing to the end of user_iflags_t.
"""
    return _ida_hexrays.user_iflags_end(map)


def user_iflags_next(p: 'user_iflags_iterator_t') ->'user_iflags_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.user_iflags_next(p)


def user_iflags_prev(p: 'user_iflags_iterator_t') ->'user_iflags_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.user_iflags_prev(p)


def user_iflags_erase(map: 'user_iflags_t', p: 'user_iflags_iterator_t'
    ) ->None:
    """Erase current element from user_iflags_t.
"""
    return _ida_hexrays.user_iflags_erase(map, p)


def user_iflags_clear(map: 'user_iflags_t') ->None:
    """Clear user_iflags_t.
"""
    return _ida_hexrays.user_iflags_clear(map)


def user_iflags_size(map: 'user_iflags_t') ->int:
    """Get size of user_iflags_t.
"""
    return _ida_hexrays.user_iflags_size(map)


def user_iflags_free(map: 'user_iflags_t') ->None:
    """Delete user_iflags_t instance.
"""
    return _ida_hexrays.user_iflags_free(map)


def user_iflags_new() ->'user_iflags_t *':
    """Create a new user_iflags_t instance.
"""
    return _ida_hexrays.user_iflags_new()


class user_unions_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.user_unions_iterator_t_x_get,
        _ida_hexrays.user_unions_iterator_t_x_set)

    def __eq__(self, p: 'user_unions_iterator_t') ->bool:
        return _ida_hexrays.user_unions_iterator_t___eq__(self, p)

    def __ne__(self, p: 'user_unions_iterator_t') ->bool:
        return _ida_hexrays.user_unions_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.user_unions_iterator_t_swiginit(self, _ida_hexrays.
            new_user_unions_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_user_unions_iterator_t


_ida_hexrays.user_unions_iterator_t_swigregister(user_unions_iterator_t)


def user_unions_first(p: 'user_unions_iterator_t') ->'ea_t const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.user_unions_first(p)


def user_unions_second(p: 'user_unions_iterator_t') ->'intvec_t &':
    """Get reference to the current map value.
"""
    return _ida_hexrays.user_unions_second(p)


def user_unions_find(map: 'user_unions_t', key: 'ea_t const &'
    ) ->'user_unions_iterator_t':
    """Find the specified key in user_unions_t.
"""
    return _ida_hexrays.user_unions_find(map, key)


def user_unions_insert(map: 'user_unions_t', key: 'ea_t const &', val:
    'intvec_t const &') ->'user_unions_iterator_t':
    """Insert new (ea_t, intvec_t) pair into user_unions_t.
"""
    return _ida_hexrays.user_unions_insert(map, key, val)


def user_unions_begin(map: 'user_unions_t') ->'user_unions_iterator_t':
    """Get iterator pointing to the beginning of user_unions_t.
"""
    return _ida_hexrays.user_unions_begin(map)


def user_unions_end(map: 'user_unions_t') ->'user_unions_iterator_t':
    """Get iterator pointing to the end of user_unions_t.
"""
    return _ida_hexrays.user_unions_end(map)


def user_unions_next(p: 'user_unions_iterator_t') ->'user_unions_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.user_unions_next(p)


def user_unions_prev(p: 'user_unions_iterator_t') ->'user_unions_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.user_unions_prev(p)


def user_unions_erase(map: 'user_unions_t', p: 'user_unions_iterator_t'
    ) ->None:
    """Erase current element from user_unions_t.
"""
    return _ida_hexrays.user_unions_erase(map, p)


def user_unions_clear(map: 'user_unions_t') ->None:
    """Clear user_unions_t.
"""
    return _ida_hexrays.user_unions_clear(map)


def user_unions_size(map: 'user_unions_t') ->int:
    """Get size of user_unions_t.
"""
    return _ida_hexrays.user_unions_size(map)


def user_unions_free(map: 'user_unions_t') ->None:
    """Delete user_unions_t instance.
"""
    return _ida_hexrays.user_unions_free(map)


def user_unions_new() ->'user_unions_t *':
    """Create a new user_unions_t instance.
"""
    return _ida_hexrays.user_unions_new()


class user_labels_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.user_labels_iterator_t_x_get,
        _ida_hexrays.user_labels_iterator_t_x_set)

    def __eq__(self, p: 'user_labels_iterator_t') ->bool:
        return _ida_hexrays.user_labels_iterator_t___eq__(self, p)

    def __ne__(self, p: 'user_labels_iterator_t') ->bool:
        return _ida_hexrays.user_labels_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.user_labels_iterator_t_swiginit(self, _ida_hexrays.
            new_user_labels_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_user_labels_iterator_t


_ida_hexrays.user_labels_iterator_t_swigregister(user_labels_iterator_t)


def user_labels_first(p: 'user_labels_iterator_t') ->'int const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.user_labels_first(p)


def user_labels_second(p: 'user_labels_iterator_t') ->str:
    """Get reference to the current map value.
"""
    return _ida_hexrays.user_labels_second(p)


def user_labels_find(map: 'user_labels_t', key: 'int const &'
    ) ->'user_labels_iterator_t':
    """Find the specified key in user_labels_t.
"""
    return _ida_hexrays.user_labels_find(map, key)


def user_labels_insert(map: 'user_labels_t', key: 'int const &', val: str
    ) ->'user_labels_iterator_t':
    """Insert new (int, qstring) pair into user_labels_t.
"""
    return _ida_hexrays.user_labels_insert(map, key, val)


def user_labels_begin(map: 'user_labels_t') ->'user_labels_iterator_t':
    """Get iterator pointing to the beginning of user_labels_t.
"""
    return _ida_hexrays.user_labels_begin(map)


def user_labels_end(map: 'user_labels_t') ->'user_labels_iterator_t':
    """Get iterator pointing to the end of user_labels_t.
"""
    return _ida_hexrays.user_labels_end(map)


def user_labels_next(p: 'user_labels_iterator_t') ->'user_labels_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.user_labels_next(p)


def user_labels_prev(p: 'user_labels_iterator_t') ->'user_labels_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.user_labels_prev(p)


def user_labels_erase(map: 'user_labels_t', p: 'user_labels_iterator_t'
    ) ->None:
    """Erase current element from user_labels_t.
"""
    return _ida_hexrays.user_labels_erase(map, p)


def user_labels_clear(map: 'user_labels_t') ->None:
    """Clear user_labels_t.
"""
    return _ida_hexrays.user_labels_clear(map)


def user_labels_size(map: 'user_labels_t') ->int:
    """Get size of user_labels_t.
"""
    return _ida_hexrays.user_labels_size(map)


def user_labels_free(map: 'user_labels_t') ->None:
    """Delete user_labels_t instance.
"""
    return _ida_hexrays.user_labels_free(map)


def user_labels_new() ->'user_labels_t *':
    """Create a new user_labels_t instance.
"""
    return _ida_hexrays.user_labels_new()


class eamap_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.eamap_iterator_t_x_get,
        _ida_hexrays.eamap_iterator_t_x_set)

    def __eq__(self, p: 'eamap_iterator_t') ->bool:
        return _ida_hexrays.eamap_iterator_t___eq__(self, p)

    def __ne__(self, p: 'eamap_iterator_t') ->bool:
        return _ida_hexrays.eamap_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.eamap_iterator_t_swiginit(self, _ida_hexrays.
            new_eamap_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_eamap_iterator_t


_ida_hexrays.eamap_iterator_t_swigregister(eamap_iterator_t)


def eamap_first(p: 'eamap_iterator_t') ->'ea_t const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.eamap_first(p)


def eamap_second(p: 'eamap_iterator_t') ->'cinsnptrvec_t &':
    """Get reference to the current map value.
"""
    return _ida_hexrays.eamap_second(p)


def eamap_find(map: 'eamap_t', key: 'ea_t const &') ->'eamap_iterator_t':
    """Find the specified key in eamap_t.
"""
    return _ida_hexrays.eamap_find(map, key)


def eamap_insert(map: 'eamap_t', key: 'ea_t const &', val: 'cinsnptrvec_t'
    ) ->'eamap_iterator_t':
    """Insert new (ea_t, cinsnptrvec_t) pair into eamap_t.
"""
    return _ida_hexrays.eamap_insert(map, key, val)


def eamap_begin(map: 'eamap_t') ->'eamap_iterator_t':
    """Get iterator pointing to the beginning of eamap_t.
"""
    return _ida_hexrays.eamap_begin(map)


def eamap_end(map: 'eamap_t') ->'eamap_iterator_t':
    """Get iterator pointing to the end of eamap_t.
"""
    return _ida_hexrays.eamap_end(map)


def eamap_next(p: 'eamap_iterator_t') ->'eamap_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.eamap_next(p)


def eamap_prev(p: 'eamap_iterator_t') ->'eamap_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.eamap_prev(p)


def eamap_erase(map: 'eamap_t', p: 'eamap_iterator_t') ->None:
    """Erase current element from eamap_t.
"""
    return _ida_hexrays.eamap_erase(map, p)


def eamap_clear(map: 'eamap_t') ->None:
    """Clear eamap_t.
"""
    return _ida_hexrays.eamap_clear(map)


def eamap_size(map: 'eamap_t') ->int:
    """Get size of eamap_t.
"""
    return _ida_hexrays.eamap_size(map)


def eamap_free(map: 'eamap_t') ->None:
    """Delete eamap_t instance.
"""
    return _ida_hexrays.eamap_free(map)


def eamap_new() ->'eamap_t *':
    """Create a new eamap_t instance.
"""
    return _ida_hexrays.eamap_new()


class boundaries_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.boundaries_iterator_t_x_get,
        _ida_hexrays.boundaries_iterator_t_x_set)

    def __eq__(self, p: 'boundaries_iterator_t') ->bool:
        return _ida_hexrays.boundaries_iterator_t___eq__(self, p)

    def __ne__(self, p: 'boundaries_iterator_t') ->bool:
        return _ida_hexrays.boundaries_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.boundaries_iterator_t_swiginit(self, _ida_hexrays.
            new_boundaries_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_boundaries_iterator_t


_ida_hexrays.boundaries_iterator_t_swigregister(boundaries_iterator_t)


def boundaries_first(p: 'boundaries_iterator_t') ->'cinsn_t *const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.boundaries_first(p)


def boundaries_second(p: 'boundaries_iterator_t') ->'rangeset_t &':
    """Get reference to the current map value.
"""
    return _ida_hexrays.boundaries_second(p)


def boundaries_begin(map: 'boundaries_t') ->'boundaries_iterator_t':
    """Get iterator pointing to the beginning of boundaries_t.
"""
    return _ida_hexrays.boundaries_begin(map)


def boundaries_end(map: 'boundaries_t') ->'boundaries_iterator_t':
    """Get iterator pointing to the end of boundaries_t.
"""
    return _ida_hexrays.boundaries_end(map)


def boundaries_next(p: 'boundaries_iterator_t') ->'boundaries_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.boundaries_next(p)


def boundaries_prev(p: 'boundaries_iterator_t') ->'boundaries_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.boundaries_prev(p)


def boundaries_erase(map: 'boundaries_t', p: 'boundaries_iterator_t') ->None:
    """Erase current element from boundaries_t.
"""
    return _ida_hexrays.boundaries_erase(map, p)


def boundaries_clear(map: 'boundaries_t') ->None:
    """Clear boundaries_t.
"""
    return _ida_hexrays.boundaries_clear(map)


def boundaries_size(map: 'boundaries_t') ->int:
    """Get size of boundaries_t.
"""
    return _ida_hexrays.boundaries_size(map)


def boundaries_free(map: 'boundaries_t') ->None:
    """Delete boundaries_t instance.
"""
    return _ida_hexrays.boundaries_free(map)


def boundaries_new() ->'boundaries_t *':
    """Create a new boundaries_t instance.
"""
    return _ida_hexrays.boundaries_new()


class lvar_mapping_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.
        lvar_mapping_iterator_t_x_get, _ida_hexrays.
        lvar_mapping_iterator_t_x_set)

    def __eq__(self, p: 'lvar_mapping_iterator_t') ->bool:
        return _ida_hexrays.lvar_mapping_iterator_t___eq__(self, p)

    def __ne__(self, p: 'lvar_mapping_iterator_t') ->bool:
        return _ida_hexrays.lvar_mapping_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.lvar_mapping_iterator_t_swiginit(self, _ida_hexrays.
            new_lvar_mapping_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_lvar_mapping_iterator_t


_ida_hexrays.lvar_mapping_iterator_t_swigregister(lvar_mapping_iterator_t)


def lvar_mapping_first(p: 'lvar_mapping_iterator_t'
    ) ->'lvar_locator_t const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.lvar_mapping_first(p)


def lvar_mapping_second(p: 'lvar_mapping_iterator_t') ->'lvar_locator_t &':
    """Get reference to the current map value.
"""
    return _ida_hexrays.lvar_mapping_second(p)


def lvar_mapping_find(map: 'lvar_mapping_t', key: 'lvar_locator_t'
    ) ->'lvar_mapping_iterator_t':
    """Find the specified key in lvar_mapping_t.
"""
    return _ida_hexrays.lvar_mapping_find(map, key)


def lvar_mapping_insert(map: 'lvar_mapping_t', key: 'lvar_locator_t', val:
    'lvar_locator_t') ->'lvar_mapping_iterator_t':
    """Insert new (lvar_locator_t, lvar_locator_t) pair into lvar_mapping_t.
"""
    return _ida_hexrays.lvar_mapping_insert(map, key, val)


def lvar_mapping_begin(map: 'lvar_mapping_t') ->'lvar_mapping_iterator_t':
    """Get iterator pointing to the beginning of lvar_mapping_t.
"""
    return _ida_hexrays.lvar_mapping_begin(map)


def lvar_mapping_end(map: 'lvar_mapping_t') ->'lvar_mapping_iterator_t':
    """Get iterator pointing to the end of lvar_mapping_t.
"""
    return _ida_hexrays.lvar_mapping_end(map)


def lvar_mapping_next(p: 'lvar_mapping_iterator_t'
    ) ->'lvar_mapping_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.lvar_mapping_next(p)


def lvar_mapping_prev(p: 'lvar_mapping_iterator_t'
    ) ->'lvar_mapping_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.lvar_mapping_prev(p)


def lvar_mapping_erase(map: 'lvar_mapping_t', p: 'lvar_mapping_iterator_t'
    ) ->None:
    """Erase current element from lvar_mapping_t.
"""
    return _ida_hexrays.lvar_mapping_erase(map, p)


def lvar_mapping_clear(map: 'lvar_mapping_t') ->None:
    """Clear lvar_mapping_t.
"""
    return _ida_hexrays.lvar_mapping_clear(map)


def lvar_mapping_size(map: 'lvar_mapping_t') ->int:
    """Get size of lvar_mapping_t.
"""
    return _ida_hexrays.lvar_mapping_size(map)


def lvar_mapping_free(map: 'lvar_mapping_t') ->None:
    """Delete lvar_mapping_t instance.
"""
    return _ida_hexrays.lvar_mapping_free(map)


def lvar_mapping_new() ->'lvar_mapping_t *':
    """Create a new lvar_mapping_t instance.
"""
    return _ida_hexrays.lvar_mapping_new()


class udcall_map_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.udcall_map_iterator_t_x_get,
        _ida_hexrays.udcall_map_iterator_t_x_set)

    def __eq__(self, p: 'udcall_map_iterator_t') ->bool:
        return _ida_hexrays.udcall_map_iterator_t___eq__(self, p)

    def __ne__(self, p: 'udcall_map_iterator_t') ->bool:
        return _ida_hexrays.udcall_map_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.udcall_map_iterator_t_swiginit(self, _ida_hexrays.
            new_udcall_map_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_udcall_map_iterator_t


_ida_hexrays.udcall_map_iterator_t_swigregister(udcall_map_iterator_t)


def udcall_map_first(p: 'udcall_map_iterator_t') ->'ea_t const &':
    """Get reference to the current map key.
"""
    return _ida_hexrays.udcall_map_first(p)


def udcall_map_second(p: 'udcall_map_iterator_t') ->'udcall_t &':
    """Get reference to the current map value.
"""
    return _ida_hexrays.udcall_map_second(p)


def udcall_map_find(map: 'udcall_map_t const *', key: 'ea_t const &'
    ) ->'udcall_map_iterator_t':
    """Find the specified key in udcall_map_t.
"""
    return _ida_hexrays.udcall_map_find(map, key)


def udcall_map_insert(map: 'udcall_map_t *', key: 'ea_t const &', val:
    'udcall_t') ->'udcall_map_iterator_t':
    """Insert new (ea_t, udcall_t) pair into udcall_map_t.
"""
    return _ida_hexrays.udcall_map_insert(map, key, val)


def udcall_map_begin(map: 'udcall_map_t const *') ->'udcall_map_iterator_t':
    """Get iterator pointing to the beginning of udcall_map_t.
"""
    return _ida_hexrays.udcall_map_begin(map)


def udcall_map_end(map: 'udcall_map_t const *') ->'udcall_map_iterator_t':
    """Get iterator pointing to the end of udcall_map_t.
"""
    return _ida_hexrays.udcall_map_end(map)


def udcall_map_next(p: 'udcall_map_iterator_t') ->'udcall_map_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.udcall_map_next(p)


def udcall_map_prev(p: 'udcall_map_iterator_t') ->'udcall_map_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.udcall_map_prev(p)


def udcall_map_erase(map: 'udcall_map_t *', p: 'udcall_map_iterator_t') ->None:
    """Erase current element from udcall_map_t.
"""
    return _ida_hexrays.udcall_map_erase(map, p)


def udcall_map_clear(map: 'udcall_map_t *') ->None:
    """Clear udcall_map_t.
"""
    return _ida_hexrays.udcall_map_clear(map)


def udcall_map_size(map: 'udcall_map_t *') ->int:
    """Get size of udcall_map_t.
"""
    return _ida_hexrays.udcall_map_size(map)


def udcall_map_free(map: 'udcall_map_t *') ->None:
    """Delete udcall_map_t instance.
"""
    return _ida_hexrays.udcall_map_free(map)


def udcall_map_new() ->'udcall_map_t *':
    """Create a new udcall_map_t instance.
"""
    return _ida_hexrays.udcall_map_new()


class block_chains_iterator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    x: 'iterator_word' = property(_ida_hexrays.
        block_chains_iterator_t_x_get, _ida_hexrays.
        block_chains_iterator_t_x_set)

    def __eq__(self, p: 'block_chains_iterator_t') ->bool:
        return _ida_hexrays.block_chains_iterator_t___eq__(self, p)

    def __ne__(self, p: 'block_chains_iterator_t') ->bool:
        return _ida_hexrays.block_chains_iterator_t___ne__(self, p)

    def __init__(self):
        _ida_hexrays.block_chains_iterator_t_swiginit(self, _ida_hexrays.
            new_block_chains_iterator_t())
    __swig_destroy__ = _ida_hexrays.delete_block_chains_iterator_t


_ida_hexrays.block_chains_iterator_t_swigregister(block_chains_iterator_t)


def block_chains_get(p: 'block_chains_iterator_t') ->'chain_t &':
    """Get reference to the current set value.
"""
    return _ida_hexrays.block_chains_get(p)


def block_chains_find(set: 'block_chains_t', val: 'chain_t'
    ) ->'block_chains_iterator_t':
    """Find the specified key in set block_chains_t.
"""
    return _ida_hexrays.block_chains_find(set, val)


def block_chains_insert(set: 'block_chains_t', val: 'chain_t'
    ) ->'block_chains_iterator_t':
    """Insert new (chain_t) into set block_chains_t.
"""
    return _ida_hexrays.block_chains_insert(set, val)


def block_chains_begin(set: 'block_chains_t') ->'block_chains_iterator_t':
    """Get iterator pointing to the beginning of block_chains_t.
"""
    return _ida_hexrays.block_chains_begin(set)


def block_chains_end(set: 'block_chains_t') ->'block_chains_iterator_t':
    """Get iterator pointing to the end of block_chains_t.
"""
    return _ida_hexrays.block_chains_end(set)


def block_chains_next(p: 'block_chains_iterator_t'
    ) ->'block_chains_iterator_t':
    """Move to the next element.
"""
    return _ida_hexrays.block_chains_next(p)


def block_chains_prev(p: 'block_chains_iterator_t'
    ) ->'block_chains_iterator_t':
    """Move to the previous element.
"""
    return _ida_hexrays.block_chains_prev(p)


def block_chains_erase(set: 'block_chains_t', p: 'block_chains_iterator_t'
    ) ->None:
    """Erase current element from block_chains_t.
"""
    return _ida_hexrays.block_chains_erase(set, p)


def block_chains_clear(set: 'block_chains_t') ->None:
    """Clear block_chains_t.
"""
    return _ida_hexrays.block_chains_clear(set)


def block_chains_size(set: 'block_chains_t') ->int:
    """Get size of block_chains_t.
"""
    return _ida_hexrays.block_chains_size(set)


def block_chains_free(set: 'block_chains_t') ->None:
    """Delete block_chains_t instance.
"""
    return _ida_hexrays.block_chains_free(set)


def block_chains_new() ->'block_chains_t *':
    """Create a new block_chains_t instance.
"""
    return _ida_hexrays.block_chains_new()
