# https://github.com/Slicer/Slicer/blob/07bc92102ca225e3d46c5545af650aac3455125d/Modules/Loadable/Markups/MRML/vtkMRMLMarkupsNode.cxx#L476
# GetNthControlPoint
# SetLocked

# PROJECT_FOLDER =

import csv

project_folder = "" # sätt som constant?

current_dataset = ""

# kan även ge en lista med datasets
def loadDatasets(big_brain=True, in_vivo=True, ex_vivo=True): # även 3D_Tracts
    if big_brain:
        slicer.util.loadVolume(project_folder + "Big_brain.nrrd")
    if in_vivo:
        slicer.util.loadVolume(project_folder + "In_vivo.nrrd")
    if ex_vivo:
        slicer.util.loadVolume(project_folder + "Synthesized_FLASH25_in_MNI_v2_500um.nii") # ex_vivo

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
    with open(project_folder + "G_VT23_practical_dis_MRI_.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            if int(row["exam_nr"]) == student_id:
                structures.append(row)
    return structures

def printStructures(structures):
    for structure in structures:
        print(str("Fråga " + structure["question"] + ": " + structure["Structure"] + " i " + structure["Dataset"]))

def changeDataset(structures, val):
    if structures[val]["Dataset"]  == "Big_Brain":
        displaySelectVolume("vtkMRMLScalarVolumeNode1")
    elif structures[val]["Dataset"]  == "in_vivo":
        displaySelectVolume("vtkMRMLScalarVolumeNode2")
    elif structures[val]["Dataset"]  == "ex_vivo":
        displaySelectVolume("vtkMRMLScalarVolumeNode3")
    else:
        print("Error: Dataset " + structures[val]["Dataset"] + " not found.\n")

if __name__ == "__main__":
    loadDatasets()

    # TODO: VIKTIGT: STÄLLA IN FÖNSTRET SÅ RÄTT FOKUS, EJ UTZOOMAT, EJ INZOOMAT PÅ NÅGOT KONSTIGT STÄLLE


    running = 1

    student_id = int(input("Ange studentid: "))

    structures = retrieveStructures(student_id)

    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', str(student_id))
    node.SetLocked(1)

    node.AddNControlPoints(10, "", [0, 0, 0])
    node.SetNthControlPointLabel(5, "Test")

    #node.AddControlPoint()
    for index, structure in enumerate(structures):
        node.SetNthControlPointLabel(index, structure["Structure"])
        node.SetNthControlPointDescription(index, f"Fråga {index + 1}")
        node.SetNthControlPointLocked(index, False)
        # kolla var de hamnar och om de är i vägen
        node.UnsetNthControlPointPosition(index)

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
            print(node.GetDisplayNode())
            node.GetDisplayNode().SetActiveControlPoint(val)


        option = int(input("Vad vill du göra?\n1 - sätta ny punkt\n2 - kolla på punkten\n")) # fokusera på? centrera på?
        if option == 1:
            # TODO: Ändra koordinater
            pass
        if option == 2:
            # TODO: Visa koordinater
            #node.SetNthControlPointSelected(val, False)
            slicer.util.setSliceViewerLayers(background = node)
            slicer.util.resetSliceViews()

            pass
