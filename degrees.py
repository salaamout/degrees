import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}



def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    
    # Check source and target
    sourcePerson = people[source]["name"]
    targetPerson = people[target]["name"]
    print(f"source: {sourcePerson}, target: {targetPerson}")
    
    # Create QueueFrontier to store the frontier
    ourQueue = QueueFrontier()
    
    # Start with an empty explored set
    explored = set()
    
    # Start with a frontier that contains the initial state
    # Create node for source, with empty parent and action (movie)
    sourceNode = Node(source,None,None)
    ourQueue.add(sourceNode)
    explored.add(sourceNode.state)
    #print(explored)
    
    max_count = 100000
    current_count = 0
    
    # Repeat:
    while True:
        # If the frontier is empty, then no solution
        if ourQueue.empty():
            print("Frontier is empty.")
            path = None
            return path
            
        # Remove a node from the frontier
        node = ourQueue.remove()
        #print(explored)
        
        nodeState = people[node.state]["name"]
        #print(f"Current state: {nodeState}")
        if node.action != None:
            nodeParent = people[node.parent.state]["name"]
            nodeAction = movies[node.action]["title"]
            #print(f"parent: {nodeParent}, action: {nodeAction}")
        
        # If node contains goal state, return the solution
        if node.state == target:
            print("Solved!")
            path = [(node.action,node.state)]
            #print(path)
            while node.parent.parent != None:
                node = node.parent
                path = [(node.action,node.state)] + path
                #print(path)
            return path
            
        # Expand node add resulting nodes to the frontier
        neighbors = neighbors_for_person(node.state)
        #print(node.state)
        #print(neighbors)
        for neighbor in neighbors:
            #print(f"before {neighbor[1]}")
            if neighbor[1] not in explored:
                #print(f"Add: {neighbor[1]}")
                neighborNode = Node(neighbor[1],node,neighbor[0])
                ourQueue.add(neighborNode)
                explored.add(neighbor[1])
        
        
        current_count = current_count+1
        if current_count>max_count:
            print("Exceeded limit")
            #path = None
            break
        
            
    return path


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
