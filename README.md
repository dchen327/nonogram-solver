# Nonogram Solver
Nonograms are picture logic puzzles in which cells in a grid must be colored or left blank according to numbers at the side of the grid to reveal a hidden picture. 

This solver uses the basic idea of solving lines individually. Progress in a line is made by looking at overlaps in all possible patterns fitting the current rule.

Currently, on my laptop I can finish a 25x25 board in around 30 seconds.
# Demo
![nonogram](https://user-images.githubusercontent.com/37674516/103415878-195f2780-4b52-11eb-8cea-a281a96953e2.gif)

# Future Todos
- Switch to using PyAutoGui for faster clicking
- Incorporate mouse dragging instead of independent clicks
- Caching of common patterns