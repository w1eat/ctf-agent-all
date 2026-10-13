import sys
from collections import defaultdict

# frames (step from caller = frame+0x10 managed in transitions)
# We track T = rbp_place - rbp_current_function_below_startpos
# state: 'SP','IC','RO','BD','TS','UC','OI','SPEAK'
# terminal when OI chooses cancel: T += 0x1A0 (OI step) then we are at cancel rbp
# Emitting sequences carefully.

targets=[0x400,0x480,0x520,0x570,0x5a0,0x640,0x690,0x6c0,0x760,0x7b0,0x7e0,0x800,0x880]
TFROM=0x440  # T of base path

# We'll DFS. To bound, limit T <= 0x880+0x440 = 0xCC0 (so E<=0x880) plus allow up to maybe 0x880.
MAXT=0x440+0x900

solutions=defaultdict(list)

def dfs(state, T, seq, budget):
    if T>MAXT: return
    if len(seq)>200: return
    if state=='SP':
        # scream
        dfs('SP', T+0x120, seq+["3","5"], budget-1)
        # to initial_call
        dfs('IC', T+0x120, seq+["1"], budget-1)
    elif state=='IC':
        dfs('RO', T+0x180, seq+["2"], budget-1)   # IC->RO
        dfs('BD', T+0x180, seq+["3"], budget-1)
        dfs('TS', T+0x180, seq+["4"], budget-1)
        dfs('UC', T+0x180, seq+["5"], budget-1)
        dfs('OI', T+0x180, seq+["6"], budget-1)
        # 1 -> start_service dead
    elif state=='RO':
        # RO reads outage address, then calls SP
        dfs('SP', T+0x160, seq+["addr"], budget-1)
    elif state=='BD':
        # BD: login(3), menu choice(1), payment_info(4) -> SP
        dfs('SP', T+0x190, seq+["L","L","L","1","cc","sc","nm","ex"], budget-1)
        # choice 2 also leads SP (after payment_info)
        dfs('SP', T+0x190, seq+["L","L","L","2","cc","sc","nm","ex"], budget-1)
        # recursion (choice other) -> BD
        dfs('BD', T+0x190, seq+["L","L","L","9"], budget-1)
    elif state=='TS':
        dfs('RO', T+0x170, seq+["1"], budget-1)          # TS->RO
        dfs('SP', T+0x170, seq+["2","L","L","L"], budget-1) # TS->login->SP
        dfs('TS', T+0x170, seq+["9"], budget-1)          # recursion
    elif state=='UC':
        dfs('SP', T+0x1A0, seq+["1"], budget-1)          # UC->SP
        dfs('UC', T+0x1A0, seq+["9"], budget-1)          # recursion
    elif state=='OI':
        # cancel terminal: add OI step 0x1A0
        Tc=T+0x1A0
        E=Tc-TFROM
        if E in targets:
            solutions[E].append(list(seq+["2"]))
        # speak -> SP
        dfs('SP', T+0x1A0+0x80, seq+["3"], budget-1)

import sys
sys.setrecursionlimit(100000)
dfs('SP', 0x0, [], 14)
for d in targets:
    sols=solutions.get(d,[])
    print(hex(d), len(sols), (sols[0] if sols else None))
