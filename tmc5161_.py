# TMC5160 configuration
#
# Copyright (C) 2018  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import math, logging, collections
import bus

TMC_FREQUENCY=13200000.

# missed - XDIRECT , ENCM_CTRL

registers = {
    "GCONF":            0x00 ,  #
    "GSTAT":            0x01 ,  #
    #"IFCNT":       0x02 ,
    #"SLAVECONF":    0x03 ,
    "IOIN":             0x04 ,  #
    #"X_COMPARE":    0x05 ,
    #"OTP_READ":     0x07 ,
    #"FACTORY_CONF": 0x08 ,
    #"SHORT_CONF":   0x09 ,
    #"DRV_CONF":     0x0A ,
    #"GLOBAL_SCALER":0x0B ,
    #"OFFSET_READ":  0x0C ,
    "IHOLD_IRUN":       0x10 ,  #
    "TPOWERDOWN":       0x11 ,  #
    "TSTEP":            0x12 ,  #
    "TPWMTHRS":         0x13 ,  #
    "TCOOLTHRS":        0x14 ,  #
    "THIGH":            0x15 ,  #
    #"RAMPMODE":     0x20 ,
    #"XACTUAL":      0x21 ,
    #"VACTUAL":      0x22 ,
    #"VSTART":       0x23 ,
    #"A1":           0x24 ,
    #"V1":           0x25 ,
    #"AMAX":         0x26 ,
    #"VMAX":         0x27 ,
    #"DMAX":         0x28 ,
    #"D1":           0x2A ,
    #"VSTOP":        0x2B ,
    #"TZEROWAIT":    0x2C ,
    #"XTARGET":      0x2D ,
    #"VDCMIN":       0x33 ,
    #"SW_MODE":      0x34 ,
    #"RAMP_STAT":    0x35 ,
    #"XLATCH":       0x36 ,
    #"ENCMODE":      0x38 ,
    #"X_ENC":        0x39 ,
    #"ENC_CONST":    0x3A ,
    #"ENC_STATUS":   0x3B ,
    #"ENC_LATCH":    0x3C ,
    #"ENC_DEVIATION":0x3D ,
    "MSLUT0":           0x60 ,  #
    #"MSLUT1":       0x61 ,
    #"MSLUT2":       0x62 ,
    #"MSLUT3":       0x63 ,
    #"MSLUT4":       0x64 ,
    #"MSLUT5":       0x65 ,
    #"MSLUT6":       0x66 ,
    #"MSLUT7":       0x67 ,
    "MSLUTSEL":         0x68 ,  #
    "MSLUTSTART":       0x69 ,  #
    "MSCNT":            0x6A ,  #
    "MSCURACT":         0x6B ,  #
    "CHOPCONF":         0x6C ,  #
    "COOLCONF":         0x6D ,  #
    "DCCTRL":           0x6E ,  #
    "DRV_STATUS":       0x6F ,  #
    "PWMCONF":          0x70 ,  #
    "PWM_SCALE":        0x71 ,  #
    #"PWM_AUTO":     0x72 ,
    "LOST_STEPS":       0x73    #
}

# missing - XDIRECT
ReadRegisters = [
    "GCONF", "GSTAT", "IOIN", "TSTEP", "MSCNT", "MSCURACT",
    "CHOPCONF", "DRV_STATUS", "PWM_SCALE", "LOST_STEPS",
]

fields = {}

fields["GCONF"] = {
    "recalibrate":              0x01 << 0,
    "faststandstill":           0x01 << 1,
    "en_pwm_mode":              0x01 << 2,
    "multistep_filt":           0x01 << 3,
    "shaft":                    0x01 << 4,
    "diag0_error":              0x01 << 5,
    "diag0_otpw":               0x01 << 6,
    "diag0_stall":              0x01 << 7,
    "diag1_stall":              0x01 << 8,
    "diag1_index":              0x01 << 9,
    "diag1_onstate":            0x01 << 10,
    "diag1_steps_skipped":      0x01 << 11,
    "diag0_int_pushpull":       0x01 << 12,
    "diag1_poscomp_pushpull":   0x01 << 13,
    "small_hysteresis":         0x01 << 14,
    "stop_enable":              0x01 << 15,
    "direct_mode":              0x01 << 16,
    "test_mode":                0x01 << 17
}

fields["GSTAT"] = {
    "reset":                    0x01 << 0,
    "drv_err":                  0x01 << 1,
    "uv_cp":                    0x01 << 2
}

