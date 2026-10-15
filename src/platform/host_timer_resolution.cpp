#include "host_timer_resolution.hpp"

#ifdef _WIN32
#define NOMINMAX
#include <processthreadsapi.h>
#endif

bool NobleArchimedes::honorHostTimerResolution() noexcept
{
#ifdef _WIN32
    PROCESS_POWER_THROTTLING_STATE state{};
    state.Version = PROCESS_POWER_THROTTLING_CURRENT_VERSION;
    state.ControlMask = PROCESS_POWER_THROTTLING_IGNORE_TIMER_RESOLUTION;
    state.StateMask = 0;
    return SetProcessInformation(GetCurrentProcess(), ProcessPowerThrottling,
                                 &state, sizeof(state)) != FALSE;
#else
    return true;
#endif
}
