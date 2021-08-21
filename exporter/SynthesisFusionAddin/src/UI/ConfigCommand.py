from os import dup, fdopen, remove, strerror
from enum import Enum
from typing import Type
from ..general_imports import *
from ..configure import NOTIFIED, write_configuration
from ..Analytics.alert import showAnalyticsAlert
from . import Helper, FileDialogConfig, OsHelper, CustomGraphics, TableUtilities

from ..Parser.ParseOptions import (
    Gamepiece,
    Mode,
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

import adsk.core, adsk.fusion, traceback, logging
from types import SimpleNamespace

try:
    from proto.proto_out.joint_pb2 import Joint, JointMotion
except:
    pass

"""
    - File to generate all the frontend command inputs and GUI elements
    - links the Configuration Command seen when pressing the button from the Addins Panel
"""

# joint & wheel table globals
wheelTableInput = None
jointTableInput = None
gamepieceTableInput = None

# add and remove buttons globals
addWheelInput = None
removeWheelInput = None
addJointInput = None
removeJointIpnut = None
addFieldInput = None
removeFieldInput = None

duplicateSelection = None
dropdownExportMode = None
weightUnit = None

ROOT_COMP = gm.app.activeDocument.design.rootComponent

"""
    - These lists are very crucial.
    - This contain all of the selected:
        wheels (adsk.fusion.Occurrence), 
        joints (adsk.fusion.Joint) and 
        gamepieces (adsk.fusion.Occurrence)
"""
WheelListGlobal = []
JointListGlobal = []
GamepieceListGlobal = []

resources = OsHelper.getOSPath(".", "src", "Resources")

"""
Dictionary to store all icon path names in this file. All path strings are OS-dependent
"""
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
    """### Enum with joint motions and integer associations

    Args:
        Enum (enum.Enum)
    """
    RIGID = 0
    REVOLUTE = 1
    SLIDER = 2
    CYLINDRICAL = 3
    PIN_SLOT = 4
    PLANAR = 5
    BALL = 6


class ConfigureCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """### Start the Command Input Object and define all of the input groups to create our ParserOptions object.

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
            cmd.okButtonText = "Export" # replace default OK text with "export"

            inputs_root = cmd.commandInputs

            # ====================================== GENERAL TAB ======================================
            """
            Creates the general tab.
                - Parent container for all the command inputs in the tab.
            """
            inputs = inputs_root.addTabCommandInput(
                "general_settings", "General"
            ).children

            
            # ~~~~~~~~~~~~~~~~ HELP FILE ~~~~~~~~~~~~~~~~
            """
            Sets the small "i" icon in bottom left of the panel.
                - This is an HTML file that has a script to redirect to exporter workflow tutorial.
            """
            cmd.helpFile = resources + os.path.join("HTML", "info.html")


            # ~~~~~~~~~~~~~~~~ EXPORT MODE ~~~~~~~~~~~~~~~~
            """
            Dropdown to choose whether to export robot or field element
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

            
            # ~~~~~~~~~~~~~~~~ WEIGHT CONFIGURATION ~~~~~~~~~~~~~~~~
            """
            Table for weight config. 
                - Used this to align multiple commandInputs on the same row
            """
            weightTableInput = self.createTableInput(
                "weight_table",
                "Weight Table",
                inputs,
                4,
                "3:2:2:1",
                1,
            )
            weightTableInput.tablePresentationStyle = 2 # set transparent background for table

            weight_name = inputs.addStringValueInput("weight_name", "Weight")
            weight_name.value = "Weight"
            weight_name.isReadOnly = True

            auto_calc_weight = self.createBooleanInput(
                "auto_calc_weight",
                "‎",
                inputs,
                checked=False,
                tooltip="Approximate the weight of your robot assembly.",
                tooltipadvanced="<i>This may take a moment.</i>",
                enabled=True,
                isCheckBox=False
            )
            auto_calc_weight.resourceFolder = resources + "AutoCalcWeight_icon"
            auto_calc_weight.isFullWidth = True

            global weight_input
            weight_input = inputs.addValueInput(
                "weight_input",
                "Weight Input",
                "",
                adsk.core.ValueInput.createByString("0.0"),
            )
            weight_input.tooltip = "Robot weight"
            weight_input.tooltipDescription = "<i>(in pounds)</i>"

            global weight_unit
            weight_unit = inputs.addDropDownCommandInput(
                "weight_unit",
                "Weight Unit",
                adsk.core.DropDownStyles.LabeledIconDropDownStyle,
            )
            weight_unit.listItems.add("‎", True, resources + "lbs_icon") # add listdropdown mass options
            weight_unit.listItems.add("‎", False, resources + "kg_icon") # add listdropdown mass options
            weight_unit.tooltip = "Unit of mass"
            weight_unit.tooltipDescription = "<i>Configure the unit of mass for your robot.</i>"

            weightTableInput.addCommandInput(weight_name, 0, 0) # add command inputs to table
            weightTableInput.addCommandInput(auto_calc_weight, 0, 1) # add command inputs to table
            weightTableInput.addCommandInput(weight_input, 0, 2) # add command inputs to table
            weightTableInput.addCommandInput(weight_unit, 0, 3) # add command inputs to table

            
            # ~~~~~~~~~~~~~~~~ WHEEL CONFIGURATION ~~~~~~~~~~~~~~~~
            """
            Wheel configuration command input group
                - Container for wheel selection Table
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

            
            # WHEEL SELECTION TABLE
            """
            All selected wheel occurrences appear here.
            """
            wheelTableInput = self.createTableInput(
                "wheel_table",
                "Wheel Table",
                wheel_inputs,
                4,
                "1:4:2:2",
                50,
            )

            addWheelInput = wheel_inputs.addBoolValueInput("wheel_add", "Add", False) # add button

            removeWheelInput = wheel_inputs.addBoolValueInput( # remove button
                "wheel_delete", "Remove", False
            )

            addWheelInput.tooltip = "Add a wheel component" # tooltips
            removeWheelInput.tooltip = "Remove a wheel component"

            wheelSelectInput = wheel_inputs.addSelectionInput(
                "wheel_select",
                "Selection",
                "Select the wheels in your drive-train assembly.",
            )
            wheelSelectInput.addSelectionFilter("Occurrences") # filter selection to only occurrences

            wheelSelectInput.setSelectionLimits(0) # no selection count limit
            wheelSelectInput.isEnabled = False
            wheelSelectInput.isVisible = False

            wheelTableInput.addToolbarCommandInput(addWheelInput) # add buttons to the toolbar
            wheelTableInput.addToolbarCommandInput(removeWheelInput) # add buttons to the toolbar

            wheelTableInput.addCommandInput( # create textbox input using helper (component name)
                self.createTextBoxInput(
                    "name_header", "Name", wheel_inputs, "Component name", bold=False
                ),
                0,
                1,
            )

            wheelTableInput.addCommandInput(
                self.createTextBoxInput( # wheel type header
                    "parent_header",
                    "Parent",
                    wheel_inputs,
                    "Wheel type",
                    background="#d9d9d9", # textbox header background color
                ),
                0,
                2,
            )

            wheelTableInput.addCommandInput(
                self.createTextBoxInput( # Signal type header
                    "signal_header",
                    "Signal",
                    wheel_inputs,
                    "Signal type",
                    background="#d9d9d9", # textbox header background color
                ),
                0,
                3,
            )


            # AUTOMATICALLY SELECT DUPLICATES
            """
            Select duplicates?
                - creates a BoolValueCommandInput
            """
            global duplicateSelection
            duplicateSelection = self.createBooleanInput( # create bool value command input using helper
                "duplicate_selection",
                "Select Duplicates",
                wheel_inputs,
                checked=True,
                tooltip="Select duplicate wheel components.",
                tooltipadvanced="""
                When this is checked, all duplicate occurrences will be automatically selected.
                <br>This feature may fail in some circumstances where duplicates connot by found.</br>
                """, # advanced tooltip
                enabled=True,
            )


            # ~~~~~~~~~~~~~~~~ JOINT CONFIGURATION ~~~~~~~~~~~~~~~~
            """
            Joint configuration group. Container for joint selection table
            """
            jointConfig = inputs.addGroupCommandInput(
                "joint_config", "Joint Configuration"
            )
            jointConfig.isExpanded = False
            jointConfig.isVisible = True
            jointConfig.tooltip = "Select and define joint occurrences in your assembly."

            joint_inputs = jointConfig.children


            # JOINT SELECTION TABLE
            """
            All selection joints appear here.
            """
            jointTableInput = self.createTableInput( # create tablecommandinput using helper
                "joint_table",
                "Joint Table",
                joint_inputs,
                4,
                "1:2:2:2",
                50,
            )

            addJointInput = joint_inputs.addBoolValueInput("joint_add", "Add", False) # add button

            removeJointInput = joint_inputs.addBoolValueInput( # remove button
                "joint_delete", "Remove", False
            )

            addJointInput.isEnabled = \
            removeJointInput.isEnabled = True

            addJointInput.tooltip = "Add a joint selection" # tooltips
            removeJointInput.tooltip = "Remove a joint selection"

            jointSelectInput = joint_inputs.addSelectionInput(
                "joint_select",
                "Selection",
                "Select a joint in your drive-train assembly.",
            )

            jointSelectInput.addSelectionFilter("Joints") # only allow joint selection
            jointSelectInput.setSelectionLimits(0) # set no selection count limits
            jointSelectInput.isEnabled = False 
            jointSelectInput.isVisible = False # make selection box invisible

            jointTableInput.addToolbarCommandInput(addJointInput) # add bool inputs to the toolbar
            jointTableInput.addToolbarCommandInput(removeJointInput) # add bool inputs to the toolbar

            jointTableInput.addCommandInput(
                self.createTextBoxInput( # create a textBoxCommandInput for the table header (Joint Motion), using helper
                    "motion_header",
                    "Motion",
                    joint_inputs,
                    "Motion",
                    bold=False,
                ),
                0,
                0,
            )

            jointTableInput.addCommandInput(
                self.createTextBoxInput( # textBoxCommandInput for table header (Joint Name), using helper
                    "name_header", "Name", joint_inputs, "Joint name", bold=False
                ),
                0,
                1,
            )

            jointTableInput.addCommandInput(
                self.createTextBoxInput( # another header using helper
                    "parent_header",
                    "Parent",
                    joint_inputs,
                    "Parent joint",
                    background="#d9d9d9", # background color
                ),
                0,
                2,
            )

            jointTableInput.addCommandInput(
                self.createTextBoxInput( # another header using helper
                    "signal_header",
                    "Signal",
                    joint_inputs,
                    "Signal type",
                    background="#d9d9d9", # back color
                ),
                0,
                3,
            )

            for joint in ROOT_COMP.allJoints:
                if (
                    joint.jointMotion.jointType == JointMotions.REVOLUTE.value
                    or joint.jointMotion.jointType == JointMotions.SLIDER.value
                ):

                    addJointToTable(joint)


            # ~~~~~~~~~~~~~~~~ GAMEPIECE CONFIGURATION ~~~~~~~~~~~~~~~~
            """
            Gamepiece group command input, isVisible=False by default
                - Container for gamepiece selection table
            """
            gamepieceConfig = inputs.addGroupCommandInput(
                "gamepiece_config", "Gamepiece Configuration"
            )
            gamepieceConfig.isExpanded = True
            gamepieceConfig.isVisible = False
            gamepieceConfig.tooltip = "Select and define the gamepieces in your field."
            gamepiece_inputs = gamepieceConfig.children


            # GAMEPIECE MASS CONFIGURATION
            """
            Mass unit dropdown and calculation for gamepiece elements
            """
            weightTableInput_f = self.createTableInput(
                "weight_table_f", "Weight Table", gamepiece_inputs, 3, "6:2:1", 1
            )
            weightTableInput_f.tablePresentationStyle = 2 # set to clear background

            weight_name_f = gamepiece_inputs.addStringValueInput("weight_name", "Weight")
            weight_name_f.value = "Unit of Mass"
            weight_name_f.isReadOnly = True

            global auto_calc_weight_f
            auto_calc_weight_f = self.createBooleanInput( # CALCULATE button
                "auto_calc_weight_f",
                "‎",
                gamepiece_inputs,
                checked=False,
                tooltip="Approximate the weight of all your selected gamepieces.",
                enabled=True,
                isCheckBox=False
            )
            auto_calc_weight_f.resourceFolder = resources + "AutoCalcWeight_icon"
            auto_calc_weight_f.isFullWidth = True

            global weight_unit_f
            weight_unit_f = gamepiece_inputs.addDropDownCommandInput(
                "weight_unit_f",
                "Unit of Mass",
                adsk.core.DropDownStyles.LabeledIconDropDownStyle,
            )
            weight_unit_f.listItems.add("‎", True, resources + "lbs_icon") # add listdropdown mass options
            weight_unit_f.listItems.add("‎", False, resources + "kg_icon") # add listdropdown mass options
            weight_unit_f.tooltip = "Unit of mass"
            weight_unit_f.tooltipDescription = "<i>Configure the unit of mass for a gamepiece.</i>"

            weightTableInput_f.addCommandInput(weight_name_f, 0, 0) # add command inputs to table
            weightTableInput_f.addCommandInput(auto_calc_weight_f, 0, 1) # add command inputs to table
            weightTableInput_f.addCommandInput(weight_unit_f, 0, 2) # add command inputs to table

            
            # GAMEPIECE SELECTION TABLE
            """
            All selected gamepieces appear here
            """
            global gamepieceTableInput

            gamepieceTableInput = self.createTableInput(
                "gamepiece_table",
                "Gamepiece",
                gamepiece_inputs,
                4,
                "1:8:4:12",
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


            # ====================================== ADVANCED TAB ======================================
            """
            Creates the advanced tab, which is the parent container for internal command inputs
            """
            advancedSettings = inputs_root.addTabCommandInput(
                "advanced_settings", "Advanced"
            )
            advancedSettings.tooltip = "Additional Advanced Settings to change how your model will be translated into Unity."
            a_input = advancedSettings.children


            # ~~~~~~~~~~~~~~~~ PHYSICS SETINGS ~~~~~~~~~~~~~~~~
            """
            Physics settings group command
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
                "<i>Friction coefficients range from 0 (ice) to 1 (rubber).</i>"
            )

            frictionOverrideTable.addCommandInput(frictionOverride, 0, 0)
            frictionOverrideTable.addCommandInput(frictionCoeff, 0, 1)


            # ~~~~~~~~~~~~~~~~ JOINT SETTINGS ~~~~~~~~~~~~~~~~
            """
            Joint settings group command
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


            # ~~~~~~~~~~~~~~~~ CONTROLLER SETTINGS ~~~~~~~~~~~~~~~~
            """
            Controller settings group command
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

            # clear all selections before instantiating handlers.
            gm.ui.activeSelections.clear()


            # ====================================== EVENT HANDLERS ======================================
            """
            Instantiating all the event handlers
            """
            onExecute = ConfigureCommandExecuteHandler(
                json.dumps(previous, default=lambda o: o.__dict__, sort_keys=True, indent=1),
                previous.filePath,
            )
            cmd.execute.add(onExecute)
            gm.handlers.append(onExecute)

            global onInputChanged
            onInputChanged = ConfigureCommandInputChanged(cmd, weightTableInput)
            cmd.inputChanged.add(onInputChanged)
            gm.handlers.append(onInputChanged)

            global onExecutePreview
            onExecutePreview = CommandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            gm.handlers.append(onExecutePreview)

            global onSelect
            onSelect = MySelectHandler()
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

        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
                "Failed:\n{}".format(traceback.format_exc())
            )

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
        """### Simple helper to generate all of the options for me to create a boolean command input

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
        try:
            _input = inputs.addBoolValueInput(_id, name, isCheckBox)
            _input.value = checked
            _input.isEnabled = enabled
            _input.tooltip = tooltip
            _input.tooltipDescription = tooltipadvanced
            return _input
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}.createBooleanInput()").error(
                "Failed:\n{}".format(traceback.format_exc())
            )

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
        ) -> adsk.core.TableCommandInput:
        """### Simple helper to generate all the TableCommandInput options.

        Args:
            _id (str): unique ID of command 
            name (str): displayed name
            inputs (adsk.core.CommandInputs): parent command input container
            columns (int): column count
            ratio (str): column width ratio
            maxRows (int): the maximum number of displayed rows possible
            minRows (int, optional): the minumum number of displayed rows. Defaults to 1.
            columnSpacing (int, optional): spacing in between the columns, in pixels. Defaults to 0.
            rowSpacing (int, optional): spacing in between the rows, in pixels. Defaults to 0.

        Returns:
            adsk.core.TableCommandInput: created tableCommandInput
        """
        try:
            _input = inputs.addTableCommandInput(_id, name, columns, ratio)
            _input.minimumVisibleRows = minRows
            _input.maximumVisibleRows = maxRows
            _input.columnSpacing = columnSpacing
            _input.rowSpacing = rowSpacing
            return _input
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}.createTableInput()").error(
                "Failed:\n{}".format(traceback.format_exc())
            )

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
        tooltip="",
        advanced_tooltip="",
        ) -> adsk.core.TextBoxCommandInput:
        """### Helper to generate a textbox input from inputted options.

        Args:
            _id (str): unique ID
            name (str): displayed name
            inputs (adsk.core.CommandInputs): parent command input container
            text (str): the user-visible text in command
            italics (bool, optional): is italics? Defaults to True.
            bold (bool, optional): isBold? Defaults to True.
            fontSize (int, optional): fontsize. Defaults to 10.
            alignment (str, optional): HTML style alignment (left, center, right). Defaults to "center".
            rowCount (int, optional): number of rows in textbox. Defaults to 1.
            read (bool, optional): read only? Defaults to True.
            background (str, optional): background color (HTML color names or hex) Defaults to "whitesmoke".

        Returns:
            adsk.core.TextBoxCommandInput: newly created textBoxCommandInput
        """    
        try:
            i = ["", ""]
            b = ["", ""]

            if bold:
                b[0] = "<b>"
                b[1] = "</b>"
            if italics:
                i[0] = "<i>"
                i[1] = "</i>"

            # simple wrapper for html formatting
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
            _input.tooltip = tooltip
            _input.tooltipDescription = advanced_tooltip
            return _input
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}.createTextBoxInput()").error(
                "Failed:\n{}".format(traceback.format_exc())
            )


class ConfigureCommandExecuteHandler(adsk.core.CommandEventHandler):
    """### Called when Ok is pressed confirming the export to Unity.

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
                _robotWeight = float
                _mode = Mode

                """
                Loops through all rows in the wheel table to extract all the input values
                """
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
                        _Wheel(
                            WheelListGlobal[row-1].entityToken,
                            wheelTypeIndex,
                            signalTypeIndex,
                            onSelect.wheel_joints[row-1] # GUID of wheel joint. if no joint found, default to None
                        )
                    )

                """
                Loops through all rows in the joint table to extract the input values
                """
                for row in range(jointTableInput.rowCount):
                    if row == 0:
                        continue

                    parentJointIndex = jointTableInput.getInputAtPosition(
                        row, 2
                    ).selectedItem.index # parent joint index, int

                    signalTypeIndex = jointTableInput.getInputAtPosition(
                        row, 3
                    ).selectedItem.index # signal type index, int

                    parentJointToken = ""

                    if parentJointIndex == 0:
                        _exportJoints.append(
                            _Joint(
                                JointListGlobal[row - 1].entityToken,
                                JointParentType.ROOT,
                                signalTypeIndex, # index of selected signal in dropdown
                            )  # parent joint GUID
                        )
                        continue
                    elif parentJointIndex < row:
                        parentJointToken = JointListGlobal[
                            parentJointIndex - 1
                        ].entityToken  # parent joint GUID, str
                    else:
                        parentJointToken = JointListGlobal[
                            parentJointIndex + 1
                        ].entityToken  # parent joint GUID, str

                    #for wheel in _exportWheels:
                        # find some way to get joint
                        # 1. Compare Joint occurrence1 to wheel.occurrence_token
                        # 2. if true set the parent to Root

                    _exportJoints.append(
                        _Joint(
                            JointListGlobal[row - 1].entityToken, parentJointToken, signalTypeIndex
                        )
                    )
                
                """
                Loops through all rows in the gamepiece table to extract the input values
                """
                for row in range(gamepieceTableInput.rowCount):
                    if row == 0:
                        continue

                    weightValue = gamepieceTableInput.getInputAtPosition(
                        row, 2
                    ).value # weight/mass input, float

                    if weight_unit_f.selectedItem.index == 0:
                        weightValue /= 2.2046226218

                    frictionValue = gamepieceTableInput.getInputAtPosition(
                        row, 3
                    ).valueOne # friction value, float

                    _exportGamepieces.append(
                        Gamepiece(GamepieceListGlobal[row - 1].entityToken, weightValue, frictionValue)
                    )
                
                """
                Robot Weight
                """
                if weight_unit.selectedItem.index == 0:
                    _robotWeight = float(weight_input.value) / 2.2046226218
                else:
                    _robotWeight = float(weight_input.value)

                """
                Export Mode
                """
                if dropdownExportMode.selectedItem.index == 0:
                    _mode = Mode.Synthesis
                elif dropdownExportMode.selectedItem.index == 1:
                    _mode = Mode.SynthesisField

                options = ParseOptions(
                    savepath,
                    name,
                    version,
                    materials=renderer,
                    joints=_exportJoints,
                    wheels=_exportWheels,
                    gamepieces=_exportGamepieces,
                    weight=_robotWeight,
                    mode=_mode
                )

                if options.parse(False):
                    # success
                    return
                else:
                    self.log.error(
                        f"Error: \n\t{name} could not be written to \n {savepath}"
                    )
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
            "Failed:\n{}".format(traceback.format_exc())
        )


class CommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    """### Gets an event that is fired when the command has completed gathering the required input and now needs to perform a preview.

    Args:
        adsk (CommandEventHandler): Command event handler that a client derives from to handle events triggered by a CommandEvent.
    """
    def __init__(self) -> None:
        super().__init__()

    def notify(self, args):
        """Notify member called when a command event is triggered

        Args:
            args (CommandEventArgs): command event argument
        """
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs

            if wheelTableInput.rowCount <= 1:
                removeWheelInput.isEnabled = False
            else:
                removeWheelInput.isEnabled = True

            if jointTableInput.rowCount <= 1:
                removeJointInput.isEnabled = False
            else:
                removeJointInput.isEnabled = True

            if gamepieceTableInput.rowCount <= 1:
                removeFieldInput.isEnabled = \
                auto_calc_weight_f.isEnabled = False
            else:
                removeFieldInput.isEnabled = \
                auto_calc_weight_f.isEnabled = True

            if not addWheelInput.isEnabled or not removeWheelInput:
                for wheel in WheelListGlobal:
                    wheel.component.opacity = 0.25
                    CustomGraphics.createTextGraphics(wheel, WheelListGlobal)

                gm.app.activeViewport.refresh()
            else:
                ROOT_COMP.opacity = 1
                for group in ROOT_COMP.customGraphicsGroups:
                    group.deleteMe()

            if not addJointInput.isEnabled or not removeJointInput:
                ROOT_COMP.opacity = 0.15
            else:
                ROOT_COMP.opacity = 1

            if not addFieldInput.isEnabled or not removeFieldInput:
                for gamepiece in GamepieceListGlobal:
                    gamepiece.component.opacity = 0.25
                    CustomGraphics.createTextGraphics(gamepiece, GamepieceListGlobal)
            else:
                ROOT_COMP.opacity = 1
        except AttributeError:
            pass
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
            "Failed:\n{}".format(traceback.format_exc())
        )


