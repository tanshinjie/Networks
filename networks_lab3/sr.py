import config
import threading
import time
import udt
import util

# Tan Shin Jie
# 1003715

class SelectiveRepeat:

  def __init__(self, local_port, remote_port, msg_handler):
      util.log("Starting up `Selective Repeat` protocol ... ")
      self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
      self.msg_handler = msg_handler

      # receiver
      self.receiver_base = 0
      self.is_receiver = True
      self.receiver_buffer = [None] * config.WINDOW_SIZE          # list to store packets with sequence number higher than receiver_base
      self.received_flag_list = [False] * config.WINDOW_SIZE      # list to keep track of received status for packet

      # sender
      self.sender_lock = threading.Lock()
      self.sender_base = 0
      self.next_sequence_number = 0
      self.timer_list = [None] * config.WINDOW_SIZE               # list to store of timer thread
      self.acked_flag_list = [False] * config.WINDOW_SIZE         # list to keep track of acknowledgement status for packet
  
  def set_timer(self,packet,seq_num):
      window_index = (seq_num - self.sender_base) % config.WINDOW_SIZE 
      self.timer_list[window_index] = threading.Timer((config.TIMEOUT_MSEC/1000.0), self._timeout, (packet, seq_num))

  # "send" is called by application. Return true on success, false otherwise.
  def send(self, msg):
      self.is_receiver = False
      if self.next_sequence_number < (self.sender_base + config.WINDOW_SIZE):
        self._send_helper(msg)
        return True
      else:
        util.log("Window is full. App data rejected.")
        time.sleep(1)
      return False
  
  # Helper fn for thread to send the next packet
  def _send_helper(self, msg):
    self.sender_lock.acquire()
    packet = util.make_packet(msg, config.MSG_TYPE_DATA, self.next_sequence_number)
    packet_data = util.extract_data(packet)
    window_index = ( self.next_sequence_number - self.sender_base ) % config.WINDOW_SIZE  # window_index is the index to the acked_flag_list and timer_list for a particular packet
    util.log("Sending data: " + util.pkt_to_string(packet_data))
    self.network_layer.send(packet)
    self.acked_flag_list[window_index] = False          # packet delivered to network layer, set the ACK flag to False
    current_timer = self.timer_list[window_index]       # retrieve any old timer thread 
    if current_timer:                                   # if timer thread exist
      current_timer.cancel()                            # cancel the thread
    self.set_timer(packet, self.next_sequence_number)   # set up a new timer thread 
    self.timer_list[window_index].start()
    self.next_sequence_number += 1 
    self.sender_lock.release()
    return

  def _timeout(self,*args):
    packet = args[0]
    seq_num = args[1]
    self.sender_lock.acquire()
    packet_data = util.extract_data(packet)
    util.log("Timeout! Resending packet: " + util.pkt_to_string(packet_data))
    window_index = (seq_num - self.sender_base) % config.WINDOW_SIZE     # window_index is the index to the acked_flag_list and timer_list for a particular packet
    current_timer = self.timer_list[window_index]                        # cancel the old thread
    if current_timer:                                                     
        current_timer.cancel()
    self.set_timer(packet,packet_data.seq_num)                           # set up a new timer thread
    self.network_layer.send(packet)
    self.timer_list[window_index].start()
    self.sender_lock.release()
    return
  
  # "handler" to be called by network layer when packet is ready.
  def handle_arrival_msg(self):
    msg = self.network_layer.recv()
    msg_data = util.extract_data(msg)

    if(msg_data.is_corrupt):                     
      # do nothing
      # receiver should not send out ACK packet
      # sender should ignore ACK packet, and wait for timeout to resend packet 
      util.log("Message corrupted: " + util.pkt_to_string(msg_data))
      return 

    # If ACK message, assume its for sender
    if msg_data.msg_type == config.MSG_TYPE_ACK:
      self.sender_lock.acquire()
      util.log("Received ACK: " + util.pkt_to_string(msg_data))
      target_window_index = (msg_data.seq_num - self.sender_base) % config.WINDOW_SIZE
      self.acked_flag_list[target_window_index] = True                    # set the ACKed flag to True
      current_timer = self.timer_list[target_window_index]                # retrieve timer thread for the packet
      if current_timer:                                                   
          current_timer.cancel()                                          # cancel the timer
      cumulative_acks = 0                                                 # initialize a variable to check cumulative ACKed packet starting from sender_base
      for hasACKed in self.acked_flag_list:                            
        if hasACKed:
          cumulative_acks += 1
        else:
          break
      if cumulative_acks > 0:                                             # if has cumulative ACKed packets, slide sender window forward by
        self.timer_list = self.timer_list[cumulative_acks:]               # removing the timer and ACKed flag that falls out from window
        self.acked_flag_list = self.acked_flag_list[cumulative_acks:]
        for i in range(cumulative_acks):                                  # add new default value to 
          self.timer_list.append(None)                                    # timer list
          self.acked_flag_list.append(False)                              # ACKed flag list
      self.sender_lock.release()
      self.sender_base += cumulative_acks                                 # update sender_base 

    # If DATA message, assume its for receiver
    else:
      assert msg_data.msg_type == config.MSG_TYPE_DATA
      util.log("Received DATA: " + util.pkt_to_string(msg_data))
      if (self.receiver_base - config.WINDOW_SIZE <= msg_data.seq_num <= self.receiver_base - 1):     # if packet has seq_num in range [receiver_base-N,receiver_base-1]
        ack_pkt = util.make_packet(b'', config.MSG_TYPE_ACK, msg_data.seq_num)                        # send ACK
        self.network_layer.send(ack_pkt)
        util.log("Send ACK for seq# : " + util.pkt_to_string(util.extract_data(ack_pkt)))
      if (msg_data.seq_num >= self.receiver_base):                                          # if packet has seq_num larger than receiver_base 
        ack_pkt = util.make_packet(b'', config.MSG_TYPE_ACK, msg_data.seq_num)
        self.network_layer.send(ack_pkt)
        util.log("Send ACK for seq# : " + util.pkt_to_string(util.extract_data(ack_pkt)))
        util.log("Added DATA wtih seq# : " + str(msg_data.seq_num) + ' to buffer.')       
        target_window_index = (msg_data.seq_num - self.receiver_base) % config.WINDOW_SIZE
        self.receiver_buffer[target_window_index] = msg_data.payload                        # add packet to buffer 
        self.received_flag_list[target_window_index] = True                                 # set received flag to True 
      cumulative_seqs = 0                                                 # initialize a variable to check cumulative seq_num in receiver_buffer
      for hasReceived in self.received_flag_list: 
        if hasReceived:
          cumulative_seqs += 1
        else:
          break
      if (cumulative_seqs > 0):                                           # if receiver has cumulative sequence of packets 
        for i in range(cumulative_seqs):
          self.msg_handler(self.receiver_buffer[i])                         # pass the sequence of packets to application layer
        self.receiver_buffer = self.receiver_buffer[cumulative_seqs:]       # remove delivered packet from buffer
        self.received_flag_list = self.received_flag_list[cumulative_seqs:] # and their respective received status
        for i in range(cumulative_seqs):                                    # add new default value for 
          self.receiver_buffer.append(None)                                 # receiver buffer
          self.received_flag_list.append(False)                             # received flag list 
      self.receiver_base += cumulative_seqs                                 # update receiver_base 
    return

  # Cleanup resources.
  def shutdown(self):
    if not self.is_receiver: self._wait_for_last_ACK()
    for timer in self.timer_list:
      if timer:
        if timer.is_alive(): timer.cancel()
    util.log("Connection shutting down...")
    self.network_layer.shutdown()

  def _wait_for_last_ACK(self):
    while self.sender_base != self.next_sequence_number :             # sender will exit busy wait when it is not expecting any ACKs packet
      util.log("Waiting for last ACK from receiver with sequence # "
               + str(int(self.next_sequence_number-1)) + ".")
      time.sleep(1)