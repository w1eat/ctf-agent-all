from __future__ import annotations
from sys import version_info as _swig_python_version_info
if __package__ or '.' in __name__:
    from . import _ida_hexrays_defs
else:
    import _ida_hexrays_defs
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
SWIG_PYTHON_LEGACY_BOOL = _ida_hexrays_defs.SWIG_PYTHON_LEGACY_BOOL
from typing import Tuple, List, Union
import ida_idaapi
import ida_pro
import ida_xref
import ida_typeinf
import ida_idp
import ida_gdl


class hexwarns_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def __init__(self, *args):
        _ida_hexrays_defs.hexwarns_t_swiginit(self, _ida_hexrays_defs.
            new_hexwarns_t(*args))
    __swig_destroy__ = _ida_hexrays_defs.delete_hexwarns_t

    def push_back(self, *args) ->'hexwarn_t &':
        return _ida_hexrays_defs.hexwarns_t_push_back(self, *args)

    def pop_back(self) ->None:
        return _ida_hexrays_defs.hexwarns_t_pop_back(self)

    def size(self) ->int:
        return _ida_hexrays_defs.hexwarns_t_size(self)

    def empty(self) ->bool:
        return _ida_hexrays_defs.hexwarns_t_empty(self)

    def at(self, _idx: int) ->'hexwarn_t const &':
        return _ida_hexrays_defs.hexwarns_t_at(self, _idx)

    def qclear(self) ->None:
        return _ida_hexrays_defs.hexwarns_t_qclear(self)

    def clear(self) ->None:
        return _ida_hexrays_defs.hexwarns_t_clear(self)

    def resize(self, *args) ->None:
        return _ida_hexrays_defs.hexwarns_t_resize(self, *args)

    def grow(self, *args) ->None:
        return _ida_hexrays_defs.hexwarns_t_grow(self, *args)

    def capacity(self) ->int:
        return _ida_hexrays_defs.hexwarns_t_capacity(self)

    def reserve(self, cnt: int) ->None:
        return _ida_hexrays_defs.hexwarns_t_reserve(self, cnt)

    def truncate(self) ->None:
        return _ida_hexrays_defs.hexwarns_t_truncate(self)

    def swap(self, r: 'hexwarns_t') ->None:
        return _ida_hexrays_defs.hexwarns_t_swap(self, r)

    def extract(self) ->'hexwarn_t *':
        return _ida_hexrays_defs.hexwarns_t_extract(self)

    def inject(self, s: 'hexwarn_t', len: int) ->None:
        return _ida_hexrays_defs.hexwarns_t_inject(self, s, len)

    def __eq__(self, r: 'hexwarns_t') ->bool:
        return _ida_hexrays_defs.hexwarns_t___eq__(self, r)

    def __ne__(self, r: 'hexwarns_t') ->bool:
        return _ida_hexrays_defs.hexwarns_t___ne__(self, r)

    def begin(self, *args) ->'qvector< hexwarn_t >::const_iterator':
        return _ida_hexrays_defs.hexwarns_t_begin(self, *args)

    def end(self, *args) ->'qvector< hexwarn_t >::const_iterator':
        return _ida_hexrays_defs.hexwarns_t_end(self, *args)

    def insert(self, it: 'hexwarn_t', x: 'hexwarn_t'
        ) ->'qvector< hexwarn_t >::iterator':
        return _ida_hexrays_defs.hexwarns_t_insert(self, it, x)

    def erase(self, *args) ->'qvector< hexwarn_t >::iterator':
        return _ida_hexrays_defs.hexwarns_t_erase(self, *args)

    def find(self, *args) ->'qvector< hexwarn_t >::const_iterator':
        return _ida_hexrays_defs.hexwarns_t_find(self, *args)

    def has(self, x: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarns_t_has(self, x)

    def add_unique(self, x: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarns_t_add_unique(self, x)

    def _del(self, x: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarns_t__del(self, x)

    def __len__(self) ->int:
        return _ida_hexrays_defs.hexwarns_t___len__(self)

    def __getitem__(self, i: int) ->'hexwarn_t const &':
        return _ida_hexrays_defs.hexwarns_t___getitem__(self, i)

    def __setitem__(self, i: int, v: 'hexwarn_t') ->None:
        return _ida_hexrays_defs.hexwarns_t___setitem__(self, i, v)

    def append(self, x: 'hexwarn_t') ->None:
        return _ida_hexrays_defs.hexwarns_t_append(self, x)

    def extend(self, x: 'hexwarns_t') ->None:
        return _ida_hexrays_defs.hexwarns_t_extend(self, x)
    front = ida_idaapi._qvector_front
    back = ida_idaapi._qvector_back
    __iter__ = ida_idaapi._bounded_getitem_iterator


_ida_hexrays_defs.hexwarns_t_swigregister(hexwarns_t)


class user_numforms_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr

    def at(self, _Keyval: 'operand_locator_t') ->'number_format_t &':
        return _ida_hexrays_defs.user_numforms_t_at(self, _Keyval)

    def size(self) ->int:
        return _ida_hexrays_defs.user_numforms_t_size(self)

    def __init__(self):
        _ida_hexrays_defs.user_numforms_t_swiginit(self, _ida_hexrays_defs.
            new_user_numforms_t())
    __swig_destroy__ = _ida_hexrays_defs.delete_user_numforms_t


_ida_hexrays_defs.user_numforms_t_swigregister(user_numforms_t)


def debug_hexrays_ctree(level: int, msg: str) ->None:
    return _ida_hexrays_defs.debug_hexrays_ctree(level, msg)


MAX_SUPPORTED_STACK_SIZE = _ida_hexrays_defs.MAX_SUPPORTED_STACK_SIZE
DECOMP_NO_WAIT = _ida_hexrays_defs.DECOMP_NO_WAIT
"""do not display waitbox
"""
DECOMP_NO_CACHE = _ida_hexrays_defs.DECOMP_NO_CACHE
"""do not use decompilation cache (snippets are never cached)
"""
DECOMP_NO_FRAME = _ida_hexrays_defs.DECOMP_NO_FRAME
"""do not use function frame info (only snippet mode)
"""
DECOMP_WARNINGS = _ida_hexrays_defs.DECOMP_WARNINGS
"""display warnings in the output window
"""
DECOMP_ALL_BLKS = _ida_hexrays_defs.DECOMP_ALL_BLKS
"""generate microcode for unreachable blocks
"""
DECOMP_NO_HIDE = _ida_hexrays_defs.DECOMP_NO_HIDE
"""do not close display waitbox. see close_hexrays_waitbox()
"""
DECOMP_GXREFS_DEFLT = _ida_hexrays_defs.DECOMP_GXREFS_DEFLT
"""the default behavior: do not update the global xrefs cache upon decompile() call, but when the pseudocode text is generated (e.g., through cfunc_t.get_pseudocode()) 
        """
DECOMP_GXREFS_NOUPD = _ida_hexrays_defs.DECOMP_GXREFS_NOUPD
"""do not update the global xrefs cache
"""
DECOMP_GXREFS_FORCE = _ida_hexrays_defs.DECOMP_GXREFS_FORCE
"""update the global xrefs cache immediately
"""
DECOMP_VOID_MBA = _ida_hexrays_defs.DECOMP_VOID_MBA
"""return empty mba object (to be used with gen_microcode)
"""
DECOMP_OUTLINE = _ida_hexrays_defs.DECOMP_OUTLINE
"""generate code for an outline
"""


def hexrays_alloc(size: int) ->'void *':
    return _ida_hexrays_defs.hexrays_alloc(size)


def hexrays_free(ptr: 'void *') ->None:
    return _ida_hexrays_defs.hexrays_free(ptr)


class operand_locator_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ea: ida_idaapi.ea_t = property(_ida_hexrays_defs.
        operand_locator_t_ea_get, _ida_hexrays_defs.operand_locator_t_ea_set)
    """address of the original processor instruction
"""
    opnum: int = property(_ida_hexrays_defs.operand_locator_t_opnum_get,
        _ida_hexrays_defs.operand_locator_t_opnum_set)
    """operand number in the instruction
"""

    def __init__(self, _ea: ida_idaapi.ea_t, _opnum: int):
        _ida_hexrays_defs.operand_locator_t_swiginit(self,
            _ida_hexrays_defs.new_operand_locator_t(_ea, _opnum))

    def __eq__(self, r: 'operand_locator_t') ->bool:
        return _ida_hexrays_defs.operand_locator_t___eq__(self, r)

    def __ne__(self, r: 'operand_locator_t') ->bool:
        return _ida_hexrays_defs.operand_locator_t___ne__(self, r)

    def __lt__(self, r: 'operand_locator_t') ->bool:
        return _ida_hexrays_defs.operand_locator_t___lt__(self, r)

    def __gt__(self, r: 'operand_locator_t') ->bool:
        return _ida_hexrays_defs.operand_locator_t___gt__(self, r)

    def __le__(self, r: 'operand_locator_t') ->bool:
        return _ida_hexrays_defs.operand_locator_t___le__(self, r)

    def __ge__(self, r: 'operand_locator_t') ->bool:
        return _ida_hexrays_defs.operand_locator_t___ge__(self, r)

    def compare(self, r: 'operand_locator_t') ->int:
        return _ida_hexrays_defs.operand_locator_t_compare(self, r)
    __swig_destroy__ = _ida_hexrays_defs.delete_operand_locator_t


_ida_hexrays_defs.operand_locator_t_swigregister(operand_locator_t)


class number_format_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    flags32: 'flags_t' = property(_ida_hexrays_defs.
        number_format_t_flags32_get, _ida_hexrays_defs.
        number_format_t_flags32_set)
    """low 32-bit of flags (for compatibility)
"""
    opnum: 'char' = property(_ida_hexrays_defs.number_format_t_opnum_get,
        _ida_hexrays_defs.number_format_t_opnum_set)
    """operand number: 0..UA_MAXOP
"""
    props: 'char' = property(_ida_hexrays_defs.number_format_t_props_get,
        _ida_hexrays_defs.number_format_t_props_set)
    """properties: combination of NF_ bits (Number format property bits) 
        """
    serial: 'uchar' = property(_ida_hexrays_defs.number_format_t_serial_get,
        _ida_hexrays_defs.number_format_t_serial_set)
    """for enums: constant serial number
"""
    org_nbytes: 'char' = property(_ida_hexrays_defs.
        number_format_t_org_nbytes_get, _ida_hexrays_defs.
        number_format_t_org_nbytes_set)
    """original number size in bytes
"""
    type_name: str = property(_ida_hexrays_defs.
        number_format_t_type_name_get, _ida_hexrays_defs.
        number_format_t_type_name_set)
    """for stroffs: structure for offsetof()
for enums: enum name 
        """
    flags: 'flags64_t' = property(_ida_hexrays_defs.
        number_format_t_flags_get, _ida_hexrays_defs.number_format_t_flags_set)
    """ida flags, which describe number radix, enum, etc 
        """

    def __init__(self, _opnum: int=0):
        _ida_hexrays_defs.number_format_t_swiginit(self, _ida_hexrays_defs.
            new_number_format_t(_opnum))

    def get_radix(self) ->int:
        """Get number radix 
        
:returns: 2,8,10, or 16"""
        return _ida_hexrays_defs.number_format_t_get_radix(self)

    def is_fixed(self) ->bool:
        """Is number representation fixed? Fixed representation cannot be modified by the decompiler 
        """
        return _ida_hexrays_defs.number_format_t_is_fixed(self)

    def is_hex(self) ->bool:
        """Is a hexadecimal number?
"""
        return _ida_hexrays_defs.number_format_t_is_hex(self)

    def is_dec(self) ->bool:
        """Is a decimal number?
"""
        return _ida_hexrays_defs.number_format_t_is_dec(self)

    def is_oct(self) ->bool:
        """Is a octal number?
"""
        return _ida_hexrays_defs.number_format_t_is_oct(self)

    def is_enum(self) ->bool:
        """Is a symbolic constant?
"""
        return _ida_hexrays_defs.number_format_t_is_enum(self)

    def is_char(self) ->bool:
        """Is a character constant?
"""
        return _ida_hexrays_defs.number_format_t_is_char(self)

    def is_stroff(self) ->bool:
        """Is a structure field offset?
"""
        return _ida_hexrays_defs.number_format_t_is_stroff(self)

    def is_numop(self) ->bool:
        """Is a number?
"""
        return _ida_hexrays_defs.number_format_t_is_numop(self)

    def needs_to_be_inverted(self) ->bool:
        """Does the number need to be negated or bitwise negated? Returns true if the user requested a negation but it is not done yet 
        """
        return _ida_hexrays_defs.number_format_t_needs_to_be_inverted(self)

    def has_unmutable_type(self) ->bool:
        return _ida_hexrays_defs.number_format_t_has_unmutable_type(self)
    __swig_destroy__ = _ida_hexrays_defs.delete_number_format_t


_ida_hexrays_defs.number_format_t_swigregister(number_format_t)
NF_FIXED = _ida_hexrays_defs.NF_FIXED
"""number format has been defined by the user
"""
NF_NEGDONE = _ida_hexrays_defs.NF_NEGDONE
"""temporary internal bit: negation has been performed
"""
NF_BINVDONE = _ida_hexrays_defs.NF_BINVDONE
"""temporary internal bit: inverting bits is done
"""
NF_NEGATE = _ida_hexrays_defs.NF_NEGATE
"""The user asked to negate the constant.
"""
NF_BITNOT = _ida_hexrays_defs.NF_BITNOT
"""The user asked to invert bits of the constant.
"""
NF_VALID = _ida_hexrays_defs.NF_VALID
"""internal bit: stroff or enum is valid for enums: this bit is set immediately for stroffs: this bit is set at the end of decompilation 
        """


class mba_ranges_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    pfn: 'func_t *' = property(_ida_hexrays_defs.mba_ranges_t_pfn_get,
        _ida_hexrays_defs.mba_ranges_t_pfn_set)
    """function to decompile. if not null, then function mode.
"""
    ranges: 'rangevec_t' = property(_ida_hexrays_defs.
        mba_ranges_t_ranges_get, _ida_hexrays_defs.mba_ranges_t_ranges_set)
    """snippet mode: ranges to decompile. function mode: list of outlined ranges 
        """

    def __init__(self, *args):
        _ida_hexrays_defs.mba_ranges_t_swiginit(self, _ida_hexrays_defs.
            new_mba_ranges_t(*args))

    def start(self) ->ida_idaapi.ea_t:
        return _ida_hexrays_defs.mba_ranges_t_start(self)

    def empty(self) ->bool:
        return _ida_hexrays_defs.mba_ranges_t_empty(self)

    def clear(self) ->None:
        return _ida_hexrays_defs.mba_ranges_t_clear(self)

    def is_snippet(self) ->bool:
        return _ida_hexrays_defs.mba_ranges_t_is_snippet(self)

    def is_fragmented(self) ->bool:
        return _ida_hexrays_defs.mba_ranges_t_is_fragmented(self)
    __swig_destroy__ = _ida_hexrays_defs.delete_mba_ranges_t


_ida_hexrays_defs.mba_ranges_t_swigregister(mba_ranges_t)
MERR_OK = _ida_hexrays_defs.MERR_OK
"""ok
"""
MERR_BLOCK = _ida_hexrays_defs.MERR_BLOCK
"""no error, switch to new block
"""
MERR_INTERR = _ida_hexrays_defs.MERR_INTERR
"""internal error
"""
MERR_INSN = _ida_hexrays_defs.MERR_INSN
"""cannot convert to microcode
"""
MERR_MEM = _ida_hexrays_defs.MERR_MEM
"""not enough memory
"""
MERR_BADBLK = _ida_hexrays_defs.MERR_BADBLK
"""bad block found
"""
MERR_BADSP = _ida_hexrays_defs.MERR_BADSP
"""positive sp value has been found
"""
MERR_PROLOG = _ida_hexrays_defs.MERR_PROLOG
"""prolog analysis failed
"""
MERR_SWITCH = _ida_hexrays_defs.MERR_SWITCH
"""wrong switch idiom
"""
MERR_EXCEPTION = _ida_hexrays_defs.MERR_EXCEPTION
"""exception analysis failed
"""
MERR_HUGESTACK = _ida_hexrays_defs.MERR_HUGESTACK
"""stack frame is too big
"""
MERR_LVARS = _ida_hexrays_defs.MERR_LVARS
"""local variable allocation failed
"""
MERR_BITNESS = _ida_hexrays_defs.MERR_BITNESS
"""16-bit functions cannot be decompiled
"""
MERR_BADCALL = _ida_hexrays_defs.MERR_BADCALL
"""could not determine call arguments
"""
MERR_BADFRAME = _ida_hexrays_defs.MERR_BADFRAME
"""function frame is wrong
"""
MERR_UNKTYPE = _ida_hexrays_defs.MERR_UNKTYPE
"""undefined type s (currently unused error code)
"""
MERR_BADIDB = _ida_hexrays_defs.MERR_BADIDB
"""inconsistent database information
"""
MERR_SIZEOF = _ida_hexrays_defs.MERR_SIZEOF
"""wrong basic type sizes in compiler settings
"""
MERR_REDO = _ida_hexrays_defs.MERR_REDO
"""redecompilation has been requested
"""
MERR_CANCELED = _ida_hexrays_defs.MERR_CANCELED
"""decompilation has been cancelled
"""
MERR_RECDEPTH = _ida_hexrays_defs.MERR_RECDEPTH
"""max recursion depth reached during lvar allocation
"""
MERR_OVERLAP = _ida_hexrays_defs.MERR_OVERLAP
"""variables would overlap: s
"""
MERR_PARTINIT = _ida_hexrays_defs.MERR_PARTINIT
"""partially initialized variable s
"""
MERR_COMPLEX = _ida_hexrays_defs.MERR_COMPLEX
"""too complex function
"""
MERR_LICENSE = _ida_hexrays_defs.MERR_LICENSE
"""no license available
"""
MERR_ONLY32 = _ida_hexrays_defs.MERR_ONLY32
"""only 32-bit functions can be decompiled for the current database
"""
MERR_ONLY64 = _ida_hexrays_defs.MERR_ONLY64
"""only 64-bit functions can be decompiled for the current database
"""
MERR_BUSY = _ida_hexrays_defs.MERR_BUSY
"""already decompiling a function
"""
MERR_FARPTR = _ida_hexrays_defs.MERR_FARPTR
"""far memory model is supported only for pc
"""
MERR_EXTERN = _ida_hexrays_defs.MERR_EXTERN
"""special segments cannot be decompiled
"""
MERR_FUNCSIZE = _ida_hexrays_defs.MERR_FUNCSIZE
"""too big function
"""
MERR_BADRANGES = _ida_hexrays_defs.MERR_BADRANGES
"""bad input ranges
"""
MERR_BADARCH = _ida_hexrays_defs.MERR_BADARCH
"""current architecture is not supported
"""
MERR_DSLOT = _ida_hexrays_defs.MERR_DSLOT
"""bad instruction in the delay slot
"""
MERR_STOP = _ida_hexrays_defs.MERR_STOP
"""no error, stop the analysis
"""
MERR_CLOUD = _ida_hexrays_defs.MERR_CLOUD
"""cloud: s
"""
MERR_EMULATOR = _ida_hexrays_defs.MERR_EMULATOR
"""emulator: s
"""
MERR_MAX_ERR = _ida_hexrays_defs.MERR_MAX_ERR
MERR_LOOP = _ida_hexrays_defs.MERR_LOOP
"""internal code: redo last loop (never reported)
"""
WARN_VARARG_REGS = _ida_hexrays_defs.WARN_VARARG_REGS
"""0 cannot handle register arguments in vararg function, discarded them
"""
WARN_ILL_PURGED = _ida_hexrays_defs.WARN_ILL_PURGED
"""1 odd caller purged bytes d, correcting
"""
WARN_ILL_FUNCTYPE = _ida_hexrays_defs.WARN_ILL_FUNCTYPE
"""2 invalid function type 's' has been ignored
"""
WARN_VARARG_TCAL = _ida_hexrays_defs.WARN_VARARG_TCAL
"""3 cannot handle tail call to vararg
"""
WARN_VARARG_NOSTK = _ida_hexrays_defs.WARN_VARARG_NOSTK
"""4 call vararg without local stack
"""
WARN_VARARG_MANY = _ida_hexrays_defs.WARN_VARARG_MANY
"""5 too many varargs, some ignored
"""
WARN_ADDR_OUTARGS = _ida_hexrays_defs.WARN_ADDR_OUTARGS
"""6 cannot handle address arithmetics in outgoing argument area of stack frame - unused
"""
WARN_DEP_UNK_CALLS = _ida_hexrays_defs.WARN_DEP_UNK_CALLS
"""7 found interdependent unknown calls
"""
WARN_ILL_ELLIPSIS = _ida_hexrays_defs.WARN_ILL_ELLIPSIS
"""8 erroneously detected ellipsis type has been ignored
"""
WARN_GUESSED_TYPE = _ida_hexrays_defs.WARN_GUESSED_TYPE
"""9 using guessed type s;
"""
WARN_EXP_LINVAR = _ida_hexrays_defs.WARN_EXP_LINVAR
"""10 failed to expand a linear variable
"""
WARN_WIDEN_CHAINS = _ida_hexrays_defs.WARN_WIDEN_CHAINS
"""11 failed to widen chains
"""
WARN_BAD_PURGED = _ida_hexrays_defs.WARN_BAD_PURGED
"""12 inconsistent function type and number of purged bytes
"""
WARN_CBUILD_LOOPS = _ida_hexrays_defs.WARN_CBUILD_LOOPS
"""13 too many cbuild loops
"""
WARN_NO_SAVE_REST = _ida_hexrays_defs.WARN_NO_SAVE_REST
"""14 could not find valid save-restore pair for s
"""
WARN_ODD_INPUT_REG = _ida_hexrays_defs.WARN_ODD_INPUT_REG
"""15 odd input register s
"""
WARN_ODD_ADDR_USE = _ida_hexrays_defs.WARN_ODD_ADDR_USE
"""16 odd use of a variable address
"""
WARN_MUST_RET_FP = _ida_hexrays_defs.WARN_MUST_RET_FP
"""17 function return type is incorrect (must be floating point)
"""
WARN_ILL_FPU_STACK = _ida_hexrays_defs.WARN_ILL_FPU_STACK
"""18 inconsistent fpu stack
"""
WARN_SELFREF_PROP = _ida_hexrays_defs.WARN_SELFREF_PROP
"""19 self-referencing variable has been detected
"""
WARN_WOULD_OVERLAP = _ida_hexrays_defs.WARN_WOULD_OVERLAP
"""20 variables would overlap: s
"""
WARN_ARRAY_INARG = _ida_hexrays_defs.WARN_ARRAY_INARG
"""21 array has been used for an input argument
"""
WARN_MAX_ARGS = _ida_hexrays_defs.WARN_MAX_ARGS
"""22 too many input arguments, some ignored
"""
WARN_BAD_FIELD_TYPE = _ida_hexrays_defs.WARN_BAD_FIELD_TYPE
"""23 incorrect structure member type for s::s, ignored
"""
WARN_WRITE_CONST = _ida_hexrays_defs.WARN_WRITE_CONST
"""24 write access to const memory at a has been detected
"""
WARN_BAD_RETVAR = _ida_hexrays_defs.WARN_BAD_RETVAR
"""25 wrong return variable
"""
WARN_FRAG_LVAR = _ida_hexrays_defs.WARN_FRAG_LVAR
"""26 fragmented variable at s may be wrong
"""
WARN_HUGE_STKOFF = _ida_hexrays_defs.WARN_HUGE_STKOFF
"""27 exceedingly huge offset into the stack frame
"""
WARN_UNINITED_REG = _ida_hexrays_defs.WARN_UNINITED_REG
"""28 reference to an uninitialized register has been removed: s
"""
WARN_FIXED_INSN = _ida_hexrays_defs.WARN_FIXED_INSN
"""29 fixed broken insn
"""
WARN_WRONG_VA_OFF = _ida_hexrays_defs.WARN_WRONG_VA_OFF
"""30 wrong offset of va_list variable
"""
WARN_CR_NOFIELD = _ida_hexrays_defs.WARN_CR_NOFIELD
"""31 CONTAINING_RECORD: no field 's' in struct 's' at d
"""
WARN_CR_BADOFF = _ida_hexrays_defs.WARN_CR_BADOFF
"""32 CONTAINING_RECORD: too small offset d for struct 's'
"""
WARN_BAD_STROFF = _ida_hexrays_defs.WARN_BAD_STROFF
"""33 user specified stroff has not been processed: s
"""
WARN_BAD_VARSIZE = _ida_hexrays_defs.WARN_BAD_VARSIZE
"""34 inconsistent variable size for 's'
"""
WARN_UNSUPP_REG = _ida_hexrays_defs.WARN_UNSUPP_REG
"""35 unsupported processor register 's'
"""
WARN_UNALIGNED_ARG = _ida_hexrays_defs.WARN_UNALIGNED_ARG
"""36 unaligned function argument 's'
"""
WARN_BAD_STD_TYPE = _ida_hexrays_defs.WARN_BAD_STD_TYPE
"""37 corrupted or unexisting local type 's'
"""
WARN_BAD_CALL_SP = _ida_hexrays_defs.WARN_BAD_CALL_SP
"""38 bad sp value at call
"""
WARN_MISSED_SWITCH = _ida_hexrays_defs.WARN_MISSED_SWITCH
"""39 wrong markup of switch jump, skipped it
"""
WARN_BAD_SP = _ida_hexrays_defs.WARN_BAD_SP
"""40 positive sp value a has been found
"""
WARN_BAD_STKPNT = _ida_hexrays_defs.WARN_BAD_STKPNT
"""41 wrong sp change point
"""
WARN_UNDEF_LVAR = _ida_hexrays_defs.WARN_UNDEF_LVAR
"""42 variable 's' is possibly undefined
"""
WARN_JUMPOUT = _ida_hexrays_defs.WARN_JUMPOUT
"""43 control flows out of bounds
"""
WARN_BAD_VALRNG = _ida_hexrays_defs.WARN_BAD_VALRNG
"""44 values range analysis failed
"""
WARN_BAD_SHADOW = _ida_hexrays_defs.WARN_BAD_SHADOW
"""45 ignored the value written to the shadow area of the succeeding call
"""
WARN_OPT_VALRNG = _ida_hexrays_defs.WARN_OPT_VALRNG
"""46 conditional instruction was optimized away because s
"""
WARN_RET_LOCREF = _ida_hexrays_defs.WARN_RET_LOCREF
"""47 returning address of temporary local variable 's'
"""
WARN_BAD_MAPDST = _ida_hexrays_defs.WARN_BAD_MAPDST
"""48 too short map destination 's' for variable 's'
"""
WARN_BAD_INSN = _ida_hexrays_defs.WARN_BAD_INSN
"""49 bad instruction
"""
WARN_ODD_ABI = _ida_hexrays_defs.WARN_ODD_ABI
"""50 encountered odd instruction for the current ABI
"""
WARN_UNBALANCED_STACK = _ida_hexrays_defs.WARN_UNBALANCED_STACK
"""51 unbalanced stack, ignored a potential tail call
"""
WARN_OPT_VALRNG2 = _ida_hexrays_defs.WARN_OPT_VALRNG2
"""52 mask 0xX is shortened because s <= 0xX\"
"""
WARN_OPT_VALRNG3 = _ida_hexrays_defs.WARN_OPT_VALRNG3
"""53 masking with 0XX was optimized away because s <= 0xX
"""
WARN_OPT_USELESS_JCND = _ida_hexrays_defs.WARN_OPT_USELESS_JCND
"""54 simplified comparisons for 's': s became s
"""
WARN_SUBFRAME_OVERFLOW = _ida_hexrays_defs.WARN_SUBFRAME_OVERFLOW
"""55 call arguments overflow the function chunk frame
"""
WARN_OPT_VALRNG4 = _ida_hexrays_defs.WARN_OPT_VALRNG4
"""56 the cases s were optimized away because s
"""
WARN_FRAME_ACCESS = _ida_hexrays_defs.WARN_FRAME_ACCESS
"""57 illegal frame access
"""
WARN_MAX = _ida_hexrays_defs.WARN_MAX
"""may be used in notes as a placeholder when the warning id is not available 
          """


class hexwarn_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    ea: ida_idaapi.ea_t = property(_ida_hexrays_defs.hexwarn_t_ea_get,
        _ida_hexrays_defs.hexwarn_t_ea_set)
    """Address where the warning occurred.
"""
    id: 'warnid_t' = property(_ida_hexrays_defs.hexwarn_t_id_get,
        _ida_hexrays_defs.hexwarn_t_id_set)
    """Warning id.
"""
    text: str = property(_ida_hexrays_defs.hexwarn_t_text_get,
        _ida_hexrays_defs.hexwarn_t_text_set)
    """Fully formatted text of the warning.
"""

    def __eq__(self, r: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarn_t___eq__(self, r)

    def __ne__(self, r: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarn_t___ne__(self, r)

    def __lt__(self, r: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarn_t___lt__(self, r)

    def __gt__(self, r: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarn_t___gt__(self, r)

    def __le__(self, r: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarn_t___le__(self, r)

    def __ge__(self, r: 'hexwarn_t') ->bool:
        return _ida_hexrays_defs.hexwarn_t___ge__(self, r)

    def compare(self, r: 'hexwarn_t') ->int:
        return _ida_hexrays_defs.hexwarn_t_compare(self, r)

    def __init__(self):
        _ida_hexrays_defs.hexwarn_t_swiginit(self, _ida_hexrays_defs.
            new_hexwarn_t())
    __swig_destroy__ = _ida_hexrays_defs.delete_hexwarn_t


_ida_hexrays_defs.hexwarn_t_swigregister(hexwarn_t)
MMAT_ZERO = _ida_hexrays_defs.MMAT_ZERO
"""microcode does not exist
"""
MMAT_GENERATED = _ida_hexrays_defs.MMAT_GENERATED
"""generated microcode
"""
MMAT_PREOPTIMIZED = _ida_hexrays_defs.MMAT_PREOPTIMIZED
"""preoptimized pass is complete
"""
MMAT_LOCOPT = _ida_hexrays_defs.MMAT_LOCOPT
"""local optimization of each basic block is complete. control flow graph is ready too. 
          """
MMAT_CALLS = _ida_hexrays_defs.MMAT_CALLS
"""detected call arguments. see also hxe_calls_done
"""
MMAT_GLBOPT1 = _ida_hexrays_defs.MMAT_GLBOPT1
"""performed the first pass of global optimization
"""
MMAT_GLBOPT2 = _ida_hexrays_defs.MMAT_GLBOPT2
"""most global optimization passes are done
"""
MMAT_GLBOPT3 = _ida_hexrays_defs.MMAT_GLBOPT3
"""completed all global optimization. microcode is fixed now.
"""
MMAT_LVARS = _ida_hexrays_defs.MMAT_LVARS
"""allocated local variables
"""


class vd_printer_t(object):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    tmpbuf: str = property(_ida_hexrays_defs.vd_printer_t_tmpbuf_get,
        _ida_hexrays_defs.vd_printer_t_tmpbuf_set)
    hdrlines: int = property(_ida_hexrays_defs.vd_printer_t_hdrlines_get,
        _ida_hexrays_defs.vd_printer_t_hdrlines_set)
    """number of header lines (prototype+typedef+lvars) valid at the end of print process 
        """

    def _print(self, indent: int, format: str) ->int:
        return _ida_hexrays_defs.vd_printer_t__print(self, indent, format)

    def __init__(self):
        if self.__class__ == vd_printer_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_defs.vd_printer_t_swiginit(self, _ida_hexrays_defs.
            new_vd_printer_t(_self))
    __swig_destroy__ = _ida_hexrays_defs.delete_vd_printer_t

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_defs.disown_vd_printer_t(self)
        return weakref.proxy(self)


_ida_hexrays_defs.vd_printer_t_swigregister(vd_printer_t)


class vc_printer_t(vd_printer_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    func: 'cfunc_t const *' = property(_ida_hexrays_defs.
        vc_printer_t_func_get, _ida_hexrays_defs.vc_printer_t_func_set)
    """cfunc_t to generate text for
"""
    lastchar: 'char' = property(_ida_hexrays_defs.vc_printer_t_lastchar_get,
        _ida_hexrays_defs.vc_printer_t_lastchar_set)
    """internal: last printed character 
        """

    def __init__(self, f: 'cfunc_t const *'):
        if self.__class__ == vc_printer_t:
            _self = None
        else:
            _self = self
        _ida_hexrays_defs.vc_printer_t_swiginit(self, _ida_hexrays_defs.
            new_vc_printer_t(_self, f))

    def oneliner(self) ->bool:
        """Are we generating one-line text representation? 
        
:returns: `true` if the output will occupy one line without line breaks"""
        return _ida_hexrays_defs.vc_printer_t_oneliner(self)
    __swig_destroy__ = _ida_hexrays_defs.delete_vc_printer_t

    def __disown__(self):
        self.this.disown()
        _ida_hexrays_defs.disown_vc_printer_t(self)
        return weakref.proxy(self)


_ida_hexrays_defs.vc_printer_t_swigregister(vc_printer_t)


class qstring_printer_t(vc_printer_t):
    thisown = property(lambda x: x.this.own(), lambda x, v: x.this.own(v),
        doc='The membership flag')
    __repr__ = _swig_repr
    with_tags: bool = property(_ida_hexrays_defs.
        qstring_printer_t_with_tags_get, _ida_hexrays_defs.
        qstring_printer_t_with_tags_set)
    """Generate output with color tags.
"""
    s: str = property(_ida_hexrays_defs.qstring_printer_t_s_get,
        _ida_hexrays_defs.qstring_printer_t_s_set)
    """Reference to the output string 
        """

    def _print(self, indent: int, format: str) ->int:
        return _ida_hexrays_defs.qstring_printer_t__print(self, indent, format)

    def __init__(self, f: 'cfunc_t const *', tags: bool):
        _ida_hexrays_defs.qstring_printer_t_swiginit(self,
            _ida_hexrays_defs.new_qstring_printer_t(f, tags))

    def get_s(self) ->str:
        return _ida_hexrays_defs.qstring_printer_t_get_s(self)
    s = property(lambda self: self.get_s())
    """Reference to the output string 
        """


_ida_hexrays_defs.qstring_printer_t_swigregister(qstring_printer_t)
import ida_idaapi
ida_idaapi._listify_types(hexwarns_t)
