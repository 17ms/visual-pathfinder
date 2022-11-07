<div align="center">
    <h1>visual-pathfinder</h1>
    <span><img src="https://github.com/einisto/visual-pathfinder/blob/main/.github/docs/demo.gif"></span>
</div>

### Algorithms

- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
  - Traverses through the available nodes keeping track of the distance to every node until it reaches the target node or has gone through all the available nodes
  - Creates a path back from the target node to the starter node based on the stored distances
- [A\* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
  - Maintains a tree of paths originating from the starter node
  - Extends the tree one edge at a time choosing next node based on [heuristics](https://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html) until it reaches the target node or has gone through all the available nodes

### Usage

```shell
git clone git@github.com:17ms/visual-pathfinder.git
cd visual-pathfinder

sudo apt install python3-tk
mkvirtualenv visual-pathfinder
pip3 install -r requirements.txt

chmod +x src/main.py
./src/main.py
```
