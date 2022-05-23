import pyvisa as visa
from . import logger

logger = logger.getChild(__name__)


class K2600:
    """
    Control for KEITHLEY 2410 using GPIB.
    """

    def __init__(self, source_str):
        self._inst = None
        self._source_str = source_str
        self._init_connection()
        self.clear_connection()

    def _init_connection(self):
        """
        Initialize connection with KEITHLEY and check if it is possible to identify the hardware.
        """
        try:
            rm = visa.ResourceManager()
            self._inst = rm.open_resource(self._source_str)
            logger.info(self._inst.query("*IDN?"))

        except visa.errors.VisaIOError:
            logger.error("Error Initializing connection, check input string")
            raise ConnectionError

    def close_connection(self):
        """
        Closes the VISA session and marks the handle as invalid.
        """
        self._inst.close()

    def clear_connection(self):
        """
        Clear this resource.
        """
        self._inst.clear()

    def reset_source_meter(self):
        """ Returns the SourceMeter to default conditions. """
        self._inst.write("*RST")

    def scpi_reset(self, chan):
        """
        Reset values in default values
        """
        assert (chan == "a" or chan == "b")
        self._inst.write(f'smu{chan}.reset()')

    def scpi_src_out_dcv(self, chan):
        """
        Set the source output to OUTPUT_DCVOLTS
        """
        assert (chan == "a" or chan == "b")
        self._inst.write(f'smu{chan}.source.func = smu{chan}.OUTPUT_DCVOLTS')

    def scpi_src_out_dca(self, chan):
        """
        Set the source output to OUTPUT_DCAMPS
        """
        assert (chan == "a" or chan == "b")
        self._inst.write(f'smu{chan}.source.func = smu{chan}.OUTPUT_DCAMPS')

    def scpi_src_range(self, chan, s_type, value):
        """
        Set the source range value
        """
        assert (chan == "a" or chan == "b")
        assert (s_type == "v" or s_type == "i")
        self._inst.write(f'smu{chan}.source.range{s_type} = {value}')

    def scpi_src_level(self, chan, s_type, value):
        """
        Set the source level value
        """
        assert (chan == "a" or chan == "b")
        assert (s_type == "v" or s_type == "i")
        self._inst.write(f'smu{chan}.source.level{s_type} = {value}')

    def scpi_measure_range(self, chan, s_type, value):
        """
        Set the measure range value
        """
        assert (chan == "a" or chan == "b")
        assert (s_type == "v" or s_type == "i")
        self._inst.write(f'smu{chan}.measure.range{s_type} = {value}')

    def scpi_src_limit(self, chan, s_type, value):
        """
        Set the source limit value
        """
        assert (chan == "a" or chan == "b")
        assert (s_type == "v" or s_type == "i")
        self._inst.write(f'smu{chan}.source.limit{s_type} = {value}')

    def scpi_src_output(self, chan, state):
        """
        Set the source limit value
        """
        assert (chan == "a" or chan == "b")
        assert (state == "ON" or state == "OFF")
        self._inst.write(f'smu{chan}.source.output = smu{chan}.OUTPUT_{state}')

    # ***************************** Read ***************************** #
    def scpi_src_read_limit(self, chan, s_type):
        """
        Read the source limit value
        """
        assert (chan == "a" or chan == "b")
        assert (s_type == "v" or s_type == "i")
        self._inst.write(f'limit = smu{chan}.source.limit{s_type}')
        return float(self._inst.query("print(limit)"))

    def scpi_src_read_range(self, chan, s_type):
        """
        Read the source limit value
        """
        assert (chan == "a" or chan == "b")
        assert (s_type == "v" or s_type == "i")
        self._inst.write(f'range = smu{chan}.measure.range{s_type}')
        return float(self._inst.query("print(range)"))

    def scpi_src_read_level(self, chan, s_type):
        """
        Read the source limit value
        """
        assert (chan == "a" or chan == "b")
        assert (s_type == "v" or s_type == "i")
        self._inst.write(f'level = smu{chan}.source.level{s_type}')
        return float(self._inst.query("print(level)"))

    def scpi_measure_read(self, chan, s_type):
        """
        Read the source limit value
        """
        assert (chan == "a" or chan == "b")
        assert (s_type == "v" or s_type == "i")
        try:
            self._inst.write(f'reading = smu{chan}.measure.{s_type}()')
            return float(self._inst.query("print(reading)"))
        except visa.errors.VisaIOError:
            logger.error("Impossible to read, time out occurred in measure reading")
            return -1

    # ***************************** Error ***************************** #
    def clearErrorQueue(self):
        self._inst.write("*CLS")

    def checkIfError(self):
        try:
            try:
                err = int(self._inst.query("*ESR?"))
            except visa.errors.VisaIOError:
                logger.error("pyvisa.errors.VisaIOError: Timeout expired before operation completed.")
                return -1

            err &= ~(1 << 7)  # Delete Power On bit
            err &= ~(1 << 0)  # Delete OPC bit
            if err != 0:
                if err & (1 << 6):
                    logger.debug("User request error detected")
                if err & (1 << 5):
                    logger.debug("Command error detected")
                if err & (1 << 4):
                    logger.debug("Execution error detected")
                if err & (1 << 3):
                    logger.debug("Device-Dependent error detected")
                if err & (1 << 2):
                    logger.debug("Query error detected")
            else:
                logger.info("No error in keithley operation.")
        except ValueError:
            logger.error("The output queue is full and it return data not releted with '*ESR?' command.")
            return -1

        return err