class MySelectHandler(adsk.core.SelectionEventHandler):
    """### Event fires when the user selects an entity.
    ##### This is different from a preselection where an entity is shown as being available for selection as the mouse passes over the entity. This is the actual selection where the user has clicked the mouse on the entity.

    Args: SelectionEventHandler
    """
    def __init__(self):
        super().__init__()
        self.allWheelPreselections = [] # all child occurrences of selections
        self.allGamepiecePreselections = [] # all child gamepiece occurrences of selections
        
        self.selectedOcc = None # selected occurrence (if there is one)
        self.selectedJoint = None # selected joint (if there is one)

        self.wheel_joints = []

    def traverseAssembly(self, child_occurrences: adsk.fusion.OccurrenceList, jointedOcc: dict): # recursive traversal to check if children are jointed
        """### Traverses the entire occurrence hierarchy to find a match (jointed occurrence) in self.occurrence

        Args:
            child_occurrences (adsk.fusion.OccurrenceList): a list of child occurrences

        Returns:
            occ (Occurrence): if a match is found, return the jointed occurrence
            None: if no match is found
        """
        try:
            for occ in child_occurrences:
                for joint, value in jointedOcc.items():
                    if occ in value:
                        return [joint, occ] # occurrence that is jointed
                
                if occ.childOccurrences: # if occurrence has children, traverse sub-tree
                    self.traverseAssembly(occ.childOccurrences, jointedOcc)
            return None # no jointed occurrence found
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}.traverseAssembly()").error(
            "Failed:\n{}".format(traceback.format_exc())
        )

    def wheelParent(self, occ: adsk.fusion.Occurrence):
        """### Identify an occurrence that encompasses the entire wheel component.
        
        Process:

            1. if the selection has no parent, return the selection.

            2. if the selection is directly jointed, return the selection.

            3. else keep climbing the occurrence tree until no parent is found.

            - if a jointed occurrence is in the tree, return the selection parent.

            - if no jointed occurrence was found, return the selection.

        Args:
            occ (Occurrence): The selected child occurrence

        Returns:
            occ (Occurrence): Wheel parent
        """
        try:
            parent = occ.assemblyContext
            jointedOcc = {} # dictionary with all jointed occurrences

            try:
                for joint in occ.joints:
                    if joint.jointMotion.jointType == adsk.fusion.JointTypes.RevoluteJointType:
                        #gm.ui.messageBox("Selection is directly jointed.\nReturning selection.\n\n" + "Occurrence:\n--> " + occ.name + "\nJoint:\n--> " + joint.name)
                        return [joint.entityToken, occ]
            except:
                for joint in occ.component.joints:
                    if joint.jointMotion.jointType == adsk.fusion.JointTypes.RevoluteJointType:
                        #gm.ui.messageBox("Selection is directly jointed.\nReturning selection.\n\n" + "Occurrence:\n--> " + occ.name + "\nJoint:\n--> " + joint.name)
                        return [joint.entityToken, occ]

            if parent == None: # no parent occurrence
                #gm.ui.messageBox("Selection has no parent occurrence.\nReturning selection.\n\n" + "Occurrence:\n--> " + occ.name + "\nJoint:\n--> NONE")
                return [None, occ] # return what is selected

            for joint in ROOT_COMP.allJoints:
                if joint.jointMotion.jointType != adsk.fusion.JointTypes.RevoluteJointType:
                    continue
                jointedOcc[joint.entityToken] = [joint.occurrenceOne, joint.occurrenceTwo]

            parentLevel = 0 # the number of nodes above the one selected
            returned = None # the returned value of traverseAssembly()
            parentOccurrence = occ # the parent occurrence that will be returned
            treeParent = parent # each parent that will traverse up in algorithm.
            
            while treeParent != None: # loops until reaches top-level component
                returned = self.traverseAssembly(treeParent.childOccurrences, jointedOcc)

                if returned != None:
                    for i in range(parentLevel):
                        parentOccurrence = parentOccurrence.assemblyContext
                    
                    #gm.ui.messageBox("Joint found.\nReturning parent occurrence.\n\n" + "Selected occurrence:\n--> " + occ.name + "\nParent:\n--> " + parentOccurrence.name + "\nJoint:\n--> " + returned[0] + "\nNodes above selection:\n--> " + str(parentLevel))
                    return [returned[0], parentOccurrence]
                
                parentLevel += 1
                treeParent = treeParent.assemblyContext
            #gm.ui.messageBox("No jointed occurrence found.\nReturning selection.\n\n" + "Occurrence:\n--> " + occ.name + "\nJoint:\n--> NONE")
            return [None, occ] # no jointed occurrence found, return what is selected
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}.wheelParent()").error(
            "Failed:\n{}".format(traceback.format_exc())
        )
            #gm.ui.messageBox("Selection's component has no referenced joints.\nReturning selection.\n\n" + "Occurrence:\n--> " + occ.name + "\nJoint:\n--> NONE")
            return [None, occ]
        
    def updateJointTable(self, jointGUID):
        try:
            #gm.ui.messageBox(jointGUID)
            jointObject = gm.app.activeDocument.design.findEntityByToken(jointGUID)

            index = JointListGlobal.index(jointObject[0])
            textBox = jointTableInput.getInputAtPosition(index+1, 1)

            textBox.formattedText += " [<b><i>wheel</i></b>]"
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
            "Failed:\n{}".format(traceback.format_exc())
        )
    
    def notify(self, args):
        """### Notify member is called when a selection event is triggered.

        Args:
            args (SelectionEventArgs): A selection event argument
        """
        try:
            eventArgs = adsk.core.SelectionEventArgs.cast(args)

            self.selectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)
            self.selectedJoint = adsk.fusion.Joint.cast(args.selection.entity)

            if self.selectedOcc:
                if dropdownExportMode.selectedItem.name == "Robot":
                    returned = self.wheelParent(self.selectedOcc)
                    
                    wheelJoint = returned[0]  # joint GUID
                    wheelParent = returned[1]

                    #self.updateJointTable(wheelJoint)
                    self.wheel_joints.append(wheelJoint)

                    occurrenceList = (
                        ROOT_COMP.allOccurrencesByComponent(
                            wheelParent.component
                        )
                    )

                    if duplicateSelection.value:
                        for occ in occurrenceList:
                            if occ not in WheelListGlobal:
                                addWheelToTable(occ)
                            else:
                                removeWheelFromTable(WheelListGlobal.index(occ))
                    else:
                        if wheelParent not in WheelListGlobal:
                            addWheelToTable(wheelParent)
                        else:
                            removeWheelFromTable(WheelListGlobal.index(wheelParent))

                elif dropdownExportMode.selectedItem.name == "Field":
                    occurrenceList = (
                        ROOT_COMP.allOccurrencesByComponent(
                            self.selectedOcc.component
                        )
                    )
                    for occ in occurrenceList:
                        if occ not in GamepieceListGlobal:
                            addGamepieceToTable(occ)
                        else:
                            removeGamePieceFromTable(GamepieceListGlobal.index(occ))

            elif self.selectedJoint:
                jointType = self.selectedJoint.jointMotion.jointType
                if (
                    jointType == JointMotions.REVOLUTE.value
                    or jointType == JointMotions.SLIDER.value
                ):

                    if self.selectedJoint not in JointListGlobal:
                        addJointToTable(self.selectedJoint)
                    else:
                        removeJointFromTable(self.selectedJoint)
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
            "Failed:\n{}".format(traceback.format_exc())
        )


