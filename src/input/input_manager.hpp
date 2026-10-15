#pragma once

#include <cstdint>
#include <string>
#include "../camera/camera_controller.hpp"

namespace NobleArchimedes
{

// PS2 DualShock 2 active-low bitmasks
constexpr uint16_t PAD_SELECT   = 1u << 0;  // 0x0001
constexpr uint16_t PAD_L3       = 1u << 1;  // 0x0002
constexpr uint16_t PAD_R3       = 1u << 2;  // 0x0004
constexpr uint16_t PAD_START    = 1u << 3;  // 0x0008
constexpr uint16_t PAD_UP       = 1u << 4;  // 0x0010
constexpr uint16_t PAD_RIGHT    = 1u << 5;  // 0x0020
constexpr uint16_t PAD_DOWN     = 1u << 6;  // 0x0040
constexpr uint16_t PAD_LEFT     = 1u << 7;  // 0x0080
constexpr uint16_t PAD_L2       = 1u << 8;  // 0x0100
constexpr uint16_t PAD_R2       = 1u << 9;  // 0x0200
constexpr uint16_t PAD_L1       = 1u << 10; // 0x0400
constexpr uint16_t PAD_R1       = 1u << 11; // 0x0800
constexpr uint16_t PAD_TRIANGLE = 1u << 12; // 0x1000
constexpr uint16_t PAD_CIRCLE   = 1u << 13; // 0x2000
constexpr uint16_t PAD_CROSS    = 1u << 14; // 0x4000
constexpr uint16_t PAD_SQUARE   = 1u << 15; // 0x8000

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
