#pragma once

#include <cstdint>
#include <string>
#include "../camera/camera_controller.hpp"

namespace NobleArchimedes
{

struct ModernInputState
{
    // Raw analog stick inputs [-1.0f, +1.0f]
    float moveX = 0.0f;
    float moveY = 0.0f;
    float lookX = 0.0f;
    float lookY = 0.0f;

    // Camera delta for current frame (radians)
    float cameraYawDelta = 0.0f;
    float cameraPitchDelta = 0.0f;

    // Actions
    bool attack = false;
    bool guard = false;
    bool jump = false;
    bool evade = false;
    bool steal = false;
    bool idAbility = false;
    bool lockOn = false;
    bool toggleCameraMode = false;
    bool menu = false;

    // PS2 DualShock 2 button bitmask (active-low, 0 = pressed)
    uint16_t ps2Buttons = 0xFFFFu;
    uint8_t ps2LeftStickX = 128;
    uint8_t ps2LeftStickY = 128;
    uint8_t ps2RightStickX = 128;
    uint8_t ps2RightStickY = 128;
};

class InputManager
{
public:
    InputManager();

    // Polls gamepad, keyboard, and mouse, updating camera deltas and PS2 pad bytes
    void update(float deltaTime, CameraController& camera);

    const ModernInputState& getState() const { return m_state; }

    // Settings
    float mouseSensitivity = 0.0022f; // Radians per pixel
    float stickSensitivity = 2.4f;    // Radians per second at full deflection
    float innerDeadzone = 0.12f;
    float outerDeadzone = 0.95f;
    bool invertCameraX = false;
    bool invertCameraY = false;

private:
    ModernInputState m_state;
    float m_lastMouseX = 0.0f;
    float m_lastMouseY = 0.0f;
    bool m_firstMouse = true;

    // Deadzone filter with smooth response curve
    float applyDeadzone(float rawValue) const;
};

} // namespace NobleArchimedes
