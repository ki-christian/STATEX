# https://github.com/Slicer/Slicer/blob/07bc92102ca225e3d46c5545af650aac3455125d/Modules/Loadable/Markups/MRML/vtkMRMLMarkupsNode.cxx#L476
# GetNthControlPoint
# SetLocked
# TODO: Klicka på knapp när man är klar?
# Kanske fråga, vill du byta punkten när man kollar på den?
# Eller skriv in ... när du är klar
# TODO: Centrera och byt till big_brain för varje ny användare
# TODO: Visa endast strukturer i rätt dataset
# TODO: Ändra Interaction: så kan röra punkter med musen?
# TODO: Klicka när klar: du har x antal obesvarade frågor: Vill du avsluta?
# Potentiella:
# node.UnsetAllControlPoints() - farlig
# Kanske göra to_lower_case för att hantera olika input från csv-filen

PROJECT_FOLDER_PATH = "/Users/christian/KI/Tutor/Projekt/"
BIG_BRAIN_FILE_NAME = "Big_brain.nrrd"
IN_VIVO_FILE_NAME = "In_vivo.nrrd"
EX_VIVO_FILE_NAME = "Synthesized_FLASH25_in_MNI_v2_500um.nii"
STUDENT_STRUCTURES_FILE_NAME = "G_VT23_practical_dis_MRI_.csv" # PATH --> FILE_NAME

BIG_BRAIN = "Big_Brain"
IN_VIVO = "in_vivo"
EX_VIVO = "ex_vivo"

# Kolla om man kan byta dessa?
BIG_BRAIN_VOLUME_NAME = "vtkMRMLScalarVolumeNode1"
IN_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode2"
EX_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode3"

NUMBER_OF_QUESTIONS = 10

import csv

current_dataset = ""
answered_questions = [False] * 10

# Läs även in 3D_Tracts
# Läser in dataseten big_brain, in_vivo och ex_vivo
def loadDatasets(big_brain=True, in_vivo=True, ex_vivo=True): # även 3D_Tracts
    if big_brain:
        slicer.util.loadVolume(PROJECT_FOLDER_PATH + BIG_BRAIN_FILE_NAME)
    if in_vivo:
        slicer.util.loadVolume(PROJECT_FOLDER_PATH + IN_VIVO_FILE_NAME)
    if ex_vivo:
        slicer.util.loadVolume(PROJECT_FOLDER_PATH + EX_VIVO_FILE_NAME)

# Används ej
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

def resetWindow():
    changeDataset(BIG_BRAIN)
    slicer.modules.markups.logic().JumpSlicesToLocation(0, 0, 0, True)

