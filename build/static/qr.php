<?php
# SPDX-FileCopyrightText: 2026 Kuckuck Werners Berg Project
# SPDX-License-Identifier: GPL-3.0-or-later
date_default_timezone_set('Europe/Berlin');

$s = $_GET['s'] ?? '';
if (!is_string($s) || !ctype_digit($s) || (int)$s > 18) {
    http_response_code(404);
    exit;
}
$s = (int)$s;

# Best-effort anonymous metrics: date + hour + station, nothing else.
$fp = @fopen(__DIR__ . '/metrics/.ht-qr-redirect-metrics.log', 'a');
if ($fp) {
    if (@flock($fp, LOCK_EX)) {
        @fwrite($fp, date('Y-m-d H') . "\t" . $s . "\n");
        @flock($fp, LOCK_UN);
    }
    @fclose($fp);
}

# Single remapping point if the page structure ever changes.
$target = $s === 0 ? '/kwb/index.html' : '/kwb/station/' . sprintf('%02d', $s) . '.html';
header('Location: ' . $target, true, 302);