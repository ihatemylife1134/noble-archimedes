from pathlib import Path
import sys

target = Path("tools/PS2Recomp/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp")

with open(target, "r", encoding="utf-8") as f:
    content = f.read()

normalized = content.replace("\r\n", "\n")

# 1. Update anonymous namespace: FastBlockCache + s_pacingDeadline
cache_def = """    struct FastBlockCacheSlot
    {
        uint32_t pc = 0;
        PS2Runtime::RecompiledFunction fn = nullptr;
    };
    FastBlockCacheSlot s_fastBlockCache[65536] = {};
    std::chrono::steady_clock::time_point s_pacingDeadline{};

    inline PS2Runtime::RecompiledFunction fastLookupBlock(uint32_t pc, PS2Runtime &runtime)
    {
        const uint32_t index = (pc >> 2) & 0xFFFFu;
        FastBlockCacheSlot &slot = s_fastBlockCache[index];
        if (slot.pc == pc && slot.fn != nullptr)
        {
            return slot.fn;
        }
        if (pc >= g_ps2RecompiledFunctionTableBase && pc < g_ps2RecompiledFunctionTableEnd)
        {
            const uint32_t offset = pc - g_ps2RecompiledFunctionTableBase;
            const uint32_t tableSlot = offset >> 2;
            if (tableSlot < g_ps2RecompiledFunctionTableSlotCount)
            {
                PS2Runtime::RecompiledFunction fn = g_ps2RecompiledFunctionTable[tableSlot];
                if (fn != nullptr)
                {
                    slot.pc = pc;
                    slot.fn = fn;
                    return fn;
                }
            }
        }
        if (runtime.hasFunction(pc))
        {
            PS2Runtime::RecompiledFunction fn = runtime.lookupFunction(pc);
            if (fn != nullptr)
            {
                slot.pc = pc;
                slot.fn = fn;
                return fn;
            }
        }
        return nullptr;
    }"""

# Replace existing FastBlockCacheSlot definition if present, or insert at anchor
if "struct FastBlockCacheSlot" in normalized:
    # Replace existing definition up to fastLookupBlock's closing brace
    start_pos = normalized.find("    struct FastBlockCacheSlot")
    end_marker = "    inline PS2Runtime::RecompiledFunction fastLookupBlock(uint32_t pc, PS2Runtime &runtime)\n    {\n"
    end_pos = normalized.find(end_marker)
    if end_pos != -1:
        # find the closing brace of fastLookupBlock
        closing_brace = normalized.find("    }\n", end_pos)
        if closing_brace != -1:
            old_block = normalized[start_pos:closing_brace + 6]
            normalized = normalized.replace(old_block, cache_def + "\n")
            print("1. Updated FastBlockCacheSlot and s_pacingDeadline in anonymous namespace")
else:
    anchor_ns = "    constexpr uint32_t kDebugPublishDispatchInterval = 4096u;\n"
    normalized = normalized.replace(anchor_ns, anchor_ns + "\n" + cache_def + "\n", 1)
    print("1. Added FastBlockCacheSlot and s_pacingDeadline to anonymous namespace")

# 2. Reset s_fastBlockCache and s_pacingDeadline in EeScheduler::reset
anchor_reset = "    m_executorThread = std::this_thread::get_id();\n"
reset_target = "    m_executorThread = std::this_thread::get_id();\n    std::memset(s_fastBlockCache, 0, sizeof(s_fastBlockCache));\n    s_pacingDeadline = {};\n"

# Remove any previous reset line
if "std::memset(s_fastBlockCache, 0, sizeof(s_fastBlockCache));" in normalized:
    # replace up to newline
    pos = normalized.find("    std::memset(s_fastBlockCache, 0, sizeof(s_fastBlockCache));\n")
    if pos != -1:
        # check if s_pacingDeadline = {}; is also there
        check_pacing = normalized[pos:pos+120]
        if "s_pacingDeadline = {};\n" in check_pacing:
            pass # already there
        else:
            normalized = normalized[:pos] + "    std::memset(s_fastBlockCache, 0, sizeof(s_fastBlockCache));\n    s_pacingDeadline = {};\n" + normalized[pos+64:]
            print("2. Updated s_fastBlockCache and s_pacingDeadline reset in EeScheduler::reset")
