# NVIDIA CUDA Scheduling Trace Validator
This program validates JSON traces from cuda_scheduling_examiner benchmarks against
the set of scheduling rules outlined by papers published by UNC's real-time GPU
research group at OSPERT'17 and RTSS'17. Benchmark traces will fail validation if they
do not conform to the scheduling rules.

## Current Status
Should validate traces against OSPERT'17 rules (further testing in progress..)

## Limitations
Unsupported in traces: (not yet implemented in the state machine)
1. Use of priority streams
2. Use of the NULL stream
3. Cross-stream sychronizations

Items not (yet) validated againt scheduling rules:
1. Copy operations

## Usage
`./main.py <benchmark_file_prefix> [-d][--debug]`

`<benchmark_file_prefix>` would be something like `tests/bad/badly_timed_trace`
to load `tests/bad/badly_timed_trace1.json`, `tests/bad/badly_timed_trace2.json`, etc.
for example.
