#include "../src/camera/camera_controller.hpp"

int main()
{
    NobleArchimedes::CameraController camera;
    return camera.getMode() == NobleArchimedes::CameraMode::Classic ? 0 : 1;
}
