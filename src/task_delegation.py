"""
Task Delegation System - Educational Prototype

Implements work distribution patterns for multi-agent systems.
Combines priority queuing, capability matching, and workload balancing.

Research Context:
- Task allocation in multi-agent systems (Weiss, 1999)
- Priority-based scheduling
- Capability-based routing

NOT FOR PRODUCTION USE - EDUCATIONAL PURPOSES ONLY
"""

import sqlite3
import time
import uuid
from typing import List, Dict, Optional
import threading


class TaskDelegationSystem:
    """
    Manages task distribution across multiple agents.

    Key features:
    - Priority-based task queuing (1 = highest, 10 = lowest)
    - Capability matching for task assignment
    - Workload balancing (assigns to least-busy agent)
    - Task lifecycle tracking (pending → claimed → completed)
    """

    def __init__(self, db_path: str = "coordination.db"):
        """
        Initialize task delegation system.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Create necessary database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS delegated_tasks (
                task_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                description TEXT NOT NULL,
                required_capabilities TEXT,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                parent_agent_id TEXT,
                assigned_agent_id TEXT,
                created_at REAL NOT NULL,
                claimed_at REAL,
                completed_at REAL,
                result TEXT,
                success INTEGER DEFAULT 1
            )
        """)

        # Active agents table (if not exists)
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

    def delegate_task(
        self,
        description: str,
        task_type: str,
        required_capabilities: Optional[List[str]] = None,
        priority: int = 5,
        parent_agent_id: Optional[str] = None
    ) -> Dict:
        """
        Delegate task to capable agent with lowest workload.

        Algorithm:
        1. Generate unique task ID
        2. Find agents matching required capabilities
        3. Select agent with lowest workload
        4. Assign task and increment workload

        Args:
            description: Detailed task description
            task_type: Task type (e.g., "security-audit", "data-processing")
            required_capabilities: Required agent capabilities
            priority: Priority level (1 = highest, 10 = lowest)
            parent_agent_id: Agent delegating this task

        Returns:
            Dictionary with task_id, assigned_agent, and status
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Generate task ID
            task_id = f"task-{uuid.uuid4().hex[:12]}"
            now = time.time()

            # Find capable agents
            if required_capabilities:
                # Get active agents (heartbeat within 60 seconds)
                cutoff_time = now - 60
                cursor.execute("""
                    SELECT agent_id, capabilities, workload
                    FROM active_agents
                    WHERE last_heartbeat > ?
                    ORDER BY workload ASC
                """, (cutoff_time,))

                agents = cursor.fetchall()

                # Filter by capabilities
                capable_agents = []
                for agent_id, caps_str, workload in agents:
                    agent_caps = caps_str.split(",") if caps_str else []
                    if all(cap in agent_caps for cap in required_capabilities):
                        capable_agents.append((agent_id, workload))

                # Select agent with lowest workload
                if capable_agents:
                    assigned_agent = capable_agents[0][0]
                    status = "pending"

                    # Increment workload
                    cursor.execute("""
                        UPDATE active_agents
                        SET workload = workload + 1
                        WHERE agent_id = ?
                    """, (assigned_agent,))
                else:
                    # No capable agents available
                    assigned_agent = None
                    status = "pending"
            else:
                # No capability requirements
                assigned_agent = None
                status = "pending"

            # Insert task
            caps_str = ",".join(required_capabilities) if required_capabilities else ""
            cursor.execute("""
                INSERT INTO delegated_tasks
                (task_id, task_type, description, required_capabilities, priority,
                 status, parent_agent_id, assigned_agent_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (task_id, task_type, description, caps_str, priority,
                  status, parent_agent_id, assigned_agent, now))

            conn.commit()
            conn.close()

            return {
                "task_id": task_id,
                "assigned_agent": assigned_agent,
                "status": status,
                "message": "Task delegated successfully"
            }

    def claim_task(self, task_id: str, agent_id: str) -> bool:
        """
        Agent claims a pending task.

        Args:
            task_id: Task to claim
            agent_id: Agent claiming the task

        Returns:
            True if claim successful
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update task status
            cursor.execute("""
                UPDATE delegated_tasks
                SET status = 'claimed', claimed_at = ?
                WHERE task_id = ? AND (assigned_agent_id = ? OR assigned_agent_id IS NULL)
            """, (time.time(), task_id, agent_id))

            # If task wasn't assigned, update assignment
            cursor.execute("""
                UPDATE delegated_tasks
                SET assigned_agent_id = ?
                WHERE task_id = ? AND assigned_agent_id IS NULL
            """, (agent_id, task_id))

            rows_updated = cursor.rowcount
            conn.commit()
            conn.close()

            return rows_updated > 0

    def complete_task(
        self,
        task_id: str,
        result: str,
        success: bool = True
    ) -> bool:
        """
        Mark task as completed.

        Args:
            task_id: Task to complete
            result: Task result (JSON string or text)
            success: Whether task completed successfully

        Returns:
            True if task marked complete
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update task
            cursor.execute("""
                UPDATE delegated_tasks
                SET status = ?, completed_at = ?, result = ?, success = ?
                WHERE task_id = ?
            """, ("completed" if success else "failed",
                  time.time(), result, 1 if success else 0, task_id))

            rows_updated = cursor.rowcount

            # Decrement agent workload
            cursor.execute("""
                UPDATE active_agents
                SET workload = workload - 1
                WHERE agent_id = (
                    SELECT assigned_agent_id FROM delegated_tasks WHERE task_id = ?
                )
            """, (task_id,))

            conn.commit()
            conn.close()

            return rows_updated > 0

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get current status of task.

        Args:
            task_id: Task to query

        Returns:
            Task status dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT task_id, task_type, description, required_capabilities,
                   priority, status, parent_agent_id, assigned_agent_id,
                   created_at, claimed_at, completed_at, result, success
            FROM delegated_tasks
            WHERE task_id = ?
        """, (task_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "task_id": row[0],
                "task_type": row[1],
                "description": row[2],
                "required_capabilities": row[3].split(",") if row[3] else [],
                "priority": row[4],
                "status": row[5],
                "parent_agent_id": row[6],
                "assigned_agent_id": row[7],
                "created_at": row[8],
                "claimed_at": row[9],
                "completed_at": row[10],
                "result": row[11],
                "success": bool(row[12])
            }

        return None

    def list_tasks(
        self,
        status_filter: Optional[str] = None,
        priority_order: bool = True
    ) -> List[Dict]:
        """
        List all tasks with optional filtering.

        Args:
            status_filter: Filter by status ("pending", "claimed", "completed")
            priority_order: Order by priority (highest first)

        Returns:
            List of task dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT task_id, task_type, description, priority, status, assigned_agent_id, created_at FROM delegated_tasks"

        if status_filter:
            query += f" WHERE status = ?"
            params = (status_filter,)
        else:
            params = ()

        if priority_order:
            query += " ORDER BY priority ASC, created_at ASC"
        else:
            query += " ORDER BY created_at DESC"

        cursor.execute(query, params)

        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                "task_id": row[0],
                "task_type": row[1],
                "description": row[2],
                "priority": row[3],
                "status": row[4],
                "assigned_agent_id": row[5],
                "created_at": row[6]
            })

        conn.close()
        return tasks


