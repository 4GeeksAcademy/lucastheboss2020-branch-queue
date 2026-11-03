from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone


SERVICE_TYPES = ("deposit", "withdrawal", "account_management")


@dataclass(frozen=True)
class Ticket:
    number: int
    client_name: str
    service_type: str
    issued_at: datetime


class BranchQueue:
    def __init__(self):
        self._queues = {service: deque() for service in SERVICE_TYPES}
        self._next_ticket_number = 1

    def _get_queue(self, service_type):
        if not isinstance(service_type, str) or service_type not in self._queues:
            allowed = ", ".join(SERVICE_TYPES)
            raise ValueError(f"Invalid service type. Choose one of: {allowed}.")
        return self._queues[service_type]

    def issue_ticket(self, client_name, service_type):
        queue = self._get_queue(service_type)
        if not isinstance(client_name, str) or not client_name.strip():
            raise ValueError("Client name cannot be empty.")

        ticket = Ticket(
            number=self._next_ticket_number,
            client_name=client_name.strip(),
            service_type=service_type,
            issued_at=datetime.now(timezone.utc),
        )
        queue.append(ticket)
        self._next_ticket_number += 1
        return ticket

    def call_next(self, service_type):
        queue = self._get_queue(service_type)
        if not queue:
            raise ValueError(f"No clients are waiting for {service_type}.")
        return queue.popleft()

    def peek_next(self, service_type):
        queue = self._get_queue(service_type)
        if not queue:
            raise ValueError(f"No clients are waiting for {service_type}.")
        return queue[0]

    def list_waiting(self):
        return {
            service: list(queue)
            for service, queue in self._queues.items()
        }

    def stats(self):
        counts = {service: len(queue) for service, queue in self._queues.items()}
        counts["total"] = sum(counts.values())
        return counts


def _format_ticket(ticket):
    timestamp = ticket.issued_at.isoformat(timespec="seconds")
    return (
        f"Ticket #{ticket.number}: {ticket.client_name} "
        f"({ticket.service_type}) at {timestamp}"
    )


def _print_waiting(queue_manager):
    waiting = queue_manager.list_waiting()
    for service, tickets in waiting.items():
        print(f"\n{service.replace('_', ' ').title()}:")
        if tickets:
            for ticket in tickets:
                print(f"  {_format_ticket(ticket)}")
        else:
            print("  No clients waiting.")


def _print_stats(queue_manager):
    counts = queue_manager.stats()
    print("\nWaiting clients:")
    for service in SERVICE_TYPES:
        print(f"  {service.replace('_', ' ').title()}: {counts[service]}")
    print(f"  Total: {counts['total']}")


def main():
    queue_manager = BranchQueue()
    menu = (
        "\nBranch Service Queue Manager\n"
        "1. Issue a ticket\n"
        "2. Call next client\n"
        "3. View waiting list\n"
        "4. View queue stats\n"
        "5. Exit"
    )

    try:
        while True:
            print(menu)
            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    client_name = input("Client name: ")
                    service_type = input(
                        "Service (deposit, withdrawal, account_management): "
                    ).strip()
                    ticket = queue_manager.issue_ticket(client_name, service_type)
                    print(f"Issued {_format_ticket(ticket)}")
                elif choice == "2":
                    service_type = input("Service type: ").strip()
                    ticket = queue_manager.call_next(service_type)
                    print(f"Now serving {_format_ticket(ticket)}")
                elif choice == "3":
                    _print_waiting(queue_manager)
                elif choice == "4":
                    _print_stats(queue_manager)
                elif choice == "5":
                    print("Goodbye.")
                    return
                else:
                    print("Invalid option. Choose a number from 1 to 5.")
            except ValueError as error:
                print(f"Error: {error}")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")


if __name__ == "__main__":
    main()