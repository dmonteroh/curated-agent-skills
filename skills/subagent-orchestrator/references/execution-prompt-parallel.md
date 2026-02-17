# Execution Mode: Prompt Parallel

## Use This Mode When

- Multiple domains can be defined now, but execution must remain sequential.
- Controller wants better decomposition without concurrent sessions.

## Steps

### 1) Create Multiple Packets Up Front

Prepare `T1..Tn` packets in one planning pass:

- explicit claims
- acceptance criteria
- verification commands

Output: packet set ready for execution.

### 2) Execute Sequentially Without Context Mixing

Run one worker packet at a time:

1. dispatch `Ti`
2. wait for exit
3. verify `Ti`
4. proceed to `Ti+1`

Output: per-task verified reports.

### 3) Integration Gate

- Recheck file overlaps across all executed tasks.
- Run full project quality bar.
- Re-dispatch only the smallest failing scope.

Output: final integration result.

## Decision Points

- If packet quality is low, pause and rewrite packets before execution.
- If later tasks depend on earlier outputs, update remaining packets before dispatch.
