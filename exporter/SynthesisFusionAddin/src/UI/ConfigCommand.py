from logging import PlaceHolder
from os import dup, fdopen, remove, strerror
from enum import Enum
from typing import Type
from proto.proto_out.joint_pb2 import Joint, JointMotion
from ..general_imports import *
from ..configure import NOTIFIED, write_configuration
from ..Analytics.alert import showAnalyticsAlert
from . import Helper, FileDialogConfig, OsHelper

from ..Parser.ParseOptions import (
    Gamepiece,
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
weightUnit = adsk.core.DropDownCommandInput.cast(None)

# selected wheels, joints, & gamepieces
_wheels = []
_joints = []
_gamepieces = []

resources = OsHelper.getOSPath(".", "src", "Resources")

iconPaths = {
    "omni": resources + os.path.join("WheelIcons", "omni-wheel-preview190x24.png"),
    "standard": resources + os.path.join("WheelIcons", "standard-wheel-preview190x24.png"),
    "mecanum": resources + os.path.join("WheelIcons", "mecanum-wheel-preview190x24.png"),
    "rigid": resources + os.path.join("JointIcons", "JointRigid", "rigid190x24.png"),
    "revolute": resources + os.path.join("JointIcons", "JointRev", "revolute190x24.png"),
    "slider": resources + os.path.join("JointIcons", "JointSlider", "slider190x24.png"),
    "cylindrical": resources + os.path.join("JointIcons", "JointCyl", "cylindrical190x24.png"),
    "pin_slot": resources + os.path.join("JointIcons", "JointPinSlot", "pin_slot190x24.png"),
    "planar": resources + os.path.join("JointIcons", "JointPlanar", "planar190x24.png"),
    "ball": resources + os.path.join("JointIcons", "JointBall", "ball190x24.png"),
    "blank": resources + "blank-preview16x16.png",
}


class JointMotions(Enum):
    RIGID = 0
    REVOLUTE = 1
    SLIDER = 2
    CYLINDRICAL = 3
    PIN_SLOT = 4
    PLANAR = 5
    BALL = 6


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

            app = adsk.core.Application.get()
            design = app.activeDocument.design

            if not Helper.check_solid_open():
                return

            global wheelTableInput
            global jointTableInput

            global addWheelInput
            global addJointInput
            global addFieldInput

            global removeWheelInput
            global removeJointInput
            global removeFieldInput

            global NOTIFIED

            if not NOTIFIED:
                showAnalyticsAlert()
                NOTIFIED = True
                write_configuration("analytics", "notified", "yes")

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
            cmd.helpFile = resources + os.path.join("HTML", "info.html")

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
                "weight_table", "Weight Table", inputs, 4, "3:2:3:1", 1
            )
            weightTableInput.tablePresentationStyle = 2

            weight_name = inputs.addStringValueInput("weight_name", "Weight")
            weight_name.value = "Weight"
            weight_name.isReadOnly = True

            auto_calc_weight = self.createBooleanInput(
                "auto_calc_weight",
                "‎",
                inputs,
                checked=False,
                tooltip="Automatically approximate the weight of your robot assembly.",
                tooltipadvanced="This may take a moment.",
                enabled=True,
                isCheckBox=False
            )
            auto_calc_weight.resourceFolder = resources + "AutoCalcWeight_icon"
            auto_calc_weight.isFullWidth = True

            populateweight = 0

            global weight_input
            weight_input = inputs.addValueInput(
                "weight_input",
                "Weight Input",
                "",
                adsk.core.ValueInput.createByString(str(populateweight)),
            )
            weight_input.tooltip = "Robot weight"

            global weight_unit
            weight_unit = inputs.addDropDownCommandInput(
                "weight_unit",
                "Weight Unit",
                adsk.core.DropDownStyles.LabeledIconDropDownStyle,
            )
            weight_unit.listItems.add("‎", True, resources + "lbs_icon")
            weight_unit.listItems.add("‎", False, resources + "kg_icon")
            weight_unit.tooltip = "Unit of mass"

            weightTableInput.addCommandInput(weight_name, 0, 0)
            weightTableInput.addCommandInput(auto_calc_weight, 0, 1)
            weightTableInput.addCommandInput(weight_input, 0, 2)
            weightTableInput.addCommandInput(weight_unit, 0, 3)

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
            Wheel Selection Table
            """
            wheelTableInput = self.createTableInput(
                "wheel_table",
                "Wheel Table",
                wheel_inputs,
                4,
                "1:4:2:2",
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
            Automatically Select Duplicates
            """
            global duplicateSelection
            duplicateSelection = self.createBooleanInput(
                "duplicate_selection",
                "Select Duplicates",
                wheel_inputs,
                checked=True,
                tooltip="Select duplicate wheel components.",
                tooltipadvanced="""
                When this is checked, all duplicate occurrences will be automatically selected.
                <br>This feature may fail in some circumstances where duplicates connot by found.</br>
                """,
                enabled=True,
            )

            """
            Joint Configuration
            """
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

            addJointInput.isEnabled = \
            removeJointInput.isEnabled = True

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
                if (
                    joint.jointMotion.jointType == JointMotions.REVOLUTE.value
                    or joint.jointMotion.jointType == JointMotions.SLIDER.value
                ):

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
            global weight_unit_f
            weight_unit_f = gamepiece_inputs.addDropDownCommandInput(
                "weight_unit_f",
                "Unit of Mass",
                adsk.core.DropDownStyles.LabeledIconDropDownStyle,
            )
            weight_unit_f.listItems.add("lbs", True)
            weight_unit_f.listItems.add("kg", False)
            weight_unit_f.tooltip = "Configure the unit of mass for a gamepiece."

            """
            Gamepiece Selection Table
            """
            global gamepieceTableInput

            gamepieceTableInput = self.createTableInput(
                "gamepiece_table",
                "Gamepiece",
                gamepiece_inputs,
                4,
                "1:10:4:12",
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

            frictionOverrideTable = self.createTableInput(
                "friction_override_table",
                "",
                physics_settings,
                2,
                "1:2",
                1,
                columnSpacing=25,
            )
            frictionOverrideTable.tablePresentationStyle = 2
            frictionOverrideTable.isFullWidth = True

            frictionOverride = self.createBooleanInput(
                "friction_override",
                "",
                physics_settings,
                checked=False,
                tooltip="Manually override the default friction values on the bodies in the assembly.",
                enabled=True,
                isCheckBox=False,
            )
            frictionOverride.resourceFolder = resources + "FrictionOverride_icon"
            frictionOverride.isFullWidth = True

            valueList = [1]
            for i in range(20):
                valueList.append(i / 20)

            global frictionCoeff
            frictionCoeff = physics_settings.addFloatSliderListCommandInput(
                "friction_coeff_override", "Friction Coefficient", "", valueList
            )
            frictionCoeff.isVisible = False
            frictionCoeff.valueOne = 0.5
            frictionCoeff.tooltip = "Friction coefficient of field element."
            frictionCoeff.tooltipDescription = (
                "Friction coefficients range from 0 (ice) to 1 (rubber)."
            )

            frictionOverrideTable.addCommandInput(frictionOverride, 0, 0)
            frictionOverrideTable.addCommandInput(frictionCoeff, 0, 1)

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

        onInputChanged = ConfigureCommandInputChanged(cmd)
        cmd.inputChanged.add(onInputChanged)
        gm.handlers.append(onInputChanged)

        global onExecutePreview
        onExecutePreview = CommandExecutePreviewHandler()
        cmd.executePreview.add(onExecutePreview)
        gm.handlers.append(onExecutePreview)

        global onSelect
        onSelect = MySelectHandler(cmd)
        cmd.select.add(onSelect)
        gm.handlers.append(onSelect)

        onPreSelect = MyPreSelectHandler(cmd)
        cmd.preSelect.add(onPreSelect)
        gm.handlers.append(onPreSelect)

        onPreSelectEnd = MyPreselectEndHandler(cmd)
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

                _exportWheels = [] # all selected wheels, formatted for parseOptions
                _exportJoints = [] # all selected joints, formatted for parseOptions
                _exportGamepieces = [] # TODO work on the code to populate Gamepiece

                for row in range(wheelTableInput.rowCount):
                    if row == 0:
                        continue

                    wheelTypeIndex = wheelTableInput.getInputAtPosition(
                        row, 2
                    ).selectedItem.index # This must be either 0 or 1 for standard or omni

                    signalTypeIndex = wheelTableInput.getInputAtPosition(
                        row, 3
                    ).selectedItem.index

                    _exportWheels.append(
                        _Wheel(_wheels[row-1].entityToken, wheelTypeIndex, signalTypeIndex)
                        #, onSelect.jointed_occ[row-1])
                    )

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

                    if parentJointIndex == 0:
                        _exportJoints.append(
                            _Joint(
                                _joints[row - 1].entityToken,
                                JointParentType.ROOT,
                                signalTypeIndex,
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

                    #for wheel in _exportWheels:
                        # find some way to get joint
                        # 1. Compare Joint occurrence1 to wheel.occurrence_token
                        # 2. if true set the parent to Root

                    _exportJoints.append(
                        _Joint(
                            _joints[row - 1].entityToken, parentJointToken, signalTypeIndex
                        )
                    )

                for row in range(gamepieceTableInput.rowCount):
                    if row == 0:
                        continue

                    weightValue = gamepieceTableInput.getInputAtPosition(
                        row, 2
                    ).value

                    frictionValue = gamepieceTableInput.getInputAtPosition(
                        row, 3
                    ).valueOne

                    _exportGamepieces.append(
                        Gamepiece(_gamepieces[row - 1].entityToken, weightValue, frictionValue)
                    )

                options = ParseOptions(
                    savepath,
                    name,
                    version,
                    materials=renderer,
                    joints=_exportJoints,
                    wheels=_exportWheels,
                    gamepieces=_exportGamepieces,
                )

                if options.parse(False):
                    # success
                    return
                else:
                    self.log.error(
                        f"Error: \n\t{name} could not be written to \n {savepath}"
                    )
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

            #jointType = onSelect.selectedJoint.jointMotion.jointType
            #if (
            #    jointType != JointMotions.REVOLUTE.value
            #    or jointType != JointMotions.SLIDER.value
            #):
            #    type = JointMotions(jointType).name
            #    message = type.lower().replace("_", " ") + " joint types are not supported"
            #    
            #    eventArgs.executeFailed = True
            #    eventArgs.executeFailedMessage = message

            #if eventArgs.firingEvent.name == "":

            #gm.ui.messageBox(eventArgs.objectType)

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

            if not addWheelInput.isEnabled or not removeWheelInput:
                for wheel in _wheels:
                    wheel.component.opacity = 0.25
                    createTextGraphics(wheel)

                gm.app.activeViewport.refresh()
            else:
                gm.app.activeDocument.design.rootComponent.opacity = 1
                for group in gm.app.activeDocument.design.rootComponent.customGraphicsGroups:
                    group.deleteMe()

            if not addJointInput.isEnabled or not removeJointInput:
                gm.app.activeDocument.design.rootComponent.opacity = 0.15
            else:
                gm.app.activeDocument.design.rootComponent.opacity = 1

            if not addFieldInput.isEnabled or not removeFieldInput:
                for gamepiece in _gamepieces:
                    gamepiece.component.opacity = 0.15
            else:
                gm.app.activeDocument.design.rootComponent.opacity = 1
        except AttributeError:
            pass
        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


class MySelectHandler(adsk.core.SelectionEventHandler):

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.occurrences = [] # all jointed occurrences in assembly
        
        self.allWheelPreselections = [] # all child occurrences of selections
        self.allGamepiecePreselections = [] # all child gamepiece occurrences of selections
        self.jointed_occ = [] # all joints connected to wheels

        self.selectedOcc = None
        self.selectedJoint = None

        for joint in gm.app.activeDocument.design.rootComponent.allJoints:
            if joint.jointMotion.jointType != adsk.fusion.JointTypes.RevoluteJointType:
                continue
            self.occurrences.extend((joint.occurrenceOne, joint.occurrenceTwo))

    def traverseAssembly(self, child_occurrences): # recursive traversal to check if children are jointed
        for occ in child_occurrences:
            if occ in self.occurrences:
                return occ # return jointed occurrence

            if occ.childOccurrences: # if occurrence has children, traverse sub-tree
                self.traverseAssembly(occ.childOccurrences)
        return None # no jointed occurrence found

    def wheelParent(self, occ):
        try:
            parent = occ.assemblyContext
            if parent == None: # no parent occurrence
                return occ # return what is selected

            if occ in self.occurrences: # what is selected is directly jointed, no need to do child traversal
                return occ # return what is selected

            while parent != None:
                returned = self.traverseAssembly(parent.childOccurrences)
                if returned != None: # jointed occurrence found in tree traversal
                    return occ.assemblyContext # return jointed occurrence parent
                parent = parent.assemblyContext

            return occ # no jointed occurrence found, return what is selected
        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
        
    def notify(self, args):
        try:
            eventArgs = adsk.core.SelectionEventArgs.cast(args)

            self.selectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)
            self.selectedJoint = adsk.fusion.Joint.cast(args.selection.entity)

            if self.selectedOcc:
                if dropdownExportMode.selectedItem.name == "Robot":
                    parent = self.wheelParent(self.selectedOcc)
                    occurrenceList = (
                        gm.app.activeDocument.design.rootComponent.allOccurrencesByComponent(
                            parent.component
                        )
                    )

                    if duplicateSelection.value:
                        for occ in occurrenceList:
                            if occ not in _wheels:
                                addWheelToTable(occ)
                            else:
                                removeWheelFromTable(_wheels.index(occ))
                    else:
                        if parent not in _wheels:
                            addWheelToTable(parent)
                        else:
                            removeWheelFromTable(_wheels.index(parent))

                elif dropdownExportMode.selectedItem.name == "Field":
                    occurrenceList = (
                        gm.app.activeDocument.design.rootComponent.allOccurrencesByComponent(
                            self.selectedOcc.component
                        )
                    )
                    for occ in occurrenceList:
                        if occ not in _gamepieces:
                            addGamepieceToTable(occ)
                        else:
                            removeGamePieceFromTable(_gamepieces.index(occ))

            elif self.selectedJoint:
                jointType = self.selectedJoint.jointMotion.jointType
                if (
                    jointType == JointMotions.REVOLUTE.value
                    or jointType == JointMotions.SLIDER.value
                ):

                    if self.selectedJoint not in _joints:
                        addJointToTable(self.selectedJoint)
                    else:
                        removeJointFromTable(self.selectedJoint)
        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


class MyPreSelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def notify(self, args):
        try:
            design = adsk.fusion.Design.cast(gm.app.activeProduct)
            preSelectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)

            if not preSelectedOcc or not design:
                self.cmd.setCursor("", 0, 0)
                return

            if preSelectedOcc and design:
                if dropdownExportMode.selectedItem.name == "Robot":
                    if preSelectedOcc.entityToken in onSelect.allWheelPreselections:
                    #if preSelectedOcc in _wheels:
                        self.cmd.setCursor(
                            resources + os.path.join("MousePreselectIcons", "mouse-remove-icon.png"),
                            0,
                            0,
                        )
                    else:
                        self.cmd.setCursor(
                            resources + os.path.join("MousePreselectIcons", "mouse-add-icon.png"),
                            0,
                            0,
                        )

                elif dropdownExportMode.selectedItem.name == "Field":
                    if preSelectedOcc.entityToken in onSelect.allGamepiecePreselections:
                        self.cmd.setCursor(
                            resources + os.path.join("MousePreselectIcons", "mouse-remove-icon.png"),
                            0,
                            0,
                        )
                    else:
                        self.cmd.setCursor(
                            resources + os.path.join("MousePreselectIcons", "mouse-add-icon.png"),
                            0,
                            0,
                        ) 
        except:
            if gm.ui:
                gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


class MyPreselectEndHandler(adsk.core.SelectionEventHandler):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def notify(self, args):
        try:
            design = adsk.fusion.Design.cast(gm.app.activeProduct)
            preSelectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)

            if preSelectedOcc and design:
                self.cmd.setCursor("", 0, 0)
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

    def __init__(self, cmd):
        super().__init__()
        self.log = logging.getLogger(
            f"{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}"
        )
        self.cmd = cmd
        self.allWeights = [None, None]
        self.isLbs = True

    def reset(self):
        self.cmd.setCursor("", 0, 0)
        gm.ui.activeSelections.clear()

    def weight(self, isLbs=True): # maybe add a progress dialog??
        if gm.app.activeDocument.design:
            rootComponent = gm.app.activeDocument.design.rootComponent
            physical = rootComponent.getPhysicalProperties(
                adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
            )
            value = float

            self.allWeights[0] = round(
                physical.mass * 2.2046226218, 2
            )

            self.allWeights[1] = round(
                physical.mass, 2
            )

            if isLbs:
                value = self.allWeights[0]
            else:
                value = self.allWeights[1]

            value = round(
                value, 2
            )
            return value

    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            cmdInput = eventArgs.input
            inputs = cmdInput.commandInputs

            # gm.ui.messageBox(cmdInput.id)

            wheelSelect = inputs.itemById("wheel_select")
            jointSelect = inputs.itemById("joint_select")
            gamepieceSelect = inputs.itemById("gamepiece_select")

            position = int

            if cmdInput.id == "mode":
                modeDropdown = adsk.core.DropDownCommandInput.cast(cmdInput)

                weightTableInput = inputs.itemById("weight_table")
                gamepieceConfig = inputs.itemById("gamepiece_config")
                wheelConfig = inputs.itemById("wheel_config")
                jointConfig = inputs.itemById("joint_config")

                if modeDropdown.selectedItem.name == "Robot":
                    if gamepieceConfig:
                        gm.ui.activeSelections.clear()
                        gm.app.activeDocument.design.rootComponent.opacity = 1

                        gamepieceConfig.isVisible = False
                        weightTableInput.isVisible = True

                        addFieldInput.isEnabled = \
                        wheelConfig.isVisible = \
                        jointConfig.isVisible = True

                elif modeDropdown.selectedItem.name == "Field":
                    if gamepieceConfig:
                        gm.ui.activeSelections.clear()
                        gm.app.activeDocument.design.rootComponent.opacity = 1

                        addWheelInput.isEnabled = \
                        addJointInput.isEnabled = \
                        gamepieceConfig.isVisible = True

                        jointConfig.isVisible = \
                        wheelConfig.isVisible = \
                        weightTableInput.isVisible = False

            elif cmdInput.id == "joint_config":
                gm.app.activeDocument.design.rootComponent.opacity = 1

            elif cmdInput.id == "placeholder_w" or cmdInput.id == "name_w":
                self.reset()

                wheelSelect.isEnabled = False
                addWheelInput.isEnabled = True

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

                gm.ui.activeSelections.add(_wheels[position])

            elif (
                cmdInput.id == "blank_gp"
                or cmdInput.id == "name_gp"
                or cmdInput.id == "weight_gp"
                ):
                self.reset()

                gamepieceSelect.isEnabled = False
                addFieldInput.isEnabled = True

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

                gm.ui.activeSelections.add(_gamepieces[position])

            elif cmdInput.id == "wheel_type":
                self.reset()

                wheelSelect.isEnabled = False
                addWheelInput.isEnabled = True

                cmdInput_str = cmdInput.id
                position = (
                    wheelTableInput.getPosition(
                        adsk.core.DropDownCommandInput.cast(cmdInput)
                    )[1]
                    - 1
                )
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

                elif wheelDropdown.selectedItem.name == "Mecanum":
                    getPosition = wheelTableInput.getPosition(
                        adsk.core.DropDownCommandInput.cast(cmdInput)
                    )
                    iconInput = wheelTableInput.getInputAtPosition(getPosition[1], 0)
                    iconInput.imageFile = iconPaths["mecanum"]
                    iconInput.tooltip = "Mecanum wheel"

                gm.ui.activeSelections.add(_wheels[position])

            elif cmdInput.id == "wheel_add":
                self.reset()

                wheelSelect.isEnabled = addJointInput.isEnabled = True
                addWheelInput.isEnabled = False

            elif cmdInput.id == "joint_add":
                self.reset()

                addWheelInput.isEnabled = \
                jointSelect.isEnabled = True
                addJointInput.isEnabled = False

            elif cmdInput.id == "field_add":
                self.reset()

                gamepieceSelect.isEnabled = True
                addFieldInput.isEnabled = False

            elif cmdInput.id == "wheel_delete":
                gm.ui.activeSelections.clear()

                addWheelInput.isEnabled = True
                if wheelTableInput.selectedRow == -1 or wheelTableInput.selectedRow == 0:
                    wheelTableInput.selectedRow = wheelTableInput.rowCount-1
                    gm.ui.messageBox("Select a row to delete.")
                else:
                    index = wheelTableInput.selectedRow - 1
                    removeWheelFromTable(index)

            elif cmdInput.id == "joint_delete":
                gm.ui.activeSelections.clear()

                addJointInput.isEnabled = True
                addWheelInput.isEnabled = True

                if jointTableInput.selectedRow == -1 or jointTableInput.selectedRow == 0:
                    jointTableInput.selectedRow = jointTableInput.rowCount-1
                    gm.ui.messageBox("Select a row to delete.")
                else:
                    joint = _joints[jointTableInput.selectedRow - 1]
                    removeJointFromTable(joint)

            elif cmdInput.id == "field_delete":
                gm.ui.activeSelections.clear()

                addFieldInput.isEnabled = True

                if gamepieceTableInput.selectedRow == -1 or gamepieceTableInput.selectedRow == 0:
                    gamepieceTableInput.selectedRow = gamepieceTableInput.rowCount-1
                    gm.ui.messageBox("Select a row to delete.")
                else:
                    index = gamepieceTableInput.selectedRow - 1
                    removeGamePieceFromTable(index)

            elif cmdInput.id == "wheel_select":
                self.reset()

                wheelSelect.isEnabled = False
                addWheelInput.isEnabled = True

            elif cmdInput.id == "joint_select":
                self.reset()

                jointSelect.isEnabled = False
                addJointInput.isEnabled = True

            elif cmdInput.id == "gamepiece_select":
                self.reset()

                gamepieceSelect.isEnabled = False
                addFieldInput.isEnabled = True

            elif cmdInput.id == "friction_override":
                boolValue = adsk.core.BoolValueCommandInput.cast(cmdInput)

                if boolValue.value == True:
                    frictionCoeff.isVisible = True
                else:
                    frictionCoeff.isVisible = False

            elif cmdInput.id == "weight_unit":
                unitDropdown = adsk.core.DropDownCommandInput.cast(cmdInput)
                if unitDropdown.selectedItem.index == 0:
                    self.isLbs = True
                else:
                    self.isLbs = False

            elif cmdInput.id == "auto_calc_weight":
                button = adsk.core.BoolValueCommandInput.cast(cmdInput)
                
                if button.value == True:
                    if self.allWeights.count(None) == 2:
                        if self.isLbs:
                            self.allWeights[0] = self.weight()
                            weight_input.value = self.allWeights[0]
                        else:
                            self.allWeights[1] = self.weight(False)
                            weight_input.value = self.allWeights[1]
                    else:
                        if weight_input.value != self.allWeights[0] or weight_input.value != self.allWeights[1] or not weight_input.isValidExpression:
                            if self.isLbs:
                                weight_input.value = float(self.allWeights[0])
                            else:
                                weight_input.value = float(self.allWeights[1])      
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
        jointType.isFullWidth = True
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
        signalType.listItems.add("‎", True, resources + "PWM_icon")
        signalType.listItems.add("‎", False, resources + "CAN_icon")
        signalType.listItems.add("‎", False, resources + "PASSIVE_icon")
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
    def addPreselections(child_occurrences):
        for occ in child_occurrences:
            onSelect.allWheelPreselections.append(occ.entityToken)
            
            if occ.childOccurrences:
                addPreselections(occ.childOccurrences)

    try:
        if wheel.childOccurrences:    
            addPreselections(wheel.childOccurrences)
        else:
            onSelect.allWheelPreselections.append(wheel.entityToken)

        _wheels.append(wheel)
        cmdInputs = adsk.core.CommandInputs.cast(wheelTableInput.commandInputs)

        icon = cmdInputs.addImageCommandInput(
            "placeholder_w", "Placeholder", iconPaths["standard"]
        )

        name = cmdInputs.addTextBoxCommandInput(
            "name_w", "Occurrence name", wheel.name, 1, True
        )
        name.tooltip = wheel.name

        wheelType = cmdInputs.addDropDownCommandInput(
            "wheel_type",
            "Wheel Type",
            dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
        )
        wheelType.listItems.add("Standard", True, "")
        wheelType.listItems.add("Omni", False, "")
        wheelType.listItems.add("Mecanum", False, "")
        wheelType.tooltip = "Wheel type"
        wheelType.tooltipDescription = "<Br>Omni-directional wheels can be used just like regular drive wheels but they have the advantage of being able to roll freely perpendicular to the drive direction.</Br>"
        wheelType.toolClipFilename = resources + os.path.join("WheelIcons", "omni-wheel-preview.png")

        signalType = cmdInputs.addDropDownCommandInput(
            "signal_type",
            "Signal Type",
            dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
        )
        signalType.isFullWidth = True
        signalType.listItems.add("‎", True, resources + "PWM_icon")
        signalType.listItems.add("‎", False, resources + "CAN_icon")
        signalType.listItems.add("‎", False, resources + "PASSIVE_icon")
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
    def addPreselections(child_occurrences):
        for occ in child_occurrences:
            onSelect.allGamepiecePreselections.append(occ.entityToken)
            
            if occ.childOccurrences:
                addPreselections(occ.childOccurrences)

    try:
        if gamepiece.childOccurrences:
            addPreselections(gamepiece.childOccurrences)
        else:
            onSelect.allGamepiecePreselections.append(gamepiece.entityToken)

        _gamepieces.append(gamepiece)
        cmdInputs = adsk.core.CommandInputs.cast(gamepieceTableInput.commandInputs)
        blankIcon = cmdInputs.addImageCommandInput(
            "blank_gp", "Blank", iconPaths["blank"]
        )

        type = cmdInputs.addTextBoxCommandInput(
            "name_gp", "Occurrence name", gamepiece.name, 1, True
        )

        physical = gamepiece.component.getPhysicalProperties(
                adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
        )

        value = round(
            physical.mass, 2
        )

        weight = cmdInputs.addValueInput(
            "weight_gp", "Weight Input", "", adsk.core.ValueInput.createByString(str(value))
        )

        valueList = [1]
        for i in range(20):
            valueList.append(i / 20)

        friction_coeff = cmdInputs.addFloatSliderListCommandInput(
            "friction_coeff", "", "", valueList
        )
        friction_coeff.valueOne = 0.5

        type.tooltip = "Type of field element."

        type.tooltip = gamepiece.name
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