else:
    normalized = normalized.replace(anchor_reset, reset_target, 1)
    print("2. Added s_fastBlockCache and s_pacingDeadline reset in EeScheduler::reset")

# 3. Update computeSafeQuantumBudget lambda in EeScheduler::run
new_budget_code = """    auto computeSafeQuantumBudget = [this](const GuestThread *running) noexcept -> uint32_t
    {
        if (!running || !running->invocations.empty() || running->resumeCompletion != nullptr)
        {
            return 0u;
        }
        if (m_checkpointPending.load(std::memory_order_relaxed) ||
            m_stopRequested.load(std::memory_order_relaxed) ||
            m_rescheduleRequested ||
            m_pendingEeTimerInterrupts != 0u)
        {
            return 0u;
        }

        uint64_t maxCycles = 2048ull;

        if (m_sliceEndCycle > m_eeCycle)
        {
            maxCycles = std::min(maxCycles, m_sliceEndCycle - m_eeCycle);
        }
        else
        {
            return 0u;
        }

        const uint64_t deadline = m_nextDeadlineCycle.load(std::memory_order_relaxed);
        if (deadline > m_eeCycle)
        {
            maxCycles = std::min(maxCycles, deadline - m_eeCycle);
        }

        const uint64_t timerCycles = m_runtime.memory().cyclesUntilNextEeTimerInterrupt();
        if (timerCycles > 0u)
        {
            maxCycles = std::min(maxCycles, timerCycles);
        }
        else
        {
            return 0u;
        }

        return static_cast<uint32_t>(maxCycles);
    };"""

# Replace existing computeSafeQuantumBudget if present
if "auto computeSafeQuantumBudget = " in normalized:
    pos_start = normalized.find("    auto computeSafeQuantumBudget = ")
    pos_end = normalized.find("    while (!m_stopRequested.load(std::memory_order_acquire))", pos_start)
    if pos_start != -1 and pos_end != -1:
        normalized = normalized[:pos_start] + new_budget_code + "\n\n" + normalized[pos_end:]
        print("3. Replaced computeSafeQuantumBudget with fixed non-stalling version")
else:
    anchor_budget = "        PS2Runtime::RecompiledFunction function = m_runtime.lookupFunction(context.pc);\n"
    normalized = normalized.replace(anchor_budget, new_budget_code + "\n\n" + anchor_budget, 1)
    print("3. Added fixed computeSafeQuantumBudget lambda in EeScheduler::run")

# 4. In EeScheduler::run outer loop, check s_pacingDeadline before processPendingEvents
pacing_check = """        if (s_pacingDeadline != std::chrono::steady_clock::time_point{})
        {
            if (std::chrono::steady_clock::now() >= s_pacingDeadline)
            {
                s_pacingDeadline = {};
                m_checkpointPending.store(true, std::memory_order_release);
            }
        }
        processPendingEvents();"""

old_loop_entry = """        processPendingEvents();"""

new_loop_entry = """        if (s_pacingDeadline != std::chrono::steady_clock::time_point{})
        {
            if (std::chrono::steady_clock::now() >= s_pacingDeadline)
            {
                s_pacingDeadline = {};
                m_checkpointPending.store(true, std::memory_order_release);
            }
        }
        processPendingEvents();"""

if old_loop_entry in normalized:
    normalized = normalized.replace(old_loop_entry, new_loop_entry, 1)
    print("4. Added s_pacingDeadline check in EeScheduler::run outer loop")
elif "s_pacingDeadline != std::chrono::steady_clock::time_point{}" in normalized:
    print("4. s_pacingDeadline check already present in EeScheduler::run")

# 5. In processDueDeadlines, record s_pacingDeadline when now < pacingDeadline
old_due_pacing = """            if (now < pacingDeadline)
            {
                m_eventCv.wait_until(lock, pacingDeadline, [this]()
                                     { return !m_events.empty() ||
                                              m_stopRequested.load(std::memory_order_acquire); });
                if (!m_events.empty() || m_stopRequested.load(std::memory_order_acquire))
                {
                    updateNextDeadline();
                    return;
                }
            }"""