class MyPreSelectHandler(adsk.core.SelectionEventHandler):
    """### Event fires when a entity preselection is made (mouse hovering).
    ##### When a user is selecting geometry, they move the mouse over the model and if the entity the mouse is currently over is valid for selection it will highlight indicating that it can be selected. This process of determining what is available for selection and highlighting it is referred to as the "preselect" behavior.

    Args: SelectionEventHandler
    """

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
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
            "Failed:\n{}".format(traceback.format_exc())
        )


class MyPreselectEndHandler(adsk.core.SelectionEventHandler):
    """### Event fires when the mouse is moved away from an entity that was in a preselect state.

    Args: SelectionEventArgs
    """
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def notify(self, args):
        try:
            design = adsk.fusion.Design.cast(gm.app.activeProduct)
            preSelectedOcc = adsk.fusion.Occurrence.cast(args.selection.entity)

            if preSelectedOcc and design:
                self.cmd.setCursor("", 0, 0) # if preselection ends (mouse off of design), reset the mouse icon to default
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
            "Failed:\n{}".format(traceback.format_exc())
        )


class FullMassCalculuation():
    def __init__(self):
        self.progressDialog = gm.app.userInterface.createProgressDialog()

        self.totalMass = 0.0
        self.currentBRepCount = 0
        self.bRepBodyCount = ROOT_COMP.bRepBodies.count

        self.currentOccCount = 0
        self.occurrenceCount = ROOT_COMP.allOccurrences.count
        self.currentValue = 0

        self.totalIterations = self.bRepBodyCount + self.occurrenceCount + 1

        self.progressDialog.title = "Calculating Assembly Mass"
        self.progressDialog.minimumValue = 0
        self.progressDialog.maximumValue = self.totalIterations
        self.progressDialog.show(
                "Mass Calculation", "Currently on %v of %m", 0, self.totalIterations
            )

    def _format(self):
        out = f"Mass: \t {round(self.totalMass, 2)} \n"
        out += f"\t BRepBodies: \t[ {self.currentBRepCount} / {self.bRepBodyCount}]\n"
        out += f"\t Occurrences: \t[ {self.currentOccCount} / {self.occurrenceCount} ]\n"
        out += f"{self.currentMessage}"

        return out

    def addBRep(self, name=None):
        self.currentValue += 1
        self.currentBRepCount += 1
        self.currentMessage = f"BRepBody {name}"
        self.update()

    def addOccurrence(self, name=None):
        self.currentValue += 1
        self.currentOccCount += 1
        self.currentMessage = f"Occurrence {name}"
        self.update()

    def update(self):
        self.progressDialog.message = self._format()
        self.progressDialog.progressValue = self.currentValue
        self.value = self.currentValue

    def wasCancelled(self) -> bool:
        return self.progressDialog.wasCancelled

    def bRepMassInRoot(self):
        for body in ROOT_COMP.bRepBodies:
            physical = body.getPhysicalProperties(
                adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
            )
            self.totalMass += physical.mass
            self.addBRep(body.name)

    def traverseOccurrenceHierarchy(self):
        for occ in ROOT_COMP.allOccurrences:
            comp = occ.component

            for body in comp.bRepBodies:
                physical = body.getPhysicalProperties(
                    adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
                )
                self.totalMass += physical.mass
            self.addOccurrence(occ.name)

    def getTotalMass(self):
        return self.totalMass


