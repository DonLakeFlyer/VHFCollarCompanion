from ctypes import *

libairspy = CDLL("libairspy.so")

p_airspy_dev = c_void_p

# typedef struct {
#    struct airspy_device* device;
#    void* ctx;
#    void* samples;
#    int sample_count;
#    uint64_t dropped_samples;
#    enum airspy_sample_type sample_type;
# } airspy_transfer_t, airspy_transfer;
class airspy_transfer(Structure):
    _fields_ = [("device",          p_airspy_dev),
                ("ctx",             c_void_p),
                ("samples",         POINTER(c_float)),
                ("sample_count",    c_int),
                ("dropped_samples", c_uint64),
                ("sample_type",     c_int)]

# typedef int (*airspy_sample_block_cb_fn)(airspy_transfer* transfer);
airspy_sample_block_cb_fn = CFUNCTYPE(c_int, POINTER(airspy_transfer))

# extern ADDAPI int ADDCALL airspy_init(void);
f = libairspy.airspy_init
f.restype, f.argtypes = c_int, []

# extern ADDAPI int ADDCALL airspy_exit(void);
f = libairspy.airspy_exit
f.restype, f.argtypes = c_int, []

# extern ADDAPI int ADDCALL airspy_open(struct airspy_device** device);
f = libairspy.airspy_open
f.restype, f.argtypes = c_int, [POINTER(p_airspy_dev)]

# extern ADDAPI int ADDCALL airspy_close(struct airspy_device* device);
f = libairspy.airspy_close
f.restype, f.argtypes = c_int, [p_airspy_dev]

# extern ADDAPI int ADDCALL airspy_set_sample_type(struct airspy_device* device, enum airspy_sample_type sample_type);
f = libairspy.airspy_set_sample_type
f.restype, f.argtypes = c_int, [p_airspy_dev, c_int]

# /* Parameter samplerate can be either the index of a samplerate or directly its value in Hz within the list returned by airspy_get_samplerates() */
# extern ADDAPI int ADDCALL airspy_set_samplerate(struct airspy_device* device, uint32_t samplerate);
f = libairspy.airspy_set_samplerate
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint32]

# extern ADDAPI int ADDCALL airspy_set_freq(struct airspy_device* device, const uint32_t freq_hz);
f = libairspy.airspy_set_freq
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint32]

# /* Parameter value shall be between 0 and 15 */
# extern ADDAPI int ADDCALL airspy_set_lna_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_lna_gain
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint8]

# /* Parameter value shall be between 0 and 15 */
# extern ADDAPI int ADDCALL airspy_set_mixer_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_mixer_gain
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint8]

# /* Parameter value shall be between 0 and 15 */
# extern ADDAPI int ADDCALL airspy_set_vga_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_vga_gain
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint8]

# /* Parameter value:
#     0=Disable LNA Automatic Gain Control
#     1=Enable LNA Automatic Gain Control
# */
# extern ADDAPI int ADDCALL airspy_set_lna_agc(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_lna_agc
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint8]

# /* Parameter value:
#    0=Disable MIXER Automatic Gain Control
#    1=Enable MIXER Automatic Gain Control
# */
#extern ADDAPI int ADDCALL airspy_set_mixer_agc(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_mixer_agc
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint8]

# /* Parameter value: 0..21 */
# extern ADDAPI int ADDCALL airspy_set_linearity_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_linearity_gain
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint8]

# /* Parameter value: 0..21 */
# extern ADDAPI int ADDCALL airspy_set_sensitivity_gain(struct airspy_device* device, uint8_t value);
f = libairspy.airspy_set_sensitivity_gain
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint8]

# /* Parameter value shall be 0=Disable BiasT or 1=Enable BiasT */
# extern ADDAPI int ADDCALL airspy_set_rf_bias(struct airspy_device* dev, uint8_t value);
f = libairspy.airspy_set_rf_bias
f.restype, f.argtypes = c_int, [p_airspy_dev, c_uint8]

# extern ADDAPI const char* ADDCALL airspy_error_name(enum airspy_error errcode);
f = libairspy.airspy_error_name
f.restype, f.argtypes = c_char_p, [c_int]

# extern ADDAPI int ADDCALL airspy_start_rx(struct airspy_device* device, airspy_sample_block_cb_fn callback, void* rx_ctx);
f = libairspy.airspy_start_rx
f.restype, f.argtypes = c_int, [p_airspy_dev, airspy_sample_block_cb_fn, c_void_p]

#extern ADDAPI int ADDCALL airspy_stop_rx(struct airspy_device* device);
f = libairspy.airspy_stop_rx
f.restype, f.argtypes = c_int, [p_airspy_dev]

# extern ADDAPI int ADDCALL airspy_is_streaming(struct airspy_device* device);
f = libairspy.airspy_is_streaming
f.restype, f.argtypes = c_int, [p_airspy_dev]

f = libairspy.airspy_error_name
f.restype, f.argtypes = c_char_p, [p_airspy_dev]

__all__  = ['libairspy', 'p_airspy_dev', 'rtlsdr_read_async_cb_t']
