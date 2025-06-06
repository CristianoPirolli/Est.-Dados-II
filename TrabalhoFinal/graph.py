import collections

class Graph:
    def __init__(self):
        self.adj = collections.defaultdict(list)
        self.vertices = set()

    def add_vertex(self, vertex_name):
        if vertex_name not in self.vertices:
            self.vertices.add(vertex_name)
            self.adj[vertex_name] = []

    def add_edge(self, u, v, weight, bidirectional=True):
        if u not in self.vertices:
            self.add_vertex(u)
        if v not in self.vertices:
            self.add_vertex(v)

        self.adj[u].append({'node': v, 'weight': weight})
        if bidirectional:
            self.adj[v].append({'node': u, 'weight': weight})

    def get_neighbors(self, vertex):
        return self.adj.get(vertex, [])

    def get_vertices(self):
        return list(self.vertices)

    def __str__(self):
        output = []
        for vertex in self.adj:
            output.append(f"{vertex}:")
            for edge in self.adj[vertex]:
                output.append(f" -> {edge['node']} (peso: {edge['weight']})")
        return "\n".join(output)

