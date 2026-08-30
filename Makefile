# SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
# SPDX-License-Identifier: GPL-3.0-or-later

.PHONY: all clean html convert

all: html

convert:
	python3 build/convert_stations.py

html: clean convert
	python3 build/generate.py
	mkdir -p html/assets/css html/assets/js html/assets/img/vogel
	cp build/static/css/main.css html/assets/css/
	cp build/static/js/birdgame.js html/assets/js/
	cp logos/Fuchs_small.png html/assets/img/
	cp logos/Eichhoernchen_small.png html/assets/img/
	cp logos/Kuckuck_small.png html/assets/img/
	cp logos/Kombiniert_small.png html/assets/img/
	vogel_file=$$(ls vogel/ 2>/dev/null | head -1); \
	if [ -n "$$vogel_file" ]; then cp vogel/*.png html/assets/img/vogel/; fi
	@echo "Build complete: html/"

clean:
	rm -rf html/*
	@echo "Cleaned: html/"