def removeWheelFromTable(index: int) -> None:
    wheel = _wheels[index]

    def removePreselections(child_occurrences):
        for occ in child_occurrences:
            onSelect.allWheelPreselections.remove(occ.entityToken)
            
            if occ.childOccurrences:
                removePreselections(occ.childOccurrences)

    try:
        if wheel.childOccurrences:
            removePreselections(wheel.childOccurrences)
        else:
            onSelect.allWheelPreselections.remove(wheel.entityToken)

        del _wheels[index]
        wheelTableInput.deleteRow(index + 1)
    except IndexError:
        pass
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

def removeJointFromTable(joint: adsk.fusion.Joint) -> None:
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
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

def removeGamePieceFromTable(index: int) -> None:
    gamepiece = _gamepieces[index]

    def removePreselections(child_occurrences):
        for occ in child_occurrences:
            onSelect.allGamepiecePreselections.remove(occ.entityToken)
            
            if occ.childOccurrences:
                removePreselections(occ.childOccurrences)
    try:
        if gamepiece.childOccurrences:
            removePreselections(_gamepieces[index].childOccurrences)
        else:
            onSelect.allGamepiecePreselections.remove(gamepiece.entityToken)

        del _gamepieces[index]
        gamepieceTableInput.deleteRow(index + 1)
    except IndexError:
        pass
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))

