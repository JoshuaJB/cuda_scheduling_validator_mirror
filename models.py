class Benchmark:
  kernels = []
  def __init__(self, name, label, max_thread_count):
    self.name = name
    self.label = label
    self.max_thread_count = max_thread_count
  def __repr__(self):
    return self.name + ": " + self.label + " w/ " + self.max_thread_count + " threads"

class Kernel:
  def __init__(self, name, stream, priority, benchmark):
    self.blocks = []
    self.name = name
    self.stream = stream
    self.priority = priority
    self.benchmark = benchmark
  def __repr__(self):
    return self.name + "/pri-" + str(self.priority) + "/stream-" + str(self.stream)

class Block:
  def __init__(self, smid, thread_count, kernel):
    self.smid = smid
    self.thread_count = thread_count
    self.kernel = kernel
  def __repr__(self):
    return "SM" + str(self.smid) + "/" + str(self.thread_count)

