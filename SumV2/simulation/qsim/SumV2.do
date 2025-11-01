onerror {quit -f}
vlib work
vlog -work work SumV2.vo
vlog -work work SumV2.vt
vsim -novopt -c -t 1ps -L cycloneiii_ver -L altera_ver -L altera_mf_ver -L 220model_ver -L sgate work.SumV2_vlg_vec_tst
vcd file -direction SumV2.msim.vcd
vcd add -internal SumV2_vlg_vec_tst/*
vcd add -internal SumV2_vlg_vec_tst/i1/*
add wave /*
run -all