class ConfigureCommandInputChanged(adsk.core.InputChangedEventHandler):
    """### Gets an event that is fired whenever an input value is changed.
        - Button pressed, selection made, switching tabs, etc...

    Args: InputChangedEventHandler
    """
    def __init__(self, cmd, weightTableInput):
        super().__init__()
        self.log = logging.getLogger(
            f"{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}"
        )
        self.cmd = cmd
        self.allWeights = [None, None] # [lbs, kg]
        self.isLbs = True
        self.isLbs_f = True
        self.weightTableInput = weightTableInput

    def reset(self):
        """### Process:
            - Reset the mouse icon to default
            - Clear active selections 
        """
        try:
            self.cmd.setCursor("", 0, 0)
            gm.ui.activeSelections.clear()
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}.reset()").error(
            "Failed:\n{}".format(traceback.format_exc())
        )

    def weight(self, isLbs=True): # maybe add a progress dialog??
        """### Get the total design weight using the predetermined units.

        Args:
            isLbs (bool, optional): Is selected mass unit pounds? Defaults to True.

        Returns:
            value (float): weight value in specified unit
        """
        try:
            if gm.app.activeDocument.design:
                
                massCalculation = FullMassCalculuation()
                massCalculation.bRepMassInRoot()
                massCalculation.traverseOccurrenceHierarchy()
                
                totalMass = massCalculation.getTotalMass()
                value = float

                self.allWeights[0] = round(
                    totalMass * 2.2046226218, 2
                )

                self.allWeights[1] = round(
                    totalMass, 2
                )

                if isLbs:
                    value = self.allWeights[0]
                else:
                    value = self.allWeights[1]

                value = round( # round weight to 2 decimals places
                    value, 2
                )
                return value
        except:
            gm.ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
            #logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}.weight()").error(
            #"Failed:\n{}".format(traceback.format_exc())
        #)

    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            cmdInput = eventArgs.input
            inputs = cmdInput.commandInputs

            wheelSelect = inputs.itemById("wheel_select")
            jointSelect = inputs.itemById("joint_select")
            gamepieceSelect = inputs.itemById("gamepiece_select")

            #gm.ui.messageBox(cmdInput.id)

            position = int

            if cmdInput.id == "mode":
                modeDropdown = adsk.core.DropDownCommandInput.cast(cmdInput)

                weightTableInput = inputs.itemById("weight_table")
                gamepieceConfig = inputs.itemById("gamepiece_config")
                wheelConfig = inputs.itemById("wheel_config")
                jointConfig = inputs.itemById("joint_config")

                if modeDropdown.selectedItem.index == 0:
                    if gamepieceConfig:
                        gm.ui.activeSelections.clear()
                        ROOT_COMP.opacity = 1

                        gamepieceConfig.isVisible = False
                        weightTableInput.isVisible = True

                        addFieldInput.isEnabled = \
                        wheelConfig.isVisible = \
                        jointConfig.isVisible = True

                elif modeDropdown.selectedItem.index == 1:
                    if gamepieceConfig:
                        gm.ui.activeSelections.clear()
                        ROOT_COMP.opacity = 1

                        addWheelInput.isEnabled = \
                        addJointInput.isEnabled = \
                        gamepieceConfig.isVisible = True

                        jointConfig.isVisible = \
                        wheelConfig.isVisible = \
                        weightTableInput.isVisible = False

            elif cmdInput.id == "joint_config":
                ROOT_COMP.opacity = 1

            elif (cmdInput.id == "placeholder_w"
                or cmdInput.id == "name_w"
                or cmdInput.id == "signal_type_w"
                ):
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
                elif cmdInput_str == "signal_type_w":
                    position = (
                        wheelTableInput.getPosition(
                            adsk.core.DropDownCommandInput.cast(cmdInput)
                        )[1]
                        - 1
                    )

                gm.ui.activeSelections.add(WheelListGlobal[position])

            elif (cmdInput.id == "placeholder"
                or cmdInput.id == "name_j"
                or cmdInput.id == "joint_parent"
                or cmdInput.id == "signal_type"
                ):
                self.reset()
                jointSelect.isEnabled = False
                addJointInput.isEnabled = True

            elif (cmdInput.id == "blank_gp"
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

                gm.ui.activeSelections.add(GamepieceListGlobal[position])

            elif cmdInput.id == "wheel_type_w":
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

                gm.ui.activeSelections.add(WheelListGlobal[position])

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
                    joint = JointListGlobal[jointTableInput.selectedRow - 1]
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
                weightInput = self.weightTableInput.getInputAtPosition(0, 2)
                if unitDropdown.selectedItem.index == 0:
                    self.isLbs = True

                    weightInput.tooltipDescription = "<i>(in pounds)</i>"
                elif unitDropdown.selectedItem.index == 1:
                    self.isLbs = False

                    weightInput.tooltipDescription = "<i>(in kilograms)</i>"

            elif cmdInput.id == "weight_unit_f":
                unitDropdown = adsk.core.DropDownCommandInput.cast(cmdInput)
                if unitDropdown.selectedItem.index == 0:
                    self.isLbs_f = True

                    for row in range(gamepieceTableInput.rowCount):
                        if row == 0:
                            continue
                        weightInput = gamepieceTableInput.getInputAtPosition(row, 2)
                        weightInput.tooltipDescription = "<i>(in pounds)</i>"
                elif unitDropdown.selectedItem.index == 1:
                    self.isLbs_f = False

                    for row in range(gamepieceTableInput.rowCount):
                        if row == 0:
                            continue
                        weightInput = gamepieceTableInput.getInputAtPosition(row, 2)
                        weightInput.tooltipDescription = "<i>(in kilograms)</i>"

            elif cmdInput.id == "auto_calc_weight":
                button = adsk.core.BoolValueCommandInput.cast(cmdInput)
                
                if button.value == True: # CALCULATE button pressed
                    if self.allWeights.count(None) == 2: # if button is pressed for the first time
                        if self.isLbs: # if pounds unit selected
                            self.allWeights[0] = self.weight()
                            weight_input.value = self.allWeights[0]
                        else: # if kg unit selected
                            self.allWeights[1] = self.weight(False)
                            weight_input.value = self.allWeights[1]
                    else: # if a mass value has already been configured
                        if weight_input.value != self.allWeights[0] or weight_input.value != self.allWeights[1] or not weight_input.isValidExpression:
                            if self.isLbs:
                                weight_input.value = self.allWeights[0]
                            else:
                                weight_input.value = self.allWeights[1]
            
            elif cmdInput.id == "auto_calc_weight_f":
                button = adsk.core.BoolValueCommandInput.cast(cmdInput)
                
                if button.value == True: # CALCULATE button pressed
                    if self.isLbs_f:
                        for row in range(gamepieceTableInput.rowCount):
                            if row == 0:
                                continue
                            weightInput = gamepieceTableInput.getInputAtPosition(row, 2)
                            physical = GamepieceListGlobal[row-1].component.getPhysicalProperties(
                                adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
                            )
                            value = round(
                                physical.mass * 2.2046226218, 2
                            )
                            weightInput.value = value

                    else:
                        for row in range(gamepieceTableInput.rowCount):
                            if row == 0:
                                continue
                            weightInput = gamepieceTableInput.getInputAtPosition(row, 2)
                            physical = GamepieceListGlobal[row-1].component.getPhysicalProperties(
                                adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
                            )
                            value = round(
                                physical.mass, 2
                            )
                            weightInput.value = value
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
            "Failed:\n{}".format(traceback.format_exc())
        )


