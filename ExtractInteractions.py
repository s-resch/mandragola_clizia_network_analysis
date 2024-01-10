from lxml import etree
import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv

def extractInteractions(filename):

    # Read complete play and parse into XML tree
    treePlay = etree.parse(filename)

    # Get al list of all characters in play
    listCast = treePlay.findall('//role')

    # Create Node CSV file
    with open(filename + "_Nodes.csv", "w", newline='') as the_file:
        # Manage CSV writer settings
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
        writer = csv.writer(the_file, dialect="custom")

        # Write headline
        writer.writerow(["id", "label", "timeset"])

        # Write character information into CSV        
        for i in range(len(listCast)):
            writer.writerow([i, listCast[i].text, ""])

    # Set counter variable to create ID for each entry of speech interaction
    counter = 0

    # Create Edge CSV file
    with open(filename + "_Edges.csv", "w", newline='') as the_file:
        # Manage CSV writer settings
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
        writer = csv.writer(the_file, dialect="custom")

        # Write headline
        writer.writerow(["Source", "Target", "Type", "Kind", "Id", "Label", "timeset","Weight"])

        # Write interaction information into CSV
        # Loop though all characters: Once for speaking character (who) and once for addressed character (toWhom)
        for who in range(len(listCast)):
            for toWhom in range(len(listCast)):
                # We only analyze dialogic speech acts, so ignore identic speaker and addressee
                if who != toWhom:
                    # Get speaker and addresse ID from XML
                    speaker = listCast[who].get('{http://www.w3.org/XML/1998/namespace}id')
                    addressee = listCast[toWhom].get('{http://www.w3.org/XML/1998/namespace}id')

                    # Create XPath to query all <sp> tags with attributes @who and @toWhom with corresponding values
                    xpath = "//sp[@who='#"+speaker+"'][contains(@toWhom, '#"+addressee+"')]"

                    # Execute XPath query on XML tree
                    result = treePlay.getroot().xpath(xpath)

                    # Get number of results of our query 
                    # --> How many <sp>-Tags with given @who and @toWhom configuration have we found? --> weight of edge
                    length = len(result)

                    # Write result (weight of edge) into CSV with all information needed
                    writer.writerow([who, toWhom, "Directed", "addresses", counter, "", "", length])

                    # Increment counter to make sure all entries in CSV get a unique ID
                    counter+=1
