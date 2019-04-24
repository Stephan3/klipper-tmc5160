#!/usr/bin/python2

import bus, logging, collections, tmc2130

TMC_FREQUENCY=1000000.

registers = {
    "GCONF":        0x00 ,
    "GSTAT":        0x01 ,
    "IFCNT":        0x02 ,
    "SLAVECONF":    0x03 ,
    "INP_OUT":      0x04 ,
    "X_COMPARE":    0x05 ,
    "IHOLD_IRUN":   0x10 ,
    "TPOWERDOWN":   0x11 ,
    "TSTEP":        0x12 ,
    "TPWMTHRS":     0x13 ,
    "TCOOLTHRS":    0x14 ,
    "THIGH":        0x15 ,
    "RAMPMODE":     0x20 ,
    "XACTUAL":      0x21 ,
    "VACTUAL":      0x22 ,
    "VSTART":       0x23 ,
    "A1":           0x24 ,
    "V1":           0x25 ,
    "AMAX":         0x26 ,
    "VMAX":         0x27 ,
    "DMAX":         0x28 ,
    "D1":           0x2A ,
    "VSTOP":        0x2B ,
    "TZEROWAIT":    0x2C ,
    "XTARGET":      0x2D ,
    "VDCMIN":       0x33 ,
    "SWMODE":       0x34 ,
    "RAMPSTAT":     0x35 ,
    "XLATCH":       0x36 ,
    "ENCMODE":      0x38 ,
    "XENC":         0x39 ,
    "ENC_CONST":    0x3A ,
    "ENC_STATUS":   0x3B ,
    "ENC_LATCH":    0x3C ,
    "MSLUT0":       0x60 ,
    "MSLUT1":       0x61 ,
    "MSLUT2":       0x62 ,
    "MSLUT3":       0x63 ,
    "MSLUT4":       0x64 ,
    "MSLUT5":       0x65 ,
    "MSLUT6":       0x66 ,
    "MSLUT7":       0x67 ,
    "MSLUTSEL":     0x68 ,
    "MSLUTSTART":   0x69 ,
    "MSCNT":        0x6A ,
    "MSCURACT":     0x6B ,
    "CHOPCONF":     0x6C ,
    "COOLCONF":     0x6D ,
    "DCCTRL":       0x6E ,
    "DRVSTATUS":    0x6F ,
    "PWMCONF":      0x70 ,
    "PWMSTATUS":    0x71 ,
    "ENCM_CTRL":    0x72 ,
    "LOST_STEPS":   0x73
}

#
fields = {}
fields["CHOPCONF"] = {
	"toff":						0x0F << 0,
	"hstrt":					0x07 << 4,
	"hend":						0x0F << 7,
	"fd3":						0x01 << 11,
	"disfdcc":					0x01 << 12,
	"chm":						0x01 << 14,
	"TBL":						0x03 << 15,
	"vhighfs":					0x01 << 18,
	"vhighchm":					0x01 << 19,
	"tpfd":						0x0F << 20,
	"MRES":						0x0F << 24,
	"intpol":					0x01 << 28,
	"dedge":					0x01 << 29,
	"diss2g":					0x01 << 30,
	"diss2vs":					0x01 << 31
}

fields["COOLCONF"] = {
	"semin":					0x0F << 0,
	"seup":						0x03 << 5,
	"semax":					0x0F << 8,
	"sedn":						0x03 << 13,
	"seimin":					0x01 << 15,
	"sgt":						0x7F << 16,
	"sfilt":					0x01 << 24
}

fields["GCONF"] = {
	"recalibrate":				0x01 << 0,
	"faststandstill":			0x01 << 1,
	"en_pwm_mode":				0x01 << 2,
	"multistep_filt":			0x01 << 3,
	"shaft":					0x01 << 4,
	"diag0_error":				0x01 << 5,
	"diag0_otpw":				0x01 << 6,
	"diag0_stall":				0x01 << 7,
	"diag1_stall":				0x01 << 8,
	"diag1_index":				0x01 << 9,
	"diag1_onstate":			0x01 << 10,
	"diag1_steps_skipped":		0x01 << 11,
	"diag0_int_pushpull":		0x01 << 12,
	"diag1_poscomp_pushpull":	0x01 << 13,
	"small_hysteresis":			0x01 << 14,
	"stop_enable":				0x01 << 15,
	"direct_mode":				0x01 << 16,
	"test_mode":				0x01 << 17
}

