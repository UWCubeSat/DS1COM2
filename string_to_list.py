from gnuradio.digital import ofdm_packet_utils as pkt_utils

def conv_string_to_1_0_list(s):
    """
    s = 'Hello World!''
    """
    unpacked_s = pkt_utils.conv_packed_binary_string_to_1_0_string(s)
    unpacked_s = list(unpacked_s)
    for i in range(len(unpacked_s)):
        unpacked_s[i] = int(unpacked_s[i])
    return unpacked_s