# Öppnar csv-filen med strukturer och läser in alla rader tillhörande exam_nr
def retrieveStructures(exam_nr) -> list:
    structures = []
    with open(PROJECT_FOLDER_PATH + STUDENT_STRUCTURES_FILE_NAME, encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            if int(row["exam_nr"]) == exam_nr:
                structures.append(row)
    return structures

# Printar structure i formatet: Struktur [fråga] (✓/X): [struktur] i [dataset]
def printStructure(structure):
    print(str("Struktur " + structure["question"] + " "), end = "")
    if answered_questions[int(structure["question"]) - 1]:
        print("(✓)", end = "")
    else:
        print("(X)", end = "")
    print(": " + structure["Structure"] + " i " + structure["Dataset"])

# Använder printStructure för att printa alla strukturer i structures
def printStructures(structures):
    for structure in structures:
        printStructure(structure)
    print("(✓) = Besvarad, (X) = Ej besvarad")

# Ändrar nuvarande dataset till specificerat dataset
def changeDataset(dataset):
    global current_dataset
    if dataset == current_dataset:
        return
    if dataset  == BIG_BRAIN:
        displaySelectVolume("vtkMRMLScalarVolumeNode1")
        current_dataset = BIG_BRAIN
    elif dataset == IN_VIVO:
        displaySelectVolume("vtkMRMLScalarVolumeNode2")
        current_dataset = IN_VIVO
    elif dataset == EX_VIVO:
        displaySelectVolume("vtkMRMLScalarVolumeNode3")
        current_dataset = EX_VIVO
    else:
        print("Error: Dataset " + structures[val]["Dataset"] + " not found.\n")

# Lägger till en nod med namnet [exam_nr] och lägger till tillhörande control points
# för varje struktur i structures. Namnet på varje control point blir strukturens
# namn och beskrivningen blir vilken fråga det är.
def addNodeAndControlPoints(exam_nr, structures):
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', str(exam_nr))
    node.SetLocked(1)
    node.AddNControlPoints(10, "", [0, 0, 0])

    for index, structure in enumerate(structures):
        # kanske byta ut index mot structure["question"]?
        node.SetNthControlPointLabel(index, structure["Structure"])
        node.SetNthControlPointDescription(index, f"Struktur {index + 1}")
        node.SetNthControlPointLocked(index, False)
        # kolla var de hamnar och om de är i vägen - kan avmarkera innan man placerat dem
        node.UnsetNthControlPointPosition(index)
    return node

# Ändrar till place mode så att en ny control point kan placeras ut
def setNewControlPoint(node, val):
    # Det här kommer ta bort din gamla markering, är du säker att du vill fortsätta?
    node.UnsetNthControlPointPosition(val)
    node.SetControlPointPlacementStartIndex(val)
    slicer.modules.markups.logic().StartPlaceMode(1)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    # Ta sen tillbaka till normalt läge när klar
    interactionNode.SetPlaceModePersistence(0)
    #interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    #interactionNode.SwitchToViewTransformMode()

    # also turn off place mode persistence if required
    #interactionNode.SetPlaceModePersistence(0)

# Centrerar vyerna på control point
def centreOnControlPoint(node, val):
    # TODO: Hantera för 3D_Tracts
    #node.SetNthControlPointSelected(val, False)
    controlPointCoordinates = node.GetNthControlPointPosition(val) # eller GetNthControlPointPositionWorld
    slicer.modules.markups.logic().JumpSlicesToLocation(controlPointCoordinates[0], controlPointCoordinates[1], controlPointCoordinates[2], True)

# fungerar ej om klickat 1 och sen ej satt ut (ny) punkt
def updateAnsweredQuestions(node):
    global answered_questions
    answered_questions = [False] * 10
    for i in range(node.GetNumberOfControlPoints()):
        controlPointCoordinates = node.GetNthControlPointPosition(i)
        if controlPointCoordinates[0] != 0.0 or controlPointCoordinates[1] != 0.0 or controlPointCoordinates[2] != 0.0:
            answered_questions[i] = True

# Accepterar input i range low (inklusive) till high (inklusive)
def inputNumberInRange(prompt, low, high):
    while True:
        try:
            value = int(input(prompt))
        except:
            print(f"Skriv in en siffra {low}-{high}")
            continue
        if value == 100:
            # ta bort sen
            return 100
        if value >= low and value <= high:
            return value
        else:
            print(f"Skriv in en siffra {low}-{high}")
            continue

def saveNodeToFile(exam_nr, node):
    slicer.util.saveNode(node, PROJECT_FOLDER_PATH + f"{exam_nr}.mrk.json") # eller mkp.json

def main():
    #loadDatasets()

    # TODO: VIKTIGT: STÄLLA IN FÖNSTRET SÅ RÄTT FOKUS, EJ UTZOOMAT, EJ INZOOMAT PÅ NÅGOT KONSTIGT STÄLLE
    # TODO: Centrera vyen när byter dataset
    # Återställer fönstrena och byter till big brain vid ny användare
    resetWindow()

    while True:
        try:
            exam_nr = int(input("Ange exam nr: "))
        except:
            print("Ogiltig input. Försök igen")
            continue
        structures = retrieveStructures(exam_nr)
        # Kontrollera att rätt antal strukturer har lästs in
        if len(structures) != NUMBER_OF_QUESTIONS:
            print("ERROR: Antal inlästa strukturer överensstämmer ej med antalet strukturer som ska läsas in\n")
            input("Fråga om hjälp.")
        printStructures(structures)
        print("\nOBS: Kontrollera att de inlästa strukturerna överensstämmer med dina tilldelade strukturer\n")
        is_correct_exam_nr = inputNumberInRange("Har du angett rätt exam nr?\n1 - Ja\n2 - Nej\n", 1, 2)
        if is_correct_exam_nr == 1:
            break
        if is_correct_exam_nr == 2:
            continue
    node = addNodeAndControlPoints(exam_nr, structures)

    global answered_questions
    answered_questions = [False] * 10 # NUMBER_OF_QUESTIONS

    # Efter det fråga om nästa fråga

    while True:
        #slicer.app.pythonConsole().clear()
        printStructures(structures)
        # val --> question_number
        val = inputNumberInRange("\nVilken fråga vill du besvara?\n", 1, NUMBER_OF_QUESTIONS) - 1 # anpassa för listindex
        # ha detta i en funktion?
        if val == 99:
            return
        printStructure(structures[val])
        changeDataset(structures[val]["Dataset"])
        node.GetDisplayNode().SetActiveControlPoint(val)

        # TODO: option --> action
        option = inputNumberInRange("Vad vill du göra?\n1 - sätta ny punkt\n2 - kolla på punkten\n3 - svara på en annan struktur\n4 - avsluta\n", 1, 4) # fokusera på? centrera på?
        if option == 1:
            # Ändra koordinater för control point
            # checkIfControlPointExists/coordinates?
            replace = 1 # om det inte finns en utsatt control point behöver man ej ha input
            if answered_questions[val]:
                # Om det finns en tidigare placerad control point
                replace = inputNumberInRange("Det här kommer ta bort din gamla markering. Är du säker på att du vill fortsätta?\n1 - Ja\n2 - Nej\n", 1, 2) # fortsätt/avbryt
            if replace == 1:
                # Placera en ny control point
                setNewControlPoint(node, val)
                try:
                    input("Placera punkten. Tryck Enter för att fortsätta.") # vill gå vidare?
                except:
                    # print("Hamnar här av någon anledning")
                    pass
                updateAnsweredQuestions(node)
                # Gör en backup på node
                saveNodeToFile(exam_nr, node)
            elif replace == 2:
                pass
        elif option == 2:
            # Centrera på koordinaterna för control point
            centreOnControlPoint(node, val)
        elif option == 3:
            # TODO: Svara på en annan fråga
            controlPointCoordinates = node.GetNthControlPointPosition(val) # eller GetNthControlPointPositionWorld
            print(f"Position: 1: {controlPointCoordinates[0]} 2: {controlPointCoordinates[1]} 3: {controlPointCoordinates[2]}")
            continue
        elif option == 4:
            # Inte så bra ställe
            amount_answered_questions = 0
            for is_answered in answered_questions:
                if is_answered:
                    amount_answered_questions += 1
            print(f"Du har besvarat {amount_answered_questions}/{NUMBER_OF_QUESTIONS} strukturer")
            quit_input = input("Är du säker att du vill avsluta? Skriv in 123456 för att avsluta")
            if quit_input == "123456":

                # gör något annat
                break
            else:
                continue
    saveNodeToFile(exam_nr, node)

if __name__ == "__main__":
    main()
