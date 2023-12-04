# https://github.com/Slicer/Slicer/blob/07bc92102ca225e3d46c5545af650aac3455125d/Modules/Loadable/Markups/MRML/vtkMRMLMarkupsNode.cxx#L476
# GetNthControlPoint
# SetLocked
# Eller skriv in ... när du är klar
# TODO: Visa endast strukturer i rätt dataset
# TODO: Ändra Interaction: så kan röra punkter med musen?
# Potentiella:
# node.UnsetAllControlPoints() - farlig
# Kanske göra to_lower_case för att hantera olika input från csv-filen

PROJECT_FOLDER_PATH = ""
DATASETS_FILE_NAME = "open_me.mrb"
BIG_BRAIN_FILE_NAME = "Big_brain.nrrd"
IN_VIVO_FILE_NAME = "In_vivo.nrrd"
EX_VIVO_FILE_NAME = "Synthesized_FLASH25_in_MNI_v2_500um.nii"
STUDENT_STRUCTURES_FILE_NAME = "G_VT23_practical_dis_MRI_.csv" # PATH --> FILE_NAME

BIG_BRAIN = "Big_Brain"
IN_VIVO = "in_vivo"
EX_VIVO = "ex_vivo"
TRACTS_3D = "Tracts_3D"

BIG_BRAIN_VOLUME_NAME = "vtkMRMLScalarVolumeNode3"
IN_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode1"
EX_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode2"

NUMBER_OF_QUESTIONS = 10

import csv

current_dataset = ""
answered_questions = [False] * NUMBER_OF_QUESTIONS

# Läser in dataseten big_brain, in_vivo, ex_vivo och tracts_3d
def loadDatasets(big_brain=True, in_vivo=True, ex_vivo=True, tracts_3d=True):
    slicer.util.loadScene(PROJECT_FOLDER_PATH + DATASETS_FILE_NAME)
    #if big_brain:
    #    slicer.util.loadVolume(PROJECT_FOLDER_PATH + BIG_BRAIN_FILE_NAME)
    #if in_vivo:
    #    slicer.util.loadVolume(PROJECT_FOLDER_PATH + IN_VIVO_FILE_NAME)
    #if ex_vivo:
    #    slicer.util.loadVolume(PROJECT_FOLDER_PATH + EX_VIVO_FILE_NAME)

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
    if checkIfControlPointExists(int(structure["question"]) - 1):
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
        displaySelectVolume(BIG_BRAIN_VOLUME_NAME)
        current_dataset = BIG_BRAIN
    elif dataset == IN_VIVO:
        displaySelectVolume(IN_VIVO_VOLUME_NAME)
        current_dataset = IN_VIVO
    elif dataset == EX_VIVO:
        displaySelectVolume(EX_VIVO_VOLUME_NAME)
        current_dataset = EX_VIVO
    elif dataset == TRACTS_3D:
        print(f"\n{TRACTS_3D} ses i övre högra fönstret\n")
        pass
    else:
        # Val existerar ej
        print("Datasetet existerar ej")
        #print("Error: Dataset " + structures[val]["Dataset"] + " not found.\n")

# Lägger till en nod med namnet exam_nr och lägger till tillhörande control points
# för varje struktur i structures. Namnet på varje control point blir strukturens
# namn och beskrivningen blir vilket nummer strukturen är.
def addNodeAndControlPoints(exam_nr, structures):
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', str(exam_nr))
    node.SetLocked(1)
    node.AddNControlPoints(10, "", [0, 0, 0])
    for index, structure in enumerate(structures):
        # kanske byta ut index mot structure["question"]?
        node.SetNthControlPointLabel(index, structure["Structure"])
        node.SetNthControlPointDescription(index, f"Struktur {index + 1}")
        node.SetNthControlPointLocked(index, False)
        # Avmarkerar strukturen innan man placerat den.
        # Tar bort koordinater [0, 0, 0] för skapade punkten så att den inte är i vägen.
        node.UnsetNthControlPointPosition(index)
    return node

# Ändrar till place mode så att en ny control point kan placeras ut
def setNewControlPoint(node, val):
    # Återställ control point
    node.SetNthControlPointPosition(val, 0.0, 0.0, 0.0)
    node.UnsetNthControlPointPosition(val)
    # Placera ut ny control point
    node.SetControlPointPlacementStartIndex(val)
    slicer.modules.markups.logic().StartPlaceMode(1)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    # Återgå sedan tillbaka till normalt läge när klar
    interactionNode.SetPlaceModePersistence(0)
    #interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    #interactionNode.SwitchToViewTransformMode()

    # also turn off place mode persistence if required
    #interactionNode.SetPlaceModePersistence(0)

def checkIfControlPointExists(question_number):
    return answered_questions[question_number]

