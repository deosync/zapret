MODPATH=/data/adb/modules/zapret

CURRENTSTRATEGY=$(cat $MODPATH/config/current-strategy)
. "$MODPATH/strategy/$CURRENTSTRATEGY.sh"

# Парсинг портов из переменной config
tcp_ports="$(echo $config | grep -oE '\-\-filter-tcp=[0-9,\-]+' | sed -e 's/.*=//g' | tr ',' '\n' | sort -u | tr '\n' ',' | sed 's/,$//')";
udp_ports="$(echo $config | grep -oE '\-\-filter-udp=[0-9,\-]+' | sed -e 's/.*=//g' | tr ',' '\n' | sort -u | tr '\n' ',' | sed 's/,$//')";

iptAdd() {
    iptDPort="$iMportD $2"; iptSPort="$iMportS $2";
    iptables -t mangle -I POSTROUTING -p $1 $iptDPort $iCBo $iMark -j NFQUEUE --queue-num 200 --queue-bypass
    iptables -t mangle -I PREROUTING -p $1 $iptSPort $iCBr $iMark -j NFQUEUE --queue-num 200 --queue-bypass
}

ip6tAdd() {
    ip6tDPort="$i6MportD $2"; ip6tSPort="$i6MportS $2";
    ip6tables -t mangle -I POSTROUTING -p $1 $ip6tDPort $i6CBo $i6Mark -j NFQUEUE --queue-num 200 --queue-bypass
    ip6tables -t mangle -I PREROUTING -p $1 $ip6tSPort $i6CBr $i6Mark -j NFQUEUE --queue-num 200 --queue-bypass
}

addMultiPort() {
    for current_port in $(echo "$2" | tr ',' ' '); do
        if [[ $current_port == *-* ]]; then
            # Диапазон портов (например, 1024-65535)
            start_port="${current_port%-*}"
            end_port="${current_port#*-}"
            
            # IPv4
            iptables -t mangle -I POSTROUTING -p $1 --dport $start_port:$end_port $iCBo $iMark -j NFQUEUE --queue-num 200 --queue-bypass
            iptables -t mangle -I PREROUTING -p $1 --sport $start_port:$end_port $iCBr $iMark -j NFQUEUE --queue-num 200 --queue-bypass
            
            # IPv6 (Исправлено)
            ip6tables -t mangle -I POSTROUTING -p $1 --dport $start_port:$end_port $i6CBo $i6Mark -j NFQUEUE --queue-num 200 --queue-bypass
            ip6tables -t mangle -I PREROUTING -p $1 --sport $start_port:$end_port $i6CBr $i6Mark -j NFQUEUE --queue-num 200 --queue-bypass
        else
            # Одиночные порты
            iptAdd "$1" "$current_port";
            ip6tAdd "$1" "$current_port";
        fi
    done
}

if [ "$(cat /proc/net/ip_tables_targets | grep -c 'NFQUEUE')" == "0" ]; then
    echo "iptables is bad!"
    exit
fi
if [ "$(cat /proc/net/ip6_tables_targets | grep -c 'NFQUEUE')" == "0" ]; then
    echo "ip6tables is bad!"
    exit
fi

# Проверка поддержки multiport
if [ "$(cat /proc/net/ip_tables_matches | grep -c 'multiport')" != "0" ]; then
    iMportS="-m multiport --sports"
    iMportD="-m multiport --dports"
else
    iMportS="--sport"
    iMportD="--dport"
fi
if [ "$(cat /proc/net/ip6_tables_matches | grep -c 'multiport')" != "0" ]; then
    i6MportS="-m multiport --sports"
    i6MportD="-m multiport --dports"
else
    i6MportS="--sport"
    i6MportD="--dport"
fi

# Очистка старых правил connbytes и настройка переменных
if iptables -t mangle -A POSTROUTING -p tcp -m connbytes --connbytes-dir=original --connbytes-mode=packets --connbytes 1:12 -j ACCEPT 2>/dev/null; then
    iptables -t mangle -D POSTROUTING -p tcp -m connbytes --connbytes-dir=original --connbytes-mode=packets --connbytes 1:12 -j ACCEPT 2>/dev/null
    
    cbOrig="-m connbytes --connbytes-dir=original --connbytes-mode=packets --connbytes 1:12"
    cbReply="-m connbytes --connbytes-dir=reply --connbytes-mode=packets --connbytes 1:6"
else
    cbOrig=""
    cbReply=""
fi

if [ "$(cat /proc/net/ip_tables_matches | grep -c 'connbytes')" != "0" ]; then
    iCBo="$cbOrig"
    iCBr="$cbReply"
else
    iCBo=""
    iCBr=""
fi

# Настройка Mark
if [ "$(cat /proc/net/ip_tables_matches | grep -c 'mark')" != "0" ]; then
    iMark="-m mark ! --mark 0x40000000/0x40000000"
else
    iMark=""
fi
if [ "$(cat /proc/net/ip6_tables_matches | grep -c 'mark')" != "0" ]; then
    i6Mark="-m mark ! --mark 0x40000000/0x40000000"
else
    i6Mark=""
fi

# Применение правил
addMultiPort "tcp" "$tcp_ports";
addMultiPort "udp" "$udp_ports";

# Запуск демона
while true; do
    if ! pgrep -x "nfqws" > /dev/null; then
            . "$MODPATH/zapret/make-unkillable.sh" &
            # Важно: $config не в кавычках, чтобы аргументы распарсились
            "$MODPATH/zapret/nfqws" --uid=0:0 --bind-fix4 --bind-fix6 --qnum=200 $config
    fi
    sleep 5
done
