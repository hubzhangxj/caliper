build_iperf() {
    set -e
    ./configure
    make
}

build_iperf
