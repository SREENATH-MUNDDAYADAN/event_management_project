"""Phase 1: manually implemented singly linked list for event display/management."""
class Node:
    def __init__(self, event):
        self.event = event
        self.next = None

class EventLinkedList:
    def __init__(self): self.head = None
    def insert(self, event):
        node = Node(event)
        if self.head is None: self.head = node; return
        cur = self.head
        while cur.next: cur = cur.next
        cur.next = node
    def delete(self, event_id):
        prev, cur = None, self.head
        while cur:
            if int(cur.event['event_id']) == int(event_id):
                if prev: prev.next = cur.next
                else: self.head = cur.next
                return True
            prev, cur = cur, cur.next
        return False
    def to_list(self):
        out, cur = [], self.head
        while cur: out.append(cur.event); cur = cur.next
        return out
