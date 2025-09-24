# RFD System Cleanup Plan

## Current State (MESS!)

### Multiple Implementations:
1. **src/rfd/** - ACTIVE, used by rfd-new
2. **nexus_rfd_protocol/** - DUPLICATE, should be deleted
3. **.rfd-legacy/** - ARCHIVED, keep for reference

### Multiple Databases:
1. **.rfd/memory.db** - ACTIVE, has current data
2. **src/.rfd/memory.db** - DUPLICATE
3. **.rfd-legacy/memory.db** - OLD DATA
4. **rfd-old.db** - BACKUP
5. **.rfd-legacy/rfd.db** - EMPTY

### Files to Delete:
- [ ] nexus_rfd_protocol/ (entire directory)
- [ ] src/.rfd/ (duplicate database directory)
- [ ] rfd (broken symlink)
- [ ] rfd-old.db
- [ ] rfd.original
- [ ] rfd-bulletproof.py
- [ ] install-rfd.py
- [ ] install-rfd.sh

### Files to Keep:
- [x] src/rfd/ (main code)
- [x] .rfd/memory.db (active database)
- [x] rfd-new (main executable)
- [x] .rfd-legacy/ (for reference)
- [x] PROJECT.md
- [x] .claude/commands/

### What to Fix:
1. Update slash commands to use correct paths (.rfd/memory.db)
2. Create context files in .rfd/context/
3. Implement missing features (tasks, phases, resume)
4. Remove all duplicate code

## The Truth:
**We are NOT properly dogfooding RFD because:**
- Too many duplicate implementations
- No clear source of truth
- Missing core functionality (tasks, phases, context)
- Slash commands don't actually execute

## Action Items:
1. Clean up all duplicates
2. Fix the one true implementation (src/rfd/)
3. Make slash commands work properly
4. Actually use RFD to manage RFD development