fields["IOIN"] = {
    "REFL_STEP":                0x01 << 0,
    "REFR_DIR":                 0x01 << 1,
    "ENCB_DCEN_CFG4":           0x01 << 2,
    "ENCA_DCIN_CFG5":           0x01 << 3,
    "DRV_ENN":                  0x01 << 4,
    "ENC_N_DCO_CFG6":           0x01 << 5,
    "SD_MODE":                  0x01 << 6,
    "SWCOMP_IN":                0x01 << 7,
    "VERSION":                  0xFF << 24
}

fields["IHOLD_IRUN"] = {
    "IHOLD":                    0x1F << 0,
    "IRUN":                     0x1F << 8,
    "IHOLDDELAY":               0x0F << 16
}

fields["TPOWERDOWN"] = {
    "TPOWERDOWN":               0xff << 0
}

fields["TSTEP"] = {
    "TSTEP":                    0xfffff << 0
}

fields["TPWMTHRS"] = { 
    "TPWMTHRS":                 0xfffff << 0
}

fields["TCOOLTHRS"] = {
    "TCOOLTHRS":                0xfffff << 0
}

fields["THIGH"] = {
    "THIGH":                    0xfffff << 0
}

fields["MSCNT"] = {
    "MSCNT":                    0x3ff << 0
}

fields["MSCURACT"] = {
    "CUR_A":                    0x1FF << 0,
    "CUR_B":                    0x1FF << 16
}

fields["CHOPCONF"] = {
    "toff":                     0x0F << 0,
    "hstrt":                    0x07 << 4,
    "hend":                     0x0F << 7,
    "fd3":                      0x01 << 11,
    "disfdcc":                  0x01 << 12,
    "chm":                      0x01 << 14,
    "tbl":                      0x03 << 15,
    "vhighfs":                  0x01 << 18,
    "vhighchm":                 0x01 << 19,
    "tpfd":                     0x0F << 20, # midrange resonances
    "mres":                     0x0F << 24,
    "intpol":                   0x01 << 28,
    "dedge":                    0x01 << 29,
    "diss2g":                   0x01 << 30,
    "diss2vs":                  0x01 << 31
}

fields["COOLCONF"] = {
    "semin":                    0x0F << 0,
    "seup":                     0x03 << 5,
    "semax":                    0x0F << 8,
    "sedn":                     0x03 << 13,
    "seimin":                   0x01 << 15,
    "sgt":                      0x7F << 16,
    "sfilt":                    0x01 << 24
}

fields["DRV_STATUS"] = {
    "SG_RESULT":                0x3FF << 0,
    "s2vsa":                    0x01 << 12,
    "s2vsb":                    0x01 << 13,
    "stealth":                  0x01 << 14,
    "fsactive":                 0x01 << 15,
    "CSACTUAL":                 0xFF << 16,
    "stallGuard":               0x01 << 24,
    "ot":                       0x01 << 25,
    "otpw":                     0x01 << 26,
    "s2ga":                     0x01 << 27,
    "s2gb":                     0x01 << 28,
    "ola":                      0x01 << 29,
    "olb":                      0x01 << 30,
    "stst":                     0x01 << 31
}

fields["PWMCONF"] = {
    "PWM_OFS":                  0xFF << 0,
    "PWM_GRAD":                 0xFF << 8,
    "pwm_freq":                 0x03 << 16,
    "pwm_autoscale":            0x01 << 18,
    "pwm_autograd":             0x01 << 19,
    "freewheel":                0x03 << 20,
    "PWM_REG":                  0x0F << 24,
    "PWM_LIM":                  0x0F << 28
}

fields["PWM_SCALE"] = {
    "PWM_SCALE":                0xff << 0
}

fields["LOST_STEPS"] = {
    "LOST_STEPS":               0xfffff << 0
}

FieldFormatters = {
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
    "sgt":              (lambda v: decode_signed_int(v, 7)),
}


######################################################################
# Field helpers
######################################################################

# Return the position of the first bit set in a mask
def ffs(mask):
    return (mask & -mask).bit_length() - 1

# Decode two's complement signed integer
def decode_signed_int(val, bits):
    if ((val >> (bits - 1)) & 1):
        return val - (1 << bits)
    return val

