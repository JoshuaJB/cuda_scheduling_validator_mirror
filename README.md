# NVIDIA CUDA Scheduling Trace Validator
This program validates JSON traces from cuda_scheduling_examiner benchmarks against
the set of scheduling rules outlined by papers published by UNC's real-time GPU
research group at OSPERT'17 and RTSS'17. Benchmark traces will fail validation if they
do not conform to the scheduling rules.

## Usage
`./main.py <benchmark_file_prefix> [-d][--debug]`
where `<benchmark_file_prefix>` would be something like `tests/bad/badly_timed_trace`
to load `tests/bad/badly_timed_trace1.json`, `tests/bad/badly_timed_trace2.json`, etc.
