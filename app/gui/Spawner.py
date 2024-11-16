import tkinter as tk
import json
import copy
from random import randint

class Spawner:

    def __init__(self, children, root, window):
        self.children = children
        self.subtree = self.make_subtrees()
        self.spawned = {vertex: None for vertex in self.children}
        self.edges_from = {vertex: {} for vertex in self.children}
        self.edges_to = {vertex: {} for vertex in self.children}

        self.window = window
        self.canvas = tk.Canvas(self.window)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.spawn_vertex(root)

    def make_subtrees(self):
        return {vertex: self.make_vertex_subtree(vertex) for vertex in self.children.keys()}
        
    def make_vertex_subtree(self, vertex): # super dumb
        queue = copy.copy(self.children[vertex]) # I don't want vertex in its own subtree
        for descendant in queue:
            queue.extend(self.children[descendant])
        return queue


    ## ======================================= DRAGGING ====================================== ##
    # https://stackoverflow.com/q/37280004/11143763


    def make_draggable(self, button):
        button.bind("<Button-3>", self.on_drag_start)
        button.bind("<B3-Motion>", self.on_drag_motion)

    def on_drag_start(self, event):
        button = event.widget
        button._drag_start_x = event.x
        button._drag_start_y = event.y

    def on_drag_motion(self, event):
        def update_edge_vertex(edge, new_x, new_y, shift):
            coords = self.canvas.coords(edge)
            coords[shift] = new_x
            coords[shift + 1] = new_y
            self.canvas.coords(edge, *coords)

        button = event.widget
        vertex = button._name

        # new coords
        new_x = button.winfo_x() - button._drag_start_x + event.x
        new_y = button.winfo_y() - button._drag_start_y + event.y

        # move
        button.place(x=new_x, y=new_y)

        for destination in self.edges_from[vertex]:
            edge = self.edges_from[vertex][destination]
            update_edge_vertex(edge, new_x, new_y, 0)
        
        for source in self.edges_to[vertex]:
            edge = self.edges_to[vertex][source]
            update_edge_vertex(edge, new_x, new_y, 2)


    ## ======================================= DRAWING EDGES ======================================= ##


    def draw_edge(self, source, destination):
        def get_button_coords(vertex):
            button = self.spawned[vertex]
            return button.winfo_x(), button.winfo_y()

        source_x, source_y = get_button_coords(source)
        destination_x, destination_y = get_button_coords(destination)
        new_edge = self.canvas.create_line(
            source_x, source_y,
            destination_x, destination_y 
        )

        self.edges_from[source][destination] = new_edge
        self.edges_to[destination][source] = new_edge

    def delete_edge(self, source, destination):
        edge = self.edges_from[source][destination]
        self.canvas.delete(edge)
        del self.edges_from[source][destination]
        del self.edges_to[destination][source]

    ## ======================================= SPAWNING UNITS ====================================== ##

    def place(self, vertex, MIN=0, MAX=500):
        return {'x': randint(MIN, MAX), 'y': randint(MIN, MAX)}

    def spawn_vertex(self, vertex):
        button = tk.Button(
            self.window,
            bd=4,
            bg="grey",
            text=vertex,
            name=vertex,
            command=self.spawn_children_or_despawn_subtree(vertex)
        )

        button.place(**self.place(vertex))
        self.window.update() # https://stackoverflow.com/a/50667199/11143763

        self.make_draggable(button)
        self.spawned[vertex] = button

    def despawn_vertex(self, vertex):
        button = self.spawned[vertex]
        button.destroy()
        self.spawned[vertex] = None

        # copy&paste :(
        for destination in list(self.edges_from[vertex].keys()):
            self.delete_edge(vertex, destination)
        
        for source in list(self.edges_to[vertex].keys()):
            self.delete_edge(source, vertex)

    def spawn_despawn_vertex(self, vertex):
        if self.spawned[vertex] is None:
            self.spawn_vertex(vertex)
        else:
            self.despawn_vertex(vertex)


    ## ======================================= SPAWNING BATCHES ====================================== ##


    def spawn_children(self, vertex):
        for child in self.children[vertex]:
            self.spawn_vertex(child)
            self.draw_edge(vertex, child)

    def despawn_subtree(self, vertex):
        for descendant in self.subtree[vertex]:
            if self.spawned[descendant] is not None:
                self.despawn_vertex(descendant)

    def spawn_children_or_despawn_subtree(self, vertex):
        def action():
            if self.is_off(vertex):
                self.spawn_children(vertex)
            else:
                self.despawn_subtree(vertex)
        return action

    def is_off(self, vertex):
        try:
            return self.spawned[self.children[vertex][0]] is None
        except IndexError:
            return False


## ======================================= DRIVER ====================================== ##

children = {
    "0": ["1"],
    "1": ["2", "3"],
    "2": ["4"],
    "3": ["5", "6"],
    "4": [],
    "5": [],
    "6": [],
}

window = tk.Tk()

spawner = Spawner(children, "0", window)

window.title(" !!! DRAG - RIGHT, PRESS - LEFT !!!")

window.mainloop()
