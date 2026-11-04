/*
 * Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
 * Industry through the Communications Research Centre Canada.
 * 
 * Licensed under the MIT License
 * See LICENSE file in the project root for full license text.
 */

#include "API_Config.h"
#include "DigitalMap.h"


void SetDigitalMapsBaseDirectory(const char* baseDir)
{
    ExecuteSafelyVoid([&]() {
        DigitalMap::SetBaseDirectory(baseDir);
	});
}
