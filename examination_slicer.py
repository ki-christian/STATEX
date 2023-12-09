"""examination_slicer.py: Program skapat för stationsexamination i 3D Slicer
i kursen Basvetenskap 4 på Karolinska Institutet."""

__author__ = "Christian Andersson"
#__version__ = "1.0"
__email__ = "christian.andersson.2@stud.ki.se"

import os
import csv

PROJECT_FOLDER_PATH = ""
DATASETS_FILE_NAME = "open_me.mrb"
BIG_BRAIN_FILE_NAME = "Big_brain.nrrd"
IN_VIVO_FILE_NAME = "In_vivo.nrrd"
EX_VIVO_FILE_NAME = "Synthesized_FLASH25_in_MNI_v2_500um.nii"
STUDENT_STRUCTURES_FILE_NAME = "G_VT23_practical_dis_MRI_.csv"
BACKUP_PATH = ""
MARKUP_PATH = ""

BIG_BRAIN = "Big_Brain"
IN_VIVO = "in_vivo"
EX_VIVO = "ex_vivo"
TRACTS_3D = "Tracts_3D"

BIG_BRAIN_VOLUME_NAME = "vtkMRMLScalarVolumeNode3"
IN_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode1"
EX_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode2"

NUMBER_OF_QUESTIONS = 10

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

# Byter dataset till big brain och fokuserar på koordinaterna [0, 0, 0]
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
    if dataset.lower() == current_dataset.lower():
        return
    if dataset.lower()  == BIG_BRAIN.lower():
        displaySelectVolume(BIG_BRAIN_VOLUME_NAME)
        current_dataset = BIG_BRAIN
    elif dataset.lower() == IN_VIVO.lower():
        displaySelectVolume(IN_VIVO_VOLUME_NAME)
        current_dataset = IN_VIVO
    elif dataset.lower() == EX_VIVO.lower():
        displaySelectVolume(EX_VIVO_VOLUME_NAME)
        current_dataset = EX_VIVO
    elif dataset.lower() == TRACTS_3D.lower():
        print(f"\n{TRACTS_3D} ses i övre högra fönstret\n")
        pass
    else:
        print(f"\nDataset: {dataset} existerar ej\n")

# Lägger till en nod med namnet exam_nr och lägger till tillhörande control points
# för varje struktur i structures. Namnet på varje control point blir strukturens
# namn och beskrivningen blir vilket nummer strukturen är.
def addNodeAndControlPoints(exam_nr, structures):
    node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', str(exam_nr))
    node.SetLocked(1)
    node.AddNControlPoints(10, "", [0, 0, 0])
    for _index, structure in enumerate(structures):
        # kanske byta ut index mot structure["question"]?
        try:
            index = int(structure["question"]) - 1
        except:
            index = _index
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
    # Återgå sedan till normalt läge när klar
    interactionNode.SetPlaceModePersistence(0)
    #interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    #interactionNode.SwitchToViewTransformMode()

    # also turn off place mode persistence if required
    #interactionNode.SetPlaceModePersistence(0)

def checkIfControlPointExists(question_number):
    return answered_questions[question_number]

# Centrerar vyerna på control point
# Hantera på ett bättre sätt i framtiden
def centreOnControlPoint(node, val, dataset):
    # Vill ej centrera på control point om är i Tracts_3D
    if dataset == TRACTS_3D:
        return
    controlPointCoordinates = node.GetNthControlPointPosition(val) # eller GetNthControlPointPositionWorld
    slicer.modules.markups.logic().JumpSlicesToLocation(controlPointCoordinates[0], controlPointCoordinates[1], controlPointCoordinates[2], True)

def resetAnsweredQuestions():
    global answered_questions
    answered_questions = [False] * NUMBER_OF_QUESTIONS

def updateAnsweredQuestions(node):
    global answered_questions
    resetAnsweredQuestions()
    for i in range(node.GetNumberOfControlPoints()):
        controlPointCoordinates = node.GetNthControlPointPosition(i)
        # Kan också kolla om den är set eller unset
        if controlPointCoordinates[0] != 0.0 or controlPointCoordinates[1] != 0.0 or controlPointCoordinates[2] != 0.0:
            # Om koordinater för control point ej är [0.0, 0.0, 0.0] är frågan besvarad
            answered_questions[i] = True

