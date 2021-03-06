# +-----------------------------------------------------------------------------+
# |  Copyright 2019-2020 IBM Corp. All Rights Reserved.                         |
# |                                                                             |
# |  Licensed under the Apache License, Version 2.0 (the "License");            |
# |  you may not use this file except in compliance with the License.           |
# |  You may obtain a copy of the License at                                    |
# |                                                                             |
# |      http://www.apache.org/licenses/LICENSE-2.0                             |
# |                                                                             |
# |  Unless required by applicable law or agreed to in writing, software        |
# |  distributed under the License is distributed on an "AS IS" BASIS,          |
# |  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   |
# |  See the License for the specific language governing permissions and        |
# |  limitations under the License.                                             |
# +-----------------------------------------------------------------------------+
# |  Authors: Lorenz K. Mueller, Pascal Stark                                   |
# +-----------------------------------------------------------------------------+
""" Creates a very simple recurrent network with a testbench.

This is the example used in the quickstart guide.
The network topology is as follows:

 A  - B
  \  /
   C

A testbench is used to inject time varying signals at node A and B.
"""

from colna.analyticnetwork import Network, Edge, Testbench, SymNum
import numpy as np
import matplotlib.pyplot as plt

# Define Network
net = Network()

# Add three nodes
net.add_node(name='a')
net.add_node(name='b')
net.add_node(name='c')

# Add three edges (with mixed symbolic and numeric values)
net.add_edge(Edge(start='c',end='a', phase=0.5, attenuation=0.6, delay=0.1))
net.add_edge(Edge(start='a', end='b', phase=SymNum('ph_{ab}', default=5, product=False), attenuation=0.95, delay=0.2))
net.add_edge(Edge(start='b', end='c', phase=SymNum('ph_{bc}', default=3, product=False),
                  attenuation=SymNum('amp_{bc}', default=0.8, product=True), delay=0.1))

# Visualize the network (if graphviz is installed)
net.visualize(path='./visualizations/quickstart2', format='svg')

# Create a testbench
tb = Testbench(network=net, timestep=0.1)

# Add an input signal
tb.add_input_sequence(node_name='a',x=np.array([1,2,0]),t=np.array([0,2,7,10]))

# register an output node
tb.add_output_node('c')

# set the feed dictionary for the symbolic numbers
tb.set_feed_dict({'amp_{bc}': 0.7, 'ph_{bc}': 3.1, 'ph_{ab}': 4.9})

# evaluate the network (through the testbench)
tb.evaluate_network(amplitude_cutoff=1e-6)

# Calculate the output signal at the output nodes
tb.calculate_output(n_threads=8) # uses multithreading with at most 8 threads
t, x = tb.t_out.transpose(), tb.x_out.transpose()

### Plot the Input and Output Signals
plt.plot(tb.input_t[0][:-1], np.abs(tb.input_x[0][:-1]), 'o') # Input signal
plt.plot(t, np.abs(x), 'x') # Output signal
plt.xlabel('Time')
plt.ylabel('|x|')
plt.legend(['Input', 'Output C'], loc='lower left')
# plt.savefig('./visualizations/quickstart.svg')
plt.show()

# Show paths leading to node c and output waves arriving at node c
print(tb.model.get_paths('c'))
print(tb.model.get_result('c'))
tb.model.get_html_result('c',path='./visualizations/quickstart.html', precision=3)
