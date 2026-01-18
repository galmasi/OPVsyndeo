# OPVsyndeo Homebrew Tap

This directory contains the Homebrew formula for OPVsyndeo.

## Installation

To install OPVsyndeo using Homebrew, first add this tap:

```bash
brew tap galmasi/OPVsyndeo
```

Then install the formula:

```bash
brew install opvsyndeo
```

## Usage

After installation, run OPVsyndeo:

```bash
opvsyndeo
```

The application will appear in your macOS menu bar.

## Configuration

On first run, OPVsyndeo will create a configuration file at:
```
~/Library/Application Support/OPVsyndeo/OPVsyndeo.json
```

Edit this file to configure your VPN connections.

## Requirements

- macOS
- Python 3
- sshuttle (installed automatically as a dependency)
- sudo privileges for sshuttle (OPVsyndeo will guide you through setup)
