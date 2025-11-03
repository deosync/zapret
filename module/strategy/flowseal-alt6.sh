#!/bin/bash
# Zapret Configuration - general (ALT5)
# Converted from Windows winws.exe config

# Rule 1: UDP 443 для основного списка
config="echo: --filter-udp=443 --hostlist=$MODPATH/list/list-general.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 2: правило 2
config="$config --filter-udp=19294-19344,50000-50100 --filter-l7=discord,stun --dpi-desync=fake --dpi-desync-repeats=6 --new"

# Rule 3: правило 3
config="$config --filter-l3=ipv4 --filter-tcp=443,2053,2083,2087,2096,8443, --hostlist-exclude=$MODPATH/list/list-exclude.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=syndata,multidisorder --new"

# Rule 4: правило 4
config="$config --filter-udp=443 --ipset=$MODPATH/list/ipset-all.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 5: правило 5
config="$config --filter-udp= --ipset=$MODPATH/list/ipset-all.txt --ipset-exclude=$MODPATH/list/ipset-exclude.txt --dpi-desync=fake --dpi-desync-autottl=2 --dpi-desync-repeats=14 --dpi-desync-any-protocol=1 --dpi-desync-fake-unknown-udp=$MODPATH/fake/quic_initial_www_google_com.bin --dpi-desync-cutoff=n3 --new"

