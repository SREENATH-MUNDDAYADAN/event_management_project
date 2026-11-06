"""Phase 2: manual BST keyed by event_id."""
class BSTNode:
    def __init__(self, event): self.key=int(event['event_id']); self.event=event; self.left=None; self.right=None
class EventBST:
    def __init__(self): self.root=None
    def insert(self,event):
        n=BSTNode(event)
        if self.root is None: self.root=n; return
        cur=self.root
        while True:
            if n.key < cur.key:
                if cur.left is None: cur.left=n; return
                cur=cur.left
            elif n.key > cur.key:
                if cur.right is None: cur.right=n; return
                cur=cur.right
            else: cur.event=event; return
    def search(self,key):
        cur=self.root; key=int(key)
        while cur:
            if key==cur.key: return cur.event
            cur=cur.left if key<cur.key else cur.right
        return None
    def inorder(self):
        result=[]
        def walk(n):
            if n: walk(n.left); result.append(n.event); walk(n.right)
        walk(self.root); return result
