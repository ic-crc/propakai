/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#pragma once

#if defined _WIN32 || defined __CYGWIN__
	// This logic is for Windows and Windows-like environments (Cygwin, MinGW)
	#ifdef BUILDING_PROPAKAI // This should be defined by the library's build system
		#ifdef __GNUC__
			// Using GCC on Windows/Cygwin
			#define PROPAKAI_API __attribute__ ((dllexport))
		#else
			// Using MSVC or other Windows compilers
			#define PROPAKAI_API __declspec(dllexport)
		#endif
	#else
		#ifdef __GNUC__
			// Using GCC on Windows/Cygwin
			#define PROPAKAI_API __attribute__ ((dllimport))
		#else
			// Using MSVC or other Windows compilers
			#define PROPAKAI_API __declspec(dllimport)
		#endif
	#endif
#else
	// This logic is for non-Windows platforms (Linux, macOS, etc.)
	#if __GNUC__ >= 4
		#define PROPAKAI_API __attribute__ ((visibility ("default")))
	#else
		#define PROPAKAI_API
	#endif
#endif


#ifndef __cplusplus
#include <stdbool.h> // for 'bool' in C
#endif


// ============================================================================
// Internal Helper Templates (Only visible when compiling the library itself)
// Use them to avoid letting any exception escape the dll/so/dylib boundaries.
// ============================================================================
#if defined(__cplusplus) && defined(BUILDING_PROPAKAI)

#include <iostream>
#include <limits>
#include <exception>

// Clean, short alias for quiet_NaN
constexpr double NaN = std::numeric_limits<double>::quiet_NaN();

// 1. Default version: defaults to returning NaN (double), 
//    unless you pass something else like -1 (int) or false (bool).
template <typename Func, typename FallbackType = double>
FallbackType ExecuteSafely(Func&& calculation, FallbackType fallbackValue = NaN) noexcept 
{
    try {
        return calculation();
    }
    catch (const std::exception& e) {
        std::cerr << "[PropaKai (DSO) Error] " << e.what() << '\n';
        return fallbackValue;
    }
    catch (...) {
        std::cerr << "[PropaKai (DSO) Error] Unknown internal exception.\n";
        return fallbackValue;
    }
}

// 2. For void functions
template <typename Func>
void ExecuteSafelyVoid(Func&& calculation) noexcept 
{
    try {
        calculation();
    }
    catch (const std::exception& e) {
        std::cerr << "[PropaKai (DSO) Error] " << e.what() << '\n';
    }
    catch (...) {
        std::cerr << "[PropaKai (DSO) Error] Unknown internal exception.\n";
    }
}

#endif // defined(__cplusplus) && defined(BUILDING_PROPAKAI)