new_due_pacing = """            if (now < pacingDeadline)
            {
                // A cycle-due event can still be host-future. Leave pacing to
                // the outer idle wait after guest threads get a turn.
                s_pacingDeadline = pacingDeadline;
                updateNextDeadline();
                return;
            }"""

if old_due_pacing in normalized:
    normalized = normalized.replace(old_due_pacing, new_due_pacing, 1)
    print("5. Recorded s_pacingDeadline in processDueDeadlines when now < pacingDeadline")
elif new_due_pacing in normalized:
    print("5. s_pacingDeadline already recorded in processDueDeadlines")

# 6. In processDueDeadlines, clear s_pacingDeadline when due events are moved
old_due_drain = """            due.insert(due.end(),
                       std::make_move_iterator(m_deadlines.begin()),
                       std::make_move_iterator(firstFuture));
            m_deadlines.erase(m_deadlines.begin(), firstFuture);
            updateNextDeadline();"""

new_due_drain = """            due.insert(due.end(),
                       std::make_move_iterator(m_deadlines.begin()),
                       std::make_move_iterator(firstFuture));
            m_deadlines.erase(m_deadlines.begin(), firstFuture);
            s_pacingDeadline = {};
            updateNextDeadline();"""

if old_due_drain in normalized:
    normalized = normalized.replace(old_due_drain, new_due_drain, 1)
    print("6. Cleared s_pacingDeadline in processDueDeadlines on event processing")
elif new_due_drain in normalized:
    print("6. s_pacingDeadline clearing already present in processDueDeadlines")

# 7. Update EeScheduler::updateNextDeadline()
old_update_deadline = """void EeScheduler::updateNextDeadline()
{
    if (m_deadlines.empty())
    {
        m_nextDeadlineCycle.store(0u, std::memory_order_release);
        return;
    }
    const auto it = std::min_element(m_deadlines.begin(), m_deadlines.end(),
                                     [](const ScheduledEvent &left, const ScheduledEvent &right)
                                     {
                                         if (left.deadlineCycle != right.deadlineCycle)
                                         {
                                             return left.deadlineCycle < right.deadlineCycle;
                                         }
                                         return left.sequence < right.sequence;
                                     });
    m_nextDeadlineCycle.store(it->deadlineCycle, std::memory_order_release);
}"""

new_update_deadline = """void EeScheduler::updateNextDeadline()
{
    if (m_deadlines.empty())
    {
        m_nextDeadlineCycle.store(0u, std::memory_order_release);
        return;
    }
    const auto now = std::chrono::steady_clock::now();
    uint64_t earliestFutureCycle = 0u;
    uint64_t earliestSequence = 0u;
    bool hasImmediateDueEvent = false;

    for (const ScheduledEvent &item : m_deadlines)
    {
        if (item.deadlineCycle <= m_eeCycle && item.hostDeadline <= now)
        {
            hasImmediateDueEvent = true;
        }
        else if (item.deadlineCycle > m_eeCycle)
        {
            if (earliestFutureCycle == 0u ||
                item.deadlineCycle < earliestFutureCycle ||
                (item.deadlineCycle == earliestFutureCycle && item.sequence < earliestSequence))
            {
                earliestFutureCycle = item.deadlineCycle;
                earliestSequence = item.sequence;
            }
        }
    }

    if (hasImmediateDueEvent)
    {
        m_nextDeadlineCycle.store(m_eeCycle, std::memory_order_release);
        m_checkpointPending.store(true, std::memory_order_release);
    }
    else
    {
        m_nextDeadlineCycle.store(earliestFutureCycle, std::memory_order_release);
    }
}"""

if old_update_deadline in normalized:
    normalized = normalized.replace(old_update_deadline, new_update_deadline, 1)
    print("7. Replaced updateNextDeadline() with non-stalling future deadline logic")
elif new_update_deadline in normalized:
    print("7. updateNextDeadline() already updated")
else:
    print("Warning: old_update_deadline pattern not found, checking...")

# Save file with CRLF
with open(target, "wb") as f:
    f.write(normalized.replace("\n", "\r\n").encode("utf-8"))

print("Stage A v2 patching complete!")