class FieldHelper:
    def __init__(self, all_fields, field_formatters={}, registers=None):
        self.all_fields = all_fields
        self.field_formatters = field_formatters
        self.registers = registers
        if self.registers is None:
            self.registers = {}
        self.field_to_register = { f: r for r, fields in self.all_fields.items()
                                   for f in fields }
    def get_field(self, field_name, reg_value=None, reg_name=None):
        # Returns value of the register field
        if reg_name is None:
            reg_name = self.field_to_register[field_name]
        if reg_value is None:
            reg_value = self.registers[reg_name]
        mask = self.all_fields[reg_name][field_name]
        return (reg_value & mask) >> ffs(mask)
    def set_field(self, field_name, field_value, reg_value=None, reg_name=None):
        # Returns register value with field bits filled with supplied value
        if reg_name is None:
            reg_name = self.field_to_register[field_name]
        if reg_value is None:
            reg_value = self.registers.get(reg_name, 0)
        mask = self.all_fields[reg_name][field_name]
        new_value = (reg_value & ~mask) | ((field_value << ffs(mask)) & mask)
        self.registers[reg_name] = new_value
        return new_value
    def set_config_field(self, config, field_name, default, config_name=None):
        # Allow a field to be set from the config file
        if config_name is None:
            config_name = "driver_" + field_name.upper()
        reg_name = self.field_to_register[field_name]
        mask = self.all_fields[reg_name][field_name]
        maxval = mask >> ffs(mask)
        if maxval == 1:
            val = config.getboolean(config_name, default)
        else:
            val = config.getint(config_name, default, minval=0, maxval=maxval)
        return self.set_field(field_name, val)
    def pretty_format(self, reg_name, value):
        # Provide a string description of a register
        reg_fields = self.all_fields.get(reg_name, {})
        reg_fields = sorted([(mask, name) for name, mask in reg_fields.items()])
        fields = []
        for mask, field_name in reg_fields:
            fval = (value & mask) >> ffs(mask)
            sval = self.field_formatters.get(field_name, str)(fval)
            if sval and sval != "0":
                fields.append(" %s=%s" % (field_name, sval))
        return "%-11s %08x%s" % (reg_name + ":", value, "".join(fields))


######################################################################
# Config reading helpers
######################################################################

def current_bits(current, sense_resistor, vsense_on):
    sense_resistor += 0.020
    vsense = 0.32
    if vsense_on:
        vsense = 0.18
    cs = int(32. * current * sense_resistor * math.sqrt(2.) / vsense - 1. + .5)
    return max(0, min(31, cs))

def bits_to_current(bits, sense_resistor, vsense_on):
    sense_resistor += 0.020
    vsense = 0.32
    if vsense_on:
        vsense = 0.18
    current = (bits + 1) * vsense / (32 * sense_resistor * math.sqrt(2.))
    return round(current, 2)

def calc_current_config(run_current, hold_current, sense_resistor):
    vsense = False
    irun = current_bits(run_current, sense_resistor, vsense)
    ihold = current_bits(hold_current, sense_resistor, vsense)
    if irun < 16 and ihold < 16:
        vsense = True
        irun = current_bits(run_current, sense_resistor, vsense)
        ihold = current_bits(hold_current, sense_resistor, vsense)
    return vsense, irun, ihold

def get_config_current(config):
    run_current = config.getfloat('run_current', above=0., maxval=2.)
    hold_current = config.getfloat('hold_current', run_current,
                                   above=0., maxval=2.)
    sense_resistor = config.getfloat('sense_resistor', 0.110, above=0.)
    vsense, irun, ihold = calc_current_config(
                              run_current, hold_current, sense_resistor)
    return vsense, irun, ihold, sense_resistor

def get_config_microsteps(config):
    steps = {'256': 0, '128': 1, '64': 2, '32': 3, '16': 4,
             '8': 5, '4': 6, '2': 7, '1': 8}
    return config.getchoice('microsteps', steps)

def get_config_stealthchop(config, tmc_freq):
    mres = get_config_microsteps(config)
    velocity = config.getfloat('stealthchop_threshold', 0., minval=0.)
    if not velocity:
        return mres, False, 0
    stepper_name = " ".join(config.get_name().split()[1:])
    stepper_config = config.getsection(stepper_name)
    step_dist = stepper_config.getfloat('step_distance')
    step_dist_256 = step_dist / (1 << mres)
    threshold = int(tmc_freq * step_dist_256 / velocity + .5)
    return mres, True, max(0, min(0xfffff, threshold))


######################################################################
# TMC5160 printer object
######################################################################

