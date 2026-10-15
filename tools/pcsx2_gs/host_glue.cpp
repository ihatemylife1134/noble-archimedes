/* Consumer host services only. No upstream EE/VU/IOP execution or VM startup. */
#include "Host.h"
#include "GS/GS.h"
#include "GS/GSCapture.h"
#include "GS/Renderers/Common/GSDevice.h"
#include "ImGui/ImGuiManager.h"
#include "ImGui/FullscreenUI.h"
#include "VMManager.h"
#include "GSDumpReplayer.h"
#include "PerformanceMetrics.h"
#include "imgui.h"
#include "R5900.h"
#include "DebugTools/Debug.h"
#include "SIO/Pad/Pad.h"
#include "USB/USB.h"
#include "Host/AudioStream.h"
#include "common/HostSys.h"
#include <stdexcept>
#include <cstdio>

namespace Host {
std::optional<WindowInfo> AcquireRenderWindow(bool){WindowInfo w;w.type=WindowInfo::Type::Surfaceless;w.surface_width=640;w.surface_height=480;w.surface_scale=1;return w;}
void ReleaseRenderWindow(){}
void BeginPresentFrame(){}
bool IsFullscreen(){return false;}
void SetFullscreen(bool){}
void RequestResizeHostDisplay(s32,s32){}
void OnCaptureStarted(const std::string&){}
void OnCaptureStopped(){}
void ReportErrorAsync(const std::string_view title,const std::string_view msg){std::fprintf(stderr,"[pcsx2-gs] %.*s: %.*s\n",int(title.size()),title.data(),int(msg.size()),msg.data());}
void ReportInfoAsync(const std::string_view title,const std::string_view msg){ReportErrorAsync(title,msg);}
const char* TranslateToCString(const std::string_view,const std::string_view text){return text.data();}
std::string_view TranslateToStringView(const std::string_view,const std::string_view text){return text;}
std::string TranslateToString(const std::string_view,const std::string_view text){return std::string(text);}
void AddOSDMessage(std::string text,float){ReportInfoAsync("GS",text);}
void AddKeyedOSDMessage(std::string,std::string text,float){ReportInfoAsync("GS",text);}
void AddIconOSDMessage(std::string,const char*,const std::string_view text,float){ReportInfoAsync("GS",text);}
void RemoveKeyedOSDMessage(std::string){}
bool GetBaseBoolSettingValue(const char*,const char*,bool value){return value;}
int GetBaseIntSettingValue(const char*,const char*,int value){return value;}
uint GetBaseUIntSettingValue(const char*,const char*,uint value){return value;}
float GetBaseFloatSettingValue(const char*,const char*,float value){return value;}
std::string GetBaseStringSettingValue(const char*,const char*,const char* value){return value;}
bool GetBoolSettingValue(const char*,const char*,bool value){return value;}
std::string GetStringSettingValue(const char*,const char*,const char* value){return value;}
}
namespace ImGuiManager {
bool Initialize(){if(!ImGui::GetCurrentContext())ImGui::CreateContext();auto& io=ImGui::GetIO();io.IniFilename=nullptr;io.DisplaySize=ImVec2(640,480);io.DeltaTime=1.0f/60.0f;io.BackendFlags|=ImGuiBackendFlags_RendererHasTextures|ImGuiBackendFlags_RendererHasVtxOffset;io.Fonts->AddFontDefault();ImGui::NewFrame();return true;}
void Shutdown(bool){if(ImGui::GetCurrentContext())ImGui::DestroyContext();}
void WindowResized(){}
void RequestScaleUpdate(){}
void ReloadFonts(){}
void NewFrame(){ImGui::NewFrame();}
void SkipFrame(){if(ImGui::GetCurrentContext()){ImGui::EndFrame();ImGui::NewFrame();}}
void RenderOSD(){}
float GetWindowWidth(){return 640;}
float GetWindowHeight(){return 480;}
float GetGlobalScale(){return 1;}
}
namespace FullscreenUI {void Render(){}bool IsInitialized(){return false;}bool HasActiveWindow(){return false;}}
namespace GSDumpReplayer {bool IsReplayingDump(){return false;}void RenderUI(){}}
namespace VMManager {
bool HasValidVM(){return false;}
std::string GetDiscSerial(){return {};}
u32 GetDiscCRC(){return 0;}
std::string GetTitle(bool){return "Native GS consumer";}
}
namespace PerformanceMetrics {
static u64 frames=0;
u64 GetFrameNumber(){return frames;}
void Update(bool,bool,bool){++frames;}
void OnGPUPresent(float,u64,u64){}
InternalFPSMethod GetInternalFPSMethod(){return InternalFPSMethod::None;}
bool IsSavingMetrics(){return false;}
void StartSavingMetrics(u32){}
void DumpSavedMetrics(){}
void SetGSSWThreadCount(u32){}
void SetGSSWThread(u32,Threading::ThreadHandle){}
}

