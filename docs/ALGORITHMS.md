# Coordination Algorithms

This document describes the key algorithms implemented in this research repository.

## 1. Database-Backed File Locking

### Algorithm: Pessimistic Locking with Timeout

**Purpose**: Prevent concurrent modifications to shared resources (files)

**Approach**: Pessimistic (acquire lock before access)

**Key Properties**:
- **Mutual Exclusion**: Only one agent holds lock at a time
- **Deadlock Prevention**: Automatic timeout after 5 minutes
- **Fairness**: FIFO ordering for waiting agents (via retry loop)

**Pseudocode**:

```
function acquire_lock(agent_id, file_path, timeout):
    start_time = current_time()

    while current_time() - start_time < timeout:
        with database_lock:
            # Clean up expired locks
            delete_locks_where(expires_at < current_time())

            # Check if lock exists
            existing_lock = get_lock(file_path)

            if existing_lock is None:
                # Acquire lock
                insert_lock(file_path, agent_id, expires_at=current_time() + 300)
                return True

        # Wait briefly before retry
        sleep(0.1 seconds)

    return False  # Timeout
```

**Time Complexity**: O(n) where n = timeout / retry_interval

**Space Complexity**: O(1) per lock

**Inspiration**: Lamport's Bakery Algorithm, simplified for database context

### Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Pessimistic Locking** | Simple, prevents conflicts | Can block for long periods |
| **Optimistic Locking** | Higher throughput | Requires conflict resolution |
| **Distributed Locks** | Network-aware | Complex, requires consensus |

We chose pessimistic locking for simplicity and educational clarity.

---

## 2. Heartbeat-Based Failure Detection

### Algorithm: Timeout-Based Liveness Monitoring

**Purpose**: Detect when agents have failed or become unavailable

**Approach**: Eventually perfect failure detector (◇P)

**Key Properties**:
- **Strong Completeness**: Every crashed agent is eventually suspected
- **Eventual Strong Accuracy**: No correct agent is suspected infinitely often
- **Configurable Timeout**: Balance between false positives and detection speed

**Pseudocode**:

```
function send_heartbeat(agent_id):
    with database_lock:
        update_agent(agent_id, last_heartbeat=current_time())

function get_active_agents(timeout_threshold):
    cutoff_time = current_time() - timeout_threshold
    return select_agents_where(last_heartbeat > cutoff_time)

function cleanup_stale_agents(timeout_threshold):
    cutoff_time = current_time() - timeout_threshold
    return delete_agents_where(last_heartbeat < cutoff_time)
```

**Time Complexity**:
- `send_heartbeat`: O(1)
- `get_active_agents`: O(n) where n = total agents
- `cleanup_stale_agents`: O(n)

**Space Complexity**: O(n) where n = number of agents

**Inspiration**: Chandra & Toueg's failure detector hierarchy

### Timeout Calibration

The timeout threshold should balance two concerns:

1. **False Positives**: Too short → healthy agents marked as failed
2. **Detection Delay**: Too long → slow failure detection

**Recommended**: 2-3x the expected heartbeat interval

Example:
- Heartbeat every 30 seconds
- Timeout threshold: 60-90 seconds

---

## 3. Priority-Based Task Delegation

### Algorithm: Capability Matching + Workload Balancing

**Purpose**: Distribute tasks to capable agents while balancing load

**Approach**: Greedy assignment to least-loaded capable agent

**Key Properties**:
- **Capability Matching**: Only agents with required skills can receive task
- **Workload Balancing**: Prefer agents with fewer active tasks
- **Priority Ordering**: High-priority tasks execute first

**Pseudocode**:

```
function delegate_task(description, required_capabilities, priority):
    with database_lock:
        # Find capable agents
        active_agents = get_active_agents()
        capable_agents = []

        for agent in active_agents:
            if has_all_capabilities(agent, required_capabilities):
                capable_agents.append((agent, agent.workload))

        if capable_agents.is_empty():
            # Queue for later
            create_task(status="pending", assigned_agent=None)
            return

        # Select agent with lowest workload
        capable_agents.sort_by_workload()
        selected_agent = capable_agents[0]

        # Assign task
        create_task(status="pending", assigned_agent=selected_agent)
        increment_workload(selected_agent)

        return task_id
```

**Time Complexity**: O(n \* m) where:
- n = number of agents
- m = average capabilities per agent

**Space Complexity**: O(k) where k = number of tasks

**Inspiration**: Resource allocation algorithms from operating systems

### Scheduling Policies

