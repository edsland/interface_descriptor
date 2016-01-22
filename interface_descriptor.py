import requests
import json
import getpass
import argparse
from pprint import pprint

""" The goal of this script is to gather CDP output information to create interface descriptions that describes the remote-end device and which interaface it terminates on the remote-end device """
#
# This function uses argpase to enable user to supply --username, --password, and --hostfile as arguments to run script
def parse_args():
    parser = argparse.ArgumentParser(
                                    description = 'Configured Interface description based on CDP info')
    parser.add_argument('--verbose', action='store_true',
                       help='provide additional output for verification')
    parser.add_argument('--username', help='username for SSH connections')
    parser.add_argument('--password', help='password for SSH username')
    parser.add_argument('--hostfile', help='source file for list of hosts',
                        required = True)
    args = parser.parse_args()

    if args.verbose:
        global_verbose = True
    else:
        global_verbose = False

    if args.username:
        ssh_username = args.username
    else:
        ssh_username = raw_input("Enter Username: ")
    if args.password:
        ssh_password = args.password
    else:
        ssh_password = getpass.getpass("Enter Password: ")

    try:
        with open(args.hostfile, 'r') as f:
            host_list = f.read().splitlines()
    except:
        quit("host file cannot be found")

    host_list = [x for x in host_list if x[0] != "#"]

    return global_verbose, ssh_username, ssh_password, host_list
#
# This function will either interact with nxapi to either get or push info
def go_configure(host, user, passwd, cmd, cmd_type):
    myheaders = {'content-type': 'application/json'}
    url = "http://"+host+"/ins"
    username = user
    password = passwd        
    payload= {"ins_api": {"version": "1.0", "type": cmd_type, "chunk": "0", "sid": "1", "input": cmd, "output_format": "json"}}         
    response = requests.post(url,data=json.dumps(payload),headers=myheaders,auth=(username,password)).json()
    mydict = response
    #
    #Error checking block
    #this if statement catches errors in group of commands
    if type(mydict['ins_api']['outputs']['output']) == list:
        for i in mydict['ins_api']['outputs']['output']:
            if 'clierror' in i:
                print i['clierror']
                return "FAIL"
            else:
                return "SUCCESS", mydict
    #            
    #this if statement catches error in a single command    
    elif type(mydict['ins_api']['outputs']['output']) == dict:
        for i in mydict['ins_api']['outputs']['output']:
            if 'clierror' in i:
                print mydict['ins_api']['outputs']['output']['clierror']
                return "FAIL"
            else:
                return "SUCCESS", mydict         
    else:
        print "ERROR UNKNOWN"
        return "FAIL"
#    
#Parse through mydict dictionary to make sense of connections and return lists of description values to apply on interfaces
#e.g remote switch - "int e1/1 ,description TO_SW1_e1/2"
def descriptor(cdp_output):
    description = ""
    neighbor_rows = cdp_output['ins_api']['outputs']['output']['body']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
    
    for neighbor in neighbor_rows:
        description += "interface " + neighbor["intf_id"] + " ;" + "description To_" + neighbor["device_id"] + "_" + neighbor["port_id"] + " ;"

    description = description[:-2]
    #print description
    return description
#
#Main code block
#
def main():
    #get arguments
    global_verbose, ssh_username, ssh_password, host_list = parse_args()
    #global variables
    display = "*"*60
    display2 = "-"*30
    cmd = "show cdp nei"
    cmd_type = ("cli_show", "cli_conf")

    print display
    print "Welcome to Interface Descriptor"
    print display + '\n'
    #
    for host in host_list:
        host = host.strip()
        #
        print 'Working on Host: {}'.format(host)
        print display2
        #
        cdp_result = go_configure(host, ssh_username, ssh_password, cmd, cmd_type[0])
        #
        print "Getting CDP information: {}".format(cdp_result[0])
        #
        int_config = go_configure(host, ssh_username, ssh_password, descriptor(cdp_result[1]), cmd_type[1])
        print "Configuring interface descriptions: {}".format(int_config[0]) 
        #
        print "" + '\n'
    #
    print "------------------ Script execution completed ------------------" + '\n'       

#__main__
if __name__ == '__main__':
    main()


