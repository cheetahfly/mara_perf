#!/bin/bash
# Download remaining marathon results using curl (direct GitHub)

BASE="https://raw.githubusercontent.com/AndrewMillerOnline/marathon-results/master"
OUT="data/raw/marathon_results"

mkdir -p "$OUT/Berlin" "$OUT/Chicago" "$OUT/Honolulu" "$OUT/Portland"

# Berlin missing: 2003-2019 (2003 already failed, try 2005+)
for year in 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019; do
    if [ ! -f "$OUT/Berlin/results-$year.csv" ]; then
        echo "Downloading Berlin $year..."
        curl -sL -o "$OUT/Berlin/results-$year.csv" "$BASE/Berlin/results-$year.csv" &
    fi
done

# Chicago: all years
for year in 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018; do
    if [ ! -f "$OUT/Chicago/results-$year.csv" ]; then
        echo "Downloading Chicago $year..."
        curl -sL -o "$OUT/Chicago/results-$year.csv" "$BASE/Chicago/results-$year.csv" &
    fi
done

# Honolulu
for year in 2015 2016 2017 2018 2019; do
    if [ ! -f "$OUT/Honolulu/results-$year.csv" ]; then
        echo "Downloading Honolulu $year..."
        curl -sL -o "$OUT/Honolulu/results-$year.csv" "$BASE/Honolulu/results-$year.csv" &
    fi
done

# Portland
for year in 2014 2015 2016 2017 2018 2019; do
    if [ ! -f "$OUT/Portland/results-$year.csv" ]; then
        echo "Downloading Portland $year..."
        curl -sL -o "$OUT/Portland/results-$year.csv" "$BASE/Portland/results-$year.csv" &
    fi
done

echo "All downloads started. Waiting..."
wait
echo "Done!"
