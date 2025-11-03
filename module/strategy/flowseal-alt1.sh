#!/bin/bash
# Zapret Configuration - general (ALT)
# Converted from Windows winws.exe config

# Rule 1: UDP 443 для основного списка
config="echo: --filter-udp=443 --hostlist=%LISTS%list-general.txt --hostlist-exclude=%LISTS%list-exclude.txt --ipset-exclude=%LISTS%ipset-exclude.txt --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 2: UDP 19294-19344,50000-50100 для Discord/STUN
config="$config --filter-udp=19294-19344,50000-50100 --filter-l7=discord,stun --dpi-desync=fake --dpi-desync-repeats=6 --new"

# Rule 3: TCP 2053,2083,2087,2096,8443 для Discord media
config="$config --filter-tcp=2053,2083,2087,2096,8443 --hostlist-domains=discord.media --dpi-desync=fake,fakedsplit --dpi-desync-repeats=6 --dpi-desync-fooling=ts --dpi-desync-fakedsplit-pattern=0x00 --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_www_google_com.bin --new"

# Rule 4: TCP 443 для Google списка
config="$config --filter-tcp=443 --hostlist=%LISTS%list-google.txt --ip-id=zero --dpi-desync=fake,fakedsplit --dpi-desync-repeats=6 --dpi-desync-fooling=ts --dpi-desync-fakedsplit-pattern=0x00 --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_www_google_com.bin --new"

# Rule 5: TCP 80,443 для основного списка
config="$config --filter-tcp=80,443 --hostlist=%LISTS%list-general.txt --hostlist-exclude=%LISTS%list-exclude.txt --ipset-exclude=%LISTS%ipset-exclude.txt --dpi-desync=fake,fakedsplit --dpi-desync-repeats=6 --dpi-desync-fooling=ts --dpi-desync-fakedsplit-pattern=0x00 --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_www_google_com.bin --new"

# Rule 6: UDP 443 для ipset-all
config="$config --filter-udp=443 --ipset=%LISTS%ipset-all.txt --hostlist-exclude=%LISTS%list-exclude.txt --ipset-exclude=%LISTS%ipset-exclude.txt --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 7: TCP 80,443 для ipset-all
config="$config --filter-tcp=80,443, --ipset=%LISTS%ipset-all.txt --hostlist-exclude=%LISTS%list-exclude.txt --ipset-exclude=%LISTS%ipset-exclude.txt --dpi-desync=fake,fakedsplit --dpi-desync-repeats=6 --dpi-desync-fooling=ts --dpi-desync-fakedsplit-pattern=0x00 --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_www_google_com.bin --new"

# Rule 8: UDP для ipset-all (catch-all)
config="$config --filter-udp= --ipset=%LISTS%ipset-all.txt --ipset-exclude=%LISTS%ipset-exclude.txt --dpi-desync=fake --dpi-desync-autottl=2 --dpi-desync-repeats=12 --dpi-desync-any-protocol=1 --dpi-desync-fake-unknown-udp=$MODPATH/fake/quic_initial_www_google_com.bin --dpi-desync-cutoff=n3 --new"

