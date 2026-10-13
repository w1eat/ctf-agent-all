// +build go1.14,!go1.16

package main

import (
	"cmd/internal/goobj"
	"cmd/internal/objabi"
	"cmd/internal/objfile"
	"log"
	"os"
)

func getSymbols(filename, importPath string) []Symbol {
	fileHandler, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}

	pkg, err := goobj.Parse(fileHandler, importPath)
	if err != nil {
		log.Fatal(err)
	}
	fileHandler.Close()

	f, err := objfile.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	textStart, textBytes, err := f.Text()
	textEnd := textStart + uint64(len(textBytes))
	if err != nil {
		log.Fatal(err)
	}
	f.Close()

	var symbols []Symbol
	for _, sym := range pkg.Syms {
		var outSym Symbol

		symStart := uint64(sym.Data.Offset)
		symEnd := uint64(symStart) + uint64(sym.Data.Size)
		if sym.Data.Size >= maximumFuncSize || sym.Data.Size < minimumFuncSize {
			continue
		}
		if sym.Kind != objabi.STEXT ||
			symStart < textStart || symEnd <= textStart || textEnd <= symStart {
			continue
		}
		outSym.buf = make([]byte, sym.Data.Size)
		bytes_copied := copy(outSym.buf, textBytes[symStart:symEnd])
		if int64(bytes_copied) != sym.Data.Size {
			log.Fatal("Couldn't copy textBytes from sym ", sym.SymID.Name)
		}
		outSym.name = sym.SymID.Name
		outSym.size = sym.Data.Size
		for _, r := range sym.Reloc {
			var outReloc Reloc
			outReloc.name = r.Sym.Name
			outReloc.offset = r.Offset
			outReloc.size = r.Size
			outReloc.codeRef = r.Type.IsDirectCallOrJump()
			outSym.relocs = append(outSym.relocs, outReloc)
		}
		symbols = append(symbols, outSym)
	}
	return symbols
}
