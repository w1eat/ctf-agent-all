#!/bin/sh
if [ $# -eq 0 ]; then
  echo "usage: ./gen_std_packages.bash [PATH_TO_GO_BIN]/go"
  exit 1
fi
outfilename=imports.go
echo "package main" > $outfilename
echo "import (" >> $outfilename
$1 list -f '  "{{.ImportPath}}"' std >> $outfilename
echo ")" >> $outfilename
sed -i '/internal/d' $outfilename
sed -i '/vendor/d' $outfilename
echo "wrote to $outfilename"
