import itertools
grid = {
 (0,0):('Q','s','DR'),(0,1):('W','w','R'),(0,2):('E','e','DR'),(0,3):('R','s','R'),(0,4):('T','u','DR'),
 (1,0):('A','u','DR'),(1,1):('S','q','UL'),(1,2):('D','r','DR'),(1,3):('F','_','UL'),(1,4):('G','c','DR'),(1,5):('H','}','END'),
 (2,0):('Z','n','R'),(2,1):('X','{','UL'),(2,2):('C','t','R'),(2,3):('V','y','UL'),(2,4):('B','k','R'),(2,5):('N','s','UL'),
}
moves = [(dr,dc) for dr in (-1,0,1) for dc in (-1,0,1) if not(dr==0 and dc==0)]
best=[]
for mDR in moves:
 for mR in moves:
  for mUL in moves:
   M={'DR':mDR,'R':mR,'UL':mUL}
   for start in grid:
    cur=start; seq=[]; seen=set()
    while cur in grid and cur not in seen:
        seen.add(cur)
        name,letter,arr=grid[cur]
        seq.append(letter)
        if arr=='END': break
        mv=M[arr]
        cur=(cur[0]+mv[0],cur[1]+mv[1])
    s=''.join(seq)
    # want path ending at H (}) and long
    if seq and seq[-1]=='}' and len(seq)>=8:
        best.append((len(seq),s,start,mDR,mR,mUL))
best.sort(reverse=True)
for b in best[:40]:
    print(b)
print("total",len(best))
