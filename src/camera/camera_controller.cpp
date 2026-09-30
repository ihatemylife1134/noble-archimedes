#include "camera_controller.hpp"

namespace NobleArchimedes
{

constexpr float kPi = 3.14159265358979323846f;
constexpr float kRadToDeg = 180.0f / kPi;
constexpr float kDegToRad = kPi / 180.0f;

// Pitch limits to prevent gimbal flip
constexpr float kMinPitch = -1.10f; // Look up limit (~-63°)
constexpr float kMaxPitch = 1.30f;  // Look down limit (~+74°)

CameraController::CameraController()
{
    setMode(CameraMode::Classic);
}

void CameraController::setMode(CameraMode mode)
{
    m_mode = mode;
}

void CameraController::toggleCameraMode()
{
    if (m_mode == CameraMode::ActionOrbit)
    {
        setMode(CameraMode::OverTheShoulder);
    }
    else
    {
        setMode(CameraMode::ActionOrbit);
    }
}

float CameraController::getTargetDistance() const
{
    switch (m_mode)
    {
    case CameraMode::OverTheShoulder:
        return 1.75f; // Close perspective (Resident Evil 2 Remake style)
    case CameraMode::Classic:
        return 4.2f;  // Original PS2 distance
    case CameraMode::ActionOrbit:
    default:
        return targetArmLength; // Default ~3.6m (Elden Ring / Mario Odyssey style)
    }
}

float CameraController::getTargetFov() const
{
    switch (m_mode)
    {
    case CameraMode::OverTheShoulder:
        return 65.0f; // Tighter, cinematic FOV
    case CameraMode::Classic:
        return 70.0f;
    case CameraMode::ActionOrbit:
    default:
        return 78.0f; // Expansive modern action RPG FOV
    }
}

Vector3f CameraController::getShoulderOffset() const
{
    if (m_mode == CameraMode::OverTheShoulder)
    {
        // Offset to the right side of Hector's head/shoulder (X: +0.48m, Y: +0.15m)
        Vector3f right = getRightVector();
        return right * 0.48f;
    }
    return {0.0f, 0.0f, 0.0f};
}

float CameraController::getTargetHeightOffset() const
{
    switch (m_mode)
    {
    case CameraMode::OverTheShoulder:
        return 1.45f; // Eye/shoulder line
    case CameraMode::Classic:
        return 1.6f;
    case CameraMode::ActionOrbit:
    default:
        return 1.35f; // Center of mass / chest line
    }
}

Vector3f CameraController::getForwardVector() const
{
    // Horizontal forward vector (ignoring pitch for character locomotion)
    return {std::sin(m_yaw), 0.0f, std::cos(m_yaw)};
}

Vector3f CameraController::getRightVector() const
{
    // Horizontal right vector (perpendicular to forward)
    return {std::cos(m_yaw), 0.0f, -std::sin(m_yaw)};
}

void CameraController::update(float deltaTime, const Vector3f& targetPosition, float inputYawDelta, float inputPitchDelta)
{
    // Apply input rotations with invert settings
    float dy = inputYawDelta * (invertX ? -1.0f : 1.0f);
    float dp = inputPitchDelta * (invertY ? -1.0f : 1.0f);

    m_yaw += dy;
    m_pitch += dp;

    // Wrap yaw into [-pi, +pi]
    while (m_yaw > kPi) m_yaw -= 2.0f * kPi;
    while (m_yaw < -kPi) m_yaw += 2.0f * kPi;

    // Clamp pitch
    m_pitch = std::clamp(m_pitch, kMinPitch, kMaxPitch);

    // Calculate desired look-at point (Hector's position + height offset + shoulder offset)
    Vector3f desiredLookAt = targetPosition;
    desiredLookAt.y += getTargetHeightOffset();
    desiredLookAt = desiredLookAt + getShoulderOffset();

    // Smoothly interpolate look-at target
    float lookAtSmoothing = std::clamp(deltaTime * 18.0f, 0.0f, 1.0f);
    m_currentLookAt = m_currentLookAt + (desiredLookAt - m_currentLookAt) * lookAtSmoothing;

    // Smoothly interpolate distance and FOV
    float targetDist = getTargetDistance();
    float targetFov = getTargetFov();
    float fovSmoothing = std::clamp(deltaTime * 10.0f, 0.0f, 1.0f);
    m_currentDistance += (targetDist - m_currentDistance) * fovSmoothing;
    m_currentFov += (targetFov - m_currentFov) * fovSmoothing;

    // Compute spherical position offset from look-at target
    float cosPitch = std::cos(m_pitch);
    float sinPitch = std::sin(m_pitch);
    float sinYaw = std::sin(m_yaw);
    float cosYaw = std::cos(m_yaw);

    Vector3f offset{
        -m_currentDistance * cosPitch * sinYaw,
         m_currentDistance * sinPitch,
        -m_currentDistance * cosPitch * cosYaw
    };

    Vector3f desiredCameraPos = m_currentLookAt + offset;

    // Smooth camera motion
    float posSmoothing = std::clamp(deltaTime * 24.0f, 0.0f, 1.0f);
    m_currentPosition = m_currentPosition + (desiredCameraPos - m_currentPosition) * posSmoothing;
}

} // namespace NobleArchimedes
