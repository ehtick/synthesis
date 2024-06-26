using System.Linq;
using Analytics;
using Synthesis.UI.Dynamic;
using UnityEngine;
using SynthesisAPI.Utilities;

using Logger = SynthesisAPI.Utilities.Logger;

public class ChangeDrivetrainModal : ModalDynamic {
    public const float MODAL_WIDTH  = 400f;
    public const float MODAL_HEIGHT = 55;

    private RobotSimObject.DrivetrainType _selectedType;

    public ChangeDrivetrainModal() : base(new Vector2(MODAL_WIDTH, MODAL_HEIGHT)) {}

    public override void Create() {
        if (RobotSimObject.CurrentlyPossessedRobot == string.Empty) {
            return;
        }

        Title.SetText("Change Drivetrain");

        ModalIcon.SetSprite(SynthesisAssetCollection.GetSpriteByName("drivetrain"));

        AcceptButton.AddOnClickedEvent(b => {
            MainHUD.SelectedRobot.ConfiguredDrivetrainType = _selectedType;
            AnalyticsManager.LogCustomEvent(AnalyticsEvent.DrivetrainSwitched, ("DrivetrainType", _selectedType.Name));

            DynamicUIManager.CloseActiveModal();

            MainHUD.SelectedRobot.CreateDrivetrainTooltip();
        });

        _selectedType = MainHUD.SelectedRobot.ConfiguredDrivetrainType;

        MainContent.CreateDropdown()
            .SetTopStretch<Dropdown>()
            .SetOptions(RobotSimObject.DRIVETRAIN_TYPES.Select(x => x.Name).ToArray())
            .AddOnValueChangedEvent((d, i, o) => _selectedType = RobotSimObject.DRIVETRAIN_TYPES[i])
            .SetValue(_selectedType.Value);
    }

    public override void Update() {
        if (RobotSimObject.CurrentlyPossessedRobot == string.Empty) {
            Logger.Log("Must spawn a robot first", LogLevel.Info);
            DynamicUIManager.CloseActiveModal();
        }
    }

    public override void Delete() {}
}