class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    """### Gets this event that is fired when the command is destroyed. Globals are released and active selections are cleared (when exiting the panel).
        - OK or Cancel button pressed...

    Args: CommandEventHandler
    """
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            WheelListGlobal.clear()
            JointListGlobal.clear()
            GamepieceListGlobal.clear()

            gm.ui.activeSelections.clear()
        except:
            logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.{self.__class__.__name__}").error(
            "Failed:\n{}".format(traceback.format_exc())
        )


def addJointToTable(joint: adsk.fusion.Joint) -> None:
    """### Adds a Joint object to its global list and joint table.

    Args:
        joint (adsk.fusion.Joint): Joint object to be added
    """
    try:
        JointListGlobal.append(joint)

        cmdInputs = adsk.core.CommandInputs.cast(jointTableInput.commandInputs)

        # joint type icons
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

        # joint name
        name = cmdInputs.addTextBoxCommandInput(
            "name_j", "Occurrence name", joint.name, 1, True
        )
        name.tooltip = joint.name

        jointType = cmdInputs.addDropDownCommandInput(
            "joint_parent",
            "Joint Type",
            dropDownStyle=adsk.core.DropDownStyles.LabeledIconDropDownStyle,
        )
        jointType.isFullWidth = True
        jointType.listItems.add("Root", True)

        # after each additional joint added, add joint to the dropdown of all preview rows/joints
        for row in range(jointTableInput.rowCount):
            if row != 0:
                dropDown = jointTableInput.getInputAtPosition(row, 2)
                dropDown.listItems.add(JointListGlobal[-1].name, False)

        # add all parent joint options to added joint dropdown
        for j in range(len(JointListGlobal) - 1):
            jointType.listItems.add(JointListGlobal[j].name, False)

        jointType.tooltip = "Possible parent joints"
        jointType.tooltipDescription = "<i>The root component is usually the parent.</i>"

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
        logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.addJointToTable()").error(
        "Failed:\n{}".format(traceback.format_exc())
    )

