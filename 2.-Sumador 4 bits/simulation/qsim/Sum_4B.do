onerror {quit -f}
vlib work
vlog -work work Sum_4B.vo
vlog -work work Sum_4B.vt
vsim -novopt -c -t 1ps -L cycloneiii_ver -L altera_ver -L altera_mf_ver -L 220model_ver -L sgate work.Sum_4B_vlg_vec_tst
vcd file -direction Sum_4B.msim.vcd
vcd add -internal Sum_4B_vlg_vec_tst/*
vcd add -internal Sum_4B_vlg_vec_tst/i1/*
add wave /*
run -all
