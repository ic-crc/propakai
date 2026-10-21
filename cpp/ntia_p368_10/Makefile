# Configuration: release or debug
CONFIG ?= release

CXX = g++
CXXFLAGS = -std=c++17 -fPIC -Iinclude -DLIBRARY_NAME=\"LFMF\" -DLIBRARY_VERSION=\"1.1\"
#CXXFLAGS += -Wall

ifeq ($(CONFIG), debug)
	CXXFLAGS += -g
	OUT_DIR = build/debug
else
	CXXFLAGS += -O2
	OUT_DIR = build/release
endif

ARCH_RAW = $(shell uname -m)
ifeq ($(MSYSTEM),)
    # Not in MSYS2, use uname output directly
    ifeq ($(filter-out x86_64 amd64 AMD64,$(ARCH_RAW)),)
        ARCH_DIR = x86_64
    else ifeq ($(filter-out aarch64 arm64 ARM64,$(ARCH_RAW)),)
        ARCH_DIR = arm64
    else
        ARCH_DIR = $(ARCH_RAW)
    endif
else
    # Inside MSYS2, use MSYSTEM to reflect the arch of the lib being built.
    # On ARM64 Windows, MSYS2 is a 64-bit x86 application running under
    # emulation, and uname's output within MSYS2 is 'x86_64'.
	ifeq ($(filter-out UCRT64 MINGW64 CLANG64,$(MSYSTEM)),)
        ARCH_DIR = x86_64
    else ifeq ($(MSYSTEM),CLANGARM64)
        ARCH_DIR = arm64
    else
        ARCH_DIR = $(ARCH_RAW)
    endif
endif

ifeq ($(OS),Windows_NT)
	LDFLAGS = -shared -static -static-libgcc -static-libstdc++
	DYN_LIB_PATHNAME = $(OUT_DIR)/p368_10.dll
	OS_DIR = win
else
    UNAME_S = $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
		CXXFLAGS += -arch x86_64 -arch arm64
        LDFLAGS = -arch x86_64 -arch arm64 -dynamiclib
		DYN_LIB_PATHNAME = $(OUT_DIR)/p368_10.dylib
		ARCH_DIR = universal
		OS_DIR = macos
	else
		LDFLAGS = -shared
		DYN_LIB_PATHNAME = $(OUT_DIR)/p368_10.so
		OS_DIR = linux
	endif
endif


SRC_DIR = src
SRCS = $(wildcard $(SRC_DIR)/*.cpp)
OBJS = $(addprefix $(OUT_DIR)/, $(notdir $(SRCS:.cpp=.o)))


default: build

build: prep $(DYN_LIB_PATHNAME) copyfiles

$(DYN_LIB_PATHNAME): $(OBJS)
	$(CXX) $(LDFLAGS) -o $(DYN_LIB_PATHNAME) $^
ifeq ($(CONFIG),release)
  ifeq ($(OS),Windows_NT)
	strip --strip-unneeded $(DYN_LIB_PATHNAME)
  endif
endif

$(OUT_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) -c $(CXXFLAGS) -o $@ $<

prep:
	mkdir -p $(OUT_DIR)

rebuild: clean build

clean:
	@rm -rf build

copyfiles:
	mkdir -p ../../propakai/bin/$(OS_DIR)/$(ARCH_DIR)/
	cp -f $(DYN_LIB_PATHNAME) ../../propakai/bin/$(OS_DIR)/$(ARCH_DIR)/