# Example usage
if __name__ == "__main__":
    print("=== Task Delegation Example ===\n")

    # Initialize system
    system = TaskDelegationSystem("example_coordination.db")

    # Register some agents first
    conn = sqlite3.connect("example_coordination.db")
    cursor = conn.cursor()

    # Clean up old data
    cursor.execute("DELETE FROM active_agents")
    cursor.execute("DELETE FROM delegated_tasks")

    # Register agents
    now = time.time()
    cursor.execute("""
        INSERT INTO active_agents (agent_id, capabilities, status, last_heartbeat, registered_at, workload)
        VALUES
        ('security-agent-01', 'security,code-analysis', 'active', ?, ?, 0),
        ('docker-agent-01', 'docker,deployment', 'active', ?, ?, 0),
        ('general-agent-01', 'general', 'active', ?, ?, 0)
    """, (now, now, now, now, now, now))
    conn.commit()
    conn.close()

    print("Registered 3 agents\n")

    # Delegate high-priority security task
    print("Delegating security audit task (priority 1)...")
    task1 = system.delegate_task(
        description="Analyze authentication module for vulnerabilities",
        task_type="security-audit",
        required_capabilities=["security", "code-analysis"],
        priority=1
    )
    print(f"  Task ID: {task1['task_id']}")
    print(f"  Assigned to: {task1['assigned_agent']}")

    # Delegate Docker task
    print("\nDelegating Docker build task (priority 3)...")
    task2 = system.delegate_task(
        description="Build and push Docker image",
        task_type="docker-build",
        required_capabilities=["docker"],
        priority=3
    )
    print(f"  Task ID: {task2['task_id']}")
    print(f"  Assigned to: {task2['assigned_agent']}")

    # List pending tasks
    print("\nPending tasks (ordered by priority):")
    tasks = system.list_tasks(status_filter="pending", priority_order=True)
    for task in tasks:
        print(f"  - [{task['priority']}] {task['task_type']}: {task['description'][:50]}...")

    # Claim and complete first task
    print(f"\nAgent {task1['assigned_agent']} claiming task...")
    system.claim_task(task1['task_id'], task1['assigned_agent'])

    print("Agent performing security audit...")
    time.sleep(1)

    result = {
        "vulnerabilities": 2,
        "critical": 0,
        "high": 1,
        "medium": 1,
        "details": ["Weak password validation", "Missing rate limiting"]
    }

    import json
    system.complete_task(task1['task_id'], json.dumps(result), success=True)
    print("Task completed successfully")

    # Check task status
    print(f"\nTask status for {task1['task_id']}:")
    status = system.get_task_status(task1['task_id'])
    print(f"  Status: {status['status']}")
    print(f"  Success: {status['success']}")
    print(f"  Result: {status['result'][:100]}...")

    # List all tasks
    print("\nAll tasks:")
    all_tasks = system.list_tasks()
    for task in all_tasks:
        print(f"  - {task['status']}: {task['task_type']}")