/* Header-created references and configuration metadata only. These storage
 * objects never execute an upstream CPU, service EE hardware, or load a VM.
 * Non-GS configuration services fail closed if accidentally invoked. */
alignas(16) cpuRegistersPack _cpuRegistersPack{};
alignas(__pagealignsize) u8 eeHw[Ps2MemSize::Hardware]{};
bool FMVstarted=false;
const char* ReportVideoMode(){return "Native GS";}
const char* ReportInterlaceMode(){return "External field source";}
double GetVerticalFrequency(){return 60.0;} // Optional GS statistics, not guest timing.
namespace { [[noreturn]] void unavailable(){throw std::runtime_error("upstream non-GS service is unavailable in GS-only consumer");} }
namespace Host {void RunOnCPUThread(std::function<void()> fn,bool){fn();}}
namespace MTGS {
void WaitGS(bool,bool,bool){unavailable();}
void RunOnGSThread(std::function<void()>){unavailable();}
void ApplySettings(){unavailable();}
void ToggleSoftwareRendering(){unavailable();}
}
namespace GSDumpReplayer {bool IsRunner(){return false;}void UpdateGSStats(){}}
namespace VMManager::Internal {const std::vector<u32>& GetSoftwareRendererProcessorList(){static const std::vector<u32> none;return none;}}
namespace SysMemory {u8* GetCodePtr(size_t){unavailable();}} // D3D11 never needs software JIT allocation.
namespace CrashHandler {void WriteDumpForCaller(){}}
namespace PageFaultHandler {HandlerResult HandlePageFault(void*,void*,bool){return HandlerResult::ExecuteNextHandler;}}
namespace Pad {
ControllerType GetDefaultPadType(u32){return ControllerType::NotConnected;}
const ControllerInfo* GetControllerInfo(ControllerType){unavailable();}
const ControllerInfo* GetControllerInfoByName(std::string_view){unavailable();}
std::string GetConfigSection(u32){unavailable();}
}
namespace USB {
s32 DeviceTypeNameToIndex(std::string_view){unavailable();}
const char* DeviceTypeIndexToName(s32){unavailable();}
std::string GetConfigSection(int){unavailable();}
}
void AudioStreamParameters::LoadSave(SettingsWrapper&,const char*){unavailable();}
std::optional<AudioBackend> AudioStream::ParseBackendName(const char*){unavailable();}
const char* AudioStream::GetBackendName(AudioBackend){unavailable();}
uint FileMcd_GetMtapPort(uint slot){return slot==1||slot>=5?1:0;}
uint FileMcd_GetMtapSlot(uint slot){return slot<5?slot-1:slot-4;}
bool FileMcd_IsMultitapSlot(uint slot){return slot>1;}
std::string FileMcd_GetDefaultName(uint){return {};}
namespace {const LogDescriptor disabledDescriptor{"GS-only", "Unavailable VM tracing", "No upstream VM execution"};}
TraceLogPack::TraceLogPack():SIF(disabledDescriptor){}
TraceLogPack::EE_PACK::EE_PACK():Bios(disabledDescriptor),Memory(disabledDescriptor),GIFtag(disabledDescriptor),VIFcode(disabledDescriptor),MSKPATH3(disabledDescriptor),R5900(disabledDescriptor),COP0(disabledDescriptor),COP1(disabledDescriptor),COP2(disabledDescriptor),Cache(disabledDescriptor),KnownHw(disabledDescriptor),UnknownHw(disabledDescriptor),DMAhw(disabledDescriptor),IPU(disabledDescriptor),DMAC(disabledDescriptor),Counters(disabledDescriptor),SPR(disabledDescriptor),VIF(disabledDescriptor),GIF(disabledDescriptor){}
TraceLogPack::IOP_PACK::IOP_PACK():Bios(disabledDescriptor),Memcards(disabledDescriptor),PAD(disabledDescriptor),R3000A(disabledDescriptor),COP2(disabledDescriptor),Memory(disabledDescriptor),KnownHw(disabledDescriptor),UnknownHw(disabledDescriptor),DMAhw(disabledDescriptor),DMAC(disabledDescriptor),Counters(disabledDescriptor),CDVD(disabledDescriptor),MDEC(disabledDescriptor){}
TraceLogPack TraceLogging;
/* Video capture is deliberately unavailable in this GS-only consumer. */
namespace GSCapture {
bool BeginCapture(float,GSVector2i,float,std::string){return false;}
bool DeliverVideoFrame(GSTexture*){return false;}
void DeliverAudioPacket(const float*){}
void EndCapture(){}
bool IsCapturing(){return false;}bool IsCapturingVideo(){return false;}bool IsCapturingAudio(){return false;}
GSVector2i GetSize(){return GSVector2i(0,0);}
std::string GetNextCaptureFileName(){return {};}
void Flush(){}
void FlushAudioOnly(){}
}
