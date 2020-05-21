import urllib.request
import urllib.parse
import urllib3
import ssl
import json
import requests
import sys
import inquirer


ssl._create_default_https_context = ssl._create_unverified_context
s = requests.Session()
s.verify = False
s.auth = ('<USERNAME>', '<PASSWORD>')
s.headers = {'Content-type': 'application/json'}
nsxtmgr = '<NSX-T MANAGER FQDN>'
urllib3.disable_warnings()

#OPTION A - CREATE BOGONS GROUP
def opt_a():
    
    # First check if group already exists
    url = '/policy/api/v1/infra/domains/default/groups/bogons/'
    bg_group_exist_json = s.get(nsxtmgr + str(url), headers=s.headers, auth=s.auth, verify=s.verify)

    if bg_group_exist_json.status_code == 200:
        print("\r\n Bogons IPv4 Group already exists \r\n")
        main()

    #If group does not exist, create it and populate    
    else:
        data = json.dumps({'description': 'Bogons', 'display_name': 'Bogons'})
        url = '/policy/api/v1/infra/domains/default/groups/bogons/'
        s.put(nsxtmgr + str(url), data=data, headers=s.headers, auth=s.auth, verify=s.verify)
        print("\r\n Bogons IPv4 Group Created \r\n")
        with open('<PATH TO FILE>/bogons-ipv4.txt') as f:
            ip_list = [line.rstrip() for line in f]

            #ADD ALL ELEMENTS FROM LIST INTO THE GROUP
            data = json.dumps({'resource_type': 'IPAddressExpression', 'id': 'exp1', 'ip_addresses': ip_list})
            url = '/policy/api/v1/infra/domains/default/groups/bogons/ip-address-expressions/exp1'
            s.patch(nsxtmgr + str(url), data=data, headers=s.headers, auth=s.auth, verify=s.verify) 
            print("\r\n Bogons IPv4 Group Populated \r\n")
            main()

#OPTION B - ADD IP'S TO BOGONS GROUP
def opt_b():
    
    url = '/policy/api/v1/infra/domains/default/groups/bogons/'
    bg_group_exist_json = s.get(nsxtmgr + str(url), headers=s.headers, auth=s.auth, verify=s.verify)

    # Check to ensure group already exists & then add IP's to it
    if bg_group_exist_json.status_code == 200:
    
        with open('<PATH TO FILE>/bogons-ipv4-add.txt') as f:
            ip_list = [line.rstrip() for line in f]

        #ADD ALL ELEMENTS FROM LIST INTO THE GROUP  
        data = json.dumps({"ip_addresses":ip_list})
        print(data)
        url = '/policy/api/v1/infra/domains/default/groups/bogons/ip-address-expressions/exp1?action=add'
        groups_json = s.post(nsxtmgr + str(url), data=data, headers=s.headers, auth=s.auth, verify=s.verify)
        print(groups_json.status_code)
        if groups_json.status_code == 200:
            print("\r\n IP's added to Bogons IPv4 Group \r\n ")
        else:
            print("\r\n File contains no IP Addresses.  No entries added to group \r\n")
        main()
    else:
        #If group does not exist, present message to re-run and create group first
        print("\r\n Cannot add to Bogons IPv4 Group, it does not exist.  Please run option A) first \r\n")
        main()

#OPTION C - REMOVE IP'S FROM BOGONS GROUP
def opt_c():
    url = '/policy/api/v1/infra/domains/default/groups/bogons/'
    bg_group_exist_json = s.get(nsxtmgr + str(url), headers=s.headers, auth=s.auth, verify=s.verify)

    # Check to ensure group already exists & then add IP's to it
    if bg_group_exist_json.status_code == 200:
    
        with open('<PATH TO FILE>/bogons-ipv4-remove.txt') as f:
            ip_list = [line.rstrip() for line in f]

        #REMOVE ELEMENTS FROM LIST FROM THE GROUP  
        data = json.dumps({"ip_addresses":ip_list})
        print(data)
        url = '/policy/api/v1/infra/domains/default/groups/bogons/ip-address-expressions/exp1?action=remove'
        groups_json = s.post(nsxtmgr + str(url), data=data, headers=s.headers, auth=s.auth, verify=s.verify)
        print(groups_json.status_code)
        if groups_json.status_code == 200:
            print("\r\n IP's removed from Bogons IPv4 Group\r\n ")
        else:
            print("\r\n File contains no IP Addresses.  No entries removed from group \r\n")
        main()
    else:
        #If group does not exist, present message to re-run and create group first
        print("\r\n Cannot remove from Bogons IPv4 Group, it does not exist.  Please run option A) first \r\n")
        main()

