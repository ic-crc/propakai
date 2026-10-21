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