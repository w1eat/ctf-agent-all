# GO2PAT

go2pat is a FLAIR tool that processes go object files to create PAT files.

Its purpose is to make it easy to build FLIRT signatures of the golang
runtime (or any other package, really) for any existing platform/system,
so as to make reversing of golang binaries significantly faster
(since golang programs are statically compiled, and therefore tend
to bring in a fairly large amount of the runtime, which is usually
of no interest to the reverser.)

Due to the fact that go2pat is strongly tied to the system/architecture
on which it will run and for which it will produce patterns, go2pat has
to be built for the environment it will process.

## INSTALLATION & BUILDING
go2pat currently relies on a few packages (goobj, objabi, objfile,
 archive) that are internal to the golang toolchain.
This unfortunately forces us to include go2pat into the golang toolchain
in order to compile it.

 1. clone the golang repository

  `$ git clone https://go.googlesource.com/go goroot`

 2. switch to a release branch

  `$ cd goroot`
  `$ git checkout go1.15.6`

 3. copy necessary go2pat source files into toolchain

  `$ mkdir src/cmd/go2pat`
  `$ cp $GO2PATSRC/*.go src/cmd/go2pat/`

 4. build the go toolchain

  `$ cd src`
  `$ ./make.bash`

 5. install go2pat
  
  `$ ./bin/go install ./src/cmd/go2pat`


`$GO2PATSRC`: the go2pat code is split into multiple files
  - a backend file which implements the logic to extract the symbols
  from a go object file.
    the go2pat sources already contain:
      backend0.go which handles go1.10 - go1.13
      backend1.go which handles go1.14 - go1.15
      backend2.go which handles go1.16 - go1.20

  - go2pat.go which takes the input parameters and calls the backend
  to then format the product into pattern files

## EXAMPLE USAGE
1. generate a .go file containing all ImportPaths of the standard library packages
```
$ ./gen_std_packages.sh  ~/goroot/bin/go
wrote to imports.go
```

2. *build packages and redirect compiler commands to a log file*
`$ ~/goroot/bin/go build -work -x -a imports.go 2> build_log.txt`

3. *run go2pat on the build log*
```
$ ~/goroot/bin/go tool go2pat build_log.txt
wrote to path.pat
wrote to encoding_pem.pat
wrote to net_http_internal_ascii.pat
wrote to internal_poll.pat
wrote to encoding_base64.pat
wrote to context.pat
(...)
```
("[-p regexp]" flag can be used to specify which packages to process)

4. a signature file can be generated from the pattern file via sigmake
`$ sigmake *.pat go_std.sig`

## Notate Bene
* To generate packages/binaries for other architectures and OS'es,
 use the GOOS={linux/windows/darwin/...} and GOARCH={amd64/386/arm/...}
 environment variables (see https://golang.org/doc/install/source for full list)

* To rebuild only the go2pat tool (e.g. when making changes to it) in the go toolchain use
  `~/goroot/src$ ~/goroot/bin/go install cmd/internal/go2pat`
