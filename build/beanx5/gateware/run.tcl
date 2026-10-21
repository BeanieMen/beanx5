set_device -name GW5A-25A GW5A-LV25MG121NC1/I0
add_file minimal_beanx5.cst
add_file minimal_beanx5.sdc
add_file /home/aj/pythondata-cpu-vexriscv/pythondata_cpu_vexriscv/verilog/VexRiscv.v
add_file /home/aj/beanx5/build/beanx5/gateware/minimal_beanx5.v
set_option -use_sspi_as_gpio 1
set_option -use_cpu_as_gpio 1
run all