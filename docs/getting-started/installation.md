# Installation

## Prerequisites

You need **Python 3.10 or later** installed on your machine.

```bash
python3 --version
```

If this shows a version number (e.g. `Python 3.12.4`), you're good to go. If not, install Python first:

=== "macOS"

    **Option 1: Homebrew** (recommended if you already use Homebrew):
    ```bash
    brew install python
    ```

    **Option 2: Official installer:**
    Download from [python.org/downloads](https://www.python.org/downloads/) and run the installer.

=== "Windows"

    Download from [python.org/downloads](https://www.python.org/downloads/) and run the installer.

    !!! warning "Check 'Add Python to PATH'"
        During installation, make sure to tick **"Add Python to PATH"** on the first screen. Without this, `python` and `pip` won't be available in your terminal.

=== "Linux"

    ```bash
    # Debian / Ubuntu
    sudo apt install python3 python3-pip python3-venv

    # Fedora
    sudo dnf install python3 python3-pip
    ```

## Install from PyPI

We recommend installing in a **virtual environment** to keep dependencies isolated:

```bash
# Create and activate a virtual environment
python3 -m venv youtube-mcp-env
source youtube-mcp-env/bin/activate  # On Windows: youtube-mcp-env\Scripts\activate

# Install the package
pip install youtube-insights-mcp
```

!!! tip "Why a virtual environment?"
    A virtual environment gives you a clean, isolated Python with its own `pip`. This avoids conflicts with other packages and sidesteps common issues like `ModuleNotFoundError: No module named 'pip'` on macOS.

!!! note "Activating the environment"
    You'll need to activate the virtual environment each time you open a new terminal:
    ```bash
    source youtube-mcp-env/bin/activate
    ```
    When activated, your terminal prompt will show `(youtube-mcp-env)`.

## Install from Source

For development or to run the latest unreleased code:

```bash
git clone https://github.com/appmilla/youtube-transcript-mcp.git
cd youtube-transcript-mcp
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

This installs the server and all runtime dependencies:

| Package | Purpose |
|---------|---------|
| `mcp>=1.0.0` | MCP protocol framework (FastMCP) |
| `pydantic>=2.0` | Parameter validation |
| `yt-dlp>=2024.1.0` | YouTube video metadata extraction |
| `youtube-transcript-api>=1.0.0` | Transcript fetching |

### Development Dependencies

To also install testing and linting tools:

```bash
pip install -e ".[dev]"
```

This adds pytest, ruff, mypy, and related packages.

## Verify Installation

Test the CLI interface:

```bash
youtube-insights-mcp cli ping
```

Expected output:

```json
{
  "status": "healthy",
  "server": "youtube-insights-mcp",
  "version": "0.1.3",
  "mode": "cli"
}
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'pip'` | Your system Python is misconfigured. Create a virtual environment first (see above) — this gives you a working pip. |
| `python3: command not found` | Python is not installed or not on your PATH. Follow the prerequisites above. |
| `pip: command not found` | Use `python3 -m pip install ...` instead, or activate a virtual environment. |
| `command not found: youtube-insights-mcp` | Make sure your virtual environment is activated, or the package isn't installed. Run `pip show youtube-insights-mcp` to check. |

## Next Steps

- [Quick Start](quickstart.md) - Fetch your first transcript in 5 minutes
- [Configuration](configuration.md) - Configure Claude Desktop integration
