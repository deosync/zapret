#!/bin/bash
# Zapret Configuration - general (ALT11)
# Converted from Windows winws.exe config

# Rule 1: UDP 443 для основного списка
config="--filter-udp=443 --hostlist=$MODPATH/list/list-general.txt --hostlist=$MODPATH/list/list-general-user.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --hostlist-exclude=$MODPATH/list/list-exclude-user.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake --dpi-desync-repeats=11 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 2: UDP 19294-19344,50000-50100 для Discord/STUN
config="$config --filter-udp=19294-19344,50000-50100 --filter-l7=discord,stun --dpi-desync=fake --dpi-desync-fake-discord=$MODPATH/fake/quic_initial_dbankcloud_ru.bin --dpi-desync-fake-stun=$MODPATH/fake/quic_initial_dbankcloud_ru.bin --dpi-desync-repeats=6 --new"

# Rule 3: TCP 2053,2083,2087,2096,8443 для Discord media
config="$config --filter-tcp=2053,2083,2087,2096,8443 --hostlist-domains=discord.media --dpi-desync=fake,multisplit --dpi-desync-split-seqovl=681 --dpi-desync-split-pos=1 --dpi-desync-fooling=ts --dpi-desync-repeats=8 --dpi-desync-split-seqovl-pattern=$MODPATH/fake/tls_clienthello_www_google_com.bin --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_www_google_com.bin --new"

# Rule 4: TCP 443 для Google списка
config="$config --filter-tcp=443 --hostlist=$MODPATH/list/list-google.txt --ip-id=zero --dpi-desync=fake,multisplit --dpi-desync-split-seqovl=681 --dpi-desync-split-pos=1 --dpi-desync-fooling=ts --dpi-desync-repeats=8 --dpi-desync-split-seqovl-pattern=$MODPATH/fake/tls_clienthello_www_google_com.bin --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_www_google_com.bin --new"

# Rule 5: TCP 80,443 для основного списка
config="$config --filter-tcp=80,443 --hostlist=$MODPATH/list/list-general.txt --hostlist=$MODPATH/list/list-general-user.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --hostlist-exclude=$MODPATH/list/list-exclude-user.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake,multisplit --dpi-desync-split-seqovl=664 --dpi-desync-split-pos=1 --dpi-desync-fooling=ts --dpi-desync-repeats=8 --dpi-desync-split-seqovl-pattern=$MODPATH/fake/tls_clienthello_max_ru.bin --dpi-desync-fake-tls=$MODPATH/fake/stun.bin --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_max_ru.bin --dpi-desync-fake-http=$MODPATH/fake/tls_clienthello_max_ru.bin --new"

# Rule 6: UDP 443 для ipset-all
config="$config --filter-udp=443 --ipset=$MODPATH/ipset/ipset-all.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --hostlist-exclude=$MODPATH/list/list-exclude-user.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake --dpi-desync-repeats=11 --dpi-desync-fake-quic=$MODPATH/fake/quic_initial_www_google_com.bin --new"

# Rule 7: TCP 80,443,1024-65535 для ipset-all
config="$config --filter-tcp=80,443,8443 --ipset=$MODPATH/ipset/ipset-all.txt --hostlist-exclude=$MODPATH/list/list-exclude.txt --hostlist-exclude=$MODPATH/list/list-exclude-user.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake,multisplit --dpi-desync-split-seqovl=664 --dpi-desync-split-pos=1 --dpi-desync-fooling=ts --dpi-desync-repeats=8 --dpi-desync-split-seqovl-pattern=$MODPATH/fake/tls_clienthello_max_ru.bin --dpi-desync-fake-tls=$MODPATH/fake/stun.bin --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_max_ru.bin --dpi-desync-fake-http=$MODPATH/fake/tls_clienthello_max_ru.bin --new"

# Rule 8: UDP 1024-65535 для ipset-all (catch-all)
config="$config --filter-tcp=%GameFilterTCP% --ipset=$MODPATH/ipset/ipset-all.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake,multisplit --dpi-desync-any-protocol=1 --dpi-desync-cutoff=n4 --dpi-desync-split-seqovl=664 --dpi-desync-split-pos=1 --dpi-desync-fooling=ts --dpi-desync-repeats=8 --dpi-desync-split-seqovl-pattern=$MODPATH/fake/tls_clienthello_max_ru.bin --dpi-desync-fake-tls=$MODPATH/fake/stun.bin --dpi-desync-fake-tls=$MODPATH/fake/tls_clienthello_max_ru.bin --dpi-desync-fake-http=$MODPATH/fake/tls_clienthello_max_ru.bin --new"

# Rule 9: Правило 9
config="$config --filter-udp=%GameFilterUDP% --ipset=$MODPATH/ipset/ipset-all.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude.txt --ipset-exclude=$MODPATH/ipset/ipset-exclude-user.txt --dpi-desync=fake --dpi-desync-repeats=10 --dpi-desync-any-protocol=1 --dpi-desync-fake-unknown-udp=$MODPATH/fake/quic_initial_dbankcloud_ru.bin --dpi-desync-cutoff=n4"
