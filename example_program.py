"""example_program.py: Program skapat för träning inför stationsexamination
i 3D Slicer i kursen Basvetenskap 4 på Karolinska Institutet."""

__author__ = "Christian Andersson"
__version__ = "1.0"
__email__ = "christian.andersson.2@stud.ki.se"

DATASETS_FILE_NAME = "open_me.mrb"

BIG_BRAIN = "Big_Brain"
IN_VIVO = "in_vivo"
EX_VIVO = "ex_vivo"
TRACTS_3D = "Tracts_3D"

BIG_BRAIN_VOLUME_NAME = "vtkMRMLScalarVolumeNode3"
IN_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode1"
EX_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode2"

NUMBER_OF_QUESTIONS = 10
QUIT_CODE = 99

class SlicerApplication:
    def __init__(self):
        self.current_dataset = ""
        self.answered_questions = [False] * NUMBER_OF_QUESTIONS

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

    # Läser in alla rader tillhörande exam_nr
    def retrieveStructures(self, exam_nr) -> list:
        structures = {
            241: [{'Structure': 'nucleus caudatus',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'Mesencephalon',
                'Dataset': 'Big_Brain',
                'question': '2'},
               {'Structure': 'foramen interventriculare',
                'Dataset': 'in_vivo',
                'question': '3'},
               {'Structure': 'lobus cerebelli posterior',
                'Dataset': 'in_vivo',
                'question': '4'},
               {'Structure': 'Sulcus marginalis',
                'Dataset': 'in_vivo',
                'question': '5'},
               {'Structure': 'Nodulus',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'Cortex piriformis',
                'Dataset': 'ex_vivo',
                'question': '7'},
               {'Structure': 'Thalamus',
                'Dataset': 'ex_vivo',
                'question': '8'},
               {'Structure': 'Tonsilla',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'Fasciculus longitidinalis inferior',
                'Dataset': 'Tracts_3D',
                'question': '10'}],
         242: [{'Structure': 'sulcus collateralis',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'Lamina terminalis',
                'Dataset': 'Big_Brain',
                'question': '2'},
               {'Structure': 'a. cerebri posterior (P4)',
                'Dataset': 'in_vivo',
                'question': '3'},
               {'Structure': 'capsula interna',
                'Dataset': 'in_vivo',
                'question': '4'},
               {'Structure': 'Colliculus superior',
                'Dataset': 'in_vivo',
                'question': '5'},
               {'Structure': 'lobus cerebelli anterior',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'Putamen',
                'Dataset': 'in_vivo',
                'question': '7'},
               {'Structure': 'sinus sigmoideus',
                'Dataset': 'in_vivo',
                'question': '8'},
               {'Structure': 'Thalamus',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'Ventriculus lateralis',
                'Dataset': 'ex_vivo',
                'question': '10'}],
         243: [{'Structure': 'Nucleus accumbens',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'Area postrema',
                'Dataset': 'Big_Brain',
                'question': '2'},
               {'Structure': 'Operculum parietale',
                'Dataset': 'Big_Brain',
                'question': '3'},
               {'Structure': 'a. cerebri anterior',
                'Dataset': 'in_vivo',
                'question': '4'},
               {'Structure': 'aqueductus cerebri/mesencephali',
                'Dataset': 'in_vivo',
                'question': '5'},
               {'Structure': 'falx cerebri',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'Sinus rectus',
                'Dataset': 'in_vivo',
                'question': '7'},
               {'Structure': 'Flocculus',
                'Dataset': 'ex_vivo',
                'question': '8'},
               {'Structure': 'hemispherium cerebelli',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'Medulla oblongata',
                'Dataset': 'ex_vivo',
                'question': '10'}],
         244: [{'Structure': 'basis pontis',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'a. lenticulostriatae laterales',
                'Dataset': 'in_vivo',
                'question': '2'},
               {'Structure': 'capsula externa',
                'Dataset': 'in_vivo',
                'question': '3'},
               {'Structure': 'Corpus callosum rostrum',
                'Dataset': 'in_vivo',
                'question': '4'},
               {'Structure': 'pedunculus cerebellaris inferior',
                'Dataset': 'in_vivo',
                'question': '5'},
               {'Structure': 'Ventriculus lateralis',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'capsula extrema',
                'Dataset': 'ex_vivo',
                'question': '7'},
               {'Structure': 'Hippocampus',
                'Dataset': 'ex_vivo',
                'question': '8'},
               {'Structure': 'plexus choroideus',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'sulcus hypothalamicus',
                'Dataset': 'ex_vivo',
                'question': '10'}],
         245: [{'Structure': 'pyramis medullae oblongatae',
                'Dataset': 'Big_Brain',
                'question': '1'},
               {'Structure': 'Ventriculus lateralis',
                'Dataset': 'Big_Brain',
                'question': '2'},
               {'Structure': 'Mesencephalon',
                'Dataset': 'Big_Brain',
                'question': '3'},
               {'Structure': 'Cuneus',
                'Dataset': 'Big_Brain',
                'question': '4'},
               {'Structure': 'Operculum parietale',
                'Dataset': 'Big_Brain',
                'question': '5'},
               {'Structure': 'a. carotis interna',
                'Dataset': 'in_vivo',
                'question': '6'},
               {'Structure': 'Globus pallidus externa',
                'Dataset': 'in_vivo',
                'question': '7'},
               {'Structure': 'sinus cavernosus',
                'Dataset': 'in_vivo',
                'question': '8'},
               {'Structure': 'ventriculus quartus',
                'Dataset': 'ex_vivo',
                'question': '9'},
               {'Structure': 'Area tegmentalis ventralis (VTA',
                'Dataset': 'ex_vivo',
                'question': '10'}]}
        if exam_nr >= 241 and exam_nr <= 245:
            return structures[exam_nr]
        else:
            return []

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
        node.AddNControlPoints(10, "", [0, 0, 0])
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

    def checkIfControlPointExists(self, question_number):
        return self.answered_questions[question_number]

    # Centrerar vyerna på control point
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

    # Huvudsakliga logiken för användning av programmet. Bör implementeras av alla klasser som ärver av denna klass
    def run(self):
        return

class ExampleApplication(SlicerApplication):
    def run(self):
        while True:
            # Återställer fönstrena och byter till big brain vid ny användare
            self.resetWindow()
            self.resetAnsweredQuestions()
            print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

            while True:
                exam_nr = self.readExamNr()
                if exam_nr == QUIT_CODE:
                    return
                structures = self.retrieveStructures(exam_nr)
                # Kontrollera att rätt antal strukturer har lästs in
                if len(structures) == 0:
                    print("ERROR: Inga strukturer hittades. Testa igen")
                    continue
                self.printStructures(structures)
                print("\nOBS: Kontrollera att de inlästa strukturerna överensstämmer med dina tilldelade strukturer\n")
                is_correct_exam_nr = self.inputNumberInRange("Har du angett rätt exam nr?\n1 - Ja\n2 - Nej\n", 1, 2)
                if is_correct_exam_nr == 1:
                    break
                if is_correct_exam_nr == 2:
                    continue
            node = self.addNodeAndControlPoints(exam_nr, structures)

            while True:
                self.updateAnsweredQuestions(node)
                self.printStructures(structures)
                question_option = self.inputNumberInRange(f"\nVilken fråga vill du besvara/kolla på?\n", 1, NUMBER_OF_QUESTIONS, [QUIT_CODE]) - 1 # anpassa för listindex
                if question_option == QUIT_CODE - 1:
                    amount_answered_questions = self.answered_questions.count(True)
                    print(f"Du har besvarat {amount_answered_questions}/{NUMBER_OF_QUESTIONS} strukturer")
                    try:
                        quit_input = input(f"Är du säker att du vill avsluta? Skriv in {QUIT_CODE} igen för att avsluta\n")
                        if quit_input == str(QUIT_CODE):
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
                    replace_option = self.inputNumberInRange("\nVisar din markering. Vill du ersätta den med en ny markering?\n1 - Ja\n2 - Nej\n", 1, 2)
                if replace_option == 1:
                    # Placera en ny control point
                    try:
                        input("\nLeta upp strukturen. Tryck sedan Enter för att placera punkten.")
                    except:
                        # Hamnar här ibland
                        pass
                    self.setNewControlPoint(node, question_option)
                    try:
                        input("\nKlicka här och tryck sedan Enter när du har placerat ut punkten.")
                    except:
                        # Hamnar här ibland
                        pass
                elif replace_option == 2:
                    continue

if __name__ == "__main__":
    application = ExampleApplication()
    application.run()
