#include "runtime/host_profile.h"

#include <cstdio>
#include <cstring>

int main(int argc, char **argv)
{
    const bool expectFull = argc == 2 && std::strcmp(argv[1], "full") == 0;
    {
        HostProfile::Scope scope(HostProfile::GuestExec);
    }
    const uint64_t calls = HostProfile::g_calls[HostProfile::GuestExec].load();
    if (calls != (expectFull ? 1u : 0u))
    {
        std::fprintf(stderr, "unexpected timer calls: %llu\n", static_cast<unsigned long long>(calls));
        return 1;
    }
    return 0;
}
