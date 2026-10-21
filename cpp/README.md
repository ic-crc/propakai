[Français](./README.fr.md)

## Building the Dynamic Library Files

Dynamic library files for Windows (.dll), Linux (.so), and macOS (.dylib) are already included in
the Python wheels available in the [Releases page](https://github.com/mplussier/itupropag-sandbox/releases).

If you prefer, you can rebuild the libraries manually by following these steps.

### On Windows

On Windows the provided dlls are currently compiled using [MSYS2](https://www.msys2.org/). After
completing the install instructions from MSYS2's website, install the following toolset from the
MSYS2 UCRT64 command prompt:
```
pacman -S mingw-w64-ucrt-x86_64-toolchain
```

Optionally, open a Windows command prompt as Administrator and create a symbolic link for the `make`
tool using the following (_adjust directories to have them correspond to your installation_):
```
mklink C:\msys64\ucrt64\bin\make.exe C:\msys64\ucrt64\bin\mingw32-make.exe
```

From the MSYS2 UCRT64 command prompt, use the `make` or `mingw32-make` command from one of the
directories containing a Makefile in order to build the corresponding DLL(s):
```
# if you created the symbolink link in the previous step
make rebuild

# otherwise
mingw32-make rebuild
```
Library files are copied to the `propakai/bin` directory (relative to the repository root)
automatically as part of the build.

Note: The steps above are for x86_64 (64-bit Intel/AMD) Windows. On ARM64 Windows, you can build
the DLLs in a similar way using `clang++` from the MSYS2 CLANGARM64 environment to produce native
ARM64 binaries.

Note: Make sure to [update your MSYS2 installation](https://www.msys2.org/docs/updating/) from time
to time by running the `pacman -Suy` command **twice** from the MSYS2 MSYS command prompt.


### On Linux and macOS

On Linux and macOS, you can use the standard command-line toolchain (GNU Toolchain on Linux,
Apple’s Xcode command-line tools on macOS) for the build process.

Note: On macOS, make sure the Xcode command-line tools are installed. If not, run:
`xcode-select --install`.

Use the `make` command from one of the directories containing a Makefile to build the corresponding
dynamic library file(s) (.so on Linux, .dylib on macOS):
```
make rebuild
```
Library files are also copied to the `propakai/bin` directory (relative to the repository root)
automatically as part of the build.

### Alternate Build Procedure (Windows, Linux and macOS)

The dynamic library files (.dll, .so, .dylib) may also be built using
[Zig](https://ziglang.org/download/) (version 0.16.0 or later), which supports cross-compilation to
multiple platforms from a single host machine.

Once Zig is installed, run the following command from one of the directories containing a
`build.zig` file:
```
zig build
```
Library files are also copied to the `propakai/bin` directory (relative to the repository root)
automatically as part of the build.

Note: All target platforms are built by default regardless of the host operating system. No
additional SDKs or toolchains are required.