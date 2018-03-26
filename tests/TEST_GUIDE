# Mapping of CUDA test scenarios to subsequent modifications and test cases

## OSPERT
- bad/badly_timed_trace#.json (trace with out-of-order events) 
- config/ospert_2017_figure_4.json -> ospert_2017_figure_4_log#.json
 - josh_config/ospert_2017_figure_4_K5000.json -> ospert_2017_figure_4_K5000_log#.json (adj. for Quadro K5000)
  - bad/nonexistant_sm_use#.json (using too many SMs - OSPERT Rule B2.)
  - bad/gpu_thread_overutilization#.json (using more threads than are on the GPU - OSPERT Rule B2.)
  - bad/sm_thread_overutilization#.json (using more threads than are on an SM - OSPERT Rule B2.)
- config/ospert_2017_figure_6.json -> ospert_2017_figure_6_log#.json
 - josh_config/ospert_2017_figure_6_K5000.json -> ospert_2017_figure_6_K5000_log#.json (adj. for Quadro K5000)
  - bad/oo_stream_execution#.json (Out of order execution in a stream - OSPERT Rule A.)
- config/ospert_2017_figure_7.json -> ospert_2017_figure_7_log#.json
 - josh_config/ospert_2017_figure_7_GTX1070.json -> ospert_2017_figure_7_GTX1070_log#.json (adj. for Quadro GTX 1070)
  - TODO: bad/oo_ee_execution#.json (Out of order execution in the primary queue - OSPERT Rule B1.)