# Accepterar input med meddelandet prompt i range low (inklusive) till high (inklusive)
def inputNumberInRange(prompt, low, high, exceptions=list()):
    while True:
        try:
            value = int(input(prompt))
        except:
            # Kunde ej parse:a input
            print(f"Skriv in en siffra {low}-{high}")
            continue
        if (value >= low and value <= high) or value in exceptions:
            return value
        else:
            print(f"Skriv in en siffra {low}-{high}")
            continue

# Sparar en nod med control points till en fil
def saveNodeToFile(node, path):
    slicer.util.saveNode(node, path) # eller mkp.json

# Laddar in en fil med markups
def loadNodeFromFile(path):
    return slicer.util.loadMarkups(path)

def main():
    #loadDatasets()

    while True:
        # Återställer fönstrena och byter till big brain vid ny användare
        resetWindow()
        resetAnsweredQuestions()
        # definera filename här
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

        # readExamNr()
        while True:
            # kanske studentLoop
            try:
                exam_nr = int(input("Ange exam nr: "))
            except:
                print("Ogiltig input. Försök igen")
                continue
            if exam_nr == 123456:
                return
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
        if os.path.isfile(BACKUP_PATH + f"{exam_nr}.mrk.json"):
            print(f"En fil med markups existerar redan för exam nr {exam_nr}")
            read_file_option = inputNumberInRange("Vill du läsa in den?\n1 - Ja\n2 - Nej\n", 1, 2)
            if read_file_option == 1:
                node = loadNodeFromFile(MARKUP_PATH + f"{exam_nr}.mrk.json")
            elif read_file_option == 2:
                node = addNodeAndControlPoints(exam_nr, structures)
                pass
        else:
            node = addNodeAndControlPoints(exam_nr, structures)

        while True:
            updateAnsweredQuestions(node)
            printStructures(structures)
            question_option = inputNumberInRange("\nVilken fråga vill du besvara?\n", 1, NUMBER_OF_QUESTIONS, [123456]) - 1 # anpassa för listindex
            # ha detta i en funktion?
            if question_option == 123456 - 1:
                amount_answered_questions = answered_questions.count(True)
                print(f"Du har besvarat {amount_answered_questions}/{NUMBER_OF_QUESTIONS} strukturer")
                try:
                    quit_input = input("Är du säker att du vill avsluta? Skriv in 123456 igen för att avsluta\n")
                    if quit_input == "123456":
                        # TODO: gör något annat
                        # Sessionen för student ... har avslutats.
                        break
                    else:
                        continue
                except:
                    continue

            printStructure(structures[question_option])
            changeDataset(structures[question_option]["Dataset"])
            node.GetDisplayNode().SetActiveControlPoint(question_option)

            action_option = inputNumberInRange("Vad vill du göra?\n1 - sätta ny punkt\n2 - kolla på punkten\n3 - svara på en annan struktur\n", 1, 3) # fokusera på? centrera på?
            if action_option == 1:
                # Ändra koordinater för control point
                replace_option = 1 # Om det inte finns en placerad control point behöver man ej ha input
                if checkIfControlPointExists(question_option):
                    # Om det finns en tidigare placerad control point
                    replace_option = inputNumberInRange("Det här kommer ta bort din gamla markering. Är du säker på att du vill fortsätta?\n1 - Ja\n2 - Nej\n", 1, 2) # fortsätt/avbryt
                if replace_option == 1:
                    # Placera en ny control point
                    setNewControlPoint(node, question_option)
                    try:
                        input("Placera punkten. Tryck Enter för att fortsätta.")
                        # Gör en backup på node
                        saveNodeToFile(node, BACKUP_PATH + f"{exam_nr}.mrk.json")
                    except:
                        # Hamnar här ibland
                        pass
                elif replace_option == 2:
                    pass
            elif action_option == 2:
                if checkIfControlPointExists(question_option):
                    # Centrera på koordinaterna för control point om den existerar
                    centreOnControlPoint(node, question_option, structures[question_option]["Dataset"])
            elif action_option == 3:
                # Svara på en annan fråga
                continue

        # Spara control points till en json-fil
        saveNodeToFile(node, MARKUP_PATH + f"{exam_nr}.mrk.json")
        print(f"Filen {exam_nr}.mrk.json med markups har sparats.")
        print("Vänligen dubbelkolla att filen existerar.")

if __name__ == "__main__":
    main()
