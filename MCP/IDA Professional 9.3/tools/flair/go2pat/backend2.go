// +build go1.16

package main

import (
	"cmd/internal/archive"
	"cmd/internal/goobj"
	"cmd/internal/objabi"
	"log"
	"os"
)

func objReaderFromFileHandler(file *os.File) *goobj.Reader {
	a, err := archive.Parse(file, false)
	if err != nil {
		log.Fatal(err)
	}
	for _, entry := range a.Entries {
		switch entry.Type {
		case archive.EntryGoObj:
			obj := entry.Obj
			b := make([]byte, obj.Size)
			_, err := file.ReadAt(b, obj.Offset)
			if err != nil {
				log.Fatal(err)
			}
			r := goobj.NewReaderFromBytes(b, false)
			return r
		default:
			continue
		}
	}
	log.Fatal("Couldn't create Reader from File: %v", file)
	return nil
}

func getSymbols(filename, importpath string) []Symbol {
	fileHandler, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	r := objReaderFromFileHandler(fileHandler)
	fileHandler.Close()

	nrefName := r.NRefName()
	refNames := make(map[goobj.SymRef]string, nrefName)
	for i := 0; i < nrefName; i++ {
		rn := r.RefName(i)
		refNames[rn.Sym()] = rn.Name(r)
	}
	resolveSymRef := func(s goobj.SymRef) string {
		var i uint32
		switch p := s.PkgIdx; p {
		case goobj.PkgIdxInvalid:
			if s.SymIdx != 0 {
				panic("bad sym ref")
			}
			return ""
		case goobj.PkgIdxHashed64:
			i = s.SymIdx + uint32(r.NSym())
		case goobj.PkgIdxHashed:
			i = s.SymIdx + uint32(r.NSym()+r.NHashed64def())
		case goobj.PkgIdxNone:
			i = s.SymIdx + uint32(r.NSym()+r.NHashed64def()+r.NHasheddef())
		case goobj.PkgIdxBuiltin:
			name, _ := goobj.BuiltinName(int(s.SymIdx))
			return name
		case goobj.PkgIdxSelf:
			i = s.SymIdx
		default:
			return refNames[s]
		}
		sym := r.Sym(i)
		return sym.Name(r)
	}

	var symbols []Symbol
	nsym := uint32(r.NSym())
	for i := uint32(0); i < nsym; i++ {
		var outSym Symbol
		sym := r.Sym(i)
		if sym.Name(r) == "" {
			continue
		}
		typ := objabi.SymKind(sym.Type())
		if typ != objabi.STEXT {
			continue
		}
		symSize := int(sym.Siz())
		outSym.size = int64(symSize)
		if symSize >= maximumFuncSize || symSize < minimumFuncSize {
			continue
		}
		symStart := uint32(r.DataOff(i))
		outSym.buf = make([]byte, symSize)
		bytes_copied := copy(outSym.buf, r.BytesAt(symStart, symSize))
		if bytes_copied != symSize {
			log.Fatal("Couldn't copy bytes from sym ", sym.Name(r))
		}
		outSym.name = sym.Name(r)
		relocs := r.Relocs(i)
		for _, rel := range relocs {
			var outReloc Reloc
			relocName := resolveSymRef(rel.Sym())
			outReloc.name = relocName
			outReloc.size = int64(rel.Siz())
			outReloc.offset = int64(rel.Off())
			t := objabi.RelocType(rel.Type())
			outReloc.codeRef = t.IsDirectCallOrJump()
			outSym.relocs = append(outSym.relocs, outReloc)
		}
		symbols = append(symbols, outSym)
	}
	return symbols
}
