# Academic References

## Distributed Systems Theory

### Foundational Papers

1. **Lamport, L.** (1978). "Time, Clocks, and the Ordering of Events in a Distributed System." *Communications of the ACM*, 21(7), 558-565.
   - **Key Contribution**: Logical clocks for event ordering
   - **Relevance**: Foundation for understanding causality in distributed systems
   - **DOI**: 10.1145/359545.359563

2. **Lamport, L.** (1998). "The Part-Time Parliament." *ACM Transactions on Computer Systems*, 16(2), 133-169.
   - **Key Contribution**: Paxos consensus algorithm
   - **Relevance**: Foundation for distributed agreement protocols
   - **DOI**: 10.1145/279227.279229

3. **Ricart, G., & Agrawala, A. K.** (1981). "An optimal algorithm for mutual exclusion in computer networks." *Communications of the ACM*, 24(1), 9-17.
   - **Key Contribution**: Distributed mutual exclusion without centralized control
   - **Relevance**: Optimal message complexity for lock acquisition
   - **DOI**: 10.1145/358527.358537

### Failure Detection

4. **Chandra, T. D., & Toueg, S.** (1996). "Unreliable failure detectors for reliable distributed systems." *Journal of the ACM*, 43(2), 225-267.
   - **Key Contribution**: Hierarchy of failure detector classes
   - **Relevance**: Theoretical foundation for heartbeat-based monitoring
   - **DOI**: 10.1145/226643.226647

5. **Chen, W., Toueg, S., & Aguilera, M. K.** (2002). "On the quality of service of failure detectors." *IEEE Transactions on Computers*, 51(5), 561-580.
   - **Key Contribution**: QoS metrics for failure detection
   - **Relevance**: Calibrating timeout thresholds
   - **DOI**: 10.1109/TC.2002.1004593

### Consistency and Replication

6. **Brewer, E. A.** (2000). "Towards robust distributed systems." *Proceedings of the Nineteenth Annual ACM Symposium on Principles of Distributed Computing*, 7.
   - **Key Contribution**: CAP theorem (Consistency, Availability, Partition tolerance)
   - **Relevance**: Fundamental trade-offs in distributed systems
   - **URL**: https://people.eecs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf

7. **Vogels, W.** (2009). "Eventually consistent." *Communications of the ACM*, 52(1), 40-44.
   - **Key Contribution**: Eventual consistency models
   - **Relevance**: Alternative to strong consistency for coordination
   - **DOI**: 10.1145/1435417.1435432

### Consensus Algorithms

8. **Ongaro, D., & Ousterhout, J.** (2014). "In search of an understandable consensus algorithm." *Proceedings of USENIX Annual Technical Conference*, 305-319.
   - **Key Contribution**: Raft consensus algorithm
   - **Relevance**: More understandable alternative to Paxos
   - **URL**: https://raft.github.io/raft.pdf

9. **Castro, M., & Liskov, B.** (1999). "Practical Byzantine fault tolerance." *Proceedings of the Third Symposium on Operating Systems Design and Implementation*, 173-186.
   - **Key Contribution**: PBFT algorithm for Byzantine fault tolerance
   - **Relevance**: Handling malicious agents
   - **URL**: http://pmg.csail.mit.edu/papers/osdi99.pdf

## Multi-Agent Systems

### Textbooks

10. **Weiss, G.** (Ed.). (1999). *Multiagent Systems: A Modern Approach to Distributed AI*. MIT Press.
    - **Key Topics**: Agent architectures, coordination, negotiation
    - **Relevance**: Comprehensive overview of multi-agent theory
    - **ISBN**: 978-0262232036

11. **Wooldridge, M.** (2009). *An Introduction to MultiAgent Systems* (2nd ed.). Wiley.
    - **Key Topics**: Intelligent agents, coordination mechanisms, communication
    - **Relevance**: Standard textbook for multi-agent systems
    - **ISBN**: 978-0470519462

### Coordination and Cooperation

12. **Durfee, E. H.** (1999). "Distributed problem solving and planning." In G. Weiss (Ed.), *Multiagent Systems*, 121-164. MIT Press.
    - **Key Contribution**: Distributed planning algorithms
    - **Relevance**: Task decomposition and allocation

13. **Smith, R. G.** (1980). "The contract net protocol: High-level communication and control in a distributed problem solver." *IEEE Transactions on Computers*, C-29(12), 1104-1113.
    - **Key Contribution**: Contract Net Protocol for task allocation
    - **Relevance**: Market-based coordination mechanism
    - **DOI**: 10.1109/TC.1980.1675516

### Resource Allocation

14. **Chevaleyre, Y., Dunne, P. E., Endriss, U., et al.** (2006). "Issues in multiagent resource allocation." *Informatica*, 30(1), 3-31.
    - **Key Contribution**: Survey of resource allocation problems
    - **Relevance**: Task delegation and resource management
    - **URL**: https://www.illc.uva.nl/Research/Publications/Reports/PP-2006-19.text.pdf

15. **Gerkey, B. P., & Matarić, M. J.** (2004). "A formal analysis and taxonomy of task allocation in multi-robot systems." *The International Journal of Robotics Research*, 23(9), 939-954.
    - **Key Contribution**: Taxonomy of task allocation approaches
    - **Relevance**: Systematic comparison of allocation strategies
    - **DOI**: 10.1177/0278364904045564

## AI Agent Security

### Recent Work on LLM Agents

