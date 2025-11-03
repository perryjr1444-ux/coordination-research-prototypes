"""
Heartbeat-Based Agent Liveness Monitor - Educational Prototype

Implements failure detection using periodic heartbeat signals.
Based on unreliable failure detector theory (Chandra & Toueg, 1996).

Research Context:
- Eventually perfect failure detector (◇P)
- Timeout-based liveness detection
- Graceful degradation and resource reclamation

NOT FOR PRODUCTION USE - EDUCATIONAL PURPOSES ONLY
"""

import sqlite3
import time
from typing import List, Dict, Optional
import threading


class HeartbeatMonitor:
    """
    Monitors agent liveness through periodic heartbeat signals.

    Key features:
    - Configurable timeout threshold
    - Automatic agent cleanup on timeout
    - Capability tracking for agent discovery
    - Thread-safe operations
    """

    def __init__(
        self,
        db_path: str = "coordination.db",
        timeout_seconds: int = 60
    ):
        """
        Initialize heartbeat monitor.

        Args:
            db_path: Path to SQLite database
            timeout_seconds: Heartbeat timeout threshold (default: 60s)
        """
        self.db_path = db_path
        self.timeout_seconds = timeout_seconds
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Create necessary database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Active agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_agents (
                agent_id TEXT PRIMARY KEY,
                capabilities TEXT,
                status TEXT,
                last_heartbeat REAL NOT NULL,
                registered_at REAL NOT NULL,
                workload INTEGER DEFAULT 0
            )
        """)

        conn.commit()
        conn.close()

    def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        status: str = "active"
    ) -> bool:
        """
        Register new agent in the system.

        Args:
            agent_id: Unique agent identifier
            capabilities: List of agent capabilities (e.g., ["security", "docker"])
            status: Initial status (default: "active")

        Returns:
            True if registered successfully
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = time.time()
            capabilities_str = ",".join(capabilities)

            cursor.execute("""
                INSERT OR REPLACE INTO active_agents
                (agent_id, capabilities, status, last_heartbeat, registered_at, workload)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (agent_id, capabilities_str, status, now, now, 0))

            conn.commit()
            conn.close()

            return True

    def send_heartbeat(
        self,
        agent_id: str,
        status: Optional[str] = None
    ) -> bool:
        """
        Send heartbeat signal from agent.

        This updates the last_heartbeat timestamp, indicating the agent is alive.

        Args:
            agent_id: Agent sending heartbeat
            status: Optional status update

        Returns:
            True if heartbeat recorded, False if agent not registered
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if status:
                cursor.execute("""
                    UPDATE active_agents
                    SET last_heartbeat = ?, status = ?
                    WHERE agent_id = ?
                """, (time.time(), status, agent_id))
            else:
                cursor.execute("""
                    UPDATE active_agents
                    SET last_heartbeat = ?
                    WHERE agent_id = ?
                """, (time.time(), agent_id))

            rows_updated = cursor.rowcount
            conn.commit()
            conn.close()

            return rows_updated > 0

    def get_active_agents(
        self,
        capability_filter: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get list of agents with recent heartbeat (within timeout threshold).

        Args:
            capability_filter: Optional filter by capabilities

        Returns:
            List of active agent dictionaries
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = time.time() - self.timeout_seconds

            cursor.execute("""
                SELECT agent_id, capabilities, status, last_heartbeat, registered_at, workload
                FROM active_agents
                WHERE last_heartbeat > ?
            """, (cutoff_time,))

            agents = []
            for row in cursor.fetchall():
                agent_id, caps_str, status, last_hb, registered, workload = row
                capabilities = caps_str.split(",") if caps_str else []

                # Apply capability filter if specified
                if capability_filter:
                    if not all(cap in capabilities for cap in capability_filter):
                        continue

                agents.append({
                    "agent_id": agent_id,
                    "capabilities": capabilities,
                    "status": status,
                    "last_heartbeat": last_hb,
                    "registered_at": registered,
                    "workload": workload,
                    "age_seconds": time.time() - last_hb
                })

            conn.close()
            return agents

    def cleanup_stale_agents(self) -> int:
        """
        Remove agents that haven't sent heartbeat within timeout window.

        This implements the failure detection mechanism. Agents are presumed
        dead if they haven't sent heartbeat recently.

        Returns:
            Number of agents removed
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_time = time.time() - self.timeout_seconds

            cursor.execute("""
                DELETE FROM active_agents
                WHERE last_heartbeat < ?
            """, (cutoff_time,))

            removed_count = cursor.rowcount
            conn.commit()
            conn.close()

            return removed_count

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Manually unregister agent (graceful shutdown).

        Args:
            agent_id: Agent to unregister

        Returns:
            True if agent was removed
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM active_agents
                WHERE agent_id = ?
            """, (agent_id,))

            rows_deleted = cursor.rowcount
            conn.commit()
            conn.close()

            return rows_deleted > 0

    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """
        Get detailed status of specific agent.

        Args:
            agent_id: Agent to query

        Returns:
            Agent status dictionary or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT agent_id, capabilities, status, last_heartbeat, registered_at, workload
            FROM active_agents
            WHERE agent_id = ?
        """, (agent_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            agent_id, caps_str, status, last_hb, registered, workload = row
            capabilities = caps_str.split(",") if caps_str else []

            time_since_heartbeat = time.time() - last_hb
            is_alive = time_since_heartbeat < self.timeout_seconds

            return {
                "agent_id": agent_id,
                "capabilities": capabilities,
                "status": status,
                "last_heartbeat": last_hb,
                "registered_at": registered,
                "workload": workload,
                "time_since_heartbeat": time_since_heartbeat,
                "is_alive": is_alive
            }

        return None


# Example usage
if __name__ == "__main__":
    print("=== Heartbeat Monitor Example ===\n")

    # Initialize monitor with 10-second timeout (for demo purposes)
    monitor = HeartbeatMonitor("example_coordination.db", timeout_seconds=10)

    # Register two agents
    print("Registering agents...")
    monitor.register_agent(
        agent_id="worker-01",
        capabilities=["data-processing", "analysis"],
        status="idle"
    )

    monitor.register_agent(
        agent_id="worker-02",
        capabilities=["security", "scanning"],
        status="idle"
    )

    print("Agents registered\n")

    # Simulate heartbeats
    print("Simulating heartbeats...")
    for i in range(3):
        print(f"\nIteration {i + 1}:")

        # Worker-01 sends heartbeat
        monitor.send_heartbeat("worker-01", status=f"working on task {i}")
        print("  worker-01: Heartbeat sent")

        # Worker-02 sends heartbeat only on first iteration
        if i == 0:
            monitor.send_heartbeat("worker-02", status="scanning")
            print("  worker-02: Heartbeat sent")
        else:
            print("  worker-02: No heartbeat (simulating failure)")

        # Check active agents
        active = monitor.get_active_agents()
        print(f"  Active agents: {len(active)}")
        for agent in active:
            print(f"    - {agent['agent_id']}: {agent['status']} "
                  f"(last heartbeat: {agent['age_seconds']:.1f}s ago)")

        time.sleep(3)

    # Clean up stale agents
    print("\nCleaning up stale agents...")
    removed = monitor.cleanup_stale_agents()
    print(f"Removed {removed} stale agent(s)")

    # Final status
    active = monitor.get_active_agents()
    print(f"\nFinal active agents: {len(active)}")
    for agent in active:
        print(f"  - {agent['agent_id']}")

    # Get specific agent status
    print("\nChecking worker-02 status:")
    status = monitor.get_agent_status("worker-02")
    if status:
        print(f"  Status: {status['status']}")
        print(f"  Is alive: {status['is_alive']}")
        print(f"  Time since heartbeat: {status['time_since_heartbeat']:.1f}s")
    else:
        print("  Agent not found (already cleaned up)")
