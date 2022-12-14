"""
Module to fetch data from the Council website for bin days.
"""
import notifications
import os
import logging
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
# disable warnings from using verify=False in get/post requests
disable_warnings(InsecureRequestWarning)
load_dotenv()



logging.basicConfig(
  handlers=[logging.FileHandler(filename="./log.log",
    encoding="utf-8", mode="a+")],
  level=logging.DEBUG,
  format="%(asctime)s %(message)s",
  datefmt="%m/%d/%Y %I:%M:%S %p"
)

class Bin:
  def __init__(self, color, description):
    self.color = color
    self.description = description

  def SetDate(self, date):
    ignore = "Next Collection: "
    date_string = date[len(ignore):]
    date_time = datetime.strptime(date_string, "%A %d %B %Y")
    self.collection_date = date_time


class Bins:
  """
  Bins class holds a dictionary of the bins with their colours
  """
  def __init__(self):
    self.bins : dict[str, Bin]= {}

  def AddBin(self, new_bin : Bin):
    self.bins[new_bin.color] = new_bin

  def PopulateBins(self, data):
    for item in data:
      for (key, value) in self.bins.items():
        if key in item[0]:
          value.SetDate(item[1])

  def Jsonify(self):
    bin_list = []
    for val in self.bins.values():
      val.collection_date = str(val.collection_date.date())
      bin_list.append(val.__dict__)
    return bin_list

  def SendMessage(self):
    today = datetime.today()
    colors = []
    for (key, value) in self.bins.items():
      if value.collection_date.date() - timedelta(days=1) == today.date():
        colors.append(key.lower())
    bin_string = ""

    if len(colors) > 0:
      if len(colors) == 1:
        bin_string = colors[0]
      else:
        bin_string = colors[0]
        for i in range(1, len(colors) - 1):
          bin_string += ", " + colors[i]
        bin_string += " and " + colors[-1]

      title = "⚠️ Time to BinReal. ⚠️"

      if len(colors) == 1:
        message = "The " + bin_string + " bin needs to go out tonight."
      else:
        message = "The " + bin_string + " bins need to go out tonight."
      notifications.send_notification(title, message, 136)
      # notifications.SendFakeNotification(title, message)
      # return 1 if notification is sent else 0
      return 1

    notifications.send_notification("All Good My G",
      "Give yourself a pat on the back", 15, True)
    return 0

def get_bin_data():
  bin_url = "https://ecitizen.oxford.gov.uk/citizenportal/form.aspx?form=Bin_Collection_Day"

  r1 = requests.get(bin_url, verify=False, timeout=10)
  soup1 = BeautifulSoup(r1.content, "html.parser")


  payload1 = {
    "Eform$Bin_Collection_Address_Search$AddressField_CustomerAddress$ibtnFindAddress.x" : 1,
    "Eform$Bin_Collection_Address_Search$AddressField_CustomerAddress$ibtnFindAddress.y" : 1,
    "Eform$Bin_Collection_Address_Search$AddressField_CustomerAddress$CustomerAddress" : os.getenv("POSTCODE")
  }

  payload1["__VIEWSTATE"] = soup1.select_one("#__VIEWSTATE")["value"]
  payload1["__VIEWSTATEGENERATOR"] = soup1.select_one("#__VIEWSTATEGENERATOR")["value"]
  payload1["__EVENTVALIDATION"] = soup1.select_one("#__EVENTVALIDATION")["value"]

  r2 = requests.post(bin_url, data=payload1, verify=False, cookies=r1.cookies, timeout=10)
  soup2 = BeautifulSoup(r2.text, "html.parser")

  payload2 = {
    "Eform$Bin_Collection_Address_Search$AddressField_CustomerAddress$CustomerAddress" : os.getenv("POSTCODE"),
    "Eform$Bin_Collection_Address_Search$AddressField_CustomerAddress$lstSelectAddress" : os.getenv("PROPERTYREF"),
    "Eform$Bin_Collection_Address_Search$NavigateNextButton.x" : 62,
    "Eform$Bin_Collection_Address_Search$NavigateNextButton.y" : 17
  }

  payload2["__VIEWSTATE"] = soup2.select_one("#__VIEWSTATE")["value"]
  payload2["__VIEWSTATEGENERATOR"] = soup2.select_one("#__VIEWSTATEGENERATOR")["value"]
  payload2["__EVENTVALIDATION"] = soup2.select_one("#__EVENTVALIDATION")["value"]

  r3 = requests.post(bin_url, data=payload2, verify=False, cookies=r2.cookies, timeout=10)
  soup3 = BeautifulSoup(r3.text, "html.parser")

  my_bins = Bins()
  my_bins.AddBin(Bin("Green", "General waste"))
  my_bins.AddBin(Bin("Blue", "Recycling"))
  my_bins.AddBin(Bin("Food", "Food waste"))

  bins = [item.text for item in soup3.find_all("th")]
  dates = [item.text for item in soup3.find_all("td")]

  if any("exception" in x for x in dates):
    print(soup3, file=open("error.log","a", encoding="UTF=8"))
    raise AssertionError("Wrong page returned")

  result = list(zip(bins, dates))
  # print(*result, sep='\n')

  my_bins.PopulateBins(result)
  # my_bins.PrintBins()
  # sent = my_bins.SendMessage()

  # returns 1 if message was sent and 0 if not
  return my_bins
