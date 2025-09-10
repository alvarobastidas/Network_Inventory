import meraki
import pandas as pd
import json

def get_inventory(dashboard): #Retrivev inventory for all accessible organizations
   inventory = []
   _inventory = []
   _devices  = []
   _networks = []
   _licenses = []
   _status   = []

   try:
      organizations = dashboard.organizations.getOrganizations()
      for org in organizations:
         devices  = dashboard.organizations.getOrganizationDevices(org["id"])

         for dev in devices:
            _devices.append(dev)
            item = {}
            item["organizationID"]   = org['id']
            item["organizationName"] = org['name']
            item['networkID']        = dev["networkId"]
            item["deviceName"]       = dev["name"]
            item["deviceSerial"]     = dev["serial"]
            item["productType"]      = dev["productType"]
            item["deviceModel"]      = dev["model"]
            item["deviceAddress"]    = dev["address"]
            if dev["productType"] in ("wireless", "switch"):
               item["lanIp"]          = dev["lanIp"]
               item["wan1Ip"]         = 'N/A'
               item["wan2Ip"]         = 'N/A'
            elif dev["productType"] == "appliance":
               item["lanIp"]          = 'N/A'
               item["wan1Ip"]         = dev["wan1Ip"]
               item["wan2Ip"]         = dev["wan2Ip"]
            else:
               item["lanIp"]          = 'N/A'
               item["wan1Ip"]         = 'N/A'
               item["wan2Ip"]         = 'N/A'
            inventory.append(item)

      for org in organizations:
         networks = dashboard.organizations.getOrganizationNetworks(org["id"])

         for net in networks:
            _networks.append(net)
            for device in inventory:
               if device["networkID"] == net["id"]:
                  try:
                     if device["networkName"]:
                        print('Device Network already updated')
                  except:
                     device.update({
                     'networkName': net["name"],
                     'networkTime': net["timeZone"]
                  })

      for org in organizations:
         licenses = dashboard.organizations.getOrganizationLicenses(org["id"])
         for lic in licenses:
            _licenses.append(lic)
            for device in inventory:
               if device["deviceSerial"] == lic["deviceSerial"]:
                  device.update({
                        "licenseType":    lic["licenseType"],
                        "licenseState":   lic["state"],
                        "activationDate": lic["activationDate"],
                        "expirationDate": lic["expirationDate"]
                     })
               else:
                  try:
                     if device["licenseType"]:
                        pass
                        # print('Device License already updated')
                  except:
                     device.update({
                        "licenseType": 'N/A',
                        "licenseState": 'N/A',
                        "activationDate": 'N/A',
                        "expirationDate": 'N/A'
                     })

      for org in organizations:
         status   = dashboard.organizations.getOrganizationDevicesStatuses(org["id"])
         for stat in status:
            _status.append(stat)
            for device in inventory:
               if device["deviceSerial"] == stat["serial"]:
                  device.update({
                     "devicePublicIp": stat["publicIp"],
                     "deviceStatus":   stat["status"]
                     })
               else:
                  try:
                     if device["deviceStatus"]:
                        pass
                        # print('Device Status already updated')
                  except:
                     device.update({
                        "devicePublicIp": "N/A",
                        "deviceStatus":   "N/A"
                     })

      for inv in inventory:
         _inventory.append({
            "organizationID":    inv["organizationID"],
            "organizationName":  inv["organizationName"],
            "networkID":         inv["networkID"],
            "networkName":       inv["networkName"],
            "networkTime":       inv["networkTime"],
            "deviceName":        inv["deviceName"],
            "deviceSerial":      inv["deviceSerial"],
            "productType":       inv["productType"],
            "deviceModel":       inv["deviceModel"],
            "deviceAddress":     inv["deviceAddress"],
            "lanIp":             inv["lanIp"],
            "wan1Ip":            inv["wan1Ip"],
            "wan2Ip":            inv["wan2Ip"],
            "licenseType":       inv["licenseType"],
            "licenseState":      inv["licenseState"],
            "activationDate":    inv["activationDate"],
            "expirationDate":    inv["expirationDate"],
            "devicePublicIp":    inv["devicePublicIp"],
            "deviceStatus":      inv["deviceStatus"]
         })

   except Exception as e:
      print(f"Error retrieving inventory: {e}")

   return pd.DataFrame(_inventory), pd.DataFrame(organizations), pd.DataFrame(_devices), pd.DataFrame(_networks), pd.DataFrame(_licenses), pd.DataFrame(_status)

#Path to save files
path = '/Users/fernando/Desktop/Alvaro/Personal/Study-Guides-Cert/Network Automation/LABS/Network_Inventory/outputs/'

# Replace with your Meraki Dashboard API Key
API_KEY = '25cabf2e15201ff8d36af3be61ef5ddc07ed43f0'

#Initializate the Meraki Dashboard API client
_dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)


if __name__=="__main__":
   df = get_inventory(_dashboard)
   inventory      = df[0]
   organizations  = df[1]
   devices        = df[2]
   networks       = df[3]
   licenses       = df[4]
   status         = df[5]
    
   # Save to Excel with multiple sheets
   with pd.ExcelWriter(f"{path}Meraki_inventory.xlsx", engine="openpyxl") as writer:
      inventory.to_excel(writer, sheet_name="Inventory", index=False)
      organizations.to_excel(writer, sheet_name="Organizations", index=False)
      networks.to_excel(writer, sheet_name="Networks", index=False)
      devices.to_excel(writer, sheet_name="Devices", index=False)
      licenses.to_excel(writer, sheet_name="Licenses", index=False)
      status.to_excel(writer, sheet_name="Status", index=False)

   print("\n✅ Inventory saved to 'Meraki_inventory.xlsx' ")
   print("      -Inventory sheet --> full inventory")
   print("      -Organizations sheet --> Organizations list")
   print("      -Networks sheet --> Networks list")
   print("      -Devices sheet --> Devices list")
   print("      -Licenses sheet --> Licenses Devices list")
   print("      -Status sheet --> Status Devices list")

else:
   print("\n⚠️ No inventory data retrieved")
   
      
