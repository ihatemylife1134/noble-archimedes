#pragma once

#include <cmath>
#include <algorithm>

namespace NobleArchimedes
{

enum class CameraMode
{
    ActionOrbit,       // Elden Ring / Super Mario Odyssey / Control: 360° free orbit, dynamic distance
    OverTheShoulder,   // Resident Evil 2 Remake: Tight over-the-right-shoulder, close perspective, tactical strafe
    Classic            // Original PS2 fixed follow camera
};

struct Vector3f
{
    float x = 0.0f;
    float y = 0.0f;
    float z = 0.0f;

    Vector3f operator+(const Vector3f& o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vector3f operator-(const Vector3f& o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vector3f operator*(float s) const { return {x * s, y * s, z * s}; }
    float length() const { return std::sqrt(x * x + y * y + z * z); }
    Vector3f normalized() const
    {
        float l = length();
        return l > 1e-5f ? Vector3f{x / l, y / l, z / l} : Vector3f{0, 0, 0};
    }
};

class CameraController
{
public:
    CameraController();

    // Mode management
    void setMode(CameraMode mode);
    CameraMode getMode() const { return m_mode; }
    void toggleCameraMode(); // Toggles between ActionOrbit and OverTheShoulder

    // Update with input deltas (deltaYaw, deltaPitch in degrees or radians)
    void update(float deltaTime, const Vector3f& targetPosition, float inputYawDelta, float inputPitchDelta);

    // Camera parameters
    Vector3f getPosition() const { return m_currentPosition; }
    Vector3f getLookAtTarget() const { return m_currentLookAt; }
    float getFov() const { return m_currentFov; }
    float getYaw() const { return m_yaw; }
    float getPitch() const { return m_pitch; }

    // Settings
    float mouseSensitivity = 0.15f;
    float stickSensitivityX = 120.0f; // degrees per second
    float stickSensitivityY = 90.0f;
    bool invertX = false;
    bool invertY = false;
    float targetArmLength = 3.6f;

    // Calculations for camera-relative movement
    Vector3f getForwardVector() const;
    Vector3f getRightVector() const;

private:
    CameraMode m_mode = CameraMode::Classic;

    // Angles in radians
    float m_yaw = 0.0f;
    float m_pitch = 0.25f; // Slightly looking down by default (~14°)

    // Smooth state
    Vector3f m_currentPosition{0.0f, 2.0f, -3.8f};
    Vector3f m_currentLookAt{0.0f, 1.2f, 0.0f};
    float m_currentFov = 75.0f;
    float m_currentDistance = 3.6f;

    // Target parameters based on active camera mode
    float getTargetDistance() const;
    float getTargetFov() const;
    Vector3f getShoulderOffset() const;
    float getTargetHeightOffset() const;
};

} // namespace NobleArchimedes
