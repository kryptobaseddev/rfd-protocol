# RFD Development Guide

## Understanding RFD's Architecture

RFD has two distinct modes:

### 1. Production Use (Normal Users)
Users install RFD globally as a tool:
```bash
pip install rfd-protocol
```

Then use it in their projects:
```bash
cd my-project/
rfd init  # Creates .rfd/config.yaml, CLAUDE.md, .rfd/memory.db
rfd session start my_feature
```

### 2. Development Mode (RFD Contributors)
When developing RFD itself:
```bash
git clone https://github.com/kryptobaseddev/rfd-protocol.git
cd rfd-protocol
pip install -e .  # Editable install
```

## How RFD Dogfoods Itself

Since RFD is a tool for building software, we use RFD to build RFD:

1. **We have .rfd/config.yaml** - RFD's project configuration
2. **Features in database** - Using .rfd/memory.db for features
2. **We run `./rfd`** - This uses our development version from `src/rfd/`
3. **We validate with `./rfd validate`** - Tests our implementation
4. **We checkpoint with `./rfd checkpoint`** - Saves progress

### Key Point: No Installation Into .rfd/

Unlike what was attempted with `rfd-dogfood`, we DO NOT:
- Copy source files into `.rfd/installed/`
- Create separate "dogfood" executables
- Maintain two versions of the code

Instead:
- `./rfd` runs from `src/rfd/` (development)
- `rfd` (after pip install) runs from site-packages (production)

## Testing RFD as a User Would

To test RFD as a real user:

```bash
# Create a test environment
cd /tmp
mkdir test-rfd-project
cd test-rfd-project

# Use the globally installed RFD
rfd init
rfd session start test_feature
```

## Common Confusion Points

### Q: How do we test updates without breaking our development?
A: Use virtual environments:
```bash
python -m venv test-env
source test-env/bin/activate
pip install /path/to/rfd-protocol
# Test in isolation
```

### Q: How do users update RFD?
A: Standard pip upgrade:
```bash
pip install --upgrade rfd-protocol
```

### Q: What files does RFD create in user projects?
A: Only these:
- `.rfd/config.yaml` - User's project configuration
- `.rfd/memory.db` - Features and checkpoints database
- `CLAUDE.md` - Claude integration
- `.rfd/context/` - Session context (auto-generated)

### Q: What's in `.rfd/` directory?
A: Only user data:
- `memory.db` - SQLite database
- `context/` - AI context files
- NO Python source files
- NO executables

## Release Process

1. **Develop features** using `./rfd` locally
2. **Test thoroughly** with pytest
3. **Bump version** in `setup.py`
4. **Create release** via GitHub
5. **Publish to PyPI** (automated via CI)
6. **Users upgrade** with `pip install --upgrade`

## Key Principles

1. **RFD is a tool, not a framework** - It doesn't embed itself in projects
2. **Clean separation** - User projects contain only user files
3. **Standard Python packaging** - Follow PyPI conventions
4. **No magic** - Clear, predictable file locations