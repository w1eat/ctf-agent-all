ifdef __ARM__
  ifdef __PAC__
    ARCH = arm64e
  else
    ARCH = arm64
  endif
  MACOSVER = 11.0
else
  ARCH = x86_64
  MACOSVER = 10.12
endif

BINDIR = bin/$(ARCH)/

ifeq ($(wildcard $(BINDIR)/.),)
  $(shell mkdir -p 2>/dev/null $(BINDIR))
endif

CFLAGS = -arch $(ARCH) -mmacosx-version-min=$(MACOSVER) -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk


TARGETS = helloworld getaddrinfo bluetooth
all: $(TARGETS)
.PHONY: all clean $(TARGETS)

HELLOWORLD  = $(BINDIR)helloworld
GETADDRINFO = $(BINDIR)getaddrinfo
BLUETOOTH   = $(BINDIR)bluetooth

helloworld:  $(HELLOWORLD)
getaddrinfo: $(GETADDRINFO)
bluetooth:   $(BLUETOOTH)

$(HELLOWORLD): helloworld.c
	clang $(CFLAGS) -o $@ $<
$(GETADDRINFO): getaddrinfo.c
	clang $(CFLAGS) -o $@ $<
$(BLUETOOTH): bluetooth.m
	clang $(CFLAGS) -x objective-c -o $@ $< -lobjc -framework Foundation -framework IOBluetooth

clean:
	rm -rf bin
