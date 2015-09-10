import sys
import os
import math

from veriloggen import *

def mkLed(numports=8, delay_amount=2):
    m = Module('blinkled')
    clk = m.Input('CLK')
    rst = m.Input('RST')
    led = [ m.OutputReg('led'+str(i), initval=0) for i in range(numports) ]
    
    zero = m.TmpWire()
    m.Assign(zero(0))

    par = lib.Parallel(m, 'par')
    
    count = m.Reg('count', (numports-1).bit_length() + 1, initval=0)
    par.add( count.inc(), delay=2 )
    par.add( count(zero), cond=count>=numports-1, delay=2, eager_val=True, lazy_cond=True )
    
    for i in range(numports):
        par.add( led[i](1), cond=(count==i) )
        par.add( led[i](0), cond=(count==i), delay=delay_amount )
        
    par.make_always(clk, rst)

    return m

def mkTest():
    m = Module('test')

    # target instance
    led = mkLed()
    
    # copy paras and ports
    params = m.copy_params(led)
    ports = m.copy_sim_ports(led)

    clk = ports['CLK']
    rst = ports['RST']
    
    uut = m.Instance(led, 'uut',
                     params=m.connect_params(led),
                     ports=m.connect_ports(led))

    lib.simulation.setup_waveform(m, uut)
    lib.simulation.setup_clock(m, clk, hperiod=5)
    init = lib.simulation.setup_reset(m, rst, period=100)

    nclk = lib.simulation.next_clock
    
    init.add(
        Delay(1000),
        Systask('finish'),
    )

    return m
    
if __name__ == '__main__':
    test = mkTest()
    verilog = test.to_verilog('tmp.v')
    print(verilog)
