from collections import deque
import heapq

def get_graph(users):
    """
    Constrói um grafo de adjacência a partir da lista de usuários.
    """
    graph = {}
    for user in users:
        graph[user.id] = [amigo.id for amigo in user.amigos]
    return graph

def bfs_distance(graph, start_node, target_node):
    """
    Encontra a menor distância (número de passos) entre dois usuários usando BFS.
    """
    if start_node == target_node:
        return 0
    
    visited = {start_node}
    queue = deque([(start_node, 0)])
    
    while queue:
        current, dist = queue.popleft()
        
        if current == target_node:
            return dist
            
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
                
    return float('inf')

def suggest_friends_of_friends(graph, start_node):
    """
    Sugere amigos de amigos que ainda não são amigos diretos usando BFS (nível 2).
    """
    direct_friends = set(graph.get(start_node, []))
    suggestions = {}
    
    for friend in direct_friends:
        for fof in graph.get(friend, []):
            if fof != start_node and fof not in direct_friends:
                suggestions[fof] = suggestions.get(fof, 0) + 1
                
    # Retorna lista de IDs ordenados por quantos amigos em comum possuem
    sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
    return [s[0] for s in sorted_suggestions]

def dijkstra_interest_distance(users, start_node_id, target_node_id):
    """
    Calcula o menor caminho ponderado entre dois usuários usando Dijkstra.
    O peso da aresta é inversamente proporcional ao número de interesses em comum.
    """
    user_map = {u.id: u for u in users}
    
    # Adjacência com pesos
    adj = {}
    for u in users:
        adj[u.id] = []
        u_interests = set(i.nome for i in u.interesses)
        u_skills = set(h.nome for h in u.habilidades)
        
        for amigo in u.amigos:
            amigo_interests = set(i.nome for i in amigo.interesses)
            amigo_skills = set(h.nome for h in amigo.habilidades)
            
            common_interests = len(u_interests & amigo_interests)
            common_skills = len(u_skills & amigo_skills)
            
            # Peso inicial é 10 (se apenas se seguem ou são amigos).
            # Cada interesse ou habilidade em comum diminui 1 no peso.
            weight = max(1, 10 - (common_interests + common_skills))
            adj[u.id].append((amigo.id, weight))

    distances = {u.id: float('inf') for u in users}
    distances[start_node_id] = 0
    pq = [(0, start_node_id)]
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        if current_dist > distances[current_node]:
            continue
            
        if current_node == target_node_id:
            return current_dist
            
        for neighbor, weight in adj.get(current_node, []):
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
                
    return float('inf')

def find_communities(users):
    """
    Identifica comunidades (Componentes Conectados) usando DFS.
    """
    graph = get_graph(users)
    visited = set()
    communities = []
    
    for user in users:
        if user.id not in visited:
            component = []
            stack = [user.id]
            visited.add(user.id)
            
            while stack:
                curr = stack.pop()
                component.append(curr)
                
                for neighbor in graph.get(curr, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)
            communities.append(component)
            
    return communities

def who_can_help(users, start_node_id, skill_name):
    """
    Sugere usuários até 3 graus de distância que possuam a habilidade necessária.
    Usa BFS limitado a profundidade 3.
    """
    graph = get_graph(users)
    user_map = {u.id: u for u in users}
    
    visited = {start_node_id}
    queue = deque([(start_node_id, 0)])
    results = []
    
    while queue:
        current, dist = queue.popleft()
        
        if dist > 0: # Não sugere a si mesmo
            user = user_map.get(current)
            if user and any(h.nome.lower() == skill_name.lower() for h in user.habilidades):
                results.append((current, dist))
        
        if dist < 3:
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
                    
    return results
