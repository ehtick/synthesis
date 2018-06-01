//
//  EUI.h
//  FusionSynth
//
//  Created by Madvisitor on 4/16/18.
//  Copyright © 2018 Autodesk. All rights reserved. // How did they even generate this wtf
//

#include "Exporter.h"

#ifndef EUI_h
#define EUI_h

using namespace adsk::core;
using namespace adsk::fusion;
using namespace adsk::cam;
using namespace std;


namespace Synthesis{
    
    class EUI{
    public:
        EUI();
        EUI(Ptr<UserInterface>, Ptr<Application>);
        ~EUI();
        
    private:
        Ptr<Application> _APP;
        Ptr<UserInterface> _UI;
        Ptr<Workspace> _WorkSpace;
        Ptr<Workspaces> _WorkSpaces;
        Ptr<ToolbarPanel> _ToolbarPanel;
        Ptr<ToolbarControls> _ToolbarControls;
        
        Ptr<CommandDefinition> _AddWheelCommandDef;
        Ptr<CommandDefinition> _ExportCommandDef;
        
        void configButtonWheel();
        void configButtonExporter();
        bool CreateWorkspace();
        
    };

    class CommandEventHandler : public adsk::core::CommandEventHandler{
    public:
        void notify(const Ptr<CommandEventArgs>& eventArgs) override;
    private:
        //OnExecuteEventHander onExecuteHandler;
    };
    
    class OnExecuteEventHandler : public adsk::core::CommandEventHandler{
    public:
        void notify(const Ptr<CommandEventArgs>& eventArgs) override;
    };
}


#endif /* EUI_h */