fields["IHOLD_IRUN"] = {
	"IHOLD":					0x1F << 0,
	"IRUN":						0x1F << 8,
	"IHOLDDELAY":				0x0F << 16
}

fields["PWMCONF"] = {
	"PWM_OFS":					0xFF << 0,
	"PWM_GRAD":					0xFF << 8,
	"pwm_freq":					0x03 << 16,
	"pwm_autoscale":			0x01 << 18,
	"pwm_autograd":				0x01 << 19,
	"freewheel":				0x03 << 20,
	"PWM_REG":					0x0F << 24,
	"PWM_LIM":					0x0F << 28
}

fields["TPOWERDOWN"] = {
    "TPOWERDOWN": 0xff
}
fields["TPWMTHRS"] = { 
	"TPWMTHRS": 0xfffff
}

#

FieldFormatters = {
    "MRES": (lambda v: "%d(%dusteps)" % (v, 0x100 >> v)),
    "DEDGE": (lambda v:
        "1(Both Edges Active)" if v else "0(Only Rising Edge active)"),
    "INTPOL": (lambda v: "1(On)" if v else "0(Off)"),
    "TOFF": (lambda v: ("%d" % v) if v else "0(Driver Disabled!)"),
    "CHM": (lambda v: "1(constant toff)" if v else "0(spreadCycle)"),
    "SGT": (lambda v: "%d" % (v)),
    "SFILT": (lambda v: "1(Filtered mode)" if v else "0(Standard mode)"),
    "VSENSE": (lambda v: "%d(%dmV)" % (v, 165 if v else 305)),
    "SDOFF": (lambda v: "1(Step/Dir disabled" if v else "0(Step/dir enabled)"),
    "DISS2G": (lambda v: "%d(Short to GND protection %s)" % (v,
                                          "disabled" if v else "enabled")),
    "MSTEP": (lambda v: "%d(%d, OA1 %s OA2)" % (v, v & 0xff,
                                                "<=" if v & 0x100 else "=>")),
    "SG": (lambda v: "%d(%s)" % (v, "Stall!" if v else "No Stall!")),
    "OT": (lambda v: "1(Overtemp shutdown!)" if v else ""),
    "OTPW": (lambda v: "1(Overtemp warning!)" if v else ""),
    "S2GA": (lambda v: "1(Short to GND Coil A!)" if v else ""),
    "S2GB": (lambda v: "1(Short to GND Coil B!)" if v else ""),
    "OLA": (lambda v: "1(Open Load Coil A at slow speed!)" if v else ""),
    "OLB": (lambda v: "1(Open Load Coil B at slow speed!)" if v else ""),
    "STST": (lambda v: "1(Standstill detected!)" if v else ""),
    "I_scale_analog":   (lambda v: "1(ExtVREF)" if v else ""),
    "shaft":            (lambda v: "1(Reverse)" if v else ""),
    "drv_err":          (lambda v: "1(ErrorShutdown!)" if v else ""),
    "uv_cp":            (lambda v: "1(Undervoltage!)" if v else ""),
    "VERSION":          (lambda v: "%#x" % v),
    "CUR_A":            (lambda v: decode_signed_int(v, 9)),
    "CUR_B":            (lambda v: decode_signed_int(v, 9)),
    "MRES":             (lambda v: "%d(%dusteps)" % (v, 0x100 >> v)),
    "otpw":             (lambda v: "1(OvertempWarning!)" if v else ""),
    "ot":               (lambda v: "1(OvertempError!)" if v else ""),
    "s2ga":             (lambda v: "1(ShortToGND_A!)" if v else ""),
    "s2gb":             (lambda v: "1(ShortToGND_B!)" if v else ""),
    "ola":              (lambda v: "1(OpenLoad_A!)" if v else ""),
    "olb":              (lambda v: "1(OpenLoad_B!)" if v else ""),
    "sgt":              (lambda v: decode_signed_int(v, 7))
}

