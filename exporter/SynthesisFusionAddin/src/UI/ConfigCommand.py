from logging import PlaceHolder
from os import dup, fdopen, remove, strerror
from typing import Type
from proto.proto_out.joint_pb2 import Joint
from ..general_imports import *
from ..configure import NOTIFIED, write_configuration
from ..Analytics.alert import showAnalyticsAlert
from . import Helper, FileDialogConfig, OsHelper

from ..Parser.ParseOptions import (
    ParseOptions,
    SignalType,
    _Joint,
    _Wheel,
    WheelType,
    JointParentType,
)
from .Configuration.SerialCommand import (
    Struct,
    SerialCommand,
    General,
    Advanced,
    BooleanInput,
    ExportMode,
)

import adsk.core, adsk.fusion, traceback, math
from types import SimpleNamespace

"""
File to generate and link the Configuration Command seen when pressing the button from the Addins Panel
"""
cmd = None

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
dropdownExportMode = adsk.core.DropDownCommandInput.cast(None)

# selected wheels, joints, & gamepieces
_wheels = []
_joints = []
_gamepieces = []

# easy-access image paths for icons
# TODO: make OSX accessible paths
iconPaths = {
    "omni": "src\Resources\WheelIcons\omni-wheel-preview190x24.png",
    "standard": "src\Resources\WheelIcons\standard-wheel-preview190x24.png",
    "rigid": "src/Resources/JointIcons/JointRigid/rigid190x24.png",
    "revolute": "src/Resources/JointIcons/JointRev/revolute190x24.png",
    "slider": "src/Resources/JointIcons/JointSlider/slider190x24.png",
    "planar": "src/Resources/JointIcons/JointPlanar/planar190x24.png",
    "pin_slot": "src/Resources/JointIcons/JointPinSlot/pin_slot190x24.png",
    "cylindrical": "src/Resources/JointIcons/JointCyl/cylindrical190x24.png",
    "ball": "src/Resources/JointIcons/JointBall/ball190x24.png",
    "blank": "src/Resources/blank-preview16x16.png",
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

            global wheelTableInput, jointTableInput, addWheelInput, addJointInput, removeWheelInput, removeJointInput, addFieldInput, removeFieldInput

            global NOTIFIED

            if not NOTIFIED:
                showAnalyticsAlert()
                NOTIFIED = True
                write_configuration("analytics", "notified", "yes")

            app = adsk.core.Application.get()
            design = app.activeDocument.design

            previous = None
            saved = Helper.previouslyConfigured()

            if type(saved) == str:
                try:
                    # probably need some way to validate for each usage below
                    previous = json.loads(
                        saved, object_hook=lambda d: SimpleNamespace(**d)
                    )
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

            global cmd
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = eventArgs.command

            # Set to false so won't automatically export on switch context
            cmd.isAutoExecute = False
            cmd.isExecutedWhenPreEmpted = False
            cmd.okButtonText = "Export"

            inputs_root = cmd.commandInputs

            """
            ~ General Tab ~
            """
            inputs = inputs_root.addTabCommandInput(
                "general_settings", "General"
            ).children

            # This actually has the ability to entirely create a input from just a protobuf message which is really neat
            ## NOTE: actually is super neat but I don't have time at the moment
            # self.parseMessage(inputs)

            """
            Help File
            """
            cmd.helpFile = "src\Resources\HTML\info.html"

            """
            Export Mode
            """

            global dropdownExportMode

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
                "weight_table", "Weight Table", inputs, 3, "5:3:2", 1
            )
            weightTableInput.tablePresentationStyle = 2

            weight_name = inputs.addStringValueInput("weight_name", "Weight")
            weight_name.value = "Weight"
            weight_name.isReadOnly = True

            populateweight = 0.0

            # BIG OOF THIS IS EXPENSIVO
            if design:
                rootComponent = design.rootComponent
                physical = rootComponent.getPhysicalProperties(
                    adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
                )
                populateweight = physical.mass * 2.2046226218  # kg to lbs
                populateweight = round(
                    populateweight, 2
                )  # make it more readable - why is this so small?

            weight_input = inputs.addValueInput(
                "weight_input",
                "Weight Input",
                "",
                adsk.core.ValueInput.createByString(str(populateweight)),
            )
            weight_input.tooltip = "Weight"

            weight_unit = inputs.addDropDownCommandInput(
                "weight_unit",
                "Weight Unit",
                adsk.core.DropDownStyles.LabeledIconDropDownStyle,
            )
            weight_unit.listItems.add("lbs", True)
            weight_unit.listItems.add("kg", False)
            weight_unit.tooltip = "Unit of mass"

            weightTableInput.addCommandInput(weight_name, 0, 0)
            weightTableInput.addCommandInput(weight_input, 0, 1)
            weightTableInput.addCommandInput(weight_unit, 0, 2)

            """
            Export Joints
            """
            global exportJoints
            exportJoints = self.createBooleanInput(
                "export_joints",
                "Export Joints",
                inputs,
                checked=True,
                tooltip="Export Fusion 360 joints into Unity.",
                tooltipadvanced="May be inconsistent dependening on the type of joint.",
                enabled=True,
            )

            """
            Wheel Configuration
            """

            wheelConfig = inputs.addGroupCommandInput(
                "wheel_config", "Wheel Configuration"
            )
            wheelConfig.isExpanded = True
            wheelConfig.isEnabled = True
            wheelConfig.tooltip = (
                "Select and define the drive-train wheels in your assembly."
            )

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
                4,
                "1:2:2:1",
                50,
            )

            addWheelInput = wheel_inputs.addBoolValueInput("wheel_add", "Add", False)

            removeWheelInput = wheel_inputs.addBoolValueInput(
                "wheel_delete", "Remove", False
            )

            addWheelInput.tooltip = "Add a wheel component"
            removeWheelInput.tooltip = "Remove a wheel component"

            wheelSelectInput = wheel_inputs.addSelectionInput(
                "wheel_select",
                "Selection",
                "Select the wheels in your drive-train assembly.",
            )
            wheelSelectInput.addSelectionFilter("Occurrences")

            wheelSelectInput.setSelectionLimits(0)
            wheelSelectInput.isEnabled = False
            wheelSelectInput.isVisible = False

            wheelTableInput.addToolbarCommandInput(addWheelInput)
            wheelTableInput.addToolbarCommandInput(removeWheelInput)

            wheelTableInput.addCommandInput(
                self.createTextBoxInput(
                    "name_header", "Name", wheel_inputs, "Component name", bold=False
                ),
                0,
                1,
            )

            wheelTableInput.addCommandInput(
                self.createTextBoxInput(
                    "parent_header",
                    "Parent",
                    wheel_inputs,
                    "Wheel type",
                    background="#d9d9d9",
                ),
                0,
                2,
            )

            wheelTableInput.addCommandInput(
                self.createTextBoxInput(
                    "signal_header",
                    "Signal",
                    wheel_inputs,
                    "Signal type",
                    background="#d9d9d9",
                ),
                0,
                3,
            )

            """
            Joint Configuration
            """

            global jointConfig

            jointConfig = inputs.addGroupCommandInput(
                "joint_config", "Joint Configuration"
            )
            jointConfig.isExpanded = True
            jointConfig.isVisible = True
            jointConfig.tooltip = "Select and define joint occurrences in your assembly."

            joint_inputs = jointConfig.children

            """
            Joint Selection Table
            """
            jointTableInput = self.createTableInput(
                "joint_table",
                "Joint Table",
                joint_inputs,
                4,
                "1:2:2:1",
                50,
            )

            addJointInput = joint_inputs.addBoolValueInput("joint_add", "Add", False)

            removeJointInput = joint_inputs.addBoolValueInput(
                "joint_delete", "Remove", False
            )

            addJointInput.isEnabled = removeJointInput.isEnabled = True

            addJointInput.tooltip = "Add a joint selection"
            removeJointInput.tooltip = "Remove a joint selection"

            jointSelectInput = joint_inputs.addSelectionInput(
                "joint_select",
                "Selection",
                "Select a joint in your drive-train assembly.",
            )

            jointSelectInput.addSelectionFilter("Joints")
            jointSelectInput.setSelectionLimits(0)
            jointSelectInput.isEnabled = False
            jointSelectInput.isVisible = False

            jointTableInput.addToolbarCommandInput(addJointInput)
            jointTableInput.addToolbarCommandInput(removeJointInput)

            jointTableInput.addCommandInput(
                self.createTextBoxInput(
                    "motion_header",
                    "Joint motion",
                    joint_inputs,
                    "Joint motion",
                    bold=False,
                ),
                0,
                0,
            )

            jointTableInput.addCommandInput(
                self.createTextBoxInput(
                    "name_header", "Name", joint_inputs, "Joint name", bold=False
                ),
                0,
                1,
            )

            jointTableInput.addCommandInput(
                self.createTextBoxInput(
                    "parent_header",
                    "Parent",
                    joint_inputs,
                    "Possible parent joints",
                    background="#d9d9d9",
                ),
                0,
                2,
            )

            jointTableInput.addCommandInput(
                self.createTextBoxInput(
                    "signal_header",
                    "Signal",
                    joint_inputs,
                    "Signal type",
                    background="#d9d9d9",
                ),
                0,
                3,
            )

            for joint in gm.app.activeDocument.design.rootComponent.allJoints:
                if joint.jointMotion.jointType == 0:
                    joint.isLightBulbOn = False
                else:
                    joint.isLightBulbOn == True
                    addJointToTable(joint)

            """
            Gamepiece Configuration
            """

            gamepieceConfig = inputs.addGroupCommandInput(
                "gamepiece_config", "Gamepiece Configuration"
            )
            gamepieceConfig.isExpanded = True
            gamepieceConfig.isVisible = False
            gamepieceConfig.tooltip = "Select and define the gamepieces in your field."
            gamepiece_inputs = gamepieceConfig.children

            """
            Mass Units
            """
            weight_unit = gamepiece_inputs.addDropDownCommandInput(
                "weight_unit",
                "Unit of Mass",
                adsk.core.DropDownStyles.LabeledIconDropDownStyle,
            )
            weight_unit.listItems.add("lbs", True)
            weight_unit.listItems.add("kg", False)
            weight_unit.tooltip = "Configure the unit of mass for a gamepiece."

            """
            Gamepiece Selection Table
            """
            global gamepieceTableInput

            gamepieceTableInput = self.createTableInput(
                "gamepiece_table",
                "Gamepiece",
                gamepiece_inputs,
                4,
                "1:6:2:9",
                50,
            )

            addFieldInput = gamepiece_inputs.addBoolValueInput("field_add", "Add", False)

            removeFieldInput = gamepiece_inputs.addBoolValueInput(
                "field_delete", "Remove", False
            )
            addFieldInput.isEnabled = removeFieldInput.isEnabled = True

            removeFieldInput.tooltip = "Remove a field element"
            addFieldInput.tooltip = "Add a field element"

            gamepieceSelectInput = gamepiece_inputs.addSelectionInput(
                "gamepiece_select",
                "Selection",
                "Select the unique gamepieces in your field.",
            )
            gamepieceSelectInput.addSelectionFilter("Occurrences")
            gamepieceSelectInput.setSelectionLimits(0)
            gamepieceSelectInput.isEnabled = True
            gamepieceSelectInput.isVisible = False

            gamepieceTableInput.addToolbarCommandInput(addFieldInput)
            gamepieceTableInput.addToolbarCommandInput(removeFieldInput)

            gamepieceTableInput.addCommandInput(
                self.createTextBoxInput(
                    "e_header",
                    "Gamepiece weight",
                    gamepiece_inputs,
                    "Element",
                    bold=False,
                ),
                0,
                1,
            )

            gamepieceTableInput.addCommandInput(
                self.createTextBoxInput(
                    "w_header",
                    "Gamepiece weight",
                    gamepiece_inputs,
                    "Weight",
                    background="#d9d9d9",
                ),
                0,
                2,
            )

            gamepieceTableInput.addCommandInput(
                self.createTextBoxInput(
                    "f_header",
                    "Friction coefficient",
                    gamepiece_inputs,
                    "Friction coefficient",
                    background="#d9d9d9",
                ),
                0,
                3,
            )

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
            physicsSettings = a_input.addGroupCommandInput(
                "physics_settings", "Physics Settings"
            )

            physicsSettings.isExpanded = True
            physicsSettings.isEnabled = True
            physicsSettings.tooltip = "tooltip"
            physics_settings = physicsSettings.children

            self.createBooleanInput(
                "density",
                "Density",
                physics_settings,
                checked=True,
                tooltip="tooltip",
                enabled=True,
            )

            self.createBooleanInput(
                "surface_area",
                "Surface Area",
                physics_settings,
                checked=True,
                tooltip="tooltip",
                enabled=True,
            )

            self.createBooleanInput(
                "restitution",
                "Restitution",
                physics_settings,
                checked=True,
                tooltip="tooltip",
                enabled=True,
            )

            frictionOverride = self.createBooleanInput(
                "friction_override",
                "Friction Override",
                physics_settings,
                checked=False,
                tooltip="Manually override the default friction values on the bodies in the assembly.",
                enabled=True,
                isCheckBox=True,
            )
            # frictionOverride.resourceFolder = "C:/Users/t_oubay/Documents/synthesis/exporter/SynthesisFusionAddin/src/Resources/Listitem-Icons"

            global frictionOverrideTable
            frictionOverrideTable = self.createTableInput(
                "friction_override_table",
                "",
                physics_settings,
                1,
                "1",
                1,
            )
            frictionOverrideTable.isVisible = False

            valueList = [1]
            for i in range(20):
                valueList.append(i / 20)

            frictionCoeff = physics_settings.addFloatSliderListCommandInput(
                "friction_coeff_override", "Friction Coefficient", "", valueList
            )

            frictionCoeff.isVisible = False
            frictionCoeff.valueOne = 0.5

            frictionOverrideTable.addCommandInput(frictionCoeff, 0, 0)

            """
            Joints Settings
            """
            jointsSettings = a_input.addGroupCommandInput(
                "joints_settings", "Joints Settings"
            )
            jointsSettings.isExpanded = True
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
                checked=True,
                tooltip="tooltip",
                enabled=True,
            )

            self.createBooleanInput(
                "auto_assign_ids",
                "Auto-Assign ID's",
                joints_settings,
                checked=True,
                tooltip="tooltip",
                enabled=True,
            )

            """
            Controller Settings
            """
            controllerSettings = a_input.addGroupCommandInput(
                "controller_settings", "Controller Settings"
            )

            controllerSettings.isExpanded = True
            controllerSettings.isEnabled = True
            controllerSettings.tooltip = "tooltip"
            controller_settings = controllerSettings.children

            self.createBooleanInput(
                "export_signals",
                "Export Signals",
                controller_settings,
                checked=True,
                tooltip="tooltip",
                enabled=True,
            )

        except:
            self.log.error("Failed:\n{}".format(traceback.format_exc()))
            if A_EP:
                A_EP.send_exception()
            elif gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

        onExecute = ConfigureCommandExecuteHandler(
            json.dumps(previous, default=lambda o: o.__dict__, sort_keys=True, indent=1),
            previous.filePath,
        )
        cmd.execute.add(onExecute)
        gm.handlers.append(onExecute)

        onInputChanged = ConfigureCommandInputChanged()
        cmd.inputChanged.add(onInputChanged)
        gm.handlers.append(onInputChanged)

        onExecutePreview = CommandExecutePreviewHandler()
        cmd.executePreview.add(onExecutePreview)
        gm.handlers.append(onExecutePreview)

        onSelect = MySelectHandler(False)
        cmd.select.add(onSelect)
        gm.handlers.append(onSelect)

        onPreSelect = MyPreSelectHandler()
        cmd.preSelect.add(onPreSelect)
        gm.handlers.append(onPreSelect)

        onPreSelectEnd = MyPreselectEndHandler()
        cmd.preSelectEnd.add(onPreSelectEnd)
        gm.handlers.append(onPreSelectEnd)

        onDestroy = MyCommandDestroyHandler()
        cmd.destroy.add(onDestroy)
        gm.handlers.append(onDestroy)

    def createBooleanInput(
        self,
        _id: str,
        name: str,
        inputs: adsk.core.CommandInputs,
        tooltip="",
        tooltipadvanced="",
        checked=True,
        enabled=True,
        isCheckBox=True,
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
        _input = inputs.addBoolValueInput(_id, name, isCheckBox)
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
        minRows=1,
        columnSpacing=0,
        rowSpacing=0,
    ) -> adsk.core.TableCommandInput:  # accepts an occurrence (wheel)
        _input = inputs.addTableCommandInput(_id, name, columns, ratio)
        _input.minimumVisibleRows = minRows
        _input.maximumVisibleRows = maxRows
        _input.columnSpacing = columnSpacing
        _input.rowSpacing = rowSpacing
        return _input

    def createTextBoxInput(
        self,
        _id: str,
        name: str,
        inputs: adsk.core.CommandInputs,
        text: str,
        italics=True,
        bold=True,
        fontSize=10,
        alignment="center",
        rowCount=1,
        read=True,
        background="whitesmoke",
    ) -> adsk.core.TextBoxCommandInput:

        i = ["", ""]
        b = ["", ""]

        if bold:
            b[0] = "<b>"
            b[1] = "</b>"
        if italics:
            i[0] = "<i>"
            i[1] = "</i>"

        wrapper = """<body style='background-color:%s;'>
                     <div align='%s'>
                     <p style='font-size:%spx'>
                     %s%s{}%s%s
                     </p>
                     </body>
                  """.format(
            text
        )

        _text = wrapper % (background, alignment, fontSize, b[0], i[0], i[1], b[1])

        _input = inputs.addTextBoxCommandInput(_id, name, _text, rowCount, read)
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

                for row in range(wheelTableInput.rowCount):
                    if row == 0:
                        continue

                    wheelTypeIndex = wheelTableInput.getInputAtPosition(
                        row, 2
                    ).selectedItem.index

                    signalTypeIndex = wheelTableInput.getInputAtPosition(
                        row, 3
                    ).selectedItem.index

                    wheelType = (
                        wheelTypeIndex  # This must be either 0 or 1 for standard or omni
                    )
                    signalType = signalTypeIndex

                    _exportWheels.append(
                        _Wheel(_wheels[row - 1].entityToken, wheelType, signalType)
                    )

                if exportJoints.value:
                    for row in range(jointTableInput.rowCount):
                        if row == 0:
                            continue

                        parentJointIndex = jointTableInput.getInputAtPosition(
                            row, 2
                        ).selectedItem.index

                        signalTypeIndex = jointTableInput.getInputAtPosition(
                            row, 3
                        ).selectedItem.index

                        parentJointToken = ""
                        signalType = signalTypeIndex

                        if parentJointIndex == 0:
                            _exportJoints.append(
                                _Joint(
                                    _joints[row - 1].entityToken,
                                    JointParentType.ROOT,
                                    signalType,
                                )  # Root
                            )
                            continue
                        elif parentJointIndex < row:
                            parentJointToken = _joints[
                                parentJointIndex - 1
                            ].entityToken  # str
                        else:
                            parentJointToken = _joints[
                                parentJointIndex + 1
                            ].entityToken  # str

                        _exportJoints.append(
                            _Joint(
                                _joints[row - 1].entityToken, parentJointToken, signalType
                            )
                        )

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

            generalSettingsInputs = rootCommandInput.itemById("general_settings").children
            advancedSettingsInputs = rootCommandInput.itemById(
                "advanced_settings"
            ).children

            """
            ##Removed this for now, since we are discarding SerialCommand.py

            if generalSettingsInputs and _general:
                try:
                    _general.material.checked = generalSettingsInputs.itemById("materials").value
                    _general.joints.checked = generalSettingsInputs.itemById("joints").value
                    _general.rigidGroups.checked = generalSettingsInputs.itemById("rigidGroups").value

                except:
                    # this will force an error - ignore for now
                    pass

            if advancedSettingsInputs and _advanced:
                try:
                    _advanced.friction.checked = advancedSettingsInputs.itemById("friction").value
                    _advanced.density.checked = advancedSettingsInputs.itemById("density").value
                    _advanced.mass.checked = advancedSettingsInputs.itemById("mass").value
                    _advanced.volume.checked = advancedSettingsInputs.itemById("volume").value
                    _advanced.surfaceArea.checked = advancedSettingsInputs.itemById("surfacearea").value
                    _advanced.com.checked = advancedSettingsInputs.itemById("com").value
                except:
                    pass
            """


class CommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self) -> None:
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs

            for joint in gm.app.activeDocument.design.rootComponent.allJoints:
                if joint.jointMotion.jointType == 0:
                    joint.isLightBulbOn = False

            if wheelTableInput.rowCount == 1:
                removeWheelInput.isEnabled = False
            else:
                removeWheelInput.isEnabled = True

            if jointTableInput.rowCount == 1:
                removeJointInput.isEnabled = False
            else:
                removeJointInput.isEnabled = True

            if gamepieceTableInput.rowCount == 1:
                removeFieldInput.isEnabled = False
            else:
                removeFieldInput.isEnabled = True

            if not addWheelInput.isEnabled:
                for wheel in _wheels:
                    wheel.component.opacity = 0.25
            else:
                gm.app.activeDocument.design.rootComponent.opacity = 1

            if not addJointInput.isEnabled:
                gm.app.activeDocument.design.rootComponent.opacity = 0.25
            else:
                gm.app.activeDocument.design.rootComponent.opacity = 1
        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


class MySelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self, maxWheelCount):
        super().__init__()
        self.maxWheelCount = maxWheelCount

    def notify(self, args):
        try:
            selectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)
            selectedJoint = adsk.fusion.Joint.cast(args.selection.entity)

            if selectedOcc:
                occurrenceList = (
                    gm.app.activeDocument.design.rootComponent.allOccurrencesByComponent(
                        selectedOcc.component
                    )
                )

                if dropdownExportMode.selectedItem.name == "Robot":
                    if duplicateSelection.value:
                        for occ in occurrenceList:
                            if occ not in _wheels:
                                self.maxWheelCount = addWheelToTable(occ)
                            else:
                                removeWheelFromTable(occ)
                    else:
                        if selectedOcc not in _wheels:
                            self.maxWheelCount = addWheelToTable(selectedOcc)
                        else:
                            removeWheelFromTable(selectedOcc)

                elif dropdownExportMode.selectedItem.name == "Field":
                    for occ in occurrenceList:
                        if occ not in _gamepieces:
                            addGamepieceToTable(occ)
                        else:
                            removeGamePieceFromTable(occ)

            elif selectedJoint:
                if selectedJoint.jointMotion.jointType == 0:
                    pass
                else:
                    if selectedJoint not in _joints:
                        addJointToTable(selectedJoint)
                    else:
                        removeJointFromTable(selectedJoint)

        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


class MyPreSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            design = adsk.fusion.Design.cast(gm.app.activeProduct)
            preSelectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)

            if preSelectedOcc and design:
                if dropdownExportMode.selectedItem.name == "Robot":
                    if preSelectedOcc in _wheels:
                        cmd.setCursor(
                            "src\Resources\MousePreselectIcons\mouse-remove-icon.png",
                            0,
                            0,
                        )
                    elif preSelectedOcc not in _wheels:
                        cmd.setCursor(
                            "src\Resources\MousePreselectIcons\mouse-add-icon.png", 0, 0
                        )

                elif dropdownExportMode.selectedItem.name == "Field":
                    if preSelectedOcc in _gamepieces:
                        cmd.setCursor(
                            "src\Resources\MousePreselectIcons\mouse-remove-icon.png",
                            0,
                            0,
                        )
                    else:
                        cmd.setCursor(
                            "src\Resources\MousePreselectIcons\mouse-add-icon.png", 0, 0
                        )
            else:
                cmd.setCursor("", 0, 0)
        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


class MyPreselectEndHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            design = adsk.fusion.Design.cast(gm.app.activeProduct)
            preSelectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)

            if preSelectedOcc and design:
                cmd.setCursor("", 0, 0)
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

    def __init__(
        self,
    ):

        super().__init__()
        self.log = logging.getLogger(
            f"{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}"
        )

    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            cmdInput = eventArgs.input
            inputs = cmdInput.commandInputs

            # gm.ui.messageBox(cmdInput.id)

            wheelSelect = inputs.itemById("wheel_select")
            jointSelect = inputs.itemById("joint_select")
            gamepieceSelect = inputs.itemById("gamepiece_select")

            jointConfig = inputs.itemById("joint_config")
            wheelConfig = inputs.itemById("wheel_config")

            # wheelTableInput = inputs.itemById("wheel_table")
            # gamepieceTableInput = inputs.itemById("gamepiece_table")

            if cmdInput.id == "mode":
                modeDropdown = adsk.core.DropDownCommandInput.cast(cmdInput)
                exportJoints = inputs.itemById("export_joints")
                weightTableInput = inputs.itemById("weight_table")
                gamepieceConfig = inputs.itemById("gamepiece_config")

                if modeDropdown.selectedItem.name == "Robot":
                    if gamepieceConfig:
                        gm.ui.activeSelections.clear()
                        gm.app.activeDocument.design.rootComponent.opacity = 1

                        gamepieceConfig.isVisible = False
                        exportJoints.isVisible = (
                            wheelConfig.isVisible
                        ) = weightTableInput.isVisible = True

                        if exportJoints.value == True:
                            jointConfig.isVisible = True
                        else:
                            jointConfig.isVisible = False

                elif modeDropdown.selectedItem.name == "Field":
                    if gamepieceConfig:
                        gm.ui.activeSelections.clear()
                        gm.app.activeDocument.design.rootComponent.opacity = 1

                        gamepieceConfig.isVisible = True
                        jointConfig.isVisible = (
                            exportJoints.isVisible
                        ) = wheelConfig.isVisible = weightTableInput.isVisible = False

            elif cmdInput.id == "export_joints":
                boolValue = adsk.core.BoolValueCommandInput.cast(cmdInput)

                if boolValue.value == True:
                    if jointConfig:
                        jointConfig.isVisible = True
                else:
                    if jointConfig:
                        jointConfig.isVisible = False

            elif cmdInput.id == "joint_config":
                for occ in gm.app.activeDocument.design.rootComponent.allOccurrences:
                    occ.component.opacity = 1

            elif cmdInput.id == "placeholder_w" or cmdInput.id == "name_w":
                cmd.setCursor("", 0, 0)
                wheelSelect.isEnabled = False

                addWheelInput.isEnabled = True

                position = int
                cmdInput_str = cmdInput.id

                if cmdInput_str == "placeholder_w":
                    position = (
                        wheelTableInput.getPosition(
                            adsk.core.ImageCommandInput.cast(cmdInput)
                        )[1]
                        - 1
                    )
                elif cmdInput_str == "name_w":
                    position = (
                        wheelTableInput.getPosition(
                            adsk.core.TextBoxCommandInput.cast(cmdInput)
                        )[1]
                        - 1
                    )

                gm.ui.activeSelections.clear()
                gm.ui.activeSelections.add(_wheels[position])

            elif (
                cmdInput.id == "blank_gp"
                or cmdInput.id == "name_gp"
                or cmdInput.id == "weight_gp"
            ):
                cmd.setCursor("", 0, 0)
                gamepieceSelect.isEnabled = False
                addFieldInput.isEnabled = True

                position = int
                cmdInput_str = cmdInput.id

                if cmdInput_str == "name_gp":
                    position = (
                        gamepieceTableInput.getPosition(
                            adsk.core.TextBoxCommandInput.cast(cmdInput)
                        )[1]
                        - 1
                    )
                elif cmdInput_str == "weight_gp":
                    position = (
                        gamepieceTableInput.getPosition(
                            adsk.core.ValueCommandInput.cast(cmdInput)
                        )[1]
                        - 1
                    )
                elif cmdInput_str == "blank_gp":
                    position = (
                        gamepieceTableInput.getPosition(
                            adsk.core.ImageCommandInput.cast(cmdInput)
                        )[1]
                        - 1
                    )
                else:
                    position = (
                        gamepieceTableInput.getPosition(
                            adsk.core.FloatSliderCommandInput.cast(cmdInput)
                        )[1]
                        - 1
                    )

                gm.ui.activeSelections.clear()
                gm.ui.activeSelections.add(_gamepieces[position])

            elif cmdInput.id == "wheel_type":
                cmd.setCursor("", 0, 0)
                wheelSelect.isEnabled = False
                addWheelInput.isEnabled = True
                position = int
                cmdInput_str = cmdInput.id

                position = (
                    wheelTableInput.getPosition(
                        adsk.core.DropDownCommandInput.cast(cmdInput)
                    )[1]
                    - 1
                )
                gm.ui.activeSelections.clear()
                gm.ui.activeSelections.add(_wheels[position])

                wheelDropdown = adsk.core.DropDownCommandInput.cast(cmdInput)

                if wheelDropdown.selectedItem.name == "Standard":
                    getPosition = wheelTableInput.getPosition(
                        adsk.core.DropDownCommandInput.cast(cmdInput)
                    )
                    iconInput = wheelTableInput.getInputAtPosition(getPosition[1], 0)
                    iconInput.imageFile = iconPaths["standard"]
                    iconInput.tooltip = "Standard wheel"

                elif wheelDropdown.selectedItem.name == "Omni":
                    getPosition = wheelTableInput.getPosition(
                        adsk.core.DropDownCommandInput.cast(cmdInput)
                    )
                    iconInput = wheelTableInput.getInputAtPosition(getPosition[1], 0)
                    iconInput.imageFile = iconPaths["omni"]
                    iconInput.tooltip = "Omni wheel"

            elif cmdInput.id == "wheel_add":
                cmd.setCursor("", 0, 0)
                gm.ui.activeSelections.clear()

                wheelSelect.isEnabled = addJointInput.isEnabled = True
                addWheelInput.isEnabled = False

            elif cmdInput.id == "joint_add":
                cmd.setCursor("", 0, 0)

                addWheelInput.isEnabled = True
                jointSelect.isEnabled = True
                addJointInput.isEnabled = False

            elif cmdInput.id == "field_add":
                cmd.setCursor("", 0, 0)
                gm.ui.activeSelections.clear()

                gamepieceSelect.isEnabled = True
                addFieldInput.isEnabled = False

            elif cmdInput.id == "wheel_delete":
                gm.ui.activeSelections.clear()

                addWheelInput.isEnabled = True

                if wheelTableInput.selectedRow == -1:
                    gm.ui.messageBox("Select a row to delete.")
                else:
                    wheel = _wheels[wheelTableInput.selectedRow - 1]
                    removeWheelFromTable(wheel)

            elif cmdInput.id == "joint_delete":
                gm.ui.activeSelections.clear()

                addJointInput.isEnabled = True
                addWheelInput.isEnabled = True

                if jointTableInput.selectedRow == -1:
                    gm.ui.messageBox("Select a row to delete.")
                else:
                    joint = _joints[jointTableInput.selectedRow - 1]
                    removeJointFromTable(joint)

            elif cmdInput.id == "field_delete":
                gm.ui.activeSelections.clear()

                addFieldInput.isEnabled = True

                if gamepieceTableInput.selectedRow == -1:
                    gm.ui.messageBox("Select a row to delete.")
                else:
                    gamepiece = _gamepieces[gamepieceTableInput.selectedRow - 1]
                    removeGamePieceFromTable(gamepiece)

            elif cmdInput.id == "wheel_select":
                cmd.setCursor("", 0, 0)

                wheelSelect.isEnabled = False
                addWheelInput.isEnabled = True
                gm.ui.activeSelections.clear()

            elif cmdInput.id == "joint_select":
                jointSelect.isEnabled = False
                addJointInput.isEnabled = True
                gm.ui.activeSelections.clear()

            elif cmdInput.id == "gamepiece_select":
                cmd.setCursor("", 0, 0)

                gamepieceSelect.isEnabled = False
                addFieldInput.isEnabled = True
                gm.ui.activeSelections.clear()

            elif cmdInput.id == "friction_override":
                boolValue = adsk.core.BoolValueCommandInput.cast(cmdInput)

                if boolValue.value == True:
                    frictionOverrideTable.isVisible = True
                else:
                    frictionOverrideTable.isVisible = False

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
            _gamepieces.clear()
            gm.ui.activeSelections.clear()
        except:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def occurrenceToken(occ):
    try:
        if type(occ) == str:
            return adsk.fusion.Design.cast(gm.app.activeProduct).findEntityByToken(occ)

        elif type(occ) == adsk.fusion.Joint:
            return occ.entityToken

        elif type(occ) == adsk.fusion.Occurrence:
            return occ.entityToken
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def addJointToTable(joint):
    try:
        _joints.append(joint)

        cmdInputs = adsk.core.CommandInputs.cast(jointTableInput.commandInputs)

        if joint.jointMotion.jointType == adsk.fusion.JointTypes.RigidJointType:
            icon = cmdInputs.addImageCommandInput(
                "placeholder", "Rigid", iconPaths["rigid"]
            )
            icon.tooltip = "Rigid joint"

        elif joint.jointMotion.jointType == adsk.fusion.JointTypes.RevoluteJointType:
            icon = cmdInputs.addImageCommandInput(
                "placeholder", "Revolute", iconPaths["revolute"]
            )
            icon.tooltip = "Revolute joint"

        elif joint.jointMotion.jointType == adsk.fusion.JointTypes.SliderJointType:
            icon = cmdInputs.addImageCommandInput(
                "placeholder", "Slider", iconPaths["slider"]
            )
            icon.tooltip = "Slider joint"

        elif joint.jointMotion.jointType == adsk.fusion.JointTypes.PlanarJointType:
            icon = cmdInputs.addImageCommandInput(
                "placeholder", "Planar", iconPaths["planar"]
            )
            icon.tooltip = "Planar joint"

        elif joint.jointMotion.jointType == adsk.fusion.JointTypes.PinSlotJointType:
            icon = cmdInputs.addImageCommandInput(
                "placeholder", "Pin Slot", iconPaths["pin_slot"]
            )
            icon.tooltip = "Pin slot joint"

        elif joint.jointMotion.jointType == adsk.fusion.JointTypes.CylindricalJointType:
            icon = cmdInputs.addImageCommandInput(
                "placeholder", "Cylindrical", iconPaths["cylindrical"]
            )
            icon.tooltip = "Cylindrical joint"

        elif joint.jointMotion.jointType == adsk.fusion.JointTypes.BallJointType:
            icon = cmdInputs.addImageCommandInput(
                "placeholder", "Ball", iconPaths["ball"]
            )
            icon.tooltip = "Ball joint"

        name = cmdInputs.addTextBoxCommandInput(
            "name_j", "Occurrence name", joint.name, 1, True
        )
        name.tooltip = "Selection set"

        jointType = cmdInputs.addDropDownCommandInput(
            "joint_type",
            "Joint Type",
            dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
        )
        jointType.listItems.add("Root", True)

        # after each additional joint added, add joint to the dropdown of all preview rows/joints
        for row in range(jointTableInput.rowCount):
            if row != 0:
                dropDown = jointTableInput.getInputAtPosition(row, 2)
                dropDown.listItems.add(_joints[-1].name, False)

        # add all parent joint options to added joint dropdown
        for j in range(len(_joints) - 1):
            jointType.listItems.add(_joints[j].name, True)

        jointType.tooltip = "Select the parent joint."

        signalType = cmdInputs.addDropDownCommandInput(
            "signal_type",
            "Signal Type",
            dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
        )
        signalType.listItems.add("PWM", True)
        signalType.listItems.add("CAN", False)
        signalType.listItems.add("Passive", False)
        signalType.tooltip = "Signal type"

        row = jointTableInput.rowCount

        jointTableInput.addCommandInput(icon, row, 0)
        jointTableInput.addCommandInput(name, row, 1)
        jointTableInput.addCommandInput(jointType, row, 2)
        jointTableInput.addCommandInput(signalType, row, 3)
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def addWheelToTable(wheel):
    try:

        """
        Potential selection count validation. 
        (as to not allow too many wheel selections)
        
        if len(_wheels) > 10: return False

        if len(_wheels) > 10:
            isValid = False
            while not isValid:
                (input, isCancelled) = gm.ui.inputBox(
                "The maximum number of occurrence selections has been reached.\n\
                Cancel the dialog or expand the maximum selection size.\n", 
                "Selection error", "10"
                )
                if isCancelled:
                    return False
                unitsManager = gm.app.activeDocument.design.unitsManager
                try:
                    realValue = unitsManager.evaluateExpression(input, unitsManager.defaultLengthUnits)
                    isValid = True
                except:
                    #adsk.core.MessageBoxIconTypes.CriticalIconType
                    #adsk.core.MessageBoxButtonTypes.OKCancelButtonType
                    isValid = False
                finally:
                    gm.ui.messageBox(str(realValue))
        """

        _wheels.append(wheel)
        cmdInputs = adsk.core.CommandInputs.cast(wheelTableInput.commandInputs)

        icon = cmdInputs.addImageCommandInput(
            "placeholder_w", "Placeholder", iconPaths["standard"]
        )

        name = cmdInputs.addTextBoxCommandInput(
            "name_w", "Occurrence name", wheel.name, 1, True
        )
        name.tooltip = "Selection set"

        wheelType = cmdInputs.addDropDownCommandInput(
            "wheel_type",
            "Wheel Type",
            dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
        )
        wheelType.listItems.add("Standard", True, "")
        wheelType.listItems.add("Omni", False, "")
        wheelType.tooltip = "Wheel type"
        wheelType.tooltipDescription = "<Br>Omni-directional wheels can be used just like regular drive wheels but they have the advantage of being able to roll freely perpendicular to the drive direction.</Br>"
        wheelType.toolClipFilename = "src\Resources\WheelIcons\omni-wheel-preview.png"

        signalType = cmdInputs.addDropDownCommandInput(
            "signal_type",
            "Signal Type",
            dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
        )
        signalType.listItems.add("PWM", True, "")
        signalType.listItems.add("CAN", False, "")
        signalType.listItems.add("Passive", False, "")
        signalType.tooltip = "Signal type"

        row = wheelTableInput.rowCount

        wheelTableInput.addCommandInput(icon, row, 0)
        wheelTableInput.addCommandInput(name, row, 1)
        wheelTableInput.addCommandInput(wheelType, row, 2)
        wheelTableInput.addCommandInput(signalType, row, 3)

        return True
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def addGamepieceToTable(gamepiece):
    try:
        _gamepieces.append(gamepiece)

        cmdInputs = adsk.core.CommandInputs.cast(gamepieceTableInput.commandInputs)
        blankIcon = cmdInputs.addImageCommandInput(
            "blank_gp", "Blank", iconPaths["blank"]
        )

        type = cmdInputs.addTextBoxCommandInput(
            "name_gp", "Occurrence name", gamepiece.name, 1, True
        )

        weight = cmdInputs.addValueInput(
            "weight_gp", "Weight Input", "", adsk.core.ValueInput.createByString("0.0")
        )

        valueList = [1]
        for i in range(20):
            valueList.append(i / 20)

        friction_coeff = cmdInputs.addFloatSliderListCommandInput(
            "friction_coeff", "", "", valueList
        )
        # friction_coeff.isFullWidth = True
        # friction_coeff.setText("0", "1 ")
        friction_coeff.valueOne = 0.5

        type.tooltip = "Type of field element."
        type.tooltipDescription = 'E.g. "Ball" or "Tote".'

        type.tooltip = "Type of field element."
        type.tooltipDescription = 'E.g. "Ball" or "Tote".'
        weight.tooltip = "Weight of field element."
        friction_coeff.tooltip = "Friction coefficient of field element."
        friction_coeff.tooltipDescription = (
            "Friction coefficients range from 0 (ice) to 1 (rubber)."
        )
        row = gamepieceTableInput.rowCount

        gamepieceTableInput.addCommandInput(blankIcon, row, 0)
        gamepieceTableInput.addCommandInput(type, row, 1)
        gamepieceTableInput.addCommandInput(weight, row, 2)
        gamepieceTableInput.addCommandInput(friction_coeff, row, 3)
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def removeWheelFromTable(wheel):
    try:
        index = _wheels.index(wheel)
        _wheels.remove(wheel)
        wheelTableInput.deleteRow(index + 1)
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def removeJointFromTable(joint):
    try:
        index = _joints.index(joint)
        _joints.remove(joint)

        jointTableInput.deleteRow(index + 1)

        for row in range(jointTableInput.rowCount):
            if row == 0:
                continue

            dropDown = jointTableInput.getInputAtPosition(row, 2)
            listItems = dropDown.listItems

            if row > index:
                if listItems.item(index + 1).isSelected:
                    listItems.item(index).isSelected = True
                    listItems.item(index + 1).deleteMe()
                else:
                    listItems.item(index + 1).deleteMe()
            else:
                if listItems.item(index).isSelected:
                    listItems.item(index - 1).isSelected = True
                    listItems.item(index).deleteMe()
                else:
                    listItems.item(index).deleteMe()

            # dropDown.listItems.clear()
            # dropDown.listItems.add("Root", False)

            # for joint in _joints:
            #    if _joints.index(joint) == row - 1: continue
            #    dropDown.listItems.add(joint.name, False)

            # dropDown.listItems.item(row - 1).isSelected = True
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def removeGamePieceFromTable(gamepiece):
    try:
        index = _gamepieces.index(gamepiece)
        _gamepieces.remove(gamepiece)
        gamepieceTableInput.deleteRow(index + 1)
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def createMeshGraphics():
    design = adsk.fusion.Design.cast(gm.app.activeProduct)

    if design:
        for occ in _wheels:
            for body in occ.bRepBodies:
                graphics = design.rootComponent.customGraphicsGroups.add()
                bodyMesh = body.meshManager.displayMeshes.bestMesh
                coords = adsk.fusion.CustomGraphicsCoordinates.create(
                    bodyMesh.nodeCoordinatesAsDouble
                )
                mesh = graphics.addMesh(
                    coords,
                    bodyMesh.nodeIndices,
                    bodyMesh.normalVectorsAsDouble,
                    bodyMesh.nodeIndices,
                )
                # redColor = adsk.core.Color.create(255,0,0,255)
                # solidColor = adsk.fusion.CustomGraphicsSolidColorEffect.create(redColor)
                # mesh.color = solidColor

                showThrough = adsk.fusion.CustomGraphicsShowThroughColorEffect.create(
                    adsk.core.Color.create(255, 0, 0, 255), 0.2
                )
                body.color = showThrough
                mesh.color = showThrough

            gm.app.activeViewport.refresh()
