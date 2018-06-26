#include <iostream>
#include "smartgauge.hpp"

int main(int argc, char *argv[]) {
	// The following is needed to properly reset the WattHour logging.
	SmartGauge* sg1 =  new SmartGauge();
	sg1->initDevice();
	delete sg1;
	std::cout << "SmartPower should now have been reset properly, and started the watthour measurement." << std::endl;
	return 0;
}
