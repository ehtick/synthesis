from logging import PlaceHolder
from os import dup, fdopen, remove
from proto.proto_out.joint_pb2 import Joint
from ..general_imports import *
from ..configure import NOTIFIED, write_configuration
from ..Analytics.alert import showAnalyticsAlert
from . import Helper, FileDialogConfig, OsHelper

from ..Parser.ParseOptions import ParseOptions, _Joint, _Wheel, WheelType, JointParentType
from .Configuration.SerialCommand import (
    Struct,
    SerialCommand,
    General,
    Advanced,
    BooleanInput,
    ExportMode,
)

import adsk.core, adsk.fusion, traceback
from types import SimpleNamespace

"""
File to generate and link the Configuration Command seen when pressing the button from the Addins Panel
"""
previous = None

# group globals
wheelConfig = adsk.core.GroupCommandInput.cast(None)
jointConfig = adsk.core.GroupCommandInput.cast(None)
gamepieceConfig = adsk.core.GroupCommandInput.cast(None)

# joint & wheel table globals
wheelTableInput = adsk.core.TableCommandInput.cast(None)
jointTableInput = adsk.core.TableCommandInput.cast(None)
gamepieceTableInput = adsk.core.TableCommandInput.cast(None)

# add and remove buttons globals
addWheelInput = adsk.core.BoolValueCommandInput.cast(None)
removeWheelInput = adsk.core.BoolValueCommandInput.cast(None)
addJointInput = adsk.core.BoolValueCommandInput.cast(None)
removeJointIpnut = adsk.core.BoolValueCommandInput.cast(None)
addFieldInput = adsk.core.BoolValueCommandInput.cast(None)
removeFieldInput = adsk.core.BoolValueCommandInput.cast(None)

duplicateSelection = adsk.core.BoolValueCommandInput.cast(None)
exportMode = True

# selected wheels & joints
_wheels = []
_joints = []
_gamepieces = []

# easy-access image paths for icons
iconPaths = {
    "omni": "src/Resources/omni-wheel-preview16x16.png",
    "standard": "src/Resources/standard-wheel-preview16x16.png",
    "rigid": "src/Resources/rigid-preview16x16.png",
    "revolute": "src/Resources/revolute-preview16x16.png",
    "slider": "src/Resources/slider-preview16x16.png"
}


class ConfigureCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Start the Command Input Object and define all of the input groups to create our ParserOptions object.

    Notes:
        - linked and called from (@ref HButton) and linked
        - will be called from (@ref Events.py)
    """

    def __init__(self, configure):
        super().__init__()
        self.log = logging.getLogger(f"{INTERNAL_ID}.UI.{self.__class__.__name__}")

    def notify(self, args):
        try:
            if not Helper.check_solid_open():
                return
            # remove globals
            global NOTIFIED, wheelTableInput, jointTableInput, addWheelInput, addJointInput, removeWheelInput, removeJointInput, addFieldInput, removeFieldInput
            
            if not NOTIFIED:
                showAnalyticsAlert()
                NOTIFIED = True
                write_configuration("analytics", "notified", "yes")

            global previous

            saved = Helper.previouslyConfigured()
            if type(saved) == str:
                try:
                    # probably need some way to validate for each usage below
                    previous = json.loads(
                        saved, object_hook=lambda d: SimpleNamespace(**d)
                    )
                    # self.log(f"Found previous {previous}")
                except:
                    self.log.error("Failed:\n{}".format(traceback.format_exc()))
                    gm.ui.messageBox(
                        "Failed to read previous Unity Configuration\n  - Using default configuration"
                    )
                    previous = SerialCommand()
            else:
                # new file configuration
                previous = SerialCommand()

            if A_EP:
                A_EP.send_view("export_panel")

            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = eventArgs.command

            # Set to false so won't automatically export on switch context
            cmd.isAutoExecute = False
            cmd.isExecutedWhenPreEmpted = False
            cmd.okButtonText = "Export"

            # First check if the object has previosuly had saved information
            # self._parsePrevious()

            onInputChanged = ConfigureCommandInputChanged()
            cmd.inputChanged.add(onInputChanged)
            gm.handlers.append(onInputChanged)

            onSelect = MySelectHandler()
            cmd.select.add(onSelect)
            gm.handlers.append(onSelect) 
            
            onUnSelect = MyUnSelectHandler()
            cmd.unselect.add(onUnSelect)            
            gm.handlers.append(onUnSelect)

            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            gm.handlers.append(onDestroy)

            onExecute = ConfigureCommandExecuteHandler(
                json.dumps(
                    previous, default=lambda o: o.__dict__, sort_keys=True, indent=1
                ),
                previous.filePath,
            )
            cmd.execute.add(onExecute)
            gm.handlers.append(onExecute)

            inputs_root = cmd.commandInputs

            """
            ~ General Tab ~
            """
            inputs = inputs_root.addTabCommandInput("general_settings", "General").children

            # This actually has the ability to entirely create a input from just a protobuf message which is really neat
            ## NOTE: actually is super neat but I don't have time at the moment
            # self.parseMessage(inputs)

            """
            Help File
            - Just an idea for adding additional instructions for user.
            """
            cmd.helpFile = ""

            """
            Export Mode
            """
            # This could be a button group
            dropdownExportMode = inputs.addDropDownCommandInput(
                "mode",
                "Export Mode",
                dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
            )
            dropdownExportMode.listItems.add("Robot", True)
            dropdownExportMode.listItems.add("Field", False)

            dropdownExportMode.tooltip = (
                "This will be future formats and or generic / advanced objects."
            )

            """
            Weight Configuration
            """
            weightTableInput = self.createTableInput(
                "weight_table",
                "Weight Table",
                inputs,
                3,
                "5:3:2",
                1
            )
            weightTableInput.tablePresentationStyle = 2
            weightTableInput.columnSpacing = 0

            weight_name = inputs.addStringValueInput("weight_name", "Weight")
            weight_name.value = "Weight"
            weight_name.isReadOnly = True

            weight_input = inputs.addValueInput("weight_input", "Weight Input", "", adsk.core.ValueInput.createByString("0.0"))
            weight_input.tooltip = "Weight"

            weight_unit = inputs.addDropDownCommandInput("weight_unit", "Weight Unit", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            weight_unit.listItems.add("lbs", True)
            weight_unit.listItems.add("kg", False)
            weight_unit.tooltip = "Unit of mass"

            weightTableInput.addCommandInput(weight_name, 0, 0)
            weightTableInput.addCommandInput(weight_input, 0, 1)
            weightTableInput.addCommandInput(weight_unit, 0, 2)

            """
            Export Joints
            """
            self.createBooleanInput(
                "export_joints",
                "Export Joints",
                inputs,
                checked=False,
                tooltip="Export Fusion 360 joints into Unity.",
                tooltipadvanced="May be inconsistent dependening on the type of joint.",
                enabled=True,
            )

            # if previous is defined it will go through and assign the booleans in a hard coded way
            # self._generateGeneral(inputs)

            """
            Wheel Configuration
            """
            wheelConfig = inputs.addGroupCommandInput("wheel_config", "Wheel Configuration")
            wheelConfig.isExpanded = True
            wheelConfig.isEnabled = True
            wheelConfig.tooltip = "Select and define the drive-train wheels in your assembly."
            wheel_inputs = wheelConfig.children

            """
            Automatically Select Duplicates
            """
            global duplicateSelection
            duplicateSelection = self.createBooleanInput(
                "duplicate_selection",
                "Duplicate Selection",
                wheel_inputs,
                checked=True,
                tooltip="Automatically select duplicate wheel components.",
                enabled=True,
            )

            """
            Wheel Selection Table
            """
            wheelTableInput = self.createTableInput(
                "wheel_table",
                "Wheel Table",
                wheel_inputs,
                3,
                "1:3:2",
                10,
            )

            addWheelInput = wheel_inputs.addBoolValueInput(
                "wheel_add", "Add", False
            )

            removeWheelInput = wheel_inputs.addBoolValueInput(
                "wheel_delete", "Remove", False
            )

            addWheelInput.tooltip = "Add a wheel component"
            removeWheelInput.tooltip = "Remove a wheel component"

            wheelSelectInput = wheel_inputs.addSelectionInput("wheel_select", "Selection", "Select the wheels in your drive-train assembly.")
            wheelSelectInput.addSelectionFilter("Occurrences") # limit selection to only occurrences
            wheelSelectInput.setSelectionLimits(0)
            wheelSelectInput.isEnabled = False
            wheelSelectInput.isVisible = False

            wheelTableInput.addToolbarCommandInput(addWheelInput)
            wheelTableInput.addToolbarCommandInput(removeWheelInput)

            self.log.info("Created Configuration Input successfully")

            """
            Simple wheel export button
            """
            self.createBooleanInput(
                "simple_wheel_export",
                "Simple Wheel Export",
                wheel_inputs,
                checked=False,
                tooltip="Export center of mass vector for each body.",
                enabled=True,
            )

            """
            Joint Configuration
            """
            global jointConfig

            jointConfig = inputs.addGroupCommandInput("joint_config", "Joint Configuration")
            jointConfig.isExpanded = False # later, change back to false
            jointConfig.isEnabled = False
            jointConfig.tooltip = "Select and define joint occurrences in your assembly."
            joint_inputs = jointConfig.children

            """
            Joint Selection Table
            """
            jointTableInput = self.createTableInput(
                "joint_table",
                "Joint Table",
                joint_inputs,
                3,
                "1:3:2",
                50,
            )

            addJointInput = joint_inputs.addBoolValueInput(
                "joint_add", "Enable/Disable", False
            )

            #removeJointInput = joint_inputs.addBoolValueInput(
            #    "joint_delete", "Remove", False
            #)

            addJointInput.tooltip = "Add a joint selection"
            #removeJointInput.tooltip = "Remove a joint selection"

            addJointInput.isEnabled = False
            #removeJointInput.isEnabled = False

            jointSelectInput = joint_inputs.addSelectionInput("joint_select", "Selection", "Select a joint in your drive-train assembly.")
            jointSelectInput.addSelectionFilter("Joints") # limit selection to only joints
            jointSelectInput.setSelectionLimits(0)
            jointSelectInput.isEnabled = False
            jointSelectInput.isVisible = False

            jointTableInput.addToolbarCommandInput(addJointInput)
            #jointTableInput.addToolbarCommandInput(removeJointInput)

            """
            Gamepiece Configuration
            """
            gamepieceConfig = inputs.addGroupCommandInput("gamepiece_config", "Gamepiece Configuration")
            gamepieceConfig.isExpanded = True
            gamepieceConfig.isVisible = False
            gamepieceConfig.tooltip = "Select and define the gamepieces in your field."
            gamepiece_inputs = gamepieceConfig.children

            """
            Mass Units
            """
            weight_unit = gamepiece_inputs.addDropDownCommandInput("weight_unit", "Unit of Mass", adsk.core.DropDownStyles.LabeledIconDropDownStyle)
            weight_unit.listItems.add("lbs", True)
            weight_unit.listItems.add("kg", False)
            weight_unit.tooltip = "Configure the unit of mass for a gamepiece."

            """
            Gamepiece Selection Table
            """
            global gamepieceTableInput
            gamePieceTableInput = self.createTableInput(
                "gamepiece_table",
                "Gamepiece",
                gamepiece_inputs,
                3,
                "1:1:1",
                50,
            )

            addFieldElement = gamepiece_inputs.addBoolValueInput(
                "field_add", "Add", False
            )

            removeFieldElement = gamepiece_inputs.addBoolValueInput(
                "field_delete", "Remove", False
            )

            addFieldElement.tooltip = "Add a field element"
            removeFieldElement.tooltip = "Remove a field element"

            addFieldElement.isEnabled = \
            removeFieldElement.isEnabled = True

            gamepieceSelectInput = gamepiece_inputs.addSelectionInput("gamepiece_select", "Selection", "Select the unique gamepieces in your field.")
            gamepieceSelectInput.addSelectionFilter("Occurrences") # limit selection to only bodies
            gamepieceSelectInput.setSelectionLimits(0)
            gamepieceSelectInput.isEnabled = True
            gamepieceSelectInput.isVisible = False

            gamePieceTableInput.addToolbarCommandInput(addFieldElement)
            gamePieceTableInput.addToolbarCommandInput(removeFieldElement)

            """
            ~ Advanced Tab ~
            """
            advancedSettings = inputs_root.addTabCommandInput(
                "advanced_settings", "Advanced"
            )
            advancedSettings.tooltip = "Additional Advanced Settings to change how your model will be translated into Unity."
            a_input = advancedSettings.children

            """
            Physics Settings
            """
            physicsSettings = a_input.addGroupCommandInput("physics_settings", "Physics Settings")
            physicsSettings.isExpanded = False
            physicsSettings.isEnabled = True
            physicsSettings.tooltip = "tooltip"
            physics_settings = physicsSettings.children

            self.createBooleanInput(
                "density",
                "Density",
                physics_settings,
                checked=False,
                tooltip="tooltip",
                enabled=True,
            )

            self.createBooleanInput(
                "surface_area",
                "Surface Area",
                physics_settings,
                checked=False,
                tooltip="tooltip",
                enabled=True,
            )

            self.createBooleanInput(
                "restitution",
                "Restitution",
                physics_settings,
                checked=False,
                tooltip="tooltip",
                enabled=True,
            )

            """
            Joints Settings
            """
            jointsSettings = a_input.addGroupCommandInput("joints_settings", "Joints Settings")
            jointsSettings.isExpanded = False
            jointsSettings.isEnabled = True
            jointsSettings.tooltip = "tooltip"
            joints_settings = jointsSettings.children

            self.createBooleanInput(
                "kinematic_only",
                "Kinematic Only",
                joints_settings,
                checked=False,
                tooltip="tooltip",
                enabled=True,
            )

            self.createBooleanInput(
                "calculate_limits",
                "Calculate Limits",
                joints_settings,
                checked=False,
                tooltip="tooltip",
                enabled=True,
            )

            self.createBooleanInput(
                "auto_assign_ids",
                "Auto-Assign ID's",
                joints_settings,
                checked=False,
                tooltip="tooltip",
                enabled=True,
            )

            """
            Controller Settings
            """
            controllerSettings = a_input.addGroupCommandInput("controller_settings", "Controller Settings")
            controllerSettings.isExpanded = False
            controllerSettings.isEnabled = True
            controllerSettings.tooltip = "tooltip"
            controller_settings = controllerSettings.children

        except:
            self.log.error("Failed:\n{}".format(traceback.format_exc()))
            if A_EP:
                A_EP.send_exception()
            elif gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

    def createBooleanInput(
        self,
        _id: str,
        name: str,
        inputs: adsk.core.CommandInputs,
        tooltip="",
        tooltipadvanced="",
        checked=True,
        enabled=True,
        ) -> adsk.core.BoolValueCommandInput:
        """Simple helper to generate all of the options for me to create a boolean command input

        Args:
            _id (str): id value of the object - pretty much lowercase name
            name (str): name as displayed by the command prompt
            inputs (adsk.core.CommandInputs): parent command input container
            tooltip (str, optional): Description on hover of the checkbox. Defaults to "".
            tooltipadvanced (str, optional): Long hover description. Defaults to "".
            checked (bool, optional): Is checked by default?. Defaults to True.

        Returns:
            adsk.core.BoolValueCommandInput: Recently created command input
        """
        _input = inputs.addBoolValueInput(_id, name, True)
        _input.value = checked
        _input.isEnabled = enabled
        _input.tooltip = tooltip
        _input.tooltipDescription = tooltipadvanced
        return _input

    def createTableInput(
        self,
        _id: str,
        name: str,
        inputs: adsk.core.CommandInputs,
        columns: int,
        ratio: str,
        maxRows: int,
        minRows=1
        ) -> adsk.core.TableCommandInput: # accepts an occurrence (wheel)
            _input = inputs.addTableCommandInput(_id, name, columns, ratio)
            _input.minimumVisibleRows = minRows
            _input.maximumVisibleRows = maxRows
            return _input


class ConfigureCommandExecuteHandler(adsk.core.CommandEventHandler):
    """Called when Ok is pressed confirming the export to Unity.

    Process Steps:

        1. Check for process open in explorer

        1.5. Open file dialog to allow file location save
            - Not always optimal if sending over socket for parse

        2. Check Socket bind

        3. Check Socket recv
            - if true send data about file location in temp path

        4. Parse file and focus on unity window

    """

    def __init__(self, previous, fp):
        super().__init__()
        self.log = logging.getLogger(f"{INTERNAL_ID}.UI.{self.__class__.__name__}")
        self.previous = previous
        self.current = SerialCommand()
        self.fp = fp

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            if eventArgs.executeFailed:
                self.log.error("Could not execute configuration due to failure")
                return

            mode_dropdown = eventArgs.command.commandInputs.itemById(
                "general_settings"
            ).children.itemById("mode")

            mode_dropdown = adsk.core.DropDownCommandInput.cast(mode_dropdown)
            mode = 5

            if mode_dropdown.selectedItem.name == "Synthesis Exporter":
                mode = 5

            # Get the values from the command inputs.
            try:
                self.writeConfiguration(eventArgs.command.commandInputs)
                self.log.info("Wrote Configuration")

                # if it's different
                if self.current.toJSON() != self.previous:
                    Helper.writeConfigure(self.current.toJSON())
            except:
                self.log.error("Failed:\n{}".format(traceback.format_exc()))
                gm.ui.messageBox("Failed to read previous File Export Configuration")

            if mode == 5:
                savepath = FileDialogConfig.SaveFileDialog(
                    defaultPath=self.fp, ext="Synthesis File (*.synth)"
                )
            else:
                savepath = FileDialogConfig.SaveFileDialog(defaultPath=self.fp)

            if savepath == False:
                # save was canceled
                return
            else:
                updatedPath = pathlib.Path(savepath).parent
                if updatedPath != self.current.filePath:
                    self.current.filePath = str(updatedPath)
                    Helper.writeConfigure(self.current.toJSON())

                adsk.doEvents()
                # get active document
                design = gm.app.activeDocument.design
                name = design.rootComponent.name.rsplit(" ", 1)[0]
                version = design.rootComponent.name.rsplit(" ", 1)[1]

                renderer = 0

                _exportWheels = []
                _exportJoints = []
                joint_name = []

                for i in _joints:
                    joint_name.append(i.name)

                for row in range(wheelTableInput.rowCount):
                    index = wheelTableInput.getInputAtPosition(row, 2).selectedItem.index
                    
                    if index == 0:
                            _exportWheels.append(_Wheel(_wheels[row], WheelType.STANDARD))
                    elif index == 1:
                            _exportWheels.append(_Wheel(_wheels[row], WheelType.OMNI))

                for row in range(jointTableInput.rowCount):
                    item = jointTableInput.getInputAtPosition(row, 2).selectedItem

                    if item.name == "Root":
                        _exportJoints.append(_Joint(_joints[row], JointParentType.ROOT))
                    else:
                        index = joint_name.index(item.name)
                        _exportJoints.append(_Joint(_joints[row], _joints[index]))

                options = ParseOptions(
                    savepath,
                    name,
                    version,
                    materials=renderer,
                    joints=_exportJoints,
                    wheels=_exportWheels,
                )
                
                if options.parse(False):
                    # success
                    pass
                else:
                    gm.ui.messageBox(
                        f"Error: \n\t{name} could not be written to \n {savepath}"
                    )
                    self.log.error(
                        f"Error: \n\t{name} could not be written to \n {savepath}"
                    )

            # gm.ui.messageBox(f"general materials is set to: {inputs.itemById('general_settings').children.itemById('materials').value}")
        except:
            self.log.error("Failed:\n{}".format(traceback.format_exc()))
            if A_EP:
                A_EP.send_exception()
            elif gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

    def writeConfiguration(self, rootCommandInput: adsk.core.CommandInputs):
        """Simple hard coded function to save the parameters of the export to the file

        - This is horribly written but im in a rush
        - Should have most likely been a map that could be serialized easily

        Args:
            rootCommandInput (adsk.core.CommandInputs): Base Command Inputs
        """
        if self.current:
            self.current.filePath = self.fp
            _general = self.current.general
            _advanced = self.current.advanced
            # _vr = self.previous.vrSettings

            generalSettingsInputs = rootCommandInput.itemById("general_settings").children
            advancedSettingsInputs = rootCommandInput.itemById("advanced_settings").children

            if generalSettingsInputs and _general:
                # vrSettingsInputs = generalSettingsInputs.itemById("vrSettings")

                _general.material.checked = generalSettingsInputs.itemById(
                    "materials"
                ).value
                _general.joints.checked = generalSettingsInputs.itemById("joints").value
                _general.rigidGroups.checked = generalSettingsInputs.itemById(
                    "rigidGroups"
                ).value

            if advancedSettingsInputs and _advanced:

                _advanced.friction.checked = advancedSettingsInputs.itemById(
                    "friction"
                ).value
                _advanced.density.checked = advancedSettingsInputs.itemById(
                    "density"
                ).value
                _advanced.mass.checked = advancedSettingsInputs.itemById("mass").value
                _advanced.volume.checked = advancedSettingsInputs.itemById("volume").value
                _advanced.surfaceArea.checked = advancedSettingsInputs.itemById(
                    "surfacearea"
                ).value
                _advanced.com.checked = advancedSettingsInputs.itemById("com").value


class MySelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            selectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)
            selectedJoint = adsk.fusion.Joint.cast(args.selection.entity)

            if selectedOcc: # selection breaks when you select root comp.
                if exportMode == True:
                    if duplicateSelection.value == True:
                        for occ in gm.app.activeDocument.design.rootComponent.occurrencesByComponent(selectedOcc.component):   
                            if occ not in _wheels:
                                #gm.ui.activeSelections.add(occ)
                                _wheels.append(occ)
                                addWheelToTable(occ)
                    else:
                        _wheels.append(selectedOcc)
                        addWheelToTable(selectedOcc)
                else:
                    _gamepieces.append(selectedOcc)
                    addGamepieceToTable(selectedOcc)

            elif selectedJoint:
                if selectedJoint.jointMotion.jointType == 0:
                    #gm.ui.activeSelections.removeBySelection(args.selection)
                    pass
                else:
                    index = _joints[selectedJoint]
                    jointTableInput.selectedRow = index
                    #_joints.append(selectedJoint)
                    #addJointToTable(selectedJoint)
        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


class MyUnSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            selectedWheel = adsk.fusion.Occurrence.cast(args.selection.entity) 
            selectedJoint = adsk.fusion.Joint.cast(args.selection.entity)

            if selectedWheel:
                removeWheelFromTable(selectedWheel)

            elif selectedJoint:
                removeJointFromTable(selectedJoint)
        except ValueError: # bad solution to value error. replace with somethin better
            pass
        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


class ConfigureCommandInputChanged(adsk.core.InputChangedEventHandler):
    """Gets instantiated from Fusion whenever there is a valid input change.

    Process:
        - Enable Advanced Features
        - Enable VR Features
            - Give optional hand contact set placement
            - Check for additional params on exit
            - serialize additional data
    """

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(
            f"{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}"
        )

    def notify(self, args):
        try:
            global wheelTableInput, jointConfig, exportMode, gamepieceConfig # dont use globals
            
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            cmdInput = eventArgs.input
            inputs = cmdInput.commandInputs

            wheelSelect = inputs.itemById("wheel_select")
            jointSelect = inputs.itemById("joint_select")
            gamepieceSelect = inputs.itemById("gamepieceSelect")

            if cmdInput.id == "mode":
                modeDropdown = adsk.core.DropDownCommandInput.cast(cmdInput)

                gamepieceConfig = inputs.itemById("gamepiece_config")
                jointConfig = inputs.itemById("joint_config")
                wheelConfig = inputs.itemById("wheel_config")
                weightTableInput = inputs.itemById("weight_table")
                exportJoints = inputs.itemById("export_joints")

                if modeDropdown.selectedItem.name == "Robot":
                    if gamepieceConfig:
                        gamepieceConfig.isVisible = False
                        jointConfig.isVisible = \
                        exportJoints.isVisible = \
                        wheelConfig.isVisible = \
                        exportMode = \
                        weightTableInput.isVisible = True

                elif modeDropdown.selectedItem.name == "Field":
                    if gamepieceConfig:
                        gamepieceConfig.isVisible = True
                        jointConfig.isVisible = \
                        exportJoints.isVisible = \
                        wheelConfig.isVisible = \
                        exportMode = \
                        weightTableInput.isVisible = False

            elif cmdInput.id == "export_joints":
                boolValue = adsk.core.BoolValueCommandInput.cast(cmdInput)
                jointConfig = inputs.itemById("joint_config")

                if boolValue.value == True:
                    if jointConfig:
                        #jointConfig.isExpanded = \
                        jointConfig.isEnabled = \
                        addJointInput.isEnabled = \
                        jointTableInput.isEnabled = True
                        #removeJointInput.isEnabled = True

                else:
                    if jointConfig:
                        jointConfig.isExpanded = \
                        jointConfig.isEnabled = \
                        addJointInput.isEnabled = \
                        jointTableInput.isEnabled = False
                        #removeJointInput.isEnabled = False

            elif cmdInput.id == "wheel_config":
                group = adsk.core.GroupCommandInput.cast(cmdInput)

                if not group.isExpanded:
                    gm.ui.activeSelections.clear()
                else:
                    for i in range(len(_wheels)):
                        gm.ui.activeSelections.add(_wheels[i])

            elif cmdInput.id == "joint_config":
                group = adsk.core.GroupCommandInput.cast(cmdInput)
                boolValue = adsk.core.BoolValueCommandInput.cast(cmdInput)

                jointSelect.isEnabled = True

                if not group.isExpanded:
                    gm.ui.activeSelections.clear()
                else:
                        for joint in gm.app.activeDocument.design.rootComponent.allJoints:
                            if joint.isLightBulbOn == True:
                                if joint.jointMotion.jointType == 0:
                                    joint.isLightBulbOn = False
                                else:
                                    #gm.ui.activeSelections.add(joint)
                                    _joints.append(joint)
                                    addJointToTable(joint)

            elif cmdInput.id == "wheel_type":
                wheelDropdown = adsk.core.DropDownCommandInput.cast(cmdInput)

                if wheelDropdown.selectedItem.name == "Standard":
                    getPosition = wheelTableInput.getPosition(adsk.core.DropDownCommandInput.cast(cmdInput))
                    iconInput = wheelTableInput.getInputAtPosition(getPosition[1], 0)
                    iconInput.imageFile = iconPaths["standard"]
                    iconInput.tooltip = "Standard wheel"

                elif wheelDropdown.selectedItem.name == "Omni":
                    getPosition = wheelTableInput.getPosition(adsk.core.DropDownCommandInput.cast(cmdInput))
                    iconInput = wheelTableInput.getInputAtPosition(getPosition[1], 0)
                    iconInput.imageFile = iconPaths["omni"]
                    iconInput.tooltip = "Omni wheel"

            elif cmdInput.id == "field_add":
                addFieldInput.isEnabled = True
                gamepieceSelect.isEnabled = True

            elif cmdInput.id == "field_delete":
                table = inputs.itemById("gamepiece_table")
                addWheelInput.isEnabled = True
                
                #if gamepieceConfig.isEnabled == True:
                #    addJointInput.isEnabled = True
                
                if table.selectedRow == -1:
                    gm.ui.messageBox(
                        "Select one row to delete.")
                else:
                    selectedRow = table.selectedRow
                    gamepiece = _gamepieces[table.selectedRow]
                    removeGamePieceFromTable(gamepiece)

                    gm.ui.activeSelections.removeByIndex(selectedRow)

            elif cmdInput.id == "wheel_add":
                if jointConfig.isEnabled == True:
                    addJointInput.isEnabled = True

                wheelSelect.isEnabled = True
                
                addWheelInput.isEnabled = False
                #gm.ui.activeSelections.clear()

            elif cmdInput.id == "wheel_delete":
                table = inputs.itemById("wheel_table")
                addWheelInput.isEnabled = True
                
                if jointConfig.isEnabled == True:
                    addJointInput.isEnabled = True
                
                if table.selectedRow == -1:
                    gm.ui.messageBox(
                        "Select one row to delete.")
                else:
                    selectedRow = table.selectedRow
                    wheel = _wheels[table.selectedRow]
                    removeWheelFromTable(wheel)

                    gm.ui.activeSelections.removeByIndex(selectedRow)

            elif cmdInput.id == "wheel_select":
                wheelSelect.isEnabled = False
                addWheelInput.isEnabled = True

            elif cmdInput.id == "joint_add":
                addWheelInput.isEnabled = True
                #jointSelect.isEnabled = True
                
                #addJointInput.isEnabled = False
                #gm.ui.activeSelections.clear()

           #elif cmdInput.id == "joint_delete":
           #    table = inputs.itemById("joint_table")
           #    addJointInput.isEnabled = True
           #    addWheelInput.isEnabled = True
           #    
           #    if table.selectedRow == -1:
           #        gm.ui.messageBox(
           #            "Select one row to delete.")
           #    else:
           #        selectedRow = table.selectedRow
           #        joint = _joints[table.selectedRow]
           #        removeJointFromTable(joint)

           #        #gm.ui.activeSelections.removeByIndex(selectedRow)
            
            elif cmdInput.id == "joint_select":
                jointSelect.isEnabled = False
                addJointInput.isEnabled = True
        except:
            self.log.error("Failed:\n{}".format(traceback.format_exc()))
            if A_EP:
                A_EP.send_exception()
            elif gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

          
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            _wheels.clear()
            _joints.clear()
            gm.ui.activeSelections.clear()
        except:
            gm.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def createMeshGraphics():
    design = adsk.fusion.Design.cast(gm.app.activeProduct)
    
    if design:
        for occ in _wheels:
            for body in occ.bRepBodies:
                graphics = design.rootComponent.customGraphicsGroups.add()
                bodyMesh = body.meshManager.displayMeshes.bestMesh
                coords = adsk.fusion.CustomGraphicsCoordinates.create(bodyMesh.nodeCoordinatesAsDouble)
                mesh = graphics.addMesh(
                    coords, bodyMesh.nodeIndices, bodyMesh.normalVectorsAsDouble, bodyMesh.nodeIndices
                )
                showThrough = adsk.fusion.CustomGraphicsShowThroughColorEffect.create(adsk.core.Color.create(255, 0, 0, 255), 0.2)
                body.color = showThrough
                mesh.color = showThrough

            gm.app.activeViewport.refresh()

def addJointToTable(joint):
    # get the CommandInputs object associated with the parent command.
    cmdInputs = adsk.core.CommandInputs.cast(jointTableInput.commandInputs)

    if joint.jointMotion.jointType == adsk.fusion.JointTypes.RigidJointType:
        icon = cmdInputs.addImageCommandInput("placeholder", "Rigid", iconPaths["rigid"])
        icon.tooltip = "Rigid joint"
    
    elif joint.jointMotion.jointType == adsk.fusion.JointTypes.RevoluteJointType:
        icon = cmdInputs.addImageCommandInput("placeholder", "Revolute", iconPaths["revolute"])
        icon.tooltip = "Revolute joint"

    elif joint.jointMotion.jointType == adsk.fusion.JointTypes.SliderJointType:
        icon = cmdInputs.addImageCommandInput("placeholder", "Slider", iconPaths["slider"])
        icon.tooltip = "Slider joint"
  
    name = cmdInputs.addTextBoxCommandInput("name", "Occurrence name", joint.name, 1, True)
    name.tooltip = (
        "Selection set"
    )
    jointType = cmdInputs.addDropDownCommandInput(
        "joint_type",
        "Joint Type",
        dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
    )
    jointType.listItems.add(
        "Root", True
    )

    # after each additional joint added, add joint to the dropdown of all preview rows/joints
    for i in range(jointTableInput.rowCount):
        dropDown = jointTableInput.getInputAtPosition(i, 2)
        dropDown.listItems.add(
            _joints[-1].name, False
        )
    
    # add all parent joint options to added joint dropdown
    for j in range(len(_joints) - 1):
        jointType.listItems.add(
            _joints[j].name, True
        )

    jointType.tooltip = (
        "Select the parent joint."
    )

    row = jointTableInput.rowCount

    jointTableInput.addCommandInput(icon, row, 0)
    jointTableInput.addCommandInput(name, row, 1)
    jointTableInput.addCommandInput(jointType, row, 2)

def addWheelToTable(wheel):
    # get the CommandInputs object associated with the parent command.
    cmdInputs = adsk.core.CommandInputs.cast(wheelTableInput.commandInputs)
    icon = cmdInputs.addImageCommandInput("placeholder", "Placeholder", iconPaths["standard"])
    name = cmdInputs.addTextBoxCommandInput("name", "Occurrence name", wheel.name, 1, True)
    name.tooltip = (
        "Selection set"
    )
    wheelType = cmdInputs.addDropDownCommandInput(
        "wheel_type",
        "Wheel Type",
        dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
    )
    wheelType.listItems.add(
        "Standard", True, ""
    )
    wheelType.listItems.add(
        "Omni", False, ""
    )
    wheelType.tooltip = (
        "Wheel type"
    )
    wheelType.tooltipDescription = (
        "<Br>Omni-directional wheels can be used just like regular drive wheels but they have the advantage of being able to roll freely perpendicular to the drive direction.</Br>"
    )
    wheelType.toolClipFilename = (
        "src\Resources\omni-wheel-preview.png"
    )
    row = wheelTableInput.rowCount

    wheelTableInput.addCommandInput(icon, row, 0)
    wheelTableInput.addCommandInput(name, row, 1)
    wheelTableInput.addCommandInput(wheelType, row, 2)

def addGamepieceToTable():
    cmdInputs = adsk.core.CommandInputs.cast(gamepieceTableInput.commandInputs)
    type = cmdInputs.addTextBoxCommandInput("gp_type", "GP-Type", "", 1, False)
    weight = cmdInputs.addValueInput("gp_weight", "Weight Input", "", adsk.core.ValueInput.createByString("0.0"))
    friction_coeff = cmdInputs.addIntegerSliderCommandInput("friction_coeff", "Friction", 0, 1)
    
    type.tooltip = (
        "Type of field element."
    )
    type.tooltipDescription = (
        "E.g. \"Ball\" or \"Tote\"."
    )
    weight.tooltip = (
        "Weight of field element."
    )
    friction_coeff.tooltip = (
        "Friction coefficient of field element."
    )
    friction_coeff.tooltipDescription (
        "Friction coefficients range from 0 (ice) to 1 (rubber)."
    )

    row = wheelTableInput.rowCount

    gamepieceTableInput.addCommandInput(type, row, 0)
    gamepieceTableInput.addCommandInput(weight, row, 1)
    gamepieceTableInput.addCommandInput(friction_coeff, row, 2)

def removeJointFromTable(joint):
    index = jointTableInput.selectedRow
    _joints.remove(joint)

    jointTableInput.deleteRow(index)
    
    for row in range(jointTableInput.rowCount):
        dropDown = jointTableInput.getInputAtPosition(row, 2)
        dropDown.listItems.clear()

        dropDown.listItems.add(
        "Root", False
        )

        a = [x for i, x in enumerate(_joints) if i!=row]

        for joint in a:
            dropDown.listItems.add(
                joint.name, False
            )
        dropDown.listItems.item(row).isSelected = True

def removeWheelFromTable(wheel):
    try:
        index = _wheels.index(wheel)
        _wheels.remove(wheel)
        wheelTableInput.deleteRow(index)

    except ValueError:
        pass
    except:
        if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

def removeGamePieceFromTable(gamepiece):
    try:
        index = _gamepieces.index(gamepiece)
        _gamepieces.remove(gamepiece)
        gamepieceTableInput.deleteRow(index)
    except ValueError:
        pass
    except:
        if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
