
#!/usr/bin/env python3

import argparse
import json
import sys
import time
from datetime import datetime

from orvibo.s20 import S20, discover


def get_device(host):
    """Connect to an S20 device."""
    try:
        return S20(host)
    except Exception as exc:
        raise RuntimeError(f"Cannot connect to {host}: {exc}") from exc


def discover_devices():
    """Discover S20 devices on the local network."""
    try:
        devices = discover()
    except Exception as exc:
        raise RuntimeError(f"Discovery failed: {exc}") from exc

    return devices


def get_status(host):
    """Get the current device status."""
    device = get_device(host)
    return device.on


def set_status(host, state):
    """Set the device state."""
    device = get_device(host)
    device.on = state
    return device.on


def toggle_device(host):
    """Toggle the device state."""
    device = get_device(host)
    device.on = not device.on
    return device.on


def format_status(state):
    return "ON" if state else "OFF"


def print_result(host, state, output):
    if output == "json":
        print(json.dumps({
            "host": host,
            "state": state,
            "status": format_status(state),
            "timestamp": datetime.now().astimezone().isoformat(),
        }))
    else:
        print(f"{host:<18} {format_status(state)}")


def command_discover(args):
    devices = discover_devices()

    if not devices:
        print("No devices found.")
        return

    if args.json:
        print(json.dumps(devices, indent=2, default=str))
        return

    print(f"Found {len(devices)} device(s):")
    for device in devices:
        print(f"  {device}")


def command_status(args):
    for host in args.hosts:
        try:
            state = get_status(host)
            print_result(host, state, args.output)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)


def command_on(args):
    for host in args.hosts:
        try:
            state = set_status(host, True)
            print_result(host, state, args.output)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)


def command_off(args):
    for host in args.hosts:
        try:
            state = set_status(host, False)
            print_result(host, state, args.output)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)


def command_toggle(args):
    for host in args.hosts:
        try:
            state = toggle_device(host)
            print_result(host, state, args.output)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)


def command_monitor(args):
    print(f"Monitoring {', '.join(args.hosts)} every {args.interval}s")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            for host in args.hosts:
                try:
                    state = get_status(host)
                    print_result(host, state, args.output)
                except Exception as exc:
                    print(f"{host:<18} ERROR: {exc}")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Control Orvibo S20 smart switches.",
        epilog="Example: %(prog)s status 192.168.10.240",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Shared arguments
    def add_hosts(command):
        command.add_argument(
            "hosts",
            nargs="+",
            metavar="IP",
            help="One or more device IP addresses",
        )
        command.add_argument(
            "-o", "--output",
            choices=("text", "json"),
            default="text",
            help="Output format (default: text)",
        )

    # Discover
    discover_parser = subparsers.add_parser(
        "discover",
        help="Discover devices on the local network",
    )
    discover_parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON",
    )
    discover_parser.set_defaults(func=command_discover)

    # Status
    status_parser = subparsers.add_parser(
        "status",
        help="Get device status",
    )
    add_hosts(status_parser)
    status_parser.set_defaults(func=command_status)

    # ON
    on_parser = subparsers.add_parser(
        "on",
        help="Turn devices ON",
    )
    add_hosts(on_parser)
    on_parser.set_defaults(func=command_on)

    # OFF
    off_parser = subparsers.add_parser(
        "off",
        help="Turn devices OFF",
    )
    add_hosts(off_parser)
    off_parser.set_defaults(func=command_off)

    # Toggle
    toggle_parser = subparsers.add_parser(
        "toggle",
        help="Toggle device state",
    )
    add_hosts(toggle_parser)
    toggle_parser.set_defaults(func=command_toggle)

    # Monitor
    monitor_parser = subparsers.add_parser(
        "monitor",
        help="Continuously monitor device status",
    )
    add_hosts(monitor_parser)
    monitor_parser.add_argument(
        "-i", "--interval",
        type=float,
        default=5,
        help="Polling interval in seconds (default: 5)",
    )
    monitor_parser.set_defaults(func=command_monitor)

    args = parser.parse_args()

    if hasattr(args, "interval") and args.interval <= 0:
        parser.error("--interval must be greater than zero")

    try:
        args.func(args)
    except RuntimeError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
