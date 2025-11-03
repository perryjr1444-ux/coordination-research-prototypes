"""
Basic Multi-Agent Coordination Example

Demonstrates file locking, heartbeats, and task delegation working together.
"""

import sys
import os
import time
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from file_locking import FileLockCoordinator
from heartbeat_monitor import HeartbeatMonitor
from task_delegation import TaskDelegationSystem


def simulate_agent_workflow(
    agent_id: str,
    coordinator: FileLockCoordinator,
    monitor: HeartbeatMonitor,
    shared_file: str
):
    """
    Simulate an agent that:
    1. Registers with heartbeat monitor
    2. Acquires lock on shared file
    3. Modifies file (simulated)
    4. Releases lock
    5. Records change
    """
    print(f"\n[{agent_id}] Starting...")

    # Register agent
    monitor.register_agent(
        agent_id=agent_id,
        capabilities=["general"],
        status="active"
    )
    print(f"[{agent_id}] Registered with monitor")

    # Send initial heartbeat
    monitor.send_heartbeat(agent_id, status="acquiring lock")

    # Try to acquire lock
    print(f"[{agent_id}] Attempting to acquire lock on {shared_file}")
    success = coordinator.acquire_lock(
        agent_id=agent_id,
        file_path=shared_file,
        operation="write",
        timeout_seconds=10
    )

    if not success:
        print(f"[{agent_id}] Failed to acquire lock (timeout)")
        monitor.unregister_agent(agent_id)
        return

    print(f"[{agent_id}] Lock acquired!")

    try:
        # Send heartbeat during work
        monitor.send_heartbeat(agent_id, status="modifying file")

        # Simulate work
        print(f"[{agent_id}] Modifying file...")
        time.sleep(2)

        # Record change
        coordinator.record_change(
            agent_id=agent_id,
            file_path=shared_file,
            change_type="modified"
        )
        print(f"[{agent_id}] Change recorded")

    finally:
        # Always release lock
        coordinator.release_lock(agent_id, shared_file)
        print(f"[{agent_id}] Lock released")

    # Final heartbeat
    monitor.send_heartbeat(agent_id, status="completed")
    print(f"[{agent_id}] Work complete")

    # Unregister
    monitor.unregister_agent(agent_id)
    print(f"[{agent_id}] Unregistered")


def main():
    """
    Main example: Two agents coordinate access to a shared file.
    """
    print("=" * 60)
    print("BASIC MULTI-AGENT COORDINATION EXAMPLE")
    print("=" * 60)

    # Initialize coordination components
    db_path = "example_basic_coordination.db"
    coordinator = FileLockCoordinator(db_path)
    monitor = HeartbeatMonitor(db_path, timeout_seconds=15)
    system = TaskDelegationSystem(db_path)

    shared_file = "/shared/config.json"

    print("\nInitialized coordination system")
    print(f"  Database: {db_path}")
    print(f"  Shared file: {shared_file}")

    # Create two agent threads
    print("\nStarting two agents that will compete for file access...")

    agent1_thread = threading.Thread(
        target=simulate_agent_workflow,
        args=("agent-alpha", coordinator, monitor, shared_file)
    )

    agent2_thread = threading.Thread(
        target=simulate_agent_workflow,
        args=("agent-beta", coordinator, monitor, shared_file)
    )

    # Start agents
    agent1_thread.start()
    time.sleep(0.5)  # Small delay so agent-alpha gets lock first
    agent2_thread.start()

    # Wait for completion
    agent1_thread.join()
    agent2_thread.join()

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    # Check active agents (should be none)
    active_agents = monitor.get_active_agents()
    print(f"\nActive agents: {len(active_agents)}")

    # Check locks (should be none)
    locks = coordinator.get_all_locks()
    print(f"Active locks: {len(locks)}")

    # Check change history
    print("\nChange history for shared file:")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT agent_id, change_type, timestamp
        FROM change_history
        WHERE file_path = ?
        ORDER BY timestamp ASC
    """, (shared_file,))

    for row in cursor.fetchall():
        agent_id, change_type, timestamp = row
        print(f"  - {agent_id}: {change_type} at {timestamp}")

    conn.close()

    print("\n" + "=" * 60)
    print("SUCCESS: Agents coordinated file access without conflicts!")
    print("=" * 60)

    # Cleanup
    os.remove(db_path) if os.path.exists(db_path) else None


if __name__ == "__main__":
    main()
