#!/bin/bash
# Zapret Configuration - general (ALT3).bat
# Converted from Windows winws.exe config

# Rule 1
config="echo: --filter-udp=443 --hostlist=$MODPATH/list/list-general.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 2
config="$config --filter-udp=19294-19344,50000-50100 --filter-l7=discord,stun --dpi-desync=fake --dpi-desync-repeats=6 --new"

# Rule 3
config="$config --filter-tcp=2053,2083,2087,2096,8443 --hostlist-domains=discord.media --dpi-desync=fakedsplit --dpi-desync-split-pos=1 --dpi-desync-autottl=--dpi-desync-fooling=badseq --dpi-desync-repeats=8 --new"

# Rule 4
config="$config --filter-tcp=443 --hostlist=$MODPATH/list/list-google.txt --ip-id=zero --dpi-desync=fakedsplit --dpi-desync-split-pos=1 --dpi-desync-autottl=--dpi-desync-fooling=badseq --dpi-desync-repeats=8 --new"

# Rule 5
config="$config --filter-tcp=80,443 --hostlist=$MODPATH/list/list-general.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=fakedsplit --dpi-desync-split-pos=1 --dpi-desync-autottl=--dpi-desync-fooling=badseq --dpi-desync-repeats=8 --new"

# Rule 6
config="$config --filter-udp=443 --ipset=$MODPATH/list/ipset-all.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 7
config="$config --filter-tcp=80,443, --ipset=$MODPATH/list/ipset-all.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=fakedsplit --dpi-desync-split-pos=1 --dpi-desync-autottl=--dpi-desync-fooling=badseq --dpi-desync-repeats=8 --new"

# Rule 8
config="$config --filter-udp= --ipset=$MODPATH/list/ipset-all.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=fake --dpi-desync-autottl=2 --dpi-desync-repeats=10 --dpi-desync-any-protocol=1 --dpi-desync-fake-unknown-udp=$MODPATH/fake/quic_initial_www_google_com.bin --dpi-desync-cutoff=n2 --new"

