CURRENT=`pwd`
NAME=`basename "$CURRENT"`
dir=/root/p4_16/open_src/
script_home=/root/bf-sde-9.2.0/
common_p4=${dir}/cmO6/p4src/common_p4

/p4_build.sh ${dir}/cmO6/p4src/p416_countmin_O6.p4 \
    -- P4_NAME="p416_countmin_O6" \
    P4FLAGS="--no-dead-code-elimination" \
    P4PPFLAGS="-I ${common_p4}"