def createTextGraphics(wheel:adsk.fusion.Occurrence) -> None:

    try:
        design = adsk.fusion.Design.cast(gm.app.activeProduct)

        boundingBox = wheel.boundingBox # occurrence bounding box
        min = boundingBox.minPoint.asArray() # [x, y, z] min coords
        max = boundingBox.maxPoint.asArray() # [x, y, z] max coords

        length = max[0]-min[0] # length of bounding box
        width = max[1]-min[1] # width of bounding box
        height = max[2]-min[2] # height of bounding box

        if design:
            graphics = design.rootComponent.customGraphicsGroups.add()
            matrix = adsk.core.Matrix3D.create()
            matrix.translation = adsk.core.Vector3D.create(max[0], min[1], min[2])#max[2]-(height/2))

            billBoard = adsk.fusion.CustomGraphicsBillBoard.create(adsk.core.Point3D.create(0, 0, 0))
            billBoard.billBoardStyle = adsk.fusion.CustomGraphicsBillBoardStyles.ScreenBillBoardStyle

            text = str(_wheels.index(wheel)+1)
            graphicsText = graphics.addText(text, 'Arial Black', 6, matrix)
            graphicsText.billBoarding = billBoard # make the text follow the camera
            graphicsText.isSelectable = False # make it non-selectable
            graphicsText.cullMode = adsk.fusion.CustomGraphicsCullModes.CustomGraphicsCullBack
            graphicsText.color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0, 255, 0, 255)) # bright-green color
                    
            """
            Code to create a bounding box around a wheel occurrence.
            """
            allIndices = [
                min[0],         min[1],         max[2],
                min[0],         min[1],         min[2],
                max[0],         min[1],         min[2],

                #min[0],         min[1],         min[2],
                #min[0]+length,  min[1],         min[2],
                #min[0]+length,  min[1]+width,   min[2],
                #min[0],         min[1]+width,   min[2],
                #min[0],         min[1],         min[2],

                #max[0]-length,  max[1]-width,   max[2],
                #max[0],         max[1]-width,   max[2],
                #max[0],         max[1],         max[2],
                #max[0]-length,  max[1],         max[2],
                #max[0]-length,  max[1]-width,   max[2],

                #max[0],         max[1]-width,   max[2],
                #min[0]+length,  min[1],         min[2],
                #min[0]+length,  min[1]+width,   min[2],
                #max[0],         max[1],         max[2],
                #max[0]-length,  max[1],         max[2],
                #min[0],         min[1]+width,   min[2],
            ]

            indexPairs = []
             
            for index in range(0, len(allIndices), 3):
                if index > len(allIndices)-5:
                    continue
                for i in allIndices[index:index+6]:
                    indexPairs.append(i)

            coords = adsk.fusion.CustomGraphicsCoordinates.create(
                indexPairs
            )
            line = graphics.addLines(
                coords,
                [],
                False,
            )
            line.color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0, 255, 0, 255)) # bright-green color
            line.weight = 2
            line.isScreenSpaceLineStyle = False
            line.isSelectable = False
    except:
        if gm.ui:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))