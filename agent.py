from functools import reduce
from platform import node
import agentpy as ap
from matplotlib import pyplot as plt
from matplotlib import cm, colors
import matplotlib.animation as anim
from matplotlib.axes import Axes
import networkx as nx
from networkx import Graph

class Person(ap.Agent):

    model: "SocialNetwork"
    POS = 1
    NEG = -1

    def setup(self, **kwargs):
        self.suffix = 'pos_' if kwargs['direction'] == self.POS else 'neg_'
        self.is_active = self.model.random.random() < 0.3
        self.opinion = self.model.random.betavariate(0.2, 0.8) * kwargs['direction']
        self.self_belief = 0.15
        self.social_influence_factor = 0.6
    
    def __get_opinion_influence(self, neighbors):
        
        opinion_similarity = lambda u, v: 1 - (abs(u - v)) / 2.0

        active_opinions = [n.opinion for n in neighbors if n.is_active and n is not self]
        neighbor_opinions = [n.opinion for n in neighbors]

        active_os = reduce(lambda x, y: x + opinion_similarity(y, self.opinion), active_opinions, 0)
        total_os = reduce(lambda x, y: x + opinion_similarity(y, self.opinion), neighbor_opinions, 0)

        if total_os == 0:
            return 0

        return active_os / total_os

    def __get_relation_influence(self, neighbors):
        
        status_pressure = lambda deg_u, deg_v: deg_u / (deg_u + deg_v)

        degree = nx.degree(self.model.network.graph, self.model.network.positions[self])
        self.model.network.agents

        active_degrees = [self.model.network.graph.degree(self.model.network.positions[n]) for n in neighbors if n is not self and n.is_active]
        total_degrees = [self.model.network.graph.degree(self.model.network.positions[n]) for n in neighbors if n is not self]

        active_status = reduce(lambda x, y: x + status_pressure(y, degree), active_degrees, 0)
        total_status = reduce(lambda x, y: x + status_pressure(y, degree), total_degrees, 0)

        if total_status == 0:
            return 0

        return active_status / total_status

    def get_social_influence(self):
        try:
            neighbors = self.model.network.neighbors(self).to_list()
            return self.social_influence_factor * self.__get_opinion_influence(neighbors) + (1 - self.social_influence_factor) * self.__get_relation_influence(neighbors)
        
        except nx.exception.NetworkXError:
            print(f'Not found: {self}, {self.model.network.positions[self]}')
    
    def update_opinion(self):
        neighbors = self.model.network.neighbors(self).to_list()

        active_opinions = [n.opinion for n in neighbors if n is not self and n.is_active]
        average_opinion = reduce(lambda x, y: x + y, active_opinions) / len(active_opinions)

        self.opinion = self.self_belief * self.opinion + (1 - self.self_belief) * average_opinion


class SocialNetwork(ap.Model):
    def setup(self):
        
        self.agents, self.network = self.initialize_network()
        self.agents.network = self.network

        self.active_agents = [ agent for agent in self.agents if agent.is_active ]
        self.activated_agents = [ agent for agent in self.agents if agent.is_active ]

    
    def initialize_network(self):
        g_pos: Graph = nx.powerlaw_cluster_graph(50, 5, 0.5)
        g_neg = nx.powerlaw_cluster_graph(50, 5, 0.5)

        pos_agents = ap.AgentList(self)
        neg_agents = ap.AgentList(self)

        for _ in range(50):
            agent = Person(self, direction=Person.POS)
            pos_agents.append(agent)

        for _ in range(50):
            agent = Person(self, direction=Person.NEG)
            neg_agents.append(agent)
        
        netwk_pos = ap.Network(self, g_pos)
        netwk_neg = ap.Network(self, g_neg)    
        
        # for nodes in netwk_pos.nodes:
        #     nodes.label *= 1

        # for nodes in netwk_neg.nodes:
        #     nodes.label *= -1         

        netwk_pos.add_agents(pos_agents, netwk_pos.nodes)
        netwk_neg.add_agents(neg_agents, netwk_neg.nodes)    

        netwk_pos.graph = nx.relabel_nodes(netwk_pos.graph, { n: n.label for n in netwk_pos.graph.nodes })
        netwk_neg.graph = nx.relabel_nodes(netwk_neg.graph, { n: n.label * -1 for n in netwk_neg.graph.nodes })

        # shared = Person(self, direction=Person.POS)
        # shared_node1 = netwk_pos.add_node('s')
        # shared_node2 = netwk_neg.add_node('s')
        # netwk_pos.add_agents([shared], [shared_node1])
        # netwk_neg.add_agents([shared], [shared_node2])
        # netwk_pos.graph.add_edge(shared_node1, self.random.choice(list(netwk_pos.nodes)))
        # netwk_neg.graph.add_edge(shared_node2, self.random.choice(list(netwk_neg.nodes)))

        g = nx.compose(netwk_pos.graph, netwk_neg.graph)
        nx.edgelist.write_edgelist(g, 'egdelist7.csv', delimiter=',', data=['source', 'target', 'attr'])
        # g = nx.relabel_nodes(g, { nd: ap.AgentNode(nd) for nd in g.nodes })
        n = ap.Network(self, g)
        
        a = ap.AgentList(self)
        a.extend(pos_agents)
        # a.append(shared)
        a.extend(neg_agents)
        nds = [ap.AgentNode(n) for n in list(netwk_pos.nodes)]
        # nds.append(shared_node1)
        nds.extend([ap.AgentNode(n) for n in list(netwk_neg.nodes)])
        n.add_agents(a, nds)
        
        for agent in a:
            n.move_to(agent, n.positions[agent])

        return a, n
    
        

    def update(self):
        with open('test', 'a') as file:
            file.write(f'{self.model.t}\t Opinion: {self.agents[0].opinion}\t is_aticve: {self.agents[0].is_active}\t si: {self.agents[0].get_social_influence()}\n')

    
    def step(self):

        if self.t >= 50:
            self.stop()

        self.activated_agents = self.active_agents.copy()

        self.activated_agents: ap.AgentList
        active_agent: Person

        for active_agent in self.activated_agents:
            inactive_neighbors = [ n for n in self.network.neighbors(active_agent) if not n in self.active_agents ]
            
            neighbor: Person
            for neighbor in inactive_neighbors:
                social_influence = neighbor.get_social_influence()

                if social_influence >= neighbor.self_belief:
                    self.active_agents.append(neighbor)
                    neighbor.is_active = True
                    neighbor.update_opinion()

        
    
    def end(self):
        return super().end()

social_network = SocialNetwork()
# social_network.run()

def animation_plot(m: SocialNetwork, axs):
    ax1: Axes
    ax1, ax2 = axs
    ax1.set_title(f't = {m.t}')

    # Plot stackplot on first axis
    opinions = [o for o in m.agents.opinion]
    ax1.hist(opinions, 20)

    norm = colors.Normalize(vmin=-1.0, vmax=1.0)
    mapper = cm.ScalarMappable(norm=norm, cmap='plasma')
    # Plot network on second axis
    color = [ mapper.to_rgba(opinion) for opinion in m.agents.opinion ]
    nx.draw_shell(m.network.graph, node_size=10, ax=ax2, node_color=color, width=0.5, with_labels=False)

fig, axs = plt.subplots(1, 2, figsize=(8*1.5, 4*1.5)) # Prepare figure
fig.tight_layout()
animation = ap.animate(SocialNetwork(), fig, axs, animation_plot)
# writervideo = anim.FFMpegWriter()
animation.save('test.gif', writer='pillow', fps=10)
