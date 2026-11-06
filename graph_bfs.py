"""Phase 4: adjacency-list graph and manual BFS for venue connections."""
from collections import deque
class VenueGraph:
    def __init__(self): self.adj={}
    def add_vertex(self, name): self.adj.setdefault(name, [])
    def add_edge(self, a, b):
        self.add_vertex(a); self.add_vertex(b)
        if b not in self.adj[a]: self.adj[a].append(b)
        if a not in self.adj[b]: self.adj[b].append(a)
    def bfs(self, start):
        if start not in self.adj: return []
        seen={start}; q=deque([start]); order=[]
        while q:
            v=q.popleft(); order.append(v)
            for nxt in self.adj[v]:
                if nxt not in seen: seen.add(nxt); q.append(nxt)
        return order
