# Building an OpenFlow SDN Controller from Scratch using POX

A lightweight Software Defined Networking (SDN) controller developed using the **POX framework**. This project demonstrates the core concepts behind SDN controller design, including topology discovery, host learning, shortest-path routing, flow installation, traffic monitoring, and automatic idle-flow removal.

Rather than relying on an existing controller such as Ryu or ONOS, this project implements these networking functions from scratch to better understand how OpenFlow controllers operate internally.

---

# Features

- OpenFlow 1.0 Controller
- LLDP-based topology discovery
- Dynamic host discovery
- Host database maintenance
- Breadth First Search (BFS) shortest path routing
- Automatic end-to-end flow installation
- Flow statistics collection
- Idle flow detection
- Automatic removal of inactive flow rules
- Automatic path reinstallation when new traffic arrives
- Modular controller architecture

---

# Architecture

```
                    +------------------------+
                    |     Mininet Hosts      |
                    +-----------+------------+
                                |
                         OpenFlow Network
                                |
                    +-----------+------------+
                    |           |            |
                  Switch 1   Switch 2    Switch 3
                    |           |            |
                    +-----------+------------+
                                |
                         OpenFlow Channel
                                |
                      +-------------------+
                      |   POX Controller  |
                      +-------------------+
                                |
      ---------------------------------------------------------
      |          |          |          |          |            |
   Learning    LLDP     Topology    Routing     Path      Flow Stats
    Engine     Module     Manager    Manager    Manager    Database
```

---

# Controller Workflow

```
                 PacketIn Event
                       |
                       |
                Is LLDP Packet?
                  /          \
               Yes            No
               |              |
        Update Topology    Learn Host
                               |
                               |
                    Destination Known?
                      /            \
                   No               Yes
                   |                 |
             Flood Packet      Compute BFS Path
                                     |
                              Install Flow Rules
                                     |
                              Forward First Packet
                                     |
                          Collect Flow Statistics
                                     |
                         Remove Idle Flow Rules
```

---

# Repository Structure

```
mycontroller/
│
├── __init__.py
├── controller.py
├── learning.py
├── topology.py
├── routing.py
├── path.py
├── host.py
├── lldp.py
└── switch_manager.py
Readme.md
```

### Module Description

| File | Description |
|------|-------------|
| `controller.py` | Initializes the SDN controller and creates all controller modules |
| `learning.py` | Handles PacketIn events, host learning, packet forwarding, statistics collection, and idle flow removal |
| `topology.py` | Maintains the network topology discovered through LLDP |
| `routing.py` | Computes shortest paths using Breadth First Search (BFS) |
| `path.py` | Installs and removes OpenFlow rules along the computed path |
| `host.py` | Maintains the host database |
| `lldp.py` | Generates and parses LLDP packets |
| `switch_manager.py` | Maintains switch OpenFlow connections |

---

# Prerequisites

The project requires:

- Ubuntu Linux
- Python 3
- Open vSwitch
- Mininet
- POX Controller
- OpenFlow 1.0 compatible switches

---

# Installation

Since this repository contains **only the controller implementation**, first clone the POX repository.

## 1. Clone POX

```bash
git clone https://github.com/noxrepo/pox.git
```

---

## 2. Copy the controller

Copy the `mycontroller` folder into the POX source directory.

```
pox/
└── pox/
    └── mycontroller/
```

Example:

```bash
cp -r mycontroller pox/pox/
```

---

## 3. Verify the directory structure

```
pox/
│
├── pox.py
│
└── pox/
    │
    ├── forwarding/
    ├── openflow/
    ├── lib/
    └── mycontroller/
```

---

# Running the Controller

Navigate to the POX directory.

```bash
cd pox
```

Start the controller.

```bash
python3 pox.py mycontroller
```

You should see output similar to:

```
POX 0.7.0 (gar)

Switch connected

Controller initialized

Sent LLDP packets...
```

---

# Running Mininet

Example using a linear topology:

```bash
sudo mn \
--topo linear,3 \
--mac \
--switch ovsk \
--controller remote
```
Or 
```bash
sudo mn \
--topo tree,2 \
--mac \
--switch ovsk \
--controller remote
```
Or use your own custom Mininet topology.

---

# Testing the Controller

Ping all hosts.

```bash
mininet> pingall
```

Ping between two hosts.

```bash
mininet> h1 ping -c 1 h3
```

Generate TCP traffic.

```bash
mininet> iperf h1 h3
```

---

# Example Output

Topology Discovery

```
Added link 1:2 -> 3:3

Added link 3:3 -> 1:2

Added link 1:1 -> 2:3
```

Host Learning

```
Host 02:f5:e3:f8:cc:9b -> Switch 2 Port 1

Host 5e:3d:25:de:f0:59 -> Switch 3 Port 1
```

Path Installation

```
Installing path

Switch 2 -> output port 3

Switch 1 -> output port 2

Switch 3 -> output port 1
```

Flow Statistics

```
Source MAC          Destination MAC

Packets

Bytes

Age
```

Idle Flow Removal

```
Removed path

5e:3d:25:de:f0:59

->

02:f5:e3:f8:cc:9b
```

---

# Design Overview

The controller performs the following operations:

1. Discovers switches using OpenFlow connections.
2. Discovers links using LLDP.
3. Learns host locations dynamically.
4. Builds a network topology graph.
5. Computes shortest paths using BFS.
6. Installs flow rules across every switch on the path.
7. Periodically collects flow statistics.
8. Detects idle flows.
9. Removes inactive flow entries.
10. Reinstalls paths automatically when traffic resumes.

---

# Implemented Algorithms

### Topology Discovery

- LLDP packet generation
- LLDP packet parsing
- Dynamic link discovery

### Routing

- Breadth First Search (BFS)
- Shortest-hop routing

### Learning

- MAC learning
- Host database maintenance

### Flow Management

- End-to-end flow installation
- Flow statistics monitoring
- Idle flow detection
- Automatic flow removal

---

# Limitations

This controller is intended for educational purposes.

Current limitations include:

- Breadth First Search routing only
- Static link cost
- No load balancing
- No Equal Cost Multi Path (ECMP)
- No failure recovery
- OpenFlow 1.0 support only
- Single controller architecture

---

# Future Work

Possible extensions include:

- Dijkstra shortest path routing
- Dynamic link cost computation
- Load-aware routing
- Link failure recovery
- Fast rerouting
- OpenFlow 1.3 support
- REST API integration
- Multi-controller deployment
- Traffic engineering
- QoS-aware routing

---

# Learning Outcomes

This project demonstrates the implementation of several fundamental SDN controller components:

- OpenFlow packet processing
- LLDP topology discovery
- Host learning
- Network graph construction
- Shortest-path routing
- Flow rule management
- Controller-driven forwarding
- Flow statistics monitoring
- Idle flow cleanup

---

# Author

**Monil Desai**

Developed as a learning project to understand the internal working of Software Defined Networking (SDN) controllers using the POX framework.

---

# License

This project is intended for educational and academic use.