16. **Pasquini, D., Kornaropoulos, E. M., & Ateniese, G.** (2024). "Hacking Back the AI-Hacker: Prompt Injection as a Defense Against LLM-driven Cyberattacks." *arXiv preprint arXiv:2410.20911*.
    - **Key Contribution**: Using prompt injection defensively
    - **Relevance**: Security considerations for AI agent coordination
    - **URL**: https://arxiv.org/abs/2410.20911

17. **Greshake, K., Abdelnabi, S., Mishra, S., et al.** (2023). "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection." *Proceedings of the 2023 ACM Workshop on Secure and Trustworthy Deep Learning Systems*, 79-90.
    - **Key Contribution**: Indirect prompt injection attacks
    - **Relevance**: Security vulnerabilities in LLM agents
    - **DOI**: 10.1145/3605764.3623985

18. **Perez, F., & Ribeiro, I.** (2022). "Ignore Previous Prompt: Attack Techniques For Language Models." *arXiv preprint arXiv:2211.09527*.
    - **Key Contribution**: Taxonomy of prompt injection attacks
    - **Relevance**: Understanding attack vectors
    - **URL**: https://arxiv.org/abs/2211.09527

## Implementation References

### Database Systems

19. **Hipp, R. D.** (2020). "SQLite: The Database at the Edge of the Network." *Communications of the ACM*, 63(10), 66-73.
    - **Key Contribution**: SQLite design and use cases
    - **Relevance**: Understanding database choice trade-offs
    - **DOI**: 10.1145/3416508

20. **Bernstein, P. A., & Goodman, N.** (1981). "Concurrency control in distributed database systems." *ACM Computing Surveys*, 13(2), 185-221.
    - **Key Contribution**: Survey of concurrency control mechanisms
    - **Relevance**: Locking protocols and isolation levels
    - **DOI**: 10.1145/356842.356846

### Distributed Coordination Services

21. **Hunt, P., Konar, M., Junqueira, F. P., & Reed, B.** (2010). "ZooKeeper: Wait-free coordination for Internet-scale systems." *Proceedings of the 2010 USENIX Annual Technical Conference*, 11.
    - **Key Contribution**: Production coordination service
    - **Relevance**: Real-world implementation of coordination primitives
    - **URL**: https://www.usenix.org/legacy/event/atc10/tech/full_papers/Hunt.pdf

22. **Burrows, M.** (2006). "The Chubby lock service for loosely-coupled distributed systems." *Proceedings of the 7th Symposium on Operating Systems Design and Implementation*, 335-350.
    - **Key Contribution**: Google's distributed lock service
    - **Relevance**: Production-scale coordination at Google
    - **URL**: https://research.google/pubs/pub27897/

## Software Engineering

### Concurrent Programming

23. **Herlihy, M., & Shavit, N.** (2012). *The Art of Multiprocessor Programming* (2nd ed.). Morgan Kaufmann.
    - **Key Topics**: Concurrent data structures, synchronization
    - **Relevance**: Thread-safe coordination implementations
    - **ISBN**: 978-0123973375

24. **Goetz, B., Peierls, T., Bloch, J., et al.** (2006). *Java Concurrency in Practice*. Addison-Wesley.
    - **Key Topics**: Concurrency patterns, thread safety
    - **Relevance**: Best practices for concurrent systems
    - **ISBN**: 978-0321349606

## Online Resources

### Distributed Systems

- **MIT 6.824: Distributed Systems** - http://nil.csail.mit.edu/6.824/
  - Comprehensive course on distributed systems fundamentals

- **Distributed Systems Reading Group** - https://dsrg.pdos.csail.mit.edu/
  - Curated list of important papers

### Multi-Agent Systems

- **AAMAS Conference Proceedings** - https://www.ifaamas.org/
  - International Conference on Autonomous Agents and Multiagent Systems

- **JAIR: Journal of Artificial Intelligence Research** - https://jair.org/
  - High-quality AI research papers

### Code Examples

- **Raft Consensus Implementations** - https://raft.github.io/
  - Reference implementations of Raft in various languages

- **etcd Documentation** - https://etcd.io/
  - Distributed key-value store with coordination primitives

## Citation Format

For use in academic papers:

```bibtex
@misc{coordination-research-prototypes,
  title={Multi-Agent Coordination Theory: Research Prototypes},
  author={Research Contributor},
  year={2025},
  publisher={GitHub},
  howpublished={\url{https://github.com/yourusername/coordination-research-prototypes}}
}

@article{lamport1978time,
  title={Time, clocks, and the ordering of events in a distributed system},
  author={Lamport, Leslie},
  journal={Communications of the ACM},
  volume={21},
  number={7},
  pages={558--565},
  year={1978},
  publisher={ACM New York, NY, USA}
}

@article{chandra1996unreliable,
  title={Unreliable failure detectors for reliable distributed systems},
  author={Chandra, Tushar Deepak and Toueg, Sam},
  journal={Journal of the ACM (JACM)},
  volume={43},
  number={2},
  pages={225--267},
  year={1996},
  publisher={ACM New York, NY, USA}
}

@misc{pasquini2024hacking,
  title={Hacking Back the AI-Hacker: Prompt Injection as a Defense Against LLM-driven Cyberattacks},
  author={Pasquini, Dario and Kornaropoulos, Evgenios M and Ateniese, Giuseppe},
  journal={arXiv preprint arXiv:2410.20911},
  year={2024}
}
```
