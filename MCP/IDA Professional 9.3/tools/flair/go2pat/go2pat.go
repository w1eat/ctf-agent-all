package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"regexp"
	"strings"
)

const (
	minimumFuncSize = 12
	maximumFuncSize = 0x8000
)

func sanitizeName(str string) string {
	var s string
	s = str
	s = strings.Replace(s, "[", "", -1)
	s = strings.Replace(s, "]", "", -1)
	s = strings.Replace(s, "(", "", -1)
	s = strings.Replace(s, ")", "", -1)
	s = strings.Replace(s, "{", "", -1)
	s = strings.Replace(s, "}", "", -1)
	s = strings.Replace(s, "\\", "", -1)
	s = strings.Replace(s, "\"", "", -1)
	s = strings.Replace(s, ";", "", -1)

	s = strings.Replace(s, " ", "_", -1)
	s = strings.Replace(s, "-", "_", -1)
	s = strings.Replace(s, "/", "_", -1)

	s = strings.Replace(s, " ", "_", -1)
	s = strings.Replace(s, "-", "_", -1)
	s = strings.Replace(s, "*", "_ptr_", -1)
	s = strings.Replace(s, ",", "_comma_", -1)
	s = strings.Replace(s, "<-", "_chan_left_", -1)
	return s
}

func crc16(buffer []uint8, start uint64, length uint64) uint16 {
	var data uint32
	var crc uint16
	crc = 0xffff
	if length == 0 {
		return ^crc
	}
	end := start + length
	for start < end {
		data = uint32(buffer[start])
		for i := 0; i < 8; i++ {
			if (uint32(crc&0x0001) ^ (data & 0x1)) != 0 {
				crc = (crc >> 1) ^ 0x8408
			} else {
				crc >>= 1
			}
			data >>= 1
		}
		start += 1
	}
	crc = (^crc & 0xFFFF)
	crc = (crc << 8) | ((crc >> 8) & 0xFF)
	return crc
}

type Reloc struct {
	name    string
	offset  int64
	size    int64
	codeRef bool
}

type Symbol struct {
	name   string
	size   int64
	buf    []byte
	relocs []Reloc
}

func processPackage(filename, importPath string) {
	symbols := getSymbols(filename, importPath)

	outfilename := strings.Replace(strings.Replace(importPath, "/", "_", -1), ".", "_", -1) + ".pat"
	outfile, err := os.Create(outfilename)
	if err != nil {
		log.Fatal(err)
	}
	defer log.Printf("wrote to %s\n", outfilename)
	defer outfile.Close()
	for _, sym := range symbols {
		hexBuffer := fmt.Sprintf("%x", sym.buf)

		empty_extension := 64 - len(hexBuffer)
		if empty_extension > 0 {
			hexBuffer += strings.Repeat(".", empty_extension)
		}
		names := sanitizeName(sym.name)
		for _, r := range sym.relocs {
			if r.size < 1 {
				continue
			}
			relocName := sanitizeName(r.name)
			if len(relocName) > 0 && r.codeRef {
				names += fmt.Sprintf(" ^%04X %s", r.offset, relocName)
			}
			startIdx := r.offset * 2
			endIdx := startIdx + (r.size * 2)
			hexBuffer = hexBuffer[:startIdx] + strings.Repeat(".", int(r.size)*2) + hexBuffer[endIdx:]
		}
		var crclen uint
		var crc uint16
		if sym.size > 32 {
			idx := 64
			buflen := len(hexBuffer)
			for idx < buflen && hexBuffer[idx] != '.' && crclen < 255 {
				idx += 2
				crclen += 1
			}
			crc = crc16(sym.buf, 32, uint64(crclen))
		}
		buffer := fmt.Sprintf("%s %02X %04X %04X :00000000 %s %s\n", hexBuffer[:64], crclen, crc, sym.size, names, hexBuffer[64+(crclen*2):])
		outfile.WriteString(buffer)
	}
	outfile.WriteString("---\n")
}

func extractPackages(buildOutputFile string) map[string]string {
	fileContents, err := ioutil.ReadFile(buildOutputFile)
	if err != nil {
		log.Fatal(err)
	}

	re := regexp.MustCompile(`WORK=.*`)
	workDir := string(re.Find(fileContents))
	if len(workDir) == 0 {
		log.Fatal("Couldn't find WORK directory")
	}
	workDir = workDir[5:]

	re = regexp.MustCompile(`packagefile .*`)
	packageLinesBytes := re.FindAll(fileContents, -1)
	if packageLinesBytes == nil {
		log.Fatal("No packages found")
	}
	var packages map[string]string = make(map[string]string, 0)
	for _, packageLine := range packageLinesBytes {
		lineToks := strings.Split(string(packageLine[12:]), "=")
		packages[lineToks[0]] = strings.Replace(lineToks[1], "$WORK", workDir, 1)
	}
	return packages
}

func Usage() {
	fmt.Fprintf(os.Stderr, "usage: go2pat [options] build_output_file.txt\n")
	fmt.Fprintf(os.Stderr, "Flags:\n")
	flag.PrintDefaults()
	os.Exit(2)
}

func main() {
	packageSubsetRE := flag.String("p", ".*", "regexp to match specific package file import paths")
	flag.Parse()
	if flag.NArg() != 1 {
		Usage()
	}
	packages := extractPackages(flag.Arg(0))
	re := regexp.MustCompile(*packageSubsetRE)
	for importPath, path := range packages {
		if re.Match([]byte(importPath)) {
			processPackage(path, importPath)
		}
	}
}
