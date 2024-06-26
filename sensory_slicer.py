"""sensory_slicer.py: Program skapat för övning i 3D Slicer på sensorisk
neuroanatomi i kursen Basvetenskap 4 på Karolinska Institutet."""

__author__ = "Christian Andersson"
#__version__ = "1.0"
__email__ = "christian.andersson.2@stud.ki.se"

import os
import csv

DATASET_PATH = r"G:\My Drive\Neuro\BV4\Slicer intro"
SENSORY_STRUCTURES_PATH = r"G:\My Drive\Neuro\BV4\Slicer intro"
DATASETS_FILE_NAME = "Start_slicerintro.mrml"
SENSORY_STRUCTURES_FILE_NAME = "Slicer_intro.csv"

LOAD_DATASETS = False

BIG_BRAIN = "Big_Brain"
IN_VIVO = "in_vivo"
EX_VIVO = "ex_vivo"
TRACTS_3D = "3d"

BIG_BRAIN_VOLUME_NAME = "vtkMRMLScalarVolumeNode1"
IN_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode3"
EX_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode2"

NUMBER_OF_QUESTIONS = 30
QUIT_CODE = 99

class SlicerApplication:
    def __init__(self):
        self.current_dataset = ""
        self.answered_questions = [False] * NUMBER_OF_QUESTIONS

    # Läser in dataseten big_brain, in_vivo, ex_vivo och tracts_3d
    def loadDatasets(big_brain=True, in_vivo=True, ex_vivo=True, tracts_3d=True):
        slicer.util.loadScene(os.path.join(DATASET_PATH, DATASETS_FILE_NAME))

    def displaySelectVolume(self, a):
        layoutManager = slicer.app.layoutManager()
        for sliceViewName in layoutManager.sliceViewNames():
            view = layoutManager.sliceWidget(sliceViewName).sliceView()
            sliceNode = view.mrmlSliceNode()
            sliceLogic = slicer.app.applicationLogic().GetSliceLogic(sliceNode)
            compositeNode = sliceLogic.GetSliceCompositeNode()
            compositeNode.SetBackgroundVolumeID(str(a))

    # Byter dataset till big brain och fokuserar på koordinaterna [0, 0, 0]
    def resetWindow(self):
        self.changeDataset(BIG_BRAIN)
        slicer.modules.markups.logic().JumpSlicesToLocation(0, 0, 0, True)

    def readExamNr(self):
        while True:
            try:
                exam_nr = int(input("Ange exam nr: "))
                break
            except:
                print("Ogiltig input. Försök igen")
                continue
        return exam_nr

    # Öppnar csv-filen med strukturer och läser in alla rader tillhörande exam_nr
    def retrieveStructures(self, exam_nr) -> list:
        structures = []
        with open(os.path.join(SENSORY_STRUCTURES_PATH, SENSORY_STRUCTURES_FILE_NAME), encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                if int(row["exam_nr"]) == exam_nr:
                    structures.append(row)
        return structures

    # Printar structure i formatet: Struktur [fråga] (✓/X): [struktur] i [dataset]
    def printStructure(self, structure):
        print(str("Struktur " + structure["question"] + " "), end = "")
        if self.checkIfControlPointExists(int(structure["question"]) - 1):
            print("(✓)", end = "")
        else:
            print("(X)", end = "")
        print(": " + structure["Structure"] + " i " + structure["Dataset"])

    # Använder printStructure för att printa alla strukturer i structures
    def printStructures(self, structures):
        for structure in structures:
            self.printStructure(structure)
        print("(✓) = Besvarad, (X) = Ej besvarad")

    # Ändrar nuvarande dataset till specificerat dataset
    def changeDataset(self, dataset):
        if dataset.lower() == self.current_dataset.lower():
            return
        if dataset.lower()  == BIG_BRAIN.lower():
            self.displaySelectVolume(BIG_BRAIN_VOLUME_NAME)
            self.current_dataset = BIG_BRAIN
        elif dataset.lower() == IN_VIVO.lower():
            self.displaySelectVolume(IN_VIVO_VOLUME_NAME)
            self.current_dataset = IN_VIVO
        elif dataset.lower() == EX_VIVO.lower():
            self.displaySelectVolume(EX_VIVO_VOLUME_NAME)
            self.current_dataset = EX_VIVO
        elif dataset.lower() == TRACTS_3D.lower():
            print(f"\n{TRACTS_3D} ses i övre högra fönstret\n")
            pass
        else:
            print(f"\nDataset: {dataset} existerar ej\n")

    # Lägger till en nod med namnet exam_nr och lägger till tillhörande control points
    # för varje struktur i structures. Namnet på varje control point blir strukturens
    # namn och beskrivningen blir vilket nummer strukturen är.
    def addNodeAndControlPoints(self, exam_nr, structures):
        node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', str(exam_nr))
        node.SetLocked(1)
        node.AddNControlPoints(NUMBER_OF_QUESTIONS, "", [0, 0, 0])
        for _index, structure in enumerate(structures):
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
    def setNewControlPoint(self, node, index):
        # Återställ control point
        node.SetNthControlPointPosition(index, 0.0, 0.0, 0.0)
        node.UnsetNthControlPointPosition(index)
        # Placera ut ny control point
        node.SetControlPointPlacementStartIndex(index)
        slicer.modules.markups.logic().StartPlaceMode(1)
        interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        # Återgå sedan till normalt läge när klar
        interactionNode.SetPlaceModePersistence(0)
        #interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
        #interactionNode.SwitchToViewTransformMode()

        # also turn off place mode persistence if required
        #interactionNode.SetPlaceModePersistence(0)

    def checkIfControlPointExists(self, question_number):
        return self.answered_questions[question_number]

    # Centrerar vyerna på control point
    # Hantera på ett bättre sätt i framtiden
    def centreOnControlPoint(self, node, index, dataset):
        # Vill ej centrera på control point om är i Tracts_3D
        if dataset == TRACTS_3D:
            return
        controlPointCoordinates = node.GetNthControlPointPosition(index) # eller GetNthControlPointPositionWorld
        slicer.modules.markups.logic().JumpSlicesToLocation(controlPointCoordinates[0], controlPointCoordinates[1], controlPointCoordinates[2], True)

    def resetAnsweredQuestions(self):
        self.answered_questions = [False] * NUMBER_OF_QUESTIONS

    def updateAnsweredQuestions(self, node):
        self.resetAnsweredQuestions()
        for i in range(node.GetNumberOfControlPoints()):
            controlPointCoordinates = node.GetNthControlPointPosition(i)
            # Kan också kolla om den är set eller unset
            if controlPointCoordinates[0] != 0.0 or controlPointCoordinates[1] != 0.0 or controlPointCoordinates[2] != 0.0:
                # Om koordinater för control point ej är [0.0, 0.0, 0.0] är frågan besvarad
                self.answered_questions[i] = True

    # Accepterar input med meddelandet prompt i range low (inklusive) till high (inklusive)
    def inputNumberInRange(self, prompt, low, high, exceptions=list()):
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

    # Sparar en nod med control points till en fil
    def saveNodeToFile(self, node, path):
        slicer.util.saveNode(node, path) # eller mkp.json

    # Laddar in en fil med markups
    def loadNodeFromFile(self, path):
        return slicer.util.loadMarkups(path)

    # Huvudsakliga logiken för användning av programmet. Bör implementeras av alla klasser som ärver av denna klass
    def run(self):
        if LOAD_DATASETS:
            self.loadDatasets()

class SensoryApplication(SlicerApplication):
    def run(self):
        super().run()

        while True:
            # Återställer fönstrena och byter till big brain vid ny användare
            self.resetWindow()
            self.resetAnsweredQuestions()
            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

            while True:
                # kanske studentLoop
                exam_nr = self.readExamNr()
                if exam_nr == QUIT_CODE:
                    return
                structures = self.retrieveStructures(exam_nr)
                if len(structures) > 0:
                    break

            node = self.addNodeAndControlPoints("Sensorisk neuroanatomi", structures)

            while True:
                self.updateAnsweredQuestions(node)
                self.printStructures(structures)
                question_option = self.inputNumberInRange(f"\nVilken fråga vill du besvara/kolla på?\n", 1, NUMBER_OF_QUESTIONS, [QUIT_CODE]) - 1 # anpassa för listindex
                # ha detta i en funktion?
                if question_option == QUIT_CODE - 1:
                    amount_answered_questions = self.answered_questions.count(True)
                    print(f"Du har besvarat {amount_answered_questions}/{NUMBER_OF_QUESTIONS} strukturer")
                    try:
                        quit_input = input(f"Är du säker att du vill avsluta? Skriv in {QUIT_CODE} igen för att avsluta\n")
                        if quit_input == str(QUIT_CODE):
                            # TODO: gör något annat
                            print(f"Sessionen för student med exam nr: {exam_nr} har avslutats")
                            break
                        else:
                            continue
                    except:
                        continue
                self.printStructure(structures[question_option])
                self.changeDataset(structures[question_option]["Dataset"])
                node.GetDisplayNode().SetActiveControlPoint(question_option)
                replace_option = 1 # Om det inte finns en placerad control point behöver man ej ha input
                if self.checkIfControlPointExists(question_option):
                    # Om det finns en tidigare placerad control point
                    # Centrera på koordinaterna för control point om den existerar
                    self.centreOnControlPoint(node, question_option, structures[question_option]["Dataset"])
                    replace_option = self.inputNumberInRange("\nVisar din markering. Vill du ersätta den med en ny markering?\n1 - Ja\n2 - Nej\n", 1, 2) # fortsätt/avbryt
                if replace_option == 1:
                    # Placera en ny control point
                    try:
                        input("\nLeta upp strukturen. Tryck sedan Enter för att placera punkten.")
                    except:
                        # Hamnar här ibland
                        pass
                    self.setNewControlPoint(node, question_option)
                    try:
                        input("\nTryck Enter när du placerat ut punkten.")
                    except:
                        # Hamnar här ibland
                        pass
                elif replace_option == 2:
                    continue

if __name__ == "__main__":
    application = SensoryApplication()
    application.run()
