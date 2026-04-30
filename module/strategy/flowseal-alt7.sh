#!/bin/bash
# Zapret Configuration - general (ALT5)
# Converted from Windows winws.exe config

# Rule 1: UDP 443 для основного списка
config="--filter-udp=443 --hostlist=$MODPATH/list/list-general.txt --hostlist=$MODPATH/list/list-general-user.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --hostlist-exclude=$MODPATH/list/list-exclude-user.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 2: UDP 19294-19344,50000-50100 для Discord/STUN
config="$config --filter-udp=19294-19344,50000-50100 --filter-l7=discord,stun --dpi-desync=fake --dpi-desync-fake-discord=$MODPATH/fake/quic_initial_www_google_com.bin --dpi-desync-fake-stun=$MODPATH/fake/quic_initial_www_google_com.bin --dpi-desync-repeats=6 --new"

# Rule 3: TCP 2053,2083,2087,2096,8443 для Discord media
config="$config --filter-l3=ipv4 --filter-tcp=80,443,2053,2083,2087,2096,8443 --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=syndata,multidisorder --new"

# Rule 4: TCP 443 для Google списка
config="$config --filter-tcp=%GameFilterTCP% --ipset=$MODPATH/ipset/ipset-all.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=syndata,multidisorder --dpi-desync-any-protocol=1 --dpi-desync-cutoff=n4 --new"

# Rule 5: TCP 80,443 для основного списка
config="$config --filter-udp=443 --ipset=$MODPATH/ipset/ipset-all.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --hostlist-exclude=$MODPATH/list/list-exclude-user.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 6: UDP 443 для ipset-all
config="$config --filter-udp=443 --ipset=$MODPATH/ipset/ipset-all.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake --dpi-desync-repeats=14 --dpi-desync-any-protocol=1 --dpi-desync-fake-unknown-udp=$MODPATH/fake/quic_initial_dbankcloud_ru.bin --dpi-desync-cutoff=n3"