This implementation uses **greedy workload balancing**, but other policies are possible:

| Policy | Description | Use Case |
|--------|-------------|----------|
| **Round-Robin** | Rotate through agents | Fair distribution |
| **Workload Balancing** | Minimize variance in load | Prevent bottlenecks |
| **Priority Queuing** | High-priority tasks first | SLA guarantees |
| **Capability Matching** | Route by specialization | Expert systems |

---

## 4. Task Dependency Resolution

### Algorithm: Topological Sort for Task Graphs

**Purpose**: Execute tasks in correct order when dependencies exist

**Approach**: Dependency graph with topological ordering

**Key Properties**:
- **Acyclic**: Circular dependencies rejected
- **Ordered Execution**: Dependencies complete before dependents
- **Parallel Execution**: Independent tasks can run concurrently

**Pseudocode**:

```
function create_task_graph(tasks_with_dependencies):
    # Build adjacency list
    graph = {}
    in_degree = {}

    for task in tasks:
        graph[task.id] = task.dependencies
        in_degree[task.id] = len(task.dependencies)

    # Topological sort (Kahn's algorithm)
    queue = [task for task in tasks if in_degree[task.id] == 0]
    execution_order = []

    while queue.is_not_empty():
        task = queue.dequeue()
        execution_order.append(task)

        # Decrement in-degree for dependents
        for dependent in graph[task.id]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.enqueue(dependent)

    if len(execution_order) != len(tasks):
        raise Error("Circular dependency detected")

    return execution_order
```

**Time Complexity**: O(V + E) where:
- V = number of tasks (vertices)
- E = number of dependencies (edges)

**Space Complexity**: O(V + E)

**Inspiration**: Kahn's algorithm for topological sorting

---

## 5. Conflict Detection via Change History

### Algorithm: Time-Window Based Conflict Check

**Purpose**: Warn when file was recently modified by another agent

**Approach**: Query change history within time window

**Key Properties**:
- **Configurable Window**: Default 5 minutes
- **Non-Blocking**: Check doesn't prevent access, just warns
- **Audit Trail**: Full history of changes maintained

**Pseudocode**:

```
function check_conflicts(file_path, window_seconds):
    cutoff_time = current_time() - window_seconds

    recent_changes = select_changes_where(
        file_path = file_path AND
        timestamp > cutoff_time
    )

    if recent_changes.is_not_empty():
        last_change = recent_changes[0]
        return {
            has_conflict: True,
            last_agent: last_change.agent_id,
            change_type: last_change.change_type,
            age_seconds: current_time() - last_change.timestamp
        }

    return {has_conflict: False}
```

**Time Complexity**: O(log n) with index on (file_path, timestamp)

**Space Complexity**: O(h) where h = history size (grows unbounded)

**Optimization**: Periodically archive old change history

---

## Implementation Trade-offs

### Database Choice: SQLite

**Pros**:
- Simple, no server required
- ACID transactions
- Portable (single file)
- Good for single-machine coordination

**Cons**:
- Limited concurrency (one writer at a time)
- Not network-distributed
- No built-in replication

**For Production**: Consider PostgreSQL, Redis, or etcd for distributed coordination

### Threading Model

This implementation uses:
- **Lock-based synchronization** (Python `threading.Lock`)
- **Blocking database operations**

**Alternative**: Async/await with connection pooling for higher throughput

---

## Future Algorithm Extensions

### 1. Byzantine Fault Tolerance

Handle malicious or misbehaving agents:
- **PBFT (Practical Byzantine Fault Tolerance)**: Consensus despite <1/3 malicious nodes
- **Signature-based verification**: Cryptographically verify agent actions

### 2. Distributed Consensus

For multi-machine coordination:
- **Raft**: Leader-based consensus
- **Paxos**: Classic consensus algorithm
- **ZooKeeper**: Production-ready coordination service

### 3. Optimistic Locking

Alternative to pessimistic locks:
- Version numbers or timestamps
- Detect conflicts on commit
- Automatic retry on conflict

### 4. Resource Quotas

Prevent resource exhaustion:
- CPU/memory reservations
- Rate limiting per agent
- Fair queuing algorithms

---

## References

1. Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System."
2. Ricart, G., & Agrawala, A. K. (1981). "An optimal algorithm for mutual exclusion."
3. Chandra, T. D., & Toueg, S. (1996). "Unreliable failure detectors for reliable distributed systems."
4. Kahn, A. B. (1962). "Topological sorting of large networks."
5. Brewer, E. A. (2000). "Towards robust distributed systems." (CAP theorem)
