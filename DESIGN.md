# Design Notes

## Queue structure

Each service type has its own `collections.deque`. A client can therefore be
selected directly from that service's queue without scanning clients waiting
for other services. Appending a ticket and removing the oldest ticket are both
constant-time deque operations, so `call_next` takes O(1) time regardless of
how many clients are waiting across the branch.

Ticket numbers come from one counter shared by all service queues. This keeps
numbers globally sequential while each individual queue still preserves
arrival order. Ticket state is held in memory and resets when the program exits.

## Simultaneous calls

`call_next` removes the first ticket from the selected queue before returning
it. In a truly concurrent implementation, checking that the queue is non-empty
and removing its first ticket must happen as one atomic state mutation, such as
inside a lock. Otherwise, two callers could both observe the same first ticket
before either removes it. The current menu is synchronous and does not add
threading or a lock.