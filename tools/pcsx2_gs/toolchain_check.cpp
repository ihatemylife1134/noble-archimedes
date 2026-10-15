#include <d3d11.h>
#include <string>
#include <vector>
#include <cstdio>
int main(){
 std::vector<std::string> proof={"MSVC STL/CRT linked","D3D11 surfaceless hardware device"};
 ID3D11Device* device=nullptr;ID3D11DeviceContext* context=nullptr;D3D_FEATURE_LEVEL level{};
 const auto hr=D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_HARDWARE,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&device,&level,&context);
 if(FAILED(hr)){std::printf("FAIL D3D11CreateDevice hr=%08x\n",unsigned(hr));return 1;}
 for(const auto& s:proof)std::puts(s.c_str());std::printf("FeatureLevel=%04x\n",unsigned(level));context->Release();device->Release();return 0;
}
