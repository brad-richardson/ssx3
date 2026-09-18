#!/system/bin/sh
# odin_sampler.sh PID ERRFILE OUTFILE NTICKS INTERVAL
# On-device scheduler/placement/clock sampler (D1; extends aff-sampler.sh).
# One tick per INTERVAL seconds: wall clock, process + per-thread CPU times,
# device cpu line, ps thread table, latest metrics sample= line (maps ticks
# to m-time), plus per tick: scaling_cur_freq for cpu0..cpu7, thermal zones
# whose type starts with cpu-, gpuss, or skin (type + temp), and the Adreno
# gpuclk. Existing per-thread CPU and PSR columns are unchanged.
PID=$1; ERRF=$2; OUT=$3; N=$4; IV=$5
{
echo "SAMPLER_START wall=$(date +%s.%N) pid=$PID"
echo "--- affinity"
taskset -a -p $PID
echo "--- cpuset"
cat /proc/$PID/cpuset
echo "--- procstart"
awk '{print $22}' /proc/$PID/stat
i=0
while [ $i -lt $N ]; do
  if [ ! -d /proc/$PID ]; then echo "EXITED wall=$(date +%s.%N) tick=$i"; break; fi
  echo "=== TICK wall=$(date +%s.%N) i=$i"
  echo "--- procstat"
  cat /proc/$PID/stat
  echo "--- cpustat"
  head -1 /proc/stat
  echo "--- metric"
  grep -o 'sample=[0-9]*' $ERRF 2>/dev/null | tail -1
  echo "--- threads"
  for d in /proc/$PID/task/*; do
    t=${d##*/}
    c=$(cat $d/comm 2>/dev/null | tr ' \t' '__')
    s=$(sed 's/.*) //' $d/stat 2>/dev/null | awk '{print $12, $13, $16, $17, $37}')
    echo "$t $c $s"
  done
  echo "--- ps"
  ps -T -p $PID -o TID,PSR,PRI,NI,SCH,RTPRIO,PCY,TIME+,CMD 2>/dev/null
  echo "--- cpufreq"
  c=0
  while [ $c -le 7 ]; do
    echo "cpu$c $(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_cur_freq 2>/dev/null)"
    c=$((c+1))
  done
  echo "--- thermal"
  for z in /sys/class/thermal/thermal_zone*; do
    t=$(cat $z/type 2>/dev/null)
    case "$t" in
      cpu-*|gpuss*|skin*)
        echo "$t $(cat $z/temp 2>/dev/null)"
        ;;
    esac
  done
  echo "--- gpuclk"
  cat /sys/class/kgsl/kgsl-3d0/gpuclk 2>/dev/null
  if [ $i -eq 0 ]; then
    echo "--- chrt"
    for d in /proc/$PID/task/*; do
      t=${d##*/}
      echo -n "$t: "
      chrt -p $t 2>&1 | tr '\n' ';'
      echo
    done
  fi
  i=$((i+1))
  sleep $IV
done
echo "SAMPLER_END wall=$(date +%s.%N)"
} >> $OUT 2>&1
