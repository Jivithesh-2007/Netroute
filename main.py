#!/usr/bin/env python3
"""
NetRoute – Interactive Data Structures & Network Routing Simulator
Course: Data Structures and Algorithms (25CS306)

Main application entry point.
"""
import sys
import os

# Add application root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application import NetRouteApp


def main():
    """Launch NetRoute Desktop Application."""
    app = NetRouteApp()
    app.mainloop()


if __name__ == "__main__":
    main()