def addWheelToTable(wheel: adsk.fusion.Occurrence) -> None:
    """### Adds a wheel occurrence to its global list and wheel table.

    Args:
        wheel (adsk.fusion.Occurrence): wheel Occurrence object to be added.
    """
    try:
        def addPreselections(child_occurrences):
            for occ in child_occurrences:
                onSelect.allWheelPreselections.append(occ.entityToken)

                if occ.childOccurrences:
                    addPreselections(occ.childOccurrences)

        if wheel.childOccurrences:    
            addPreselections(wheel.childOccurrences)
        else:
            onSelect.allWheelPreselections.append(wheel.entityToken)

        WheelListGlobal.append(wheel)
        cmdInputs = adsk.core.CommandInputs.cast(wheelTableInput.commandInputs)

        icon = cmdInputs.addImageCommandInput(
            "placeholder_w", "Placeholder", iconPaths["standard"]
        )

        name = cmdInputs.addTextBoxCommandInput(
            "name_w", "Occurrence name", wheel.name, 1, True
        )
        name.tooltip = wheel.name

        wheelType = cmdInputs.addDropDownCommandInput(
            "wheel_type_w",
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
            "signal_type_w",
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

    except:
        logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.addWheelToTable()").error(
        "Failed:\n{}".format(traceback.format_exc())
    )

