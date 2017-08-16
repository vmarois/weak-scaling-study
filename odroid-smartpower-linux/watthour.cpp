#include <iostream>
#include "smartgauge.hpp"

int main(int argc, char *argv[]){

	// Get WattHour logging.
	SmartGauge sg;
	sg.initDevice();
	std::cout <<  sg.getWattHour();

	return 0;
}

