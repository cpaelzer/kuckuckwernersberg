# SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
# SPDX-License-Identifier: GPL-3.0-or-later

.PHONY: all clean html run

all: html

html: clean
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

run: html
	@{ trap 'kill 0' EXIT; \
	   python3 -c "print('Watching station/, build/, vogel/, logos/ for changes...')"; \
	   while inotifywait -q -e modify,create,delete,move -r station/ build/ vogel/ logos/ --exclude '\.yaml\.bak' 2>/dev/null; do \
	     $(MAKE) -s html; \
	   done & \
	   WATCHER_PID=$$!; \
	   LOCAL_IP=$$(ip -4 route get 1 2>/dev/null | awk '{print $$7; exit}'); \
	   [ -z "$$LOCAL_IP" ] && LOCAL_IP="localhost"; \
	   echo ""; \
	   echo "============================================"; \
	   echo "  Serving at http://localhost:8080"; \
	   echo "  Local IP:   http://$$LOCAL_IP:8080"; \
	   echo "  Press Ctrl+C to stop"; \
	   echo "============================================"; \
	   echo ""; \
	   python3 -m http.server 8080 --directory html; \
	   kill $$WATCHER_PID 2>/dev/null; \
	 }
