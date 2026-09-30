#pragma once

#include "../camera/camera_controller.hpp"
#include "../input/input_manager.hpp"

class PS2Runtime;

namespace NobleArchimedes
{

class ModernOverlay
{
public:
    ModernOverlay();

    void initialize();
    void draw(PS2Runtime& runtime, CameraController& camera, InputManager& input);
    void shutdown();

    bool isVisible() const { return m_visible; }
    void setVisible(bool visible) { m_visible = visible; }
    void toggleVisible() { m_visible = !m_visible; }

private:
    bool m_initialized = false;
    bool m_visible = false;
    bool m_showCameraSettings = true;
    bool m_showInputMonitor = true;
    bool m_showIdEvolutionTree = false;
    bool m_showStealHelper = true;

    // Steal cue simulation / state tracking
    bool m_stealCueActive = false;
    float m_stealCueTimer = 0.0f;
};

} // namespace NobleArchimedes
