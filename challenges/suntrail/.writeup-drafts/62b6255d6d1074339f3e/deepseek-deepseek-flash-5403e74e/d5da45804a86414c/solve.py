# suntrail.klc : Windows keyboard layout
# shift-state-0 column encodes a trail direction as Unicode arrows:
#   U+2198 (down-right) ~ step down ; U+2192 (right) ~ step right ; U+2196 (up-left) ~ step up ; U+25A0 (square) = END
# shift-state-1 column encodes the character printed on each key.
# Applying arrows to a 3-row keyboard grid yields a Hamiltonian path through every key.

grid = {
 (0,0):('Q','s','DR'),(0,1):('W','w','R'),(0,2):('E','e','DR'),(0,3):('R','s','R'),(0,4):('T','u','DR'),
 (1,0):('A','u','DR'),(1,1):('S','q','UL'),(1,2):('D','r','DR'),(1,3):('F','_','UL'),(1,4):('G','c','DR'),(1,5):('H','}','END'),
 (2,0):('Z','n','R'),(2,1):('X','{','UL'),(2,2):('C','t','R'),(2,3):('V','y','UL'),(2,4):('B','k','R'),(2,5):('N','s','UL'),
}
M={'DR':(1,0),'R':(0,1),'UL':(-1,0)}   # arrows: down / right / up on the grid
cur=(0,0); path=[]
while cur in grid:
    name,letter,arr=grid[cur]
    path.append((name,letter))
    if arr=='END': break
    dr,dc=M[arr]; cur=(cur[0]+dr,cur[1]+dc)
print(" -> ".join(f"{n}({l})" for n,l in path))
flag=''.join(l for _,l in path)
print("FLAG:", flag)
