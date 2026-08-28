class DNCService:
    def __init__(self): self.items=set()
    def n(self,p): return "".join(c for c in p.strip() if c.isdigit() or c=="+")
    def add(self,p): self.items.add(self.n(p))
    def remove(self,p): self.items.discard(self.n(p))
    def contains(self,p): return self.n(p) in self.items
dnc=DNCService()
