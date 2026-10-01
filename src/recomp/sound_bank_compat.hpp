#pragma once
#include <cstdint>

namespace noble_sound
{
void acceptedCommand(uint8_t* ram, uint32_t command, uint32_t argument);
uint32_t bankStatus(const uint8_t* ram, uint32_t pc, uint32_t channel);
}
