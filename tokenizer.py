from enum import Enum
import models

WARNING = '\033[93m'
ENDC = '\033[0m'

"""
Convert a JSON log file to a sorted array of event objects
"""
def tokenize_events(benchObj):
  events = []
  # Create events in order that they're rendered in the json, then sort
  # Per-benchmark times
  benchmark = models.Benchmark(benchObj["benchmark_name"], benchObj["label"], benchObj["max_resident_threads"])
  events.append(BenchmarkEvent(EventType.BENCHMARK_RELEASE, benchObj["release_time"], benchmark))
  # We can ignore "cpu_times" as that's just a duplicate of the start of copy_in and the end of copy_out
  events.append(BenchmarkEvent(EventType.BENCHMARK_COPY_IN_START, benchObj["times"][1]["copy_in_times"][0], benchmark))
  events.append(BenchmarkEvent(EventType.BENCHMARK_COPY_IN_END, benchObj["times"][1]["copy_in_times"][1], benchmark))
  events.append(BenchmarkEvent(EventType.BENCHMARK_COPY_OUT_START, benchObj["times"][1]["copy_out_times"][0], benchmark))
  events.append(BenchmarkEvent(EventType.BENCHMARK_COPY_OUT_END, benchObj["times"][1]["copy_out_times"][1], benchmark))
  events.append(BenchmarkEvent(EventType.BENCHMARK_EXE_START, benchObj["times"][1]["execute_times"][0], benchmark))
  events.append(BenchmarkEvent(EventType.BENCHMARK_EXE_END, benchObj["times"][1]["execute_times"][1], benchmark))
  # Per-kernel times
  for kernelObj in benchObj["times"][2:]:
    # *** HACK *** HACK *** MAGIC NUMBERS AND PLACEHOLDER DATA. FIXME with real stream and priority data
    kernel = models.Kernel(kernelObj["kernel_name"], benchObj["TID"], 0, benchmark)
    benchmark.kernels.append(kernel) 
    events.append(KernelEvent(EventType.KERNEL_LAUNCH_START, kernelObj["cuda_launch_times"][0], kernel))
    events.append(KernelEvent(EventType.KERNEL_LAUNCH_END, kernelObj["cuda_launch_times"][1], kernel))
    # Kernel end time is optional (depends on application of cudaStreamSynchronize)
    # Falls back to last block time plus one nanosecond if unavailable
    kernel_end_time = 0
    if kernelObj["cuda_launch_times"][2] == 0:
      print(WARNING + "WARNING: Using last block time + 1ns as substitute to missing cudaStreamSynchronize timestamp for kernel " + kernel.name + ENDC)
      kernel_end_time = sorted(kernelObj["block_times"])[-1] + 0.000000001
    else:
      kernel_end_time = kernelObj["cuda_launch_times"][2]
    events.append(KernelEvent(EventType.KERNEL_END, kernel_end_time, kernel))
    # Per-block times
    idx = 0
    while idx * 2 < len(kernelObj["block_times"]):
      block = models.Block(kernelObj["block_smids"][idx], kernelObj["thread_count"], kernel)
      kernel.blocks.append(block)
      events.append(BlockEvent(EventType.BLOCK_START, kernelObj["block_times"][idx * 2], block))
      events.append(BlockEvent(EventType.BLOCK_END, kernelObj["block_times"][idx * 2 + 1], block))
      idx += 1
  return sorted(events, key=lambda event: event.timestamp)
    

"""
Enumeration of every possible GPU-assoc. event
Ordering matters. Any timestamp conflicts are resolved with lowest enum value first
"""
class EventType(Enum):
  BENCHMARK_RELEASE = 0
  BENCHMARK_COPY_IN_START = 1
  BENCHMARK_COPY_IN_END = 2
  BENCHMARK_EXE_START = 3
  BENCHMARK_EXE_END = 4
  BENCHMARK_COPY_OUT_START = 5
  BENCHMARK_COPY_OUT_END = 6
  KERNEL_LAUNCH_START = 7
  KERNEL_LAUNCH_END = 8
  KERNEL_END = 9 # Peudo-event; KERNEL_END_SYNC when available, otherwise last block end time
  BLOCK_START = 11
  BLOCK_END = 10

class Event:
  def __init__(self, eventType, timestamp):
    self.eventType = eventType # EventType enum
    self.timestamp = timestamp # CPU timestamp

class KernelEvent(Event):
  def __init__(self, eventType, timestamp, kernel):
    super().__init__(eventType, timestamp)
    self.kernel = kernel

class BlockEvent(Event):
  def __init__(self, eventType, timestamp, block):
    super().__init__(eventType, timestamp)
    self.block = block

class BenchmarkEvent(Event):
  def __init__(self, eventType, timestamp, benchmark):
    super().__init__(eventType, timestamp)
    self.benchmark = benchmark

