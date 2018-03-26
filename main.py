#!/usr/bin/python3
import tokenizer
import json
import sys
import fsm

def print_usage_and_quit():
  print("Usage: " + sys.argv[0] + " <benchmark_file_prefix> [-d][--debug]")
  exit(1)

if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
  print_usage_and_quit()

DEBUG = "-d" in sys.argv or "--debug" in sys.argv
prefix = sys.argv[1]
benchmarks = []
events = []

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# Load, parse, tokenize, and sort benchmark logs
try:
  idx = 0
  benchmark_files = []
  while True:
    benchmark_files.append(open(sys.argv[1] + str(idx + 1) + ".json"))
    idx += 1
except FileNotFoundError:
  if not benchmark_files:
    print("Benchmark file \"" + sys.argv[1] +  "1.json\" not found.")
    print_usage_and_quit()
  for benchmark_file in benchmark_files:
    benchmark = json.load(benchmark_file)
    benchmarks.append(benchmark)
    events.extend(tokenizer.tokenize_events(benchmark))
  events.sort(key=lambda event: (event.timestamp, event.eventType.value))

def kernel_info(kernel):
  return "(" + kernel.name + "/pri-" + str(kernel.priority) + "/stream-" + str(kernel.stream) +  ")"
def benchmark_info(benchmark):
  return "(" + benchmark.name + ": " + benchmark.label + ")"
def block_info(block):
  return "(SM" + str(block.smid) + "/" + str(block.thread_count) + ")"

print(HEADER + "Validating scenario \"" + benchmarks[0]["scenario_name"] + "\"" + ENDC)
if DEBUG:
  # Print event stream to console
  print("Time (sec) | Event Name")
  for event in events:
    additional_data = " "
    if type(event) is tokenizer.BenchmarkEvent:
      additional_data += benchmark_info(event.benchmark)
    if type(event) is tokenizer.KernelEvent:
      additional_data += kernel_info(event.kernel) + " " + benchmark_info(event.kernel.benchmark)
    if type(event) is tokenizer.BlockEvent:
      additional_data += block_info(event.block) + " " + kernel_info(event.block.kernel) + " " + benchmark_info(event.block.kernel.benchmark)
    print("{:11.9f}".format(event.timestamp) + ": " + event.eventType.name + additional_data)
# First event should always be the release
if events[0].eventType != tokenizer.EventType.BENCHMARK_RELEASE:
  raise Exception("Malformed trace - BENCHMARK_RELEASE is not first event")
current_state = fsm.IdleState(events[0])
# Validate
for event in events[1:]:
  if type(event) is tokenizer.BenchmarkEvent:
    continue
  # Begin Debug
  additional_data = " "
  if type(event) is tokenizer.KernelEvent:
    additional_data += kernel_info(event.kernel) + " " + benchmark_info(event.kernel.benchmark)
  if type(event) is tokenizer.BlockEvent:
    additional_data += block_info(event.block) + " " + kernel_info(event.block.kernel) + " " + benchmark_info(event.block.kernel.benchmark)
  if DEBUG:
    print(BOLD + "Validating: " + event.eventType.name + additional_data + ENDC)
  else:
    print("Validating: " + event.eventType.name + additional_data)
  # End Debug
  try:
    if event.eventType not in current_state.transitions:
      raise fsm.StateException("Event " + event.eventType.name + " is not valid for current state " + type(current_state).__name__)
    current_state = current_state.transitions[event.eventType](event)
  except fsm.StateException as error:
    print(FAIL + "Validation failed: {}".format(error) + ENDC)
    exit(1)
  if DEBUG:
    print("Timestamp: {:11.9f}".format(event.timestamp)) 
    print("Stream queue states: " + str(current_state.stream_queues))
    print("EE queue state: " + str(current_state.ee_queue))
print(OKGREEN + "Validation successful." + ENDC)