class TMC5160:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.spi = bus.MCU_SPI_from_config(config, 3, default_speed=4000000)
        # Allow virtual endstop to be created
        self.diag1_pin = config.get('diag1_pin', None)
        ppins = self.printer.lookup_object("pins")
        ppins.register_chip("tmc5160_" + self.name, self)
        # Add DUMP_TMC, INIT_TMC command
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "SET_TMC_CURRENT", "STEPPER", self.name,
            self.cmd_SET_TMC_CURRENT, desc=self.cmd_SET_TMC_CURRENT_help)
        gcode.register_mux_command(
            "DUMP_TMC", "STEPPER", self.name,
            self.cmd_DUMP_TMC, desc=self.cmd_DUMP_TMC_help)
        gcode.register_mux_command(
            "SET_TMC_FIELD", "STEPPER", self.name,
            self.cmd_SET_TMC_FIELD, desc=self.cmd_SET_TMC_FIELD_help)
        gcode.register_mux_command(
            "INIT_TMC", "STEPPER", self.name,
            self.cmd_INIT_TMC, desc=self.cmd_INIT_TMC_help)
        # Setup basic register values
        self.regs = collections.OrderedDict()
        self.fields = FieldHelper(fields, FieldFormatters, self.regs)
        vsense, irun, ihold, self.sense_resistor = get_config_current(config)
        #self.fields.set_field("vsense", vsense)
        self.fields.set_field("IHOLD", ihold)
        self.fields.set_field("IRUN", irun)
        mres, en_pwm, thresh = get_config_stealthchop(config, TMC_FREQUENCY)
        self.fields.set_field("mres", mres)
        self.fields.set_field("en_pwm_mode", en_pwm)
        self.fields.set_field("TPWMTHRS", thresh)
        # from 2208
        self.fields.set_field("multistep_filt", True)
        # Allow other registers to be set from the config
        set_config_field = self.fields.set_config_field
        set_config_field(config, "toff", 3)
        set_config_field(config, "hstrt", 4)
        set_config_field(config, "hend", 1)
        set_config_field(config, "tbl", 2)
        set_config_field(config, "intpol", True, "interpolate")
        set_config_field(config, "IHOLDDELAY", 6)
        set_config_field(config, "TPOWERDOWN", 10)
        set_config_field(config, "PWM_OFS", 128)   #   ob das so rich iss 2130 PWM_AMPL
        set_config_field(config, "PWM_GRAD", 14) #   not in example took from 2208
        set_config_field(config, "pwm_freq", 1) #   not in example
        set_config_field(config, "pwm_autoscale", True)
        set_config_field(config, "pwm_autograd", True)
        set_config_field(config, "PWM_REG", 8)
        set_config_field(config, "PWM_LIM", 12)
        sgt = config.getint('driver_SGT', 0, minval=-64, maxval=63) & 0x7f
        self.fields.set_field("sgt", sgt)
        self._init_registers()
    def _init_registers(self, min_clock = 0):
        # Send registers
        for reg_name, val in self.regs.items():
            self.set_register(reg_name, val, min_clock)
    def setup_pin(self, pin_type, pin_params):
        if pin_type != 'endstop' or pin_params['pin'] != 'virtual_endstop':
            raise pins.error("tmc5160 virtual endstop only useful as endstop")
        if pin_params['invert'] or pin_params['pullup']:
            raise pins.error("Can not pullup/invert tmc5160 virtual endstop")
        return TMC5160VirtualEndstop(self)
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
    def get_microsteps(self):
        return 256 >> self.fields.get_field("MRES")
    def get_phase(self):
        mscnt = self.fields.get_field("MSCNT", self.get_register("MSCNT"))
        return mscnt >> self.fields.get_field("MRES")
    cmd_SET_TMC_CURRENT_help = "Set the current of a TMC5160 driver"
    def cmd_SET_TMC_CURRENT(self, params):
        gcode = self.printer.lookup_object('gcode')
        vsense = bool(self.fields.get_field("vsense"))
        if 'HOLDCURRENT' in params:
            hold_current = gcode.get_float(
                'HOLDCURRENT', params, above=0., maxval=2.)
        else:
            hold_current = bits_to_current(
                    self.fields.get_field("IHOLD"),
                    self.sense_resistor,
                    vsense)
        if 'CURRENT' in params:
            run_current = gcode.get_float(
                'CURRENT', params, minval=hold_current, maxval=2.)
        else:
            run_current = bits_to_current(
                    self.fields.get_field("IRUN"),
                    self.sense_resistor,
                    vsense)
        if 'HOLDCURRENT' in params or 'CURRENT' in params:
            print_time = self.printer.lookup_object('toolhead')\
                             .get_last_move_time()
            min_clock = self.spi.get_mcu().print_time_to_clock(print_time)
            vsense_calc, irun, ihold = calc_current_config(run_current,
                                            hold_current, self.sense_resistor)
            if (vsense_calc != vsense):
                self.fields.set_field("vsense", vsense_calc)
                self.set_register("CHOPCONF", self.regs["CHOPCONF"], min_clock)
            self.fields.set_field("IHOLD", ihold)
            self.fields.set_field("IRUN", irun)
            self.set_register("IHOLD_IRUN", self.regs["IHOLD_IRUN"], min_clock)
        else:
            gcode.respond_info(
                "Run Current: %0.2fA Hold Current: %0.2fA"
                % (run_current, hold_current))
    cmd_DUMP_TMC_help = "Read and display TMC stepper driver registers"
    def cmd_DUMP_TMC(self, params):
        self.printer.lookup_object('toolhead').get_last_move_time()
        gcode = self.printer.lookup_object('gcode')
        logging.info("DUMP_TMC %s", self.name)
        gcode.respond_info("========== Write-only registers ==========")
        for reg_name, val in self.regs.items():
            if reg_name not in ReadRegisters:
                gcode.respond_info(self.fields.pretty_format(reg_name, val))
        gcode.respond_info("========== Queried registers ==========")
        for reg_name in ReadRegisters:
            val = self.get_register(reg_name)
            gcode.respond_info(self.fields.pretty_format(reg_name, val))
    cmd_INIT_TMC_help = "Initialize TMC stepper driver registers"
    def cmd_INIT_TMC(self, params):
        logging.info("INIT_TMC 5160 %s", self.name)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        min_clock = self.spi.get_mcu().print_time_to_clock(print_time)
        self._init_registers(min_clock)
    cmd_SET_TMC_FIELD_help = "Set a register field of a TMC5160 driver"
    def cmd_SET_TMC_FIELD(self, params):
        gcode = self.printer.lookup_object('gcode')
        if ('FIELD' not in params or
            'VALUE' not in params):
            raise gcode.error("Invalid command format")
        field = gcode.get_str('FIELD', params)
        reg = self.fields.field_to_register[field]
        value = gcode.get_int('VALUE', params)
        self.fields.set_field(field, value)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        min_clock = self.spi.get_mcu().print_time_to_clock(print_time)
        self.set_register(reg, self.regs[reg], min_clock)

