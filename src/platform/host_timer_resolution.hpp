#pragma once

namespace NobleArchimedes
{
// Keep the host's requested timer resolution effective while its window is
// hidden or covered. This does not change guest timing or process priority.
bool honorHostTimerResolution() noexcept;
}
