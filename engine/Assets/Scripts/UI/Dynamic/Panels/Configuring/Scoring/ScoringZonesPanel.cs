using System;
using System.Collections.Generic;
using System.Linq;
using JetBrains.Annotations;
using Newtonsoft.Json;
using Synthesis.Gizmo;
using Synthesis.Physics;
using Synthesis.UI.Dynamic;
using Synthesis.PreferenceManager;
using TMPro;
using UnityEngine;
using Object = UnityEngine.Object;

public record ScoringZoneData() {
    public string Name { get; set; }                                        = "";
    public Alliance Alliance { get; set; }                                  = Alliance.Blue;
    public string Parent { get; set; }                                      = "grounded";
    public int Points { get; set; }                                         = 0;
    public bool DestroyGamepiece { get; set; }                              = false;
    public bool PersistentPoints { get; set; }                              = true;
    public (float x, float y, float z) LocalPosition { get; set; }          = (0, 0, 0);
    public (float x, float y, float z, float w) LocalRotation { get; set; } = (0, 0, 0, 1);
    public (float x, float y, float z) LocalScale { get; set; }             = (1, 1, 1);
}

public class ScoringZonesPanel : PanelDynamic {
    public static bool MatchModeSetup = false;

    private const float MODAL_WIDTH  = 500f;
    private const float MODAL_HEIGHT = 600f;

    private const float VERTICAL_PADDING   = 16f;
    private const float HORIZONTAL_PADDING = 16f;
    private const float SCROLLBAR_WIDTH    = 10f;
    private const float BUTTON_WIDTH       = 64f;
    private const float ROW_HEIGHT         = 64f;

    private float _scrollViewWidth;
    private float _entryWidth;

    private ScrollView _zonesScrollView;

    private readonly Func<UIComponent, UIComponent> VerticalLayout = (u) => {
        var offset = (-u.Parent!.RectOfChildren(u).yMin) + VERTICAL_PADDING;
        u.SetTopStretch<UIComponent>(anchoredY: offset, leftPadding: 0, rightPadding: 0);
        return u;
    };

    private readonly Func<UIComponent, UIComponent> ListVerticalLayout = (u) => {
        var offset = (-u.Parent!.RectOfChildren(u).yMin) + VERTICAL_PADDING;
        u.SetTopStretch<UIComponent>(
            anchoredY: offset, leftPadding: HORIZONTAL_PADDING, rightPadding: HORIZONTAL_PADDING);
        return u;
    };

    public ScoringZonesPanel() : base(new Vector2(MODAL_WIDTH, MODAL_HEIGHT)) {}

    public override bool Create() {
        Title.SetText("Scoring Zones");

        AcceptButton.StepIntoLabel(l => l.SetText(MatchModeSetup ? "Continue" : "Close"))
            .AddOnClickedEvent(b => DynamicUIManager.ClosePanel<ScoringZonesPanel>());
        CancelButton.RootGameObject.SetActive(false);

        _zonesScrollView = MainContent.CreateScrollView()
                               .SetRightStretch<ScrollView>()
                               .ApplyTemplate(VerticalLayout)
                               .SetHeight<ScrollView>(MODAL_HEIGHT - VERTICAL_PADDING * 2 - 50);
        _scrollViewWidth = _zonesScrollView.Parent!.RectOfChildren().width - SCROLLBAR_WIDTH;
        _entryWidth      = _scrollViewWidth - HORIZONTAL_PADDING * 2;

        MainContent.CreateButton()
            .SetTopStretch<Button>()
            .StepIntoLabel(l => l.SetText("Add Zone"))
            .AddOnClickedEvent(
                _ => { OpenScoringZoneGizmo(); })
            .ApplyTemplate(VerticalLayout);

        AddZoneEntries();

        FieldSimObject.CurrentField.ScoringZones.ForEach(x => x.VisibilityCounter++);

        // so that timer doesn't count while configuring
        // will remove later once score zones can be configured before match start, per Luca's match mode state machine
        PhysicsManager.IsFrozen = true;

        return true;
    }

    private void AddZoneEntries() {
        _zonesScrollView.Content.DeleteAllChildren();
        foreach (ScoringZone zone in FieldSimObject.CurrentField.ScoringZones) {
            AddZoneEntry(zone, true);
        }
    }

    private void AddZoneEntry(ScoringZone zone, bool isNew) {
        if (!isNew) {
            AddZoneEntries();
            return;
        }
        (Content leftContent, Content rightContent) =
            _zonesScrollView.Content.CreateSubContent(new Vector2(_entryWidth, ROW_HEIGHT))
                .ApplyTemplate(ListVerticalLayout)
                .SplitLeftRight(BUTTON_WIDTH, HORIZONTAL_PADDING);
        leftContent.StepIntoImage(i => i.SetColor((zone.Alliance == Alliance.Red) ? Color.red : Color.blue));

        (Content labelsContent, Content buttonsContent) =
            rightContent.SplitLeftRight(_entryWidth - (HORIZONTAL_PADDING + BUTTON_WIDTH) * 3, HORIZONTAL_PADDING);
        (Content topContent, Content bottomContent) = labelsContent.SplitTopBottom(ROW_HEIGHT / 2, 0);
        topContent.CreateLabel()
            .SetText(zone.Name)
            .ApplyTemplate(VerticalLayout)
            .SetAnchorLeft<Label>()
            .SetAnchoredPosition<Label>(new Vector2(0, -ROW_HEIGHT / 8));
        string points = "points";
        if (zone.Points == 1) {
            points = "point";
        }
        bottomContent.CreateLabel()
            .SetText($"{zone.Points} {points}")
            .ApplyTemplate(VerticalLayout)
            .SetAnchorLeft<Label>()
            .SetAnchoredPosition<Label>(new Vector2(0, -ROW_HEIGHT / 8));

        (Content editButtonContent, Content deleteButtonContent) =
            buttonsContent.SplitLeftRight(BUTTON_WIDTH, HORIZONTAL_PADDING);
        editButtonContent.CreateButton()
            .StepIntoLabel(l => l.SetText("Edit"))
            .AddOnClickedEvent(
                _ => OpenScoringZoneGizmo(zone))
            .ApplyTemplate(VerticalLayout)
            .SetSize<Button>(new Vector2(BUTTON_WIDTH, ROW_HEIGHT))
            .SetStretch<Button>();
        deleteButtonContent.CreateButton()
            .StepIntoLabel(l => l.SetText("Delete"))
            .AddOnClickedEvent(
                _ => {
                    FieldSimObject.CurrentField.RemoveScoringZone(zone);
                    Object.Destroy(zone.GameObject);
                    AddZoneEntries();
                })
            .ApplyTemplate(VerticalLayout)
            .SetSize<Button>(new Vector2(BUTTON_WIDTH, ROW_HEIGHT))
            .SetStretch<Button>()
            .StepIntoImage(i => i.InvertGradient());
    }

    private void OpenScoringZoneGizmo(ScoringZone zone = null) {
        DynamicUIManager.CreatePanel<ZoneConfigPanel>(persistent: true, zone);
        ZoneConfigPanel panel = DynamicUIManager.GetPanel<ZoneConfigPanel>();
        panel.SetCallback(AddZoneEntry);
    }

    public override void Update() {}

    public override void Delete() {
        FieldSimObject.CurrentField.ScoringZones.ForEach(x => {
            if (x != null)
                x.VisibilityCounter--;
        });
        PhysicsManager.IsFrozen = false;
    }
}