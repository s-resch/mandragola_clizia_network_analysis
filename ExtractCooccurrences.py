from lxml import etree
import xml.etree.ElementTree as ET
from xml.dom import minidom
import csv
import string


def extractCooccurrences(filename):

    #
    # Preparational work
    #

    # Read complete play and parse into XML tree
    treePlay = etree.parse(filename)

    # Get a list of all scenes in play - choose needed one and comment out other one
    # Mandragola version
    # listScene = treePlay.xpath("//div2[@type='scena']/stage")
    # Clizia version
    listScene = treePlay.xpath("//div[@type='scene']/stage")

    # Variable to store roles for complete play
    roles = []
    # Variable to store roles that appear together in one scene (as mentioned in scene header)
    rolesWithinScenes = []

    # Prepare translation table to remove interpunction from strings
    tr_table = str.maketrans("", "", string.punctuation)
    # Delete comma from translation table, so we can keep it in strings
    del tr_table[ord(",")]
    del tr_table[ord("'")]

    #
    # Extract roles
    #

    # Loop through all scenes
    for i in range(len(listScene)):
        # Get text from stage node
        listSceneCharacters = listScene[i].text
        # Only proceed if we don't have empty string
        if listSceneCharacters != '':
            # Save roles that appear together in current scene, remove whitespaces, interpunction (except comma) and convert to lower case
            rolesWithinScenesString = listSceneCharacters.replace(
                ", ", ",").translate(tr_table).lower()
            rolesWithinScenes.append(rolesWithinScenesString)
            # Split roles that appear in one scene into array
            sceneRoles = rolesWithinScenesString.split(',')
            # Loop though all roles that appear in our scene, only proceed if we have more than one person on stage
            if len(sceneRoles) > 1:
                for j in range(len(sceneRoles)):
                    # Check if current role hasn't been saved yet and make sure we don't have an empty string
                    if sceneRoles[j].title() not in roles and sceneRoles[j] != '':
                        # Save role in our list
                        roles.append(sceneRoles[j].title())

    #
    # Write Node CSV
    #

    # Create Node CSV file
    with open(filename + "_Cooc_Correct_Nodes.csv", "w", newline='') as the_file:
        # Manage CSV writer settings
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
        writer = csv.writer(the_file, dialect="custom")

        # Write headline
        writer.writerow(["id", "label", "timeset"])

        # Write role information into CSV
        for i in range(len(roles)):
            writer.writerow([i, roles[i], ""])

    #
    # Write Edges CSV
    #

    # Set counter variable to create ID for each entry of co-occurrence
    counter = 0

    # Create Edge CSV file
    with open(filename + "_Cooc_Correct_Edges.csv", "w", newline='') as the_file:
        # Manage CSV writer settings
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
        writer = csv.writer(the_file, dialect="custom")

        # Write headline
        writer.writerow(["Source", "Target", "Type", "Kind",
                        "Id", "Label", "timeset", "Weight"])

        # Write co-occurrence information into CSV
        # Loop though all roles, always in 'pairs', as co-occurrences are analyzes in 'pairs'
        for RoleOne in range(len(roles)):
            for RoleTwo in range(len(roles)):
                # Both roles mustn't be identic (would be illogical) and consider pairs only once (so 1-2 excvludes 2-1)
                if RoleOne != RoleTwo and RoleOne < RoleTwo:
                    # Set counter to calculate weight of edge
                    weightCounter = 0
                    # Loop though all scenes respectively though all role combinations saved for single scenes
                    for scene in range(len(rolesWithinScenes)):
                        # If both roles are present in current scene, increase weight
                        if roles[RoleOne] in rolesWithinScenes[scene] and roles[RoleTwo] in rolesWithinScenes[scene]:
                            weightCounter += 1

                    # Write result (weight of edge) into CSV with all information needed
                    writer.writerow(
                        [RoleOne, RoleTwo, "Undirected", "co-occurres on stage with", counter, "", "", weightCounter])

                    # Increment counter to make sure all entries in CSV get a unique ID
                    counter += 1