# Endstop wrapper that enables tmc5160 "sensorless homing"
class TMC5160VirtualEndstop:
    def __init__(self, tmc5160):
        self.tmc5160 = tmc5160
        if tmc5160.diag1_pin is None:
            raise pins.error("tmc5160 virtual endstop requires diag1_pin")
        ppins = tmc5160.printer.lookup_object('pins')
        self.mcu_endstop = ppins.setup_pin('endstop', tmc5160.diag1_pin)
        if self.mcu_endstop.get_mcu() is not tmc5160.spi.get_mcu():
            raise pins.error("tmc5160 virtual endstop must be on same mcu")
        self.en_pwm = tmc5160.fields.get_field("en_pwm_mode")
        # Wrappers
        self.get_mcu = self.mcu_endstop.get_mcu
        self.add_stepper = self.mcu_endstop.add_stepper
        self.get_steppers = self.mcu_endstop.get_steppers
        self.home_start = self.mcu_endstop.home_start
        self.home_wait = self.mcu_endstop.home_wait
        self.query_endstop = self.mcu_endstop.query_endstop
        self.query_endstop_wait = self.mcu_endstop.query_endstop_wait
        self.TimeoutError = self.mcu_endstop.TimeoutError
    def home_prepare(self):
        self.tmc5160.fields.set_field("en_pwm_mode", 0)
        self.tmc5160.fields.set_field("diag1_stall", 1)
        self.tmc5160.set_register("GCONF", self.tmc5160.regs['GCONF'])
        self.tmc5160.set_register("TCOOLTHRS", 0xfffff)
        self.mcu_endstop.home_prepare()
    def home_finalize(self):
        self.tmc5160.fields.set_field("en_pwm_mode", self.en_pwm)
        self.tmc5160.fields.set_field("diag1_stall", 0)
        self.tmc5160.set_register("GCONF", self.tmc5160.regs['GCONF'])
        self.tmc5160.set_register("TCOOLTHRS", 0)
        self.mcu_endstop.home_finalize()

def load_config_prefix(config):
    return TMC5160(config)