# Centrerar vyerna på control point
def centreOnControlPoint(node, val):
    # TODO: Hantera för 3D_Tracts
    controlPointCoordinates = node.GetNthControlPointPosition(val) # eller GetNthControlPointPositionWorld
    slicer.modules.markups.logic().JumpSlicesToLocation(controlPointCoordinates[0], controlPointCoordinates[1], controlPointCoordinates[2], True)

# fungerar ej om klickat 1 och sen ej satt ut (ny) punkt
def updateAnsweredQuestions(node):
    global answered_questions
    answered_questions = [False] * 10
    for i in range(node.GetNumberOfControlPoints()):
        controlPointCoordinates = node.GetNthControlPointPosition(i)
        # Kan också kolla om den är set eller unset
        if controlPointCoordinates[0] != 0.0 or controlPointCoordinates[1] != 0.0 or controlPointCoordinates[2] != 0.0:
            # Om koordinater för control point ej är [0.0, 0.0, 0.0] är frågan besvarad
            answered_questions[i] = True

# Accepterar input med meddelandet prompt i range low (inklusive) till high (inklusive)
def inputNumberInRange(prompt, low, high):
    while True:
        try:
            value = int(input(prompt))
        except:
            # Kunde ej parse:a input
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
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

    # readExamNr()
    while True:
        # kanske studentLoop
        try:
            exam_nr = int(input("Ange exam nr: "))
        except:
            print("Ogiltig input. Försök igen")
            continue
        structures = retrieveStructures(exam_nr)
        # Kontrollera att rätt antal strukturer har lästs in
        if len(structures) == 0:
            print("ERROR: Inga strukturer hittades. Testa igen")
            continue
        if len(structures) != NUMBER_OF_QUESTIONS:
            print("ERROR: Antal inlästa strukturer överensstämmer ej med antalet strukturer som ska läsas in\n")
            input("Fråga om hjälp")
        printStructures(structures)
        print("\nOBS: Kontrollera att de inlästa strukturerna överensstämmer med dina tilldelade strukturer\n")
        is_correct_exam_nr = inputNumberInRange("Har du angett rätt exam nr?\n1 - Ja\n2 - Nej\n", 1, 2)
        if is_correct_exam_nr == 1:
            break
        if is_correct_exam_nr == 2:
            continue
    node = addNodeAndControlPoints(exam_nr, structures)

    while True:
        #slicer.app.pythonConsole().clear()
        updateAnsweredQuestions(node)
        # Gör en backup på node
        saveNodeToFile(exam_nr, node)
        printStructures(structures)
        question_option = inputNumberInRange("\nVilken fråga vill du besvara?\n", 1, NUMBER_OF_QUESTIONS) - 1 # anpassa för listindex
        # ha detta i en funktion?
        if question_option == 99:
            return
        printStructure(structures[question_option])
        changeDataset(structures[question_option]["Dataset"])
        node.GetDisplayNode().SetActiveControlPoint(question_option)

        action_option = inputNumberInRange("Vad vill du göra?\n1 - sätta ny punkt\n2 - kolla på punkten\n3 - svara på en annan struktur\n4 - avsluta\n", 1, 4) # fokusera på? centrera på?
        if action_option == 1:
            # Ändra koordinater för control point
            # checkIfControlPointExists/coordinates?
            replace = 1 # Om det inte finns en placerad control point behöver man ej ha input
            if checkIfControlPointExists(question_option):
                # Om det finns en tidigare placerad control point
                replace = inputNumberInRange("Det här kommer ta bort din gamla markering. Är du säker på att du vill fortsätta?\n1 - Ja\n2 - Nej\n", 1, 2) # fortsätt/avbryt
            if replace == 1:
                # Placera en ny control point
                setNewControlPoint(node, question_option)
                try:
                    input("Placera punkten. Tryck Enter för att fortsätta.") # vill gå vidare? Även för att spara progress
                except:
                    # Hamnar här ibland
                    pass
            elif replace == 2:
                pass
        elif action_option == 2:
            # Centrera på koordinaterna för control point om den existerar
            if checkIfControlPointExists(question_option):
                centreOnControlPoint(node, question_option)
        elif action_option == 3:
            # Svara på en annan fråga
            continue
        elif action_option == 4:
            # Flytta till ett bättre ställe
            amount_answered_questions = 0
            for is_answered in answered_questions:
                if is_answered:
                    amount_answered_questions += 1
            print(f"Du har besvarat {amount_answered_questions}/{NUMBER_OF_QUESTIONS} strukturer")
            quit_input = input("Är du säker att du vill avsluta? Skriv in 123456 för att avsluta")
            if quit_input == "123456":
                # TODO: gör något annat
                break
            else:
                continue
    saveNodeToFile(exam_nr, node)

if __name__ == "__main__":
    main()