def addGamepieceToTable(gamepiece: adsk.fusion.Occurrence) -> None:
    """### Adds a gamepiece occurrence to its global list and gamepiece table.

    Args:
        gamepiece (adsk.fusion.Occurrence): Gamepiece occurrence to be added
    """
    try:
        def addPreselections(child_occurrences):
            for occ in child_occurrences:
                onSelect.allGamepiecePreselections.append(occ.entityToken)
                
                if occ.childOccurrences:
                    addPreselections(occ.childOccurrences)

        if gamepiece.childOccurrences:
            addPreselections(gamepiece.childOccurrences)
        else:
            onSelect.allGamepiecePreselections.append(gamepiece.entityToken)

        GamepieceListGlobal.append(gamepiece)
        cmdInputs = adsk.core.CommandInputs.cast(gamepieceTableInput.commandInputs)
        blankIcon = cmdInputs.addImageCommandInput(
            "blank_gp", "Blank", iconPaths["blank"]
        )

        type = cmdInputs.addTextBoxCommandInput(
            "name_gp", "Occurrence name", gamepiece.name, 1, True
        )

        physical = gamepiece.getPhysicalProperties(
                adsk.fusion.CalculationAccuracy.LowCalculationAccuracy
        )

        # check if dropdown unit is kg or lbs. bool value taken from ConfigureCommandInputChanged
        massUnitInString = ""
        if onInputChanged.isLbs_f:
            value = round(
                physical.mass * 2.2046226218, 2 # lbs
            )
            massUnitInString = "<i>(in pounds)</i>"
        else:
            value = round(
                physical.mass, 2 # kg
            )
            massUnitInString = "<i>(in kilograms)</i>"
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
        
        type.tooltip = gamepiece.name

        weight.tooltip = "Weight of field element"
        weight.tooltipDescription = massUnitInString

        friction_coeff.tooltip = "Friction coefficient of field element"
        friction_coeff.tooltipDescription = (
            "<i>Friction coefficients range from 0 (ice) to 1 (rubber).</i>"
        )
        row = gamepieceTableInput.rowCount

        gamepieceTableInput.addCommandInput(blankIcon, row, 0)
        gamepieceTableInput.addCommandInput(type, row, 1)
        gamepieceTableInput.addCommandInput(weight, row, 2)
        gamepieceTableInput.addCommandInput(friction_coeff, row, 3)
    except:
        logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.addGamepieceToTable()").error(
        "Failed:\n{}".format(traceback.format_exc())
    )

def removeWheelFromTable(index: int) -> None:
    """### Removes a wheel occurrence from its global list and wheel table.

    Args:
        index (int): index of wheel item in its global list
    """
    try:
        wheel = WheelListGlobal[index]

        def removePreselections(child_occurrences):
            for occ in child_occurrences:
                onSelect.allWheelPreselections.remove(occ.entityToken)

                if occ.childOccurrences:
                    removePreselections(occ.childOccurrences)

        if wheel.childOccurrences:
            removePreselections(wheel.childOccurrences)
        else:
            onSelect.allWheelPreselections.remove(wheel.entityToken)

        del WheelListGlobal[index]
        wheelTableInput.deleteRow(index + 1)
    except IndexError:
        pass
    except:
        logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.removeWheelFromTable()").error(
        "Failed:\n{}".format(traceback.format_exc())
    )

def removeJointFromTable(joint: adsk.fusion.Joint) -> None:
    """### Removes a joint occurrence from its global list and joint table.

    Args:
        joint (adsk.fusion.Joint): Joint object to be removed
    """
    try:
        index = JointListGlobal.index(joint)
        JointListGlobal.remove(joint)

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
        logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.removeJointFromTable()").error(
        "Failed:\n{}".format(traceback.format_exc())
    )

def removeGamePieceFromTable(index: int) -> None:
    """### Removes a gamepiece occurrence from its global list and gamepiece table.

    Args:
        index (int): index of gamepiece item in its global list.
    """
    gamepiece = GamepieceListGlobal[index]

    def removePreselections(child_occurrences):
        for occ in child_occurrences:
            onSelect.allGamepiecePreselections.remove(occ.entityToken)
            
            if occ.childOccurrences:
                removePreselections(occ.childOccurrences)
    try:
        if gamepiece.childOccurrences:
            removePreselections(GamepieceListGlobal[index].childOccurrences)
        else:
            onSelect.allGamepiecePreselections.remove(gamepiece.entityToken)

        del GamepieceListGlobal[index]
        gamepieceTableInput.deleteRow(index + 1)
    except IndexError:
        pass
    except:
        logging.getLogger("{INTERNAL_ID}.UI.ConfigCommand.removeGamePieceFromTable()").error(
        "Failed:\n{}".format(traceback.format_exc())
    )
