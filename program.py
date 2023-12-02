# https://github.com/Slicer/Slicer/blob/07bc92102ca225e3d46c5545af650aac3455125d/Modules/Loadable/Markups/MRML/vtkMRMLMarkupsNode.cxx#L476
# GetNthControlPoint
# SetLocked
# TODO: Klicka på knapp när man är klar?
# Kanske fråga, vill du byta punkten när man kollar på den?
# Eller skriv in ... när du är klar
# TODO: Centrera och byt till big_brain för varje ny användare
# TODO: Visa i konsollen vilka som är obesvarade och ej. Typ Fråga 5 (ej besvarad): Colliculus superior i in_vivo
# TODO: Fråga --> struktur
# TODO: Visa endast strukturer i rätt dataset

PROJECT_FOLDER_PATH = ""
BIG_BRAIN_FILE_NAME = "Big_brain.nrrd"
IN_VIVO_FILE_NAME = "In_vivo.nrrd"
EX_VIVO_FILE_NAME = "Synthesized_FLASH25_in_MNI_v2_500um.nii"
STUDENT_STRUCTURES_FILE_NAME = "G_VT23_practical_dis_MRI_.csv" # PATH --> FILE_NAME
# NUMBER_OF_QUESTIONS =

import csv



current_dataset = ""

# kan även ge en lista med datasets
def loadDatasets(big_brain=True, in_vivo=True, ex_vivo=True): # även 3D_Tracts
    if big_brain:
        slicer.util.loadVolume(PROJECT_FOLDER_PATH + BIG_BRAIN_FILE_NAME)
    if in_vivo:
        slicer.util.loadVolume(PROJECT_FOLDER_PATH + IN_VIVO_FILE_NAME)
    if ex_vivo:
        slicer.util.loadVolume(PROJECT_FOLDER_PATH + EX_VIVO_FILE_NAME)

def createControlPoints(node, structures):
    for structure in structures:
        node.AddControlPoint()

def displaySelectVolume(a):
    layoutManager = slicer.app.layoutManager()
    for sliceViewName in layoutManager.sliceViewNames():
        view = layoutManager.sliceWidget(sliceViewName).sliceView()
        sliceNode = view.mrmlSliceNode()
        sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
        compositeNode = sliceLogic.GetSliceCompositeNode()
        compositeNode.SetBackgroundVolumeID(str(a))

# Read excel-file for the student_id
def retrieveStructures(student_id) -> list:
    structures = []
    with open(PROJECT_FOLDER_PATH + STUDENT_STRUCTURES_FILE_NAME, encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            if int(row["exam_nr"]) == student_id:
                structures.append(row)
    return structures

def printStructures(structures):
    for structure in structures:
        print(str("Fråga " + structure["question"] + ": " + structure["Structure"] + " i " + structure["Dataset"]))

# skicka bara dataset som argument
def changeDataset(structures, val):
    if structures[val]["Dataset"]  == "Big_Brain":
        displaySelectVolume("vtkMRMLScalarVolumeNode1")
    elif structures[val]["Dataset"]  == "in_vivo":
        displaySelectVolume("vtkMRMLScalarVolumeNode2")
    elif structures[val]["Dataset"]  == "ex_vivo":
        displaySelectVolume("vtkMRMLScalarVolumeNode3")
    else:
        print("Error: Dataset " + structures[val]["Dataset"] + " not found.\n")

def addNodeAndControlPoints(student_id, structures):
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', str(student_id))
    node.SetLocked(1)

    node.AddNControlPoints(10, "", [0, 0, 0])

    #node.AddControlPoint()
    for index, structure in enumerate(structures):
        node.SetNthControlPointLabel(index, structure["Structure"])
        node.SetNthControlPointDescription(index, f"Fråga {index + 1}")
        node.SetNthControlPointLocked(index, False)
        # kolla var de hamnar och om de är i vägen
        node.UnsetNthControlPointPosition(index)
    return node

def setNewControlPoint(node, val):
    # Det här kommer ta bort din gamla markering, är du säker att du vill fortsätta?
    node.UnsetNthControlPointPosition(val)
    node.SetControlPointPlacementStartIndex(val)
    slicer.modules.markups.logic().StartPlaceMode(1)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SetPlaceModePersistence(0)
    # Ta sen tillbaka till normalt läge när klar, hur vet man? Kanske kolla när index ökat?

def centreOnControlPoint(node, val):
    #node.SetNthControlPointSelected(val, False)
    controlPointCoordinates = node.GetNthControlPointPositionWorld(val)
    slicer.modules.markups.logic().JumpSlicesToLocation(controlPointCoordinates[0], controlPointCoordinates[1], controlPointCoordinates[2], True)

    #interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    #interactionNode.SwitchToViewTransformMode()

    # also turn off place mode persistence if required
    #interactionNode.SetPlaceModePersistence(0)


if __name__ == "__main__":
    # flytta till en programlogic metod

    #loadDatasets()

    # TODO: VIKTIGT: STÄLLA IN FÖNSTRET SÅ RÄTT FOKUS, EJ UTZOOMAT, EJ INZOOMAT PÅ NÅGOT KONSTIGT STÄLLE
    # TODO: Centrera vyen när byter dataset
    # TODO: Spara vilka som inte svarat på. Obesvarade frågor. Antingen hålla koll på i array, eller loopa och se vilka som ej har koordinater.

    running = 1

    student_id = int(input("Ange studentid: "))

    structures = retrieveStructures(student_id)

    node = addNodeAndControlPoints(student_id, structures)


    #for structure in structures:
    #    slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', str(structure["question"]) + ": " + structure["Structure"])



    # testa om structures är tom, gör i while loop tills får giltigt student_id
    # spara current_dataset


    # Vad vill du göra med datapunkten: 1 - kolla på den, 2 - ändra den
    # Om valt kolla på den, vill du ändra den, eller är du klar?
    # Efter det fråga om nästa fråga

    while(running):
        printStructures(structures)
        val = int(input("\nVilken fråga vill du besvara?\n")) - 1 # anpassa för listindex
        # ha detta i en funktion?
        if val == 99:
            running = 0
            break
        if val == 53:
            # TODO: testa denna
            node.UnsetAllControlPoints()
        if val < 10:
            print("Fråga " + str(val + 1) + ": " + structures[val]["Structure"] + " i dataset " + structures[val]["Dataset"] + "\n")
            changeDataset(structures, val)

            #print(node.GetDisplayNode())
            node.GetDisplayNode().SetActiveControlPoint(val)

        option = int(input("Vad vill du göra?\n1 - sätta ny punkt\n2 - kolla på punkten\n")) # fokusera på? centrera på?
        if option == 1:
            # Ändra koordinater
            setNewControlPoint(node, val)
        if option == 2:
            # Visa koordinater
            centreOnControlPoint(node, val)
        if option == 3:
            # TODO: Svara på en annan fråga
            pass
