# Documentação de Grafos — Rede DBQP

## Sumário

1. [Introdução](#1-introdução)
2. [Modelagem do Grafo (Usuários e Conexões)](#2-modelagem-do-grafo-usuários-e-conexões)
3. [Algoritmos de Exploração (BFS)](#3-algoritmos-de-exploração-bfs)
4. [Otimização de Caminhos (Dijkstra)](#4-otimização-de-caminhos-dijkstra)
5. [Estruturas e Comunidades (DFS)](#5-estruturas-e-comunidades-dfs)
6. [Dependências e Ordem (DAG)](#6-dependências-e-ordem-dag)
7. [Visualização com vis.js](#7-visualização-com-visjs)

---

## 1. Introdução

A Rede DBQP utiliza a **Teoria dos Grafos** para gerenciar relacionamentos, analisar a estrutura da rede e fornecer ferramentas de inteligência para os usuários. Abaixo, detalhamos como os conceitos acadêmicos foram aplicados na prática.

---

## 2. Modelagem do Grafo (Usuários e Conexões)

**Onde é utilizado:** Em toda a base de dados e na visualização da rede.

**Como:** 
- **Vértices (Nós):** Representam os usuários (`Registro`).
- **Arestas (Links):** Representam as conexões de "Seguir" ou "Amizade".
- **Grafo Dirigido:** As conexões são modeladas como arcos dirigidos (A segue B não implica que B segue A).
- **Grafo Não-Dirigido:** Quando tratamos de "comunidades" ou "amizades mútuas".

**Por que:** Esta modelagem permite tratar a rede social como uma estrutura matemática passível de cálculos de distância, conectividade e caminhos mínimos.

---

## 3. Algoritmos de Exploração (BFS)

O algoritmo **BFS (Breadth-First Search)** é a base para as funcionalidades de busca em largura.

### 3.1 Menor número de passos (Distância entre usuários)
- **Onde:** Tabela de "Otimização de Caminhos" em `/network/analysis`.
- **Como:** Calcula a distância mínima ignorando pesos (passo a passo).
- **Por que:** Para saber quão "longe" um usuário está na rede social pura.

### 3.2 Sugestões de "Amigos de Amigos"
- **Onde:** Bloco de Sugestões em `/network/analysis`.
- **Como:** Executa um BFS limitado ao nível 2. Identifica vizinhos de vizinhos que ainda não são vizinhos diretos.
- **Por que:** Para incentivar o crescimento orgânico da rede através de conhecidos em comum.

### 3.3 "Quem pode me ajudar?" (Busca limitada)
- **Onde:** Funcionalidade de busca por habilidades.
- **Como:** BFS limitado a **profundidade 3**. Verifica se algum nó visitado possui a `Habilidade` desejada.
- **Por que:** Seguindo a teoria dos "seis graus de separação", limitamos a 3 para garantir que o ajudante seja alguém "próximo" o suficiente para ser confiável ou acessível.

---

## 4. Otimização de Caminhos (Dijkstra)

**Onde é utilizado:** Cálculo de "Distância baseada em Interesses" em `/network/analysis`.

**Como:** 
- Atribuímos **pesos** às arestas. O peso é inversamente proporcional ao número de interesses em comum.
- `peso = max(1, 10 - interesses_em_comum)`.
- O algoritmo de **Dijkstra** encontra o caminho que minimiza a soma desses pesos.

**Por que:** Nem sempre o caminho mais curto (menor número de passos) é o melhor. Interesses em comum tornam a conexão "mais forte" (menor peso), facilitando a comunicação entre especialistas de áreas similares.

---

## 5. Estruturas e Comunidades (DFS)

O algoritmo **DFS (Depth-First Search)** é utilizado para explorar a estrutura profunda do grafo.

### 5.1 Identificação de Comunidades (Componentes Conectados)
- **Onde:** Bloco "Sua Comunidade" em `/network/analysis`.
- **Como:** Percorre o grafo de forma recursiva/pilha para identificar todos os nós alcançáveis a partir de um ponto.
- **Por que:** Define quais usuários pertencem à mesma "ilha" de conexões, permitindo identificar grupos isolados na rede.

---

## 6. Dependências e Ordem (DAG)

**Aplicação Futura/Conceitual:**
- **Onde:** Pode ser utilizado em trilhas de aprendizado (Habilidades).
- **Como:** Modelando habilidades como um **Grafo Acíclico Dirigido (DAG)**, onde "Lógica de Programação" é pré-requisito para "Python".
- **Ordenação Topológica:** Seria usada para gerar a sequência correta de estudo das habilidades.

---

## 7. Visualização com vis.js

**Onde:** Página `/network`.

**Interatividade e Destaques:**
- **Ressaltando Conexões:** As arestas que conectam o usuário logado são destacadas em **Verde** (segue) ou **Dourado** (similaridade), enquanto as demais ficam com opacidade reduzida.
- **Clique em Arestas:** Ao clicar em uma linha, um alerta exibe exatamente quais Habilidades ou Interesses criaram aquela conexão.
- **Layout Físico (Barnes-Hut):** Otimiza o posicionamento dos nós usando simulação física com complexidade **O(n log n)**.


---

## Resumo de Complexidade

| Algoritmo | Complexidade | Função no Projeto |
|-----------|--------------|-------------------|
| **BFS**   | O(V + E)     | Distâncias e Ajuda |
| **DFS**   | O(V + E)     | Comunidades (CCs)  |
| **Dijkstra**| O(E log V) | Caminhos Otimizados|

---
*Documentação atualizada conforme os requisitos da disciplina de Teoria e Aplicabilidade de Grafos.*
