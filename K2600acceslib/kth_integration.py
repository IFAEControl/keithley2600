from K2600acceslib.kth2600 import K2600
from . import logger

logger = logger.getChild(__name__)


class K2600Probecard(K2600):
    """ Developing test for Probe card using keithley 2636B """

    def __init__(self, source_str, verbose=False):
        super().__init__(source_str)
        self.verbose = verbose

    def main(self, a_l, b_l, rnge, level, avdd_v_c, avdd_c_c, vdd_v_c, vdd_c):
        """
        Execute probecard main test.
        :param a_l: chan A source limit current.
        :param b_l: chan B source limit current.
        :param rnge: chan A and B source range, can be 20, 200, .... check K2600 manual.
        :param level: chan A and B source level, can be 20, 200, .... check K2600 manual.
        :param avdd_v_c: AVDD voltage test comparison threshold.
        :param avdd_c_c: AVDD current test comparison threshold.
        :param vdd_v_c: VDD voltage test comparison threshold.
        :param vdd_c: VDD current test comparison threshold.
        :return: Test output binary array. shape (4,).
        """
        self.clear_reset()
        self.set_values(a_l, b_l, rnge, level)
        self.set_k_out_on()
        test_output_bin, test_output = self.read_compare(avdd_v_c, avdd_c_c, vdd_v_c, vdd_c)
        return test_output_bin, test_output

    def clear_reset(self):
        # Check and clear error
        self.clear_connection()
        self.reset_source_meter()
        self.clearErrorQueue()

    def set_values(self, a_l, b_l, rnge, level):
        """ Set all values """
        self.scpi_src_out_dcv("a")
        self.scpi_src_out_dcv("b")
        self.scpi_src_limit("a", "i", a_l)
        self.scpi_src_limit("b", "i", b_l)
        self.scpi_src_range("a", "v", rnge)
        self.scpi_src_range("b", "v", rnge)
        self.scpi_src_level("a", "v", level)
        self.scpi_src_level("b", "v", level)
        self.checkIfError()

        # Read and compare values
        assert self.scpi_src_read_limit("a", "i") == a_l
        assert self.scpi_src_read_limit("b", "i") == b_l
        assert self.scpi_src_read_range("a", "v") == rnge
        assert self.scpi_src_read_range("b", "v") == rnge
        assert self.scpi_src_read_level("a", "v") == level
        assert self.scpi_src_read_level("b", "v") == level
        self.checkIfError()

    def read_compare(self, avdd_v_c, avdd_c_c, vdd_v_c, vdd_c):
        """ Read output values and compare """
        # Readout
        avdd_voltage = self.scpi_measure_read("a", "v")
        avdd_current = self.scpi_measure_read("a", "i")
        vdd_voltage = self.scpi_measure_read("b", "v")
        vdd_current = self.scpi_measure_read("b", "i")
        self.checkIfError()

        # Compare
        iv0 = avdd_voltage >= avdd_v_c
        iv1 = avdd_current >= avdd_c_c
        iv2 = vdd_voltage >= vdd_v_c
        iv3 = vdd_current >= vdd_c

        if self.verbose:
            logger.info(f"Readout values: {avdd_voltage}, {avdd_current}, {vdd_voltage}, {vdd_current}")
            logger.info(f"Readout bin result: {int(iv0)}{int(iv1)}{int(iv2)}{int(iv3)}")

        if iv0 == 0 or iv2 == 0:
            self.set_k_out_off()

        return [int(iv0), int(iv1), int(iv2), int(iv3)], [avdd_voltage, avdd_current, vdd_voltage, vdd_current]

    def set_k_out_on(self):
        """ Setting both channels of keithley off"""
        # Set both output on.
        self.scpi_src_output("a", "ON")
        self.scpi_src_output("b", "ON")
        self.checkIfError()

    def set_k_out_off(self):
        """ Setting both channels of keithley off"""
        self.scpi_src_output("a", "OFF")
        self.scpi_src_output("b", "OFF")
        self.checkIfError()
