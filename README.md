# Interface Descriptor

This is a program that automate the assignment of interface descriptions on Cisco Nexus switches using Python to interact with NXAPI.

To run this program you'll need the following:
Host file - you can edit the host.txt file in this repo.
A common credential for accessing the host devices in the host file

Run as# python interface_descriptor.py --username <username> --password <password> --hostfile host.txt

The expected behaviour of this script is as follows:
Upon execution this script will jump on each device listed in the host file and sequentially run "show cdp neighbor" to discover enabled neighbors and in turn local and remote interfaces.
This information is then used to create a description(concatenating hostname+remote_interface) on the local interface.

You can use this script to schedule job that goes and configure interfaces without descriptions and update existing ones if changes have been made.

I'll appreciate your feedback on this script and please feel free to branch out and make improvements as necessary.