# OPTION D - APPLY BOGONS GATEWAY POLICY
def opt_d():
    url = '/policy/api/v1/infra/domains/default/groups/bogons/'
    bg_group_exist_json = s.get(nsxtmgr + str(url), headers=s.headers, auth=s.auth, verify=s.verify)

    # Check to ensure group already exists
    if bg_group_exist_json.status_code == 200:
        tier0s_url = '/policy/api/v1/infra/tier-0s'
        tier0s_json = s.get(nsxtmgr + tier0s_url).json()
        tier0_count = (tier0s_json["result_count"])
        tier0_list = []
        for i in range(0,tier0_count):
            tier0_list.append(tier0s_json["results"][i]["id"])
            print(tier0_list[i])
  
        questions = [inquirer.Text('Tier-0', message="Which Tier0 do you want to apply Bogons to?")]
        answers = inquirer.prompt(questions)

        bogons_t0=list(answers.values())
        item = (bogons_t0[0])

        #CHECK IF GATEWAY ALREADY POLICY EXISTS
        url = '/policy/api/v1/infra/domains/default/gateway-policies/T0-BogonsPolicy' + str(item)
        gw_policy_exist_json = s.get(nsxtmgr + str(url), headers=s.headers, auth=s.auth, verify=s.verify)
    
        if gw_policy_exist_json.status_code == 200:
            print("\r\n Gateway Policy for " +str(item), "already exists \r\n")
            main()
        else:
            #CREATE GATEWAY POLICY
            data = json.dumps({'description': 'T0-BogonsPolicy' +str(item), 'display_name': 'T0-BogonsPolicy' +str(item)})
            url = '/policy/api/v1/infra/domains/default/gateway-policies/T0-BogonsPolicy' + str(item)
            groups_json = s.put(nsxtmgr + str(url), data=data, headers=s.headers, auth=s.auth, verify=s.verify)
            print(groups_json)

            #CREATE INBOUND GATEWAY RULE
            data = json.dumps({
                "description": "Bogons Routes Onbound for" +str(item),
                "display_name": "BogonsInbound" +str(item),
                "id": "Bogons-rule1-" +str(item),
                "sequence_number": 0,
                "source_groups": [
                    "/infra/domains/default/groups/bogons"
                ],
                "services": ["Any"],
                "destination_groups": [
                    ""
                ],
                # THIS SPECIFIES WHICH TIER0 THE RULE IS APPLIED TO BASED ON INPUT FROM THE ORIGNAL QUESTION
                "scope": [
                    "/infra/tier-0s/" +str(item) 
                ###################################################
                ],
                "action":"DROP"
            })
            url = '/policy/api/v1/infra/domains/default/gateway-policies/T0-BogonsPolicy' + str(item) + '/rules/Bogons-rule1'
            groups_json = s.patch(nsxtmgr + str(url), data=data, headers=s.headers, auth=s.auth, verify=s.verify)
            print(groups_json)

            #CREATE OUTBOUND GATEWAY RULE
            data = json.dumps({
                "description": "Bogons Routes Outbound for" +str(item),
                "display_name": "BogonsOutbound" +str(item),
                "id": "Bogons-rule2-" +str(item),
                "sequence_number": 1,
                "source_groups": [
                    ""
                ],
                "services": ["Any"],
                "destination_groups": [
                    "/infra/domains/default/groups/bogons"
                ],
                # THIS SPECIFIES WHICH TIER0 THE RULE IS APPLIED TO BASED ON INPUT FROM THE ORIGNAL QUESTION
                "scope": [
                    "/infra/tier-0s/" +str(item) 
                ###################################################
                ],
                "action":"DROP"
            })
            url = '/policy/api/v1/infra/domains/default/gateway-policies/T0-BogonsPolicy' +str(item) + '/rules/Bogons-rule2'
            groups_json = s.patch(nsxtmgr + str(url), data=data, headers=s.headers, auth=s.auth, verify=s.verify)
            print(groups_json)

            print("\r\n Bogons Security applied via Gateway Firewall to" +str(item), " Logical Router \r\n")
    
        main()
    else:
        print("\r\n Cannot apply Bogons security to Tier0 Logical Router. Bogons IPv4 Group does not exist.  Please run option A) first \r\n")
        main()

#VALIDATION CHECKER
def invalid_opt():
    print("Invalid choice")
    main()

#AVAILABLE OPTIONS
options = {"A":["Create Bogons IPv4 Group",opt_a], 
           "B":["Add to Bogons IPv4 Group",opt_b], 
           "C":["Remove from Bogons IPv4 Group",opt_c],
           "D":["Apply Bogons IPv4 Gateway Firewall to a Tier-0",opt_d], 
           "E":["Exit",quit]
        }
#CALL MAIN FUNCTION
def main():
    for option in options:
        print(option+") "+options.get(option)[0])

    choice = input("Please choose option: ")

    val = options.get(choice)

    if val is not None:
        action = val[1]
    else:
        action = invalid_opt

    action()

if __name__ == "__main__":
    main()
