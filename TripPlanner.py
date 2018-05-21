# preprocessor.py
# Hamid Sharif
# hsharif2@stu.parkland.edu
# CSC 220, Fall 2016

from graph import Graph
from shortest_paths import *  # Dijkstra's Algorithm
from linked_stack import LinkedStack
from copy import copy


class TripPlanner:
    """Trip Planner is a path finder class which finds shortest possible route
    between two cities in a routing system using Dijkstra's Algorithm ."""

    def __init__(self, timeTable, outfile=None):
        """Starts a trip planning system based on required timetable and
        optional itinerary file for output."""
        self.__timeTable = timeTable
        self.__railways = Graph()
        self.__cities, self.__path = dict(), dict()
        self.__path_stops = LinkedStack()
        self.__outfile = outfile
        self.__origin,self.__destin = None, None
        self._parseTable()

    def _parseTable(self):
        routes = set()
        print("File Loading...")
        with open(self.__timeTable, 'r') as timeTable:
            for line in timeTable.readlines():
                s, d, w = line.strip().lower().split(',')
                duration = int(w.split(':')[0]) * 60 + int(w.split(':')[1])
                if s not in self.__cities:
                    self.__cities.setdefault(s)
                    self.__cities[s] = self.__railways.insert_vertex(s)
                if d not in self.__cities:
                    self.__cities.setdefault(d)
                    self.__cities[d] = self.__railways.insert_vertex(d)
                self.__railways.insert_edge(self.__cities[s],
                                            self.__cities[d], duration)
        print(self)

    def UI(self):
        """Starts User Interface which asks for origination and destination in
        a rail system and return the fastest possible route if existed."""
        print('-' * 75)
        print("Welcome to the path finder. You can enter your current city\n"
              "and destination for the fastest possible trip in",
              self.__timeTable.split('.')[0], '.')
        while True:
            origination = input("Please enter an origination: ")
            destination = input("Please enter a destination: ")
            if origination.strip().lower() not in self.__cities:
                print("Oops,", origination, "was not found in the rail system!"
                                            " Please try again!")
            elif destination.strip().lower() not in self.__cities:
                print("Oops,", destination, "was not found in the rail system!"
                                            " Please try again!")
            else:
                self.__origin = self.__cities[origination.strip().lower()]
                self.__destin = self.__cities[destination.strip().lower()]
                self._shrotest(origination, destination)
            prompt = input("Do you want to quit?(y/n)")
            if prompt.startswith('y'):
                break
        if self.__outfile is not None:
            self.dump()

    def _shrotest(self, origination, destination):
        origin = origination.strip().lower()
        destin = destination.strip().lower()
        durations = shortest_path_lengths(self.__railways,
                                          self.__cities[origin])
        origin_vertex = self.__cities[destin]
        if durations[origin_vertex] == float("inf"):
            print("Sorry, there is no rail connections between {!s} and {!s} in "
                  "{}. Try other rail systems.".format(
                origination, destination, self.__timeTable))
            return
        path_map = shortest_path_tree(self.__railways,
                                      self.__cities[origin], durations)

        current_stop = self.__cities[destin]
        self.__path_stops = LinkedStack()
        self.__path_stops.push(current_stop)
        while current_stop != self.__cities[origin]:
            next_stop = path_map[current_stop].opposite(current_stop)
            self.__path[(current_stop, next_stop)] = self.__railways.get_edge(
                current_stop, next_stop).element()
            self.__path_stops.push(next_stop)
            current_stop = next_stop

        path_stops = copy(self.__path_stops)
        duration = 0
        pathString = ''
        while not path_stops.is_empty() and path_stops.top() is not \
                self.__cities[destin]:
            current_stop = path_stops.pop()
            next_stop = path_stops.top()
            duration += self.__railways.get_edge(current_stop,
                                                 next_stop).element()
            pathString += '{!s}{}'.format(current_stop, ' >> ')
        pathString += '{!s}\n'.format(path_stops.pop())
        hours, minutes = duration // 60, duration % 60
        print("The fastest route to", destination, "takes", hours, "hours "
                                                                   "and",
              minutes, "minutes with", len(self.__path_stops),
              "stops as following:")
        print(pathString.title())

    def dump(self):
        """Exports most recent found shortest path between requested cities
        to a gv file."""
        style, shape = '', ''
        stops = set()
        endpoints = self.__origin, self.__destin
        routeTitle = self.__timeTable.split('.')[0]

        visual_graph = open(self.__outfile, 'w')
        visual_graph.write("graph {} {}\n".format(routeTitle, '{'))
        for cities in self.__path:
            stops |= {cities[0], cities[1]}
        visual_graph.write('{}[shape=octagon,style=filled,'
                           'color="darkgreen"]\n'.format(
                            str(self.__origin).title()))
        visual_graph.write('{}[shape=octagon,style=filled,'
                           'color="skyblue"]\n'.format(
                            str(self.__destin).title()))
        for stop in stops:
            if stop not in endpoints:
                style = 'style=bold'
                shape = ''
                if self.__railways.degree(stop) > 3:
                    shape = ', shape=doublecircle'
                stop = str(stop).title()
                visual_graph.write('{}[{}{}]\n'.format(stop, style, shape))
        for route in self.__railways.edges():
            v, u = route.endpoints()
            hours, mins = route.element() // 60, route.element() % 60
            style = ''
            if (v, u) in self.__path or (u, v) in self.__path:
                style = " ,style=bold"
            else:
                style = ""
            v, u = str(v).title(), str(u).title()
            visual_graph.write('{} -- {} [label="{}h {}m"{}]\n'.format(
                v, u, hours, mins, style))
        visual_graph.write("}")

    def __str__(self):
        """Returns number of cities and rail roads in the parsed timetable."""
        output = "There are {!s} cities with {!s} connections in {}.".format(
            self.__railways.vertex_count(), self.__railways.edge_count(),
            self.__timeTable.split('.')[0])
        return output

if __name__ == '__main__':
    trip = TripPlanner('eurail.txt')
    print("This is a trip planner class.")
    print('-'*80)
    print("Here is a sample output for parsed 'eurail.txt' fastest trip"
          " from Madrid to Paris.")
    trip._shrotest('Madrid', 'Paris')