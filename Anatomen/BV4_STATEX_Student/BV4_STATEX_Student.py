import logging
import os
from typing import Annotated, Optional

import vtk

import slicer, qt
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode

import functools

import os
import csv
import re

EXAM_FOLDER_PATH = r"C:\Exam program"
MEGA_FOLDER_PATH = r"C:\Users\Christian\Documents\Tutor"
DATASET_PATH = os.path.join(EXAM_FOLDER_PATH, "Dataset")
STUDENT_STRUCTURES_PATH = os.path.join(MEGA_FOLDER_PATH, "Exams")
DATASETS_FILE_NAME = "2024-05-06-Scene.mrml" #"open_me.mrb"
BIG_BRAIN_FILE_NAME = "Big_brain.nii.gz"
IN_VIVO_FILE_NAME = "In_vivo.nii"
EX_VIVO_FILE_NAME = "Ex_vivo.nii.gz"
WHITE_TRACTS_FILE_NAME = "White_matter_tracts_1.nrrd"
STUDENT_STRUCTURES_FILE_NAME = "G_VT23_practical_dis_MRI_.csv"
LOCAL_BACKUP_PATH = os.path.join(EXAM_FOLDER_PATH, "Backups")
LOCAL_MARKUP_PATH = os.path.join(EXAM_FOLDER_PATH, "markups")
G_DRIVE_MARKUP_PATH = r"G:\Min enhet\Neuro\BV4\EXAM 05-16\MARKUPS"
MEGA_MARKUP_PATH = os.path.join(MEGA_FOLDER_PATH, "Markups")

LOAD_DATASETS = False

BIG_BRAIN = "Big_Brain"
IN_VIVO = "in_vivo"
EX_VIVO = "ex_vivo"
TRACTS_3D = "Tracts_3D"

BIG_BRAIN_VOLUME_NAME = "vtkMRMLScalarVolumeNode3"
IN_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode1"
EX_VIVO_VOLUME_NAME = "vtkMRMLScalarVolumeNode2"

NUMBER_OF_QUESTIONS = 10
QUIT_CODE = 1234

#
# BV4_STATEX_Student
#


class BV4_STATEX_Student(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("BV4_STATEX_Student")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Anatomen")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#BV4_STATEX_Student">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""")

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#


def registerSampleData():
    """Add data sets to Sample Data module."""
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData

    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # BV4_STATEX_Student1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="BV4_STATEX_Student",
        sampleName="BV4_STATEX_Student1",
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, "BV4_STATEX_Student1.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames="BV4_STATEX_Student1.nrrd",
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums="SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        # This node name will be used when the data set is loaded
        nodeNames="BV4_STATEX_Student1",
    )

    # BV4_STATEX_Student2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="BV4_STATEX_Student",
        sampleName="BV4_STATEX_Student2",
        thumbnailFileName=os.path.join(iconsPath, "BV4_STATEX_Student2.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames="BV4_STATEX_Student2.nrrd",
        checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="BV4_STATEX_Student2",
    )


#
# BV4_STATEX_StudentParameterNode
#


@parameterNodeWrapper
class BV4_STATEX_StudentParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """

    inputVolume: vtkMRMLScalarVolumeNode
    imageThreshold: Annotated[float, WithinRange(-100, 500)] = 100
    invertThreshold: bool = False
    thresholdedVolume: vtkMRMLScalarVolumeNode
    invertedVolume: vtkMRMLScalarVolumeNode


#
# BV4_STATEX_StudentWidget
#


class BV4_STATEX_StudentWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath("UI/BV4_STATEX_Student.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = BV4_STATEX_StudentLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        #self.partialFunction = functools.partial(self.onStructureButton, number=1)
        self.ui.pushButton_Structure_1.connect("clicked(bool)", self.onStructureButton1) ## SANNOLIKT PROBLEM
        self.ui.pushButton_Structure_5.connect("clicked(bool)", self.onStructureButton5)
        self.ui.pushButton_Load_Structures.connect("clicked(bool)", self.onLoadStructuresButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """Ensure parameter node exists and observed."""
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputVolume:
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(self, inputParameterNode: Optional[BV4_STATEX_StudentParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputVolume and self._parameterNode.thresholdedVolume:
            self.ui.applyButton.toolTip = _("Compute output volume")
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = _("Select input and output volume nodes")
            self.ui.applyButton.enabled = False

    def onStructureButton1(self) -> None:
        """Run processing when user clicks "Apply" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            self.logic.onStructureButtonPressed(1)
            str_Result = self.ui.inputBox_Exam_Number.text
            qt.QMessageBox.information(slicer.util.mainWindow(), 'SL Tutorial: GUI HelloWorld', str_Result)

    def onStructureButton5(self) -> None:
        """Run processing when user clicks "Apply" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            self.logic.onStructureButtonPressed(5)
            str_Result = self.ui.inputBox_Exam_Number.text
            qt.QMessageBox.information(slicer.util.mainWindow(), 'SL Tutorial: GUI HelloWorld', str_Result)

    def onLoadStructuresButton(self) -> None:
        """Run processing when user clicks "Ladda in strukturer" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            print("HELLO")
            student_name = self.ui.inputBox_Student_Name.text
            exam_number = self.ui.inputBox_Exam_Number.text
            self.logic.onLoadStructuresButtonPressed(student_name, exam_number)
            self.ui.pushButton_Structure_1.setText(f"Struktur 1: {self.logic.structures[0]['Structure']}")
            self.ui.pushButton_Structure_2.setText(f"Struktur 2: {self.logic.structures[1]['Structure']}")
            self.ui.pushButton_Structure_3.setText(f"Struktur 3: {self.logic.structures[2]['Structure']}")
            self.ui.pushButton_Structure_4.setText(f"Struktur 4: {self.logic.structures[3]['Structure']}")
            self.ui.pushButton_Structure_5.setText(f"Struktur 5: {self.logic.structures[4]['Structure']}")
            self.ui.pushButton_Structure_6.setText(f"Struktur 6: {self.logic.structures[5]['Structure']}")
            self.ui.pushButton_Structure_7.setText(f"Struktur 7: {self.logic.structures[6]['Structure']}")
            self.ui.pushButton_Structure_8.setText(f"Struktur 8: {self.logic.structures[7]['Structure']}")
            self.ui.pushButton_Structure_9.setText(f"Struktur 9: {self.logic.structures[8]['Structure']}")
            self.ui.pushButton_Structure_10.setText(f"Struktur 10: {self.logic.structures[9]['Structure']}")

#
# BV4_STATEX_StudentLogic
#


class BV4_STATEX_StudentLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)
        self.structures = []
        self.current_dataset = ""
        self.answered_questions = [False] * NUMBER_OF_QUESTIONS
        self.node = None

    def getParameterNode(self):
        return BV4_STATEX_StudentParameterNode(super().getParameterNode())

    def process(self,
                inputVolume: vtkMRMLScalarVolumeNode,
                outputVolume: vtkMRMLScalarVolumeNode,
                imageThreshold: float,
                invert: bool = False,
                showResult: bool = True) -> None:
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time

        startTime = time.time()
        logging.info("Processing started")

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            "InputVolume": inputVolume.GetID(),
            "OutputVolume": outputVolume.GetID(),
            "ThresholdValue": imageThreshold,
            "ThresholdType": "Above" if invert else "Below",
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f"Processing completed in {stopTime-startTime:.2f} seconds")

    def onLoadStructuresButtonPressed(self, student_name, exam_nr):
        self.retrieveStructures(exam_nr)
        self.addNodeAndControlPoints(exam_nr, student_name, self.structures)

    def onStructureButtonPressed(self, number):
        self.changeDataset(self.structures[number - 1]["Dataset"])
        #self.centreOnControlPoint(self.node, number, self.structures[number]["Dataset"])
        self.setNewControlPoint(self.node, number - 1)

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

    # Öppnar csv-filen med strukturer och läser in alla rader tillhörande exam_nr
    def retrieveStructures(self, exam_nr) -> list:
        structures = []
        with open(os.path.join(STUDENT_STRUCTURES_PATH, STUDENT_STRUCTURES_FILE_NAME), encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                if row["exam_nr"] == exam_nr:
                    structures.append(row)
        self.structures = structures
        # Kan kanske ta bort return
        return structures

    # Ändrar nuvarande dataset till specificerat dataset
    def changeDataset(self, dataset):
        #if dataset.lower() == self.current_dataset.lower():
        #    return
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
    def addNodeAndControlPoints(self, exam_nr, student_name, structures):
        node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode', f"{exam_nr}_{student_name}")
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
        self.node = node
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

    # Sparar en nod med control points till en fil
    def saveNodeToFile(self, node, path):
        slicer.util.saveNode(node, path) # eller mkp.json

    # Laddar in en fil med markups
    def loadNodeFromFile(self, path):
        return slicer.util.loadMarkups(path)

#
# BV4_STATEX_StudentTest
#


class BV4_STATEX_StudentTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_BV4_STATEX_Student1()

    def test_BV4_STATEX_Student1(self):
        """Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData

        registerSampleData()
        inputVolume = SampleData.downloadSample("BV4_STATEX_Student1")
        self.delayDisplay("Loaded test data set")

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = BV4_STATEX_StudentLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay("Test passed")
