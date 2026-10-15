#include "input_manager.hpp"
#include "raylib.h"
#include <cmath>
#include <algorithm>

namespace NobleArchimedes
{

InputManager::InputManager()
{
    m_state = ModernInputState{};
}

float InputManager::applyDeadzone(float raw) const
{
    float mag = std::abs(raw);
    if (mag < innerDeadzone)
        return 0.0f;
    if (mag > outerDeadzone)
        return (raw > 0.0f) ? 1.0f : -1.0f;

    // Rescale smoothly from [innerDeadzone, outerDeadzone] to [0.0, 1.0]
    float scaled = (mag - innerDeadzone) / (outerDeadzone - innerDeadzone);
    // Smoothstep curve for responsiveness and accuracy
    float smooth = scaled * scaled * (3.0f - 2.0f * scaled);
    return (raw > 0.0f) ? smooth : -smooth;
}

void InputManager::update(float deltaTime, CameraController& camera)
{
    m_state.ps2Buttons = 0xFFFFu; // All buttons unpressed by default (active-low)
    auto pressButton = [this](uint16_t mask) {
        m_state.ps2Buttons &= ~mask;
    };

    float rawMoveX = 0.0f;
    float rawMoveY = 0.0f;
    float rawLookX = 0.0f;
    float rawLookY = 0.0f;

    // --- 1. GAMEPAD POLLING ---
    constexpr int kPad = 0;
    const bool hasGamepad = IsGamepadAvailable(kPad);
    if (hasGamepad)
    {
        // Analog sticks
        rawMoveX = applyDeadzone(GetGamepadAxisMovement(kPad, GAMEPAD_AXIS_LEFT_X));
        rawMoveY = -applyDeadzone(GetGamepadAxisMovement(kPad, GAMEPAD_AXIS_LEFT_Y)); // Invert so +Y is forward

        rawLookX = applyDeadzone(GetGamepadAxisMovement(kPad, GAMEPAD_AXIS_RIGHT_X));
        rawLookY = applyDeadzone(GetGamepadAxisMovement(kPad, GAMEPAD_AXIS_RIGHT_Y));

        // Face buttons
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_RIGHT_FACE_LEFT))  // X (Xbox) / Square
            pressButton(PAD_SQUARE);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_RIGHT_FACE_UP))    // Y (Xbox) / Triangle
            pressButton(PAD_TRIANGLE);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_RIGHT_FACE_DOWN))  // A (Xbox) / Cross
            pressButton(PAD_CROSS);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_RIGHT_FACE_RIGHT)) // B (Xbox) / Circle
            pressButton(PAD_CIRCLE);

        // Shoulders & Triggers
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_LEFT_TRIGGER_1))  // LB / L1
            pressButton(PAD_L1);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_RIGHT_TRIGGER_1)) // RB / R1
            pressButton(PAD_R1);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_LEFT_TRIGGER_2))  // LT / L2
            pressButton(PAD_L2);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_RIGHT_TRIGGER_2)) // RT / R2
            pressButton(PAD_R2);

        // D-Pad
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_LEFT_FACE_UP))
            pressButton(PAD_UP);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_LEFT_FACE_DOWN))
            pressButton(PAD_DOWN);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_LEFT_FACE_LEFT))
            pressButton(PAD_LEFT);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_LEFT_FACE_RIGHT))
            pressButton(PAD_RIGHT);

        // Stick Clicks & Menu
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_LEFT_THUMB))
            pressButton(PAD_L3);
        if (IsGamepadButtonPressed(kPad, GAMEPAD_BUTTON_RIGHT_THUMB))
        {
            pressButton(PAD_R3);
            camera.toggleCameraMode(); // R3 click toggles 2026 Camera Mode!
        }
        else if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_RIGHT_THUMB))
        {
            pressButton(PAD_R3);
        }

        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_MIDDLE_RIGHT)) // Start / Menu
            pressButton(PAD_START);
        if (IsGamepadButtonDown(kPad, GAMEPAD_BUTTON_MIDDLE_LEFT))  // Back / Select
            pressButton(PAD_SELECT);
    }

    // --- 2. KEYBOARD & MOUSE POLLING (PC MASTER CONTROLS) ---
    // Locomotion keys (WASD)
    if (IsKeyDown(KEY_W)) rawMoveY += 1.0f;
    if (IsKeyDown(KEY_S)) rawMoveY -= 1.0f;
    if (IsKeyDown(KEY_D)) rawMoveX += 1.0f;
    if (IsKeyDown(KEY_A)) rawMoveX -= 1.0f;

    // Normalize diagonal keyboard movement
    float kbLen = std::sqrt(rawMoveX * rawMoveX + rawMoveY * rawMoveY);
    if (kbLen > 1.0f)
    {
        rawMoveX /= kbLen;
        rawMoveY /= kbLen;
    }

    // Action Key Mappings
    if (IsMouseButtonDown(MOUSE_BUTTON_LEFT) || IsKeyDown(KEY_J))  // Attack / Combo
        pressButton(PAD_SQUARE);
    if (IsMouseButtonDown(MOUSE_BUTTON_RIGHT) || IsKeyDown(KEY_K)) // Special / Finisher
        pressButton(PAD_TRIANGLE);
    if (IsKeyDown(KEY_SPACE))                                      // Jump
        pressButton(PAD_CROSS);
    if (IsKeyDown(KEY_E) || IsKeyDown(KEY_L))                      // Action / Evade
        pressButton(PAD_CIRCLE);
    if (IsKeyDown(KEY_LEFT_SHIFT))                                 // Guard / Perfect Guard
        pressButton(PAD_R1);
    if (IsKeyDown(KEY_TAB))                                        // Lock-on Target
        pressButton(PAD_R2);
    if (IsKeyDown(KEY_Q))                                          // Summon / ID Command
        pressButton(PAD_L1);
    if (IsKeyDown(KEY_F))                                          // Steal Target Focus
        pressButton(PAD_L2);
    if (IsKeyDown(KEY_ESCAPE) || IsKeyDown(KEY_ENTER))             // Pause / Menu
        pressButton(PAD_START);
    if (IsKeyDown(KEY_M))                                          // Map
        pressButton(PAD_SELECT);

    // Camera Mode Toggle Hotkey
    if (IsKeyPressed(KEY_V))
    {
        camera.toggleCameraMode();
    }

    // Arrow keys fallback for D-Pad
    if (IsKeyDown(KEY_UP))    pressButton(PAD_UP);
    if (IsKeyDown(KEY_DOWN))  pressButton(PAD_DOWN);
    if (IsKeyDown(KEY_LEFT))  pressButton(PAD_LEFT);
    if (IsKeyDown(KEY_RIGHT)) pressButton(PAD_RIGHT);

    // --- 3. MOUSE LOOK (SMOOTH 360° ORBIT / OTS AIM) ---
    Vector2 mouseDelta = GetMouseDelta();
    float mouseYawDelta = 0.0f;
    float mousePitchDelta = 0.0f;

    // Right-click or cursor captured gives free mouse look
    if (IsMouseButtonDown(MOUSE_BUTTON_RIGHT) || IsCursorHidden())
    {
        mouseYawDelta = mouseDelta.x * mouseSensitivity * (invertCameraX ? -1.0f : 1.0f);
        mousePitchDelta = mouseDelta.y * mouseSensitivity * (invertCameraY ? -1.0f : 1.0f);
    }

    // Stick look delta
    float stickYawDelta = rawLookX * stickSensitivity * deltaTime * (invertCameraX ? -1.0f : 1.0f);
    float stickPitchDelta = rawLookY * stickSensitivity * deltaTime * (invertCameraY ? -1.0f : 1.0f);

    float totalYawDelta = mouseYawDelta + stickYawDelta;
    float totalPitchDelta = mousePitchDelta + stickPitchDelta;

    // --- 4. UPDATE STORED STATE ---
    m_state.moveX = rawMoveX;
    m_state.moveY = rawMoveY;
    m_state.lookX = rawLookX;
    m_state.lookY = rawLookY;
    m_state.cameraYawDelta = totalYawDelta;
    m_state.cameraPitchDelta = totalPitchDelta;

    // Convert raw move input into PS2 Left Stick byte coordinates [0..255] with 128 center
    int lxByte = 128 + static_cast<int>(std::round(rawMoveX * 127.0f));
    int lyByte = 128 + static_cast<int>(std::round(-rawMoveY * 127.0f)); // PS2 stick: 0 is UP, 255 is DOWN
    m_state.ps2LeftStickX = static_cast<uint8_t>(std::clamp(lxByte, 0, 255));
    m_state.ps2LeftStickY = static_cast<uint8_t>(std::clamp(lyByte, 0, 255));

    // Convert look input into PS2 Right Stick byte coordinates [0..255]
    int rxByte = 128 + static_cast<int>(std::round(rawLookX * 127.0f));
    int ryByte = 128 + static_cast<int>(std::round(rawLookY * 127.0f));
    m_state.ps2RightStickX = static_cast<uint8_t>(std::clamp(rxByte, 0, 255));
    m_state.ps2RightStickY = static_cast<uint8_t>(std::clamp(ryByte, 0, 255));

    // Update camera controller with current deltas
    Vector3f dummyTarget{0.0f, 0.0f, 0.0f}; // Hector's position will be tracked or centered
    camera.update(deltaTime, dummyTarget, totalYawDelta, totalPitchDelta);
}

} // namespace NobleArchimedes
