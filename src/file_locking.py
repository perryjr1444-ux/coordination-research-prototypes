"""
File Locking Coordinator - Educational Prototype

Implements distributed mutual exclusion for file access coordination.
Based on database-backed locking with timeout mechanisms.

Research Context:
- Lamport's mutual exclusion algorithms
- Timeout-based deadlock prevention
- Fair queuing for waiting agents

NOT FOR PRODUCTION USE - EDUCATIONAL PURPOSES ONLY
"""

import sqlite3
import time
from typing import Optional, List, Dict
from datetime import datetime
import threading


class FileLockCoordinator:
    """
    Coordinates file access across multiple agents using pessimistic locking.

    Key features:
    - Exclusive locks with timeout
    - Automatic stale lock cleanup (5 minute expiration)
    - Change history tracking
    - Conflict detection
    """

    def __init__(self, db_path: str = "coordination.db"):
        """
        Initialize coordinator with SQLite database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Create necessary database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # File locks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_locks (
                file_path TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                lock_time REAL NOT NULL,
                expires_at REAL NOT NULL
            )
        """)

        # Change history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS change_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                change_type TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def acquire_lock(
        self,
        agent_id: str,
        file_path: str,
        operation: str = "write",
        timeout_seconds: int = 30
    ) -> bool:
        """
        Acquire exclusive lock on file.

        Algorithm:
        1. Check if lock exists
        2. If exists and not expired, wait or return False
        3. If expired, clean up stale lock
        4. Acquire new lock

        Args:
            agent_id: Unique agent identifier
            file_path: Absolute path to file
            operation: "read", "write", or "delete"
            timeout_seconds: Max seconds to wait for lock

        Returns:
            True if lock acquired, False if timeout
        """
        start_time = time.time()
        lock_expiration = 300  # 5 minutes in seconds

        while time.time() - start_time < timeout_seconds:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Clean up expired locks
                cursor.execute("""
                    DELETE FROM file_locks
                    WHERE expires_at < ?
                """, (time.time(),))

                # Check if lock exists
                cursor.execute("""
                    SELECT agent_id, lock_time, expires_at
                    FROM file_locks
                    WHERE file_path = ?
                """, (file_path,))

                existing_lock = cursor.fetchone()

                if existing_lock is None:
                    # No lock exists, acquire it
                    now = time.time()
                    expires_at = now + lock_expiration

                    cursor.execute("""
                        INSERT INTO file_locks (file_path, agent_id, operation, lock_time, expires_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (file_path, agent_id, operation, now, expires_at))

                    conn.commit()
                    conn.close()
                    return True

                conn.close()

            # Lock exists, wait briefly and retry
            time.sleep(0.1)

        # Timeout occurred
        return False

    def release_lock(self, agent_id: str, file_path: str) -> bool:
        """
        Release lock on file.

        Args:
            agent_id: Agent that holds the lock
            file_path: Path to file

        Returns:
            True if lock released, False if not held by this agent
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM file_locks
                WHERE file_path = ? AND agent_id = ?
            """, (file_path, agent_id))

            rows_deleted = cursor.rowcount
            conn.commit()
            conn.close()

            return rows_deleted > 0

    def record_change(
        self,
        agent_id: str,
        file_path: str,
        change_type: str
    ) -> int:
        """
        Record file change for audit trail and conflict detection.

        Args:
            agent_id: Agent that made the change
            file_path: Path to file
            change_type: "created", "modified", or "deleted"

        Returns:
            Change record ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO change_history (agent_id, file_path, change_type, timestamp)
            VALUES (?, ?, ?, ?)
        """, (agent_id, file_path, change_type, time.time()))

        change_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return change_id

    def check_conflicts(
        self,
        file_path: str,
        window_seconds: int = 300
    ) -> Optional[Dict]:
        """
        Check for recent changes by other agents (conflict detection).

        Args:
            file_path: Path to file
            window_seconds: Time window to check (default: 5 minutes)

        Returns:
            Dictionary with conflict info, or None if no conflicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_time = time.time() - window_seconds

        cursor.execute("""
            SELECT agent_id, change_type, timestamp
            FROM change_history
            WHERE file_path = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (file_path, cutoff_time))

        result = cursor.fetchone()
        conn.close()

        if result:
            agent_id, change_type, timestamp = result
            return {
                "has_conflict": True,
                "last_agent": agent_id,
                "change_type": change_type,
                "timestamp": timestamp,
                "age_seconds": time.time() - timestamp
            }

        return None

    def get_all_locks(self) -> List[Dict]:
        """
        Get all active file locks.

        Returns:
            List of lock dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clean up expired locks first
        cursor.execute("""
            DELETE FROM file_locks
            WHERE expires_at < ?
        """, (time.time(),))
        conn.commit()

        cursor.execute("""
            SELECT file_path, agent_id, operation, lock_time, expires_at
            FROM file_locks
        """)

        locks = []
        for row in cursor.fetchall():
            locks.append({
                "file_path": row[0],
                "agent_id": row[1],
                "operation": row[2],
                "lock_time": row[3],
                "expires_at": row[4],
                "age_seconds": time.time() - row[3]
            })

        conn.close()
        return locks


# Example usage
if __name__ == "__main__":
    # Initialize coordinator
    coordinator = FileLockCoordinator("example_coordination.db")

    # Simulate two agents trying to modify the same file
    print("=== File Locking Example ===\n")

    # Agent A acquires lock
    print("Agent A: Attempting to acquire lock...")
    success = coordinator.acquire_lock(
        agent_id="agent-a",
        file_path="/shared/config.json",
        operation="write",
        timeout_seconds=5
    )

    if success:
        print("Agent A: Lock acquired!")

        # Simulate work
        print("Agent A: Modifying file...")
        time.sleep(2)

        # Record change
        coordinator.record_change(
            agent_id="agent-a",
            file_path="/shared/config.json",
            change_type="modified"
        )
        print("Agent A: Change recorded")

        # Agent B tries to acquire same lock
        print("\nAgent B: Attempting to acquire lock...")
        success_b = coordinator.acquire_lock(
            agent_id="agent-b",
            file_path="/shared/config.json",
            operation="write",
            timeout_seconds=3
        )

        if not success_b:
            print("Agent B: Lock timeout (expected - Agent A still holds lock)")

        # Agent A releases lock
        coordinator.release_lock("agent-a", "/shared/config.json")
        print("\nAgent A: Lock released")

        # Agent B tries again
        print("\nAgent B: Attempting to acquire lock again...")
        success_b = coordinator.acquire_lock(
            agent_id="agent-b",
            file_path="/shared/config.json",
            operation="write",
            timeout_seconds=5
        )

        if success_b:
            print("Agent B: Lock acquired!")

            # Check for conflicts
            conflict = coordinator.check_conflicts("/shared/config.json")
            if conflict:
                print(f"Agent B: Warning - File modified by {conflict['last_agent']} "
                      f"{conflict['age_seconds']:.1f} seconds ago")

            coordinator.release_lock("agent-b", "/shared/config.json")
            print("Agent B: Lock released")

    # Show all locks (should be empty now)
    locks = coordinator.get_all_locks()
    print(f"\nActive locks: {len(locks)}")
