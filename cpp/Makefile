# Build/rebuild all libraries

.PHONY: default clean build rebuild

default: build

clean:
	$(MAKE) clean -C propakai_cpp
	$(MAKE) clean -C ntia_p528_5
	$(MAKE) clean -C ntia_p368_10

build:
	$(MAKE) -C propakai_cpp
	$(MAKE) -C ntia_p528_5
	$(MAKE) -C ntia_p368_10

rebuild: clean build
