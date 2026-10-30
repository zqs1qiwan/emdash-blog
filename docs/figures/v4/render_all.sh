#!/bin/bash
CHROME=/opt/hermes/tools/chromium-1208/chrome-linux64/chrome
for spec in "w44-f5 1000" "w44-f6 1000" "w44-cover 1200" "id-f1 1000" "id-f2 1000" "id-f3 1000" "id-f4 1000" "id-f5 1000" "id-cover 1200"; do
  set -- $spec
  $CHROME --headless=new --disable-gpu --no-sandbox --hide-scrollbars --force-device-scale-factor=2 \
    --window-size=1600,$2 --screenshot=$1.png "file:///opt/data/news/figures/v4/$1.html" >/dev/null 2>&1
  echo "done $1 $2 $(stat -c%s $1.png)"
done
echo ALL_DONE
