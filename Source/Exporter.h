#pragma once

#include <Core/CoreAll.h>
#include <Fusion/FusionAll.h>
#include <CAM/CAMAll.h>
#include <string>
#include <Core/UserInterface/ToolbarControls.h>
#include <Core/UserInterface/Command.h>
#include <Core/UserInterface/CommandEvent.h>
#include <Core/UserInterface/CommandEventHandler.h>
#include <Core/UserInterface/CommandEventArgs.h>
#include <time.h>
#include "AddIn/EUI.h"
#include "Data/BXDA/Mesh.h"
#include "Data/BinaryRWObject.h"
#include <chrono>
#include <numeric>

using namespace adsk::core;
using namespace adsk::fusion;
using namespace adsk::cam;

namespace Synthesis
{
	enum logLevels { info, warn, critikal };

	class Exporter
	{
	public:
		Exporter(Ptr<Application>);
		~Exporter();

		void loadMeshes();

	private:
		Ptr<Application> _app;
		Ptr<UserInterface> _ui;

	};
}
