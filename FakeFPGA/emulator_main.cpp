#include "ChipObject/NiFakeFpga.h"
#include "ChipObject/NiFpga.h"
#include "ChipObject/NiFpgaState.h"
#include <string.h>
#include <stdio.h>
#include <WPILib.h>
#include <math.h>
#include <tDIO.h>
#include "ChipObject/tDIOImpl.h"
#include "ChipObject/tSolenoidImpl.h"
#include "OSAL/System.h"
#include "PWMDecoder.h"
#include "StateNetwork/StatePacket.h"
#include "StateNetwork/StateNetworkServer.h"

#ifndef __ROBOTDEMO
#define __ROBOTDEMO
class RobotDemo : public SimpleRobot {
private:
	RobotDrive drive;
	Joystick joy;
public:
	RobotDemo(void): drive(1,2), joy(1) {
	}
	void Autonomous(void) {
		printf("Entering autonomous!\n");
	}
	void OperatorControl(void) {
		printf("Entering teleop!\n");
	}
};
START_ROBOT_CLASS(RobotDemo)
#endif

int main(int argc, char ** argv) {
	printf("Start now!\n");
	NiFpga_Initialize();
	printf("Init FPGA\n");
	FRC_UserProgram_StartupLibraryInit();
	/*StatePacket pack = StatePacket();
	StateNetworkServer serv = StateNetworkServer();
	serv.Open();
	tRioStatusCode status;
	while (true) {
		/*j += 0.1;
		float val = (float) sin(j);
		t->Set(val);
		for (int i = 0; i<8; i++){
		float curr = PWMDecoder::decodePWM(GetFakeFPGA()->getDIO(0), i);
		pack.pwmValues[i] = curr;
		}
		pack.solenoidValues = GetFakeFPGA()->getSolenoid()->readDO7_0(0, &status);
		serv.SendStatePacket(pack);
		sleep_ms(50);
	}*/
}
