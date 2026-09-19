# SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
# SPDX-License-Identifier: GPL-3.0-or-later

.PHONY: all clean html run sync analyze qrcodes

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
	cp build/static/.htaccess html/.htaccess
	cp build/static/qr.php html/qr.php
	mkdir -p html/metrics
	cp build/static/metrics/.htaccess html/metrics/.htaccess
	vogel_file=$$(ls vogel/ 2>/dev/null | head -1); \
	if [ -n "$$vogel_file" ]; then cp vogel/*.png html/assets/img/vogel/; fi
	@echo "Build complete: html/"

clean:
	rm -rf html
	rm -f qrcodes/*.svg qrcodes/*.pdf
	@echo "Cleaned: html/ and regenerable qrcodes/ artifacts"

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

sync: html
	@command -v rclone >/dev/null 2>&1 || { echo "Error: rclone is not installed. See https://rclone.org/install/"; exit 1; }
	@rclone listremotes | grep -q '^kwb:$$' || { echo "Error: rclone remote 'kwb:' is not configured. See 'rclone config'."; exit 1; }
	rclone sync ./html/ kwb: --progress --exclude "/metrics/.ht-qr-redirect-metrics.log"
	mkdir -p metrics
	rclone copyto kwb:metrics/.ht-qr-redirect-metrics.log metrics/.ht-qr-redirect-metrics.log || echo "Note: no metrics data on the server yet (first deployment?)"
	@echo "Sync complete."

analyze:
	python3 metrics/analyze_metrics.py

qrcodes:
	@for n in $$(seq 0 18); do \
	  num=$$(printf '%02d' $$n); \
	  echo "Generating $$num ..."; \
	  python3 qrcodes/create_qr_codes.py \
	    --url "https://wernersberg.de/kwb/$$n" \
	    --logo logos/Kombiniert_vector_color.svg \
	    --output qrcodes/$$num.svg || exit 1; \
	  done
	@echo "QR codes generated in qrcodes/ (SVG artwork + CMYK print PDF)"