#######################################################################################

class TMC5160:

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.spi = bus.MCU_SPI_from_config(config, 3, default_speed=4000000)
        self.gcode = self.printer.lookup_object("gcode")
        #
        self.gcode.register_mux_command("DUMP_TMC", "STEPPER", self.name, self.cmd_DUMP_TMC, desc=self.cmd_DUMP_TMC_help)
        #
        # Setup basic register values
        self.regs = collections.OrderedDict()
        self.fields = tmc2130.FieldHelper(fields, FieldFormatters, self.regs)
        vsense, irun, ihold, self.sense_resistor = tmc2130.get_config_current(config)
        #self.fields.set_field("vsense", vsense)
        self.fields.set_field("IHOLD", ihold)
        self.fields.set_field("IRUN", irun)
        mres, en_pwm, thresh = tmc2130.get_config_stealthchop(config, TMC_FREQUENCY)
        self.fields.set_field("MRES", mres)
        self.fields.set_field("en_pwm_mode", en_pwm)
        self.fields.set_field("TPWMTHRS", thresh)
        #
        #
        # Allow other registers to be set from the config
        set_config_field = self.fields.set_config_field
        set_config_field(config, "toff", 3)
        set_config_field(config, "hstrt", 4)
        set_config_field(config, "hend", 1)
        set_config_field(config, "TBL", 2)
        set_config_field(config, "intpol", True, "interpolate")
        set_config_field(config, "IHOLDDELAY", 6)
        set_config_field(config, "TPOWERDOWN", 10)
        set_config_field(config, "PWM_OFS", 128) #
        set_config_field(config, "PWM_GRAD", 4) #
        set_config_field(config, "pwm_freq", 1)
        set_config_field(config, "pwm_autoscale", True)
        sgt = config.getint('driver_SGT', 0, minval=-64, maxval=63) & 0x7f
        self.fields.set_field("sgt", sgt)
        set_config_field(config, "test_mode", 0)
        set_config_field(config, "direct_mode", 0)
        

        #
        self._init_registers()
    def _init_registers(self, min_clock=0):
        # Send registers
        logging.error("======== 5160 ============")
        for reg_name, val in self.regs.items():
            logging.error( reg_name )
            logging.info( val )
            self.set_register(reg_name, val, min_clock)

    cmd_DUMP_TMC_help = "Read and display TMC stepper driver registers"
    def cmd_DUMP_TMC(self, params):
        logging.info("DUMP_TMC %s", self.name)
        for reg_ in registers.keys():
            repl_ = self.get_register(reg_)
            logging.info( reg_ + "\t" + hex(repl_) )
        logging.info("=======================")

        for reg_name, val in self.regs.items():
            try:
                logging.error( str(reg_name) + " - " + str(val) )
                logging.error(self.fields.pretty_format(reg_name, val) + "\n")
            except Exception as e:
                pass

    def get_register(self, reg_name):
        reg = registers[reg_name]
        self.spi.spi_send([reg, 0x00, 0x00, 0x00, 0x00])
        params = self.spi.spi_transfer([reg, 0x00, 0x00, 0x00, 0x00])
        pr = bytearray(params['response'])
        return (pr[1] << 24) | (pr[2] << 16) | (pr[3] << 8) | pr[4]

    def set_register(self, reg_name, val, min_clock = 0):
        reg = registers[reg_name]
        data = [(reg | 0x80) & 0xff, (val >> 24) & 0xff, (val >> 16) & 0xff,
                (val >> 8) & 0xff, val & 0xff]
        self.spi.spi_send(data, min_clock)


def load_config_prefix(config):
    return TMC5160(config)