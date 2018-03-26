from tokenizer import EventType, BlockEvent, KernelEvent, BenchmarkEvent
from collections import deque
"""
This file models all the states of a CUDA-capable GPU
"""
THREADS_PER_SM = 2048

class StateException(Exception):
  pass

class CommonState:
  stream_queues = {} # Map of stream ids to deques of kernels ordered with deque[0] as the head
  ee_queue = deque() # deque[0] is head
  SM_threads_avail = {} # Map of SMIDs to their available threads
  MAX_SMs = 0

  def __init__(self, event):
    benchmark = None
    if type(event) is BenchmarkEvent:
      benchmark = event.benchmark
    if type(event) is KernelEvent:
      benchmark = event.kernel.benchmark
    if type(event) is BlockEvent:
      benchmark = event.block.kernel.benchmark
    self.MAX_SMs = benchmark.max_thread_count / THREADS_PER_SM

  def nop(self, event):
    return self

class IdleState(CommonState):
  transitions = {}
  transitions[EventType.KERNEL_LAUNCH_START] = lambda event: ExecutingState(event)

class ExecutingState(CommonState):
  transitions = {}
  def __init__(self, event):
    super().__init__(event)
    self.transitions[EventType.KERNEL_LAUNCH_START] = self.kernel_launch_start
    self.transitions[EventType.KERNEL_LAUNCH_END] = self.nop
    self.transitions[EventType.KERNEL_END] = self.kernel_end
    self.transitions[EventType.BLOCK_START] = self.block_start
    self.transitions[EventType.BLOCK_END] = self.block_end
    if event.eventType != EventType.KERNEL_LAUNCH_START:
      raise StateException("Unimplemented entry event for ExecutingState")
    self.kernel_launch_start(event)

  def kernel_launch_start(self, event):
    # Deferred instantiation
    if event.kernel.stream not in self.stream_queues:
      self.stream_queues[event.kernel.stream] = deque()
    self.stream_queues[event.kernel.stream].append(event.kernel)
    # If at head, add to EE queue
    if event.kernel == self.stream_queues[event.kernel.stream][0]:
      self.ee_queue.append(event.kernel)
    return self

  def kernel_end(self, event):
    # Validate not in EE queue
    if event.kernel in self.ee_queue:
      raise StateException("Terminating kernel is not fully dispatched (still in EE queue)")
    # Validate at head of stream queue and pop
    if self.stream_queues[event.kernel.stream][0] != event.kernel:
      raise StateException("Terminating kernel not found at queue head")
    self.stream_queues[event.kernel.stream].popleft()
    # Put next kernel (if any in our stream's queue) in the ee queue
    if self.stream_queues[event.kernel.stream]:
      self.ee_queue.append(self.stream_queues[event.kernel.stream][0])
    # Compute summed queue length 
    queue_length = 0
    for queue_idx in self.stream_queues:
      queue_length += len(self.stream_queues[queue_idx])
    # Stay in this state if there's more work to do
    if queue_length != 0:
      return self
    else:
      return IdleState(event)

  def block_start(self, event):
    # Deferred instantiation
    if event.block.smid not in self.SM_threads_avail:
      if len(self.SM_threads_avail) < self.MAX_SMs:
        self.SM_threads_avail[event.block.smid] = THREADS_PER_SM
      else:
        raise StateException("Kernel starting on non-existant SM")
    # Update thread counts
    self.SM_threads_avail[event.block.smid] -= event.block.thread_count
    if self.SM_threads_avail[event.block.smid] < 0:
      raise StateException("More threads running on SM then physically possible")
    # Remove block from parent DANGER: side effect =l
    event.block.kernel.blocks.remove(event.block)
    # Verify EE queue properties
    if len(self.ee_queue) is 0 or event.block.kernel is not self.ee_queue[0]:
      raise StateException("Block starting for kernel not at head of EE queue")
    # If no more blocks to execute for this kernel, remove us from the EE queue
    if not event.block.kernel.blocks:
      self.ee_queue.popleft()
    return self

  def block_end(self, event):
    # Verify parent queue state
    found = False
    for queue_idx in self.stream_queues:
      if event.block.kernel in self.stream_queues[queue_idx]:
        found = True
    if not found:
      raise StateException("Block ending for already-terminated parent (likely a benchmark timing bug)")
    # Verify thread properties
    self.SM_threads_avail[event.block.smid] += event.block.thread_count
    if self.SM_threads_avail[event.block.smid] > THREADS_PER_SM:
      raise StateException("Threads terminating which never started")
    return self

