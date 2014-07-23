/*
* NiFpgaState.cpp
*
*  Created on: Jul 18, 2014
*      Author: localadmin
*/

#include <ChipObject/NiFpgaState.h>

#include "ChipObject/tDIOImpl.h"
#include "ChipObject/tAIImpl.h"
#include "ChipObject/tSolenoidImpl.h"
#include "ChipObject/tGlobalImpl.h"
#include "ChipObject/tEncoderImpl.h"
#include "ChipObject/tAccumulatorImpl.h"
#include "ChipObject/tInterruptImpl.h"
#include "ChipObject/tCounterImpl.h"
#include "ChipObject/tAnalogTriggerImpl.h"

#include "ChipObject/NiIRQImpl.h"
#include <stdio.h>

namespace nFPGA {

	NiFpgaState::NiFpgaState() {
		irqManager = new NiIRQ_Impl();

		ai = NULL;
		solenoid = NULL;
		dio = new tDIO_Impl*[tDIO_Impl::kNumSystems];
		ai = new tAI_Impl*[tAI_Impl::kNumSystems];
		accum = new tAccumulator_Impl*[tAccumulator_Impl::kNumSystems];
		encoder = new tEncoder_Impl*[tEncoder_Impl::kNumSystems];
		interrupt = new tInterrupt_Impl*[tInterrupt_Impl::kNumSystems];
		counter = new tCounter_Impl*[tCounter_Impl::kNumSystems];
		analogTrigger = new tAnalogTrigger_Impl*[tAnalogTrigger_Impl::kNumSystems];
		solenoid = NULL;
		global = NULL;

		for (int i = 0; i < tDIO_Impl::kNumSystems; i++) {
			dio[i] = NULL;
		}
		for (int i = 0; i < tAI_Impl::kNumSystems;i++) {
			ai[i] = NULL;
		}
		for (int i = 0; i < tAccumulator_Impl::kNumSystems; i++) {
			accum[i] = NULL;
		}
		for (int i = 0; i < tEncoder_Impl::kNumSystems; i++) {
			encoder[i] = NULL;
		}
		for (int i = 0; i < tInterrupt_Impl::kNumSystems; i++) {
			interrupt[i] = NULL;
		}
		for (int i = 0; i < tCounter_Impl::kNumSystems; i++) {
			counter[i] = NULL;
		}
		for (int i = 0; i < tAnalogTrigger_Impl::kNumSystems; i++) {
			analogTrigger[i] = NULL;
		}
	}

	NiFpgaState::~NiFpgaState() {
		delete[] accum;
		delete[] ai;
		delete[] dio;
		delete[] encoder;
		delete[] interrupt;
		delete[] analogTrigger;
		if (solenoid != NULL){
			delete solenoid;
		}
		if (global != NULL) {
			delete global;
		}
		if (irqManager != NULL) {
			delete irqManager;
		}
	}

	NiIRQ_Impl *NiFpgaState::getIRQManager() {
		return irqManager;
	}

	tDIO_Impl *NiFpgaState::getDIO(unsigned char module) {
		if (dio[module] == NULL) {
			dio[module] = new tDIO_Impl(this, module);
		}
		return dio[module];
	}

	tAI_Impl *NiFpgaState::getAnalog(unsigned char module) {
		if (ai[module] == NULL) {
			ai[module] = new tAI_Impl(this, module);
		}
		return ai[module];
	}

	tAccumulator_Impl *NiFpgaState::getAccumulator(unsigned char sys_index) {
		if (accum[sys_index] == NULL) {
			//accum[sys_index] = new tAccumulator_Impl(this, sys_index);
		}
		return accum[sys_index];
	}

	tSolenoid_Impl *NiFpgaState::getSolenoid() {
		if (solenoid == NULL) {
			solenoid = new tSolenoid_Impl(this);
		}
		return solenoid;
	}

	tGlobal_Impl *NiFpgaState::getGlobal() {
		if (global == NULL) {
			global = new tGlobal_Impl(this);
		}
		return global;
	}

	tEncoder_Impl *NiFpgaState::getEncoder(unsigned char sys_index) {
		if (encoder[sys_index] == NULL) {
			encoder[sys_index] = new tEncoder_Impl(this, sys_index);
		}
		return encoder[sys_index];
	}

	tInterrupt_Impl *NiFpgaState::getInterrupt(unsigned char sys_index) {
		if (interrupt[sys_index] == NULL) {
			interrupt[sys_index] = new tInterrupt_Impl(this, sys_index);
		}
		return interrupt[sys_index];
	}
	
	tCounter_Impl *NiFpgaState::getCounter(unsigned char sys_index) {
		if (counter[sys_index] == NULL) {
			counter[sys_index] = new tCounter_Impl(this, sys_index);
		}
		return counter[sys_index];
	}

	tAnalogTrigger_Impl *NiFpgaState::getAnalogTrigger(unsigned char sys_index) {
		if (analogTrigger[sys_index] == NULL) {
			analogTrigger[sys_index] = new tAnalogTrigger_Impl(this, sys_index);
		}
		return analogTrigger[sys_index];
	}

	const uint16_t NiFpgaState::getExpectedFPGAVersion() {
		return 0;
	}

	const uint32_t NiFpgaState::getExpectedFPGARevision() {
		return 0;
	}

	const uint32_t* const NiFpgaState::getExpectedFPGASignature() {
		return new uint32_t[3];
	}

	void NiFpgaState::getHardwareFpgaSignature(uint32_t* guid_ptr,
		tRioStatusCode* status) {
			*status =  NiFpga_Status_Success;
	}

	uint32_t NiFpgaState::getLVHandle(tRioStatusCode* status) {
		*status =  NiFpga_Status_Success;
		return 0;
	}

	uint32_t NiFpgaState::getHandle() {
		return 0;
	}

} /* namespace nFPGA */
