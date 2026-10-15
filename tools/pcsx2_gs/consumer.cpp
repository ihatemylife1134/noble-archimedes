#include "pcsx2_gs_abi.h"
#include "GS/GS.h"
#include "GS/GSState.h"
#include "GS/Renderers/Common/GSRenderer.h"
#include "GS/Renderers/DX11/GSDevice11.h"
#include "Config.h"
#include "ImGui/ImGuiManager.h"
#include <array>
#include <vector>
#include <mutex>
#include <memory>
#include <string>
#include <cstring>
#include <stdexcept>
#include <limits>

namespace {
std::mutex guard;
struct ErrorText {
 std::array<char,2048> text{};
 void operator=(const char* s) noexcept {if(!s)s="unknown error";const auto n=std::min(std::strlen(s),text.size()-1);std::memcpy(text.data(),s,n);text[n]=0;}
 size_t size() const noexcept{return std::strlen(text.data());}
 const char* data() const noexcept{return text.data();}
} failure;
struct Session {
 alignas(16) GSPrivRegSet registers{};
 std::array<std::vector<u8>,4> fragments;
 std::vector<u8> image;
 uintptr_t token=0;
 wil::com_ptr_nothrow<ID3D11Query> completion;
 uint64_t epoch=0,frameEpoch=~uint64_t(0);
 uint32_t requestWidth=0,requestHeight=0,frameWidth=0,frameHeight=0;
 std::vector<u32> frame;
 NoblePcsx2GsPrivRegs lastPriv{};
};
std::unique_ptr<Session> active;
uintptr_t nextToken=1;
template<class F> int32_t protect(F&& fn) noexcept {
 try {std::lock_guard lock(guard);
  try{return fn();}
  catch(const std::exception& e){failure=e.what();return NOBLE_GS_INTERNAL_ERROR;}
  catch(...){failure="unknown exception inside GS consumer";return NOBLE_GS_INTERNAL_ERROR;}
 }catch(...){return NOBLE_GS_INTERNAL_ERROR;} // Even a mutex failure cannot cross C ABI.
}
bool valid(NoblePcsx2GsInstance h){return active&&h==reinterpret_cast<void*>(active->token);}
template<class F> int32_t use(NoblePcsx2GsInstance h,F&& fn,bool allowPath1=false){return protect([&]()->int32_t{
 if(!valid(h)){failure="invalid or closed GS instance";return NOBLE_GS_INVALID_ARGUMENT;}
 if(!allowPath1&&(!active->fragments[0].empty()||!active->image.empty())){failure="incomplete PATH1/image input: operation would overtake withheld input";return NOBLE_GS_UNSUPPORTED;}
 return fn();});}
void finishGpu(){
 auto* dev=GSDevice11::GetInstance();auto* context=dev->GetD3DContext();context->End(active->completion.get());context->Flush();
 const auto start=GetTickCount64();HRESULT hr;
 while((hr=context->GetData(active->completion.get(),nullptr,0,0))==S_FALSE){
  if(GetTickCount64()-start>10000)throw std::runtime_error("D3D11 GPU completion timed out");
  SwitchToThread();
 }
 if(FAILED(hr))throw std::runtime_error("D3D11 GPU completion query failed");
}
const char* identity(){return "PCSX2 GS 646df006a4688063e56c0826e7ea4b8bb0c112c4 D3D11 surfaceless C ABI1";}
int32_t lastError(char* dst,uint32_t size){return protect([&]()->int32_t{if(!dst||!size)return NOBLE_GS_INVALID_ARGUMENT;const auto n=std::min<size_t>(failure.size(),size-1);std::memcpy(dst,failure.data(),n);dst[n]=0;return NOBLE_GS_OK;});}
bool cleanup() noexcept {
 try{GSclose();return true;}catch(...){
  // Preserve ownership ordering: renderer/texture-cache, ImGui, then GPU device.
  g_gs_renderer.reset();
  try{ImGuiManager::Shutdown(true);}catch(...){}
  if(g_gs_device){try{g_gs_device->Destroy();}catch(...){}g_gs_device.reset();}
  return false;
 }
}
int32_t open(const NoblePcsx2GsConfig* c,NoblePcsx2GsInstance* out){return protect([&]()->int32_t{
 if(!out)return NOBLE_GS_INVALID_ARGUMENT;*out=nullptr;
 if(!c||c->size!=sizeof(*c)||c->renderer!=NOBLE_GS_D3D11_SURFACELESS||!c->resources_utf8||!c->width||!c->height||c->width>8192||c->height>8192||c->flags||c->reserved)return NOBLE_GS_INVALID_ARGUMENT;
 if(active)return NOBLE_GS_ALREADY_OPEN;
 EmuFolders::Resources=c->resources_utf8;
 if(!nextToken)return NOBLE_GS_UNAVAILABLE;
 auto s=std::make_unique<Session>();s->token=nextToken++;
 struct Rollback {bool armed=true;~Rollback(){if(armed)cleanup();}} rollback;
 Pcsx2Config::GSOptions options;options.Renderer=GSRendererType::DX11;options.UpscaleMultiplier=1.0f;
 if(!GSopen(options,GSRendererType::DX11,reinterpret_cast<u8*>(&s->registers),GSVSyncMode::Disabled,false)){failure="upstream GSopen D3D11 failed; inspect consumer stderr";return NOBLE_GS_UNAVAILABLE;}
 D3D11_QUERY_DESC query{D3D11_QUERY_EVENT,0};
 if(FAILED(GSDevice11::GetInstance()->GetD3DDevice()->CreateQuery(&query,s->completion.put()))){failure="D3D11 completion query creation failed";return NOBLE_GS_UNAVAILABLE;}
 GSreset(true);*out=reinterpret_cast<void*>(s->token);active=std::move(s);rollback.armed=false;return NOBLE_GS_OK;
});}
int32_t close(NoblePcsx2GsInstance h){return use(h,[&]()->int32_t{const bool clean=cleanup();active.reset();if(!clean){failure="GS teardown required exception cleanup";return NOBLE_GS_INTERNAL_ERROR;}return NOBLE_GS_OK;},true);}
int32_t reset(NoblePcsx2GsInstance h){return use(h,[&]()->int32_t{GSreset(true);for(auto& a:active->fragments)a.clear();active->image.clear();++active->epoch;return NOBLE_GS_OK;},true);}
void transfer(unsigned path,const u8* p,uint32_t qwc){
 switch(path){case 0:g_gs_renderer->Transfer<0>(p,qwc);break;case 1:GSgifTransfer2(const_cast<u8*>(p),qwc);break;case 2:GSgifTransfer3(const_cast<u8*>(p),qwc);break;case 3:GSgifTransfer(p,qwc);break;default:throw std::invalid_argument("GIF path");}
}
int32_t raw(NoblePcsx2GsInstance h,uint32_t path,const uint8_t* data,uint32_t bytes){return use(h,[&]()->int32_t{
 if(path<1||path>3||(!data&&bytes)||bytes>64u*1024u*1024u)return NOBLE_GS_INVALID_ARGUMENT;
 if(!active->image.empty()){failure="physical path input while standalone image is incomplete";return NOBLE_GS_UNSUPPORTED;}
 if(path!=1&&!active->fragments[0].empty()){failure="cross-path input while PATH1 packet is incomplete";return NOBLE_GS_UNSUPPORTED;}
 if(!bytes)return NOBLE_GS_OK;auto& b=active->fragments[path-1];
 if(b.size()+bytes>64u*1024u*1024u)return NOBLE_GS_INVALID_ARGUMENT;
 b.insert(b.end(),data,data+bytes);++active->epoch;
 if(path==1){
  // Upstream Transfer<0> resets incomplete nloop and stops at EOP. Feed only
  // complete EOP-delimited packets; reject other operations while withheld.
  size_t done=0,cursor=0;
  while(b.size()-cursor>=16){
   uint64_t lo;std::memcpy(&lo,b.data()+cursor,8);const auto n=lo&0x7fff;const auto flg=(lo>>58)&3;const auto r=((lo>>60)&15)?((lo>>60)&15):16;
   const size_t qwc=n?(flg==0?n*r:flg==1?(n*r+1)/2:n):0;
   const auto total=(1+qwc)*16;if(b.size()-cursor<total)break;cursor+=total;
   if(lo&(1ull<<15)){transfer(0,b.data()+done,uint32_t((cursor-done)/16));done=cursor;}
  }
  b.erase(b.begin(),b.begin()+done);return NOBLE_GS_OK;
 }
 const auto whole=b.size()&~size_t(15);if(whole)transfer(path-1,b.data(),uint32_t(whole/16));b.erase(b.begin(),b.begin()+whole);return NOBLE_GS_OK;
},true);}
int32_t reg(NoblePcsx2GsInstance h,uint32_t address,uint64_t value){return use(h,[&]()->int32_t{
 if(address>0x7f)return NOBLE_GS_INVALID_ARGUMENT;
 alignas(16) uint64_t packet[4]={1ull|(1ull<<15)|(1ull<<60),0xe,value,address};transfer(3,reinterpret_cast<u8*>(packet),2);++active->epoch;return NOBLE_GS_OK;
});}
int32_t image(NoblePcsx2GsInstance h,const uint8_t* p,uint32_t bytes){return use(h,[&]()->int32_t{
 if(!active->fragments[0].empty()){failure="standalone image while PATH1 packet is incomplete";return NOBLE_GS_UNSUPPORTED;}
 if((!p&&bytes)||bytes>64u*1024u*1024u)return NOBLE_GS_INVALID_ARGUMENT;if(!bytes)return NOBLE_GS_OK;
 auto& b=active->image;b.insert(b.end(),p,p+bytes);const auto whole=b.size()&~size_t(15);size_t done=0;
 while(done<whole){const auto qwc=std::min<size_t>((whole-done)/16,32767);std::vector<uint64_t> packet(2+qwc*2);packet[0]=qwc|(1ull<<15)|(2ull<<58);std::memcpy(packet.data()+2,b.data()+done,qwc*16);transfer(3,reinterpret_cast<u8*>(packet.data()),uint32_t(1+qwc));done+=qwc*16;}
 b.erase(b.begin(),b.begin()+whole);++active->epoch;return NOBLE_GS_OK;
},true);}
int32_t privileged(NoblePcsx2GsInstance h,const NoblePcsx2GsPrivRegs* p){return use(h,[&]()->int32_t{
 if(!p)return NOBLE_GS_INVALID_ARGUMENT;
 static_assert(sizeof(NoblePcsx2GsPrivRegs)==19*8);
 if(std::memcmp(&active->lastPriv,p,sizeof(*p))==0)return NOBLE_GS_OK;
 if(!active->fragments[0].empty()||!active->image.empty()){failure="privileged register change while PATH1/image input is incomplete";return NOBLE_GS_UNSUPPORTED;}
 auto& r=active->registers;
 auto copy=[](auto& field,uint64_t v){static_assert(sizeof(field)==8);std::memcpy(&field,&v,8);};
 copy(r.PMODE,p->pmode);copy(r.SMODE1,p->smode1);copy(r.SMODE2,p->smode2);copy(r.SRFSH,p->srfsh);copy(r.SYNCH1,p->synch1);copy(r.SYNCH2,p->synch2);copy(r.SYNCV,p->syncv);
 copy(r.DISP[0].DISPFB,p->dispfb1);copy(r.DISP[0].DISPLAY,p->display1);copy(r.DISP[1].DISPFB,p->dispfb2);copy(r.DISP[1].DISPLAY,p->display2);
 copy(r.EXTBUF,p->extbuf);copy(r.EXTDATA,p->extdata);copy(r.EXTWRITE,p->extwrite);copy(r.BGCOLOR,p->bgcolor);copy(r.CSR,p->csr);copy(r.IMR,p->imr);copy(r.BUSDIR,p->busdir);copy(r.SIGLBLID,p->siglblid);active->lastPriv=*p;++active->epoch;return NOBLE_GS_OK;
},true);}
int32_t flush(NoblePcsx2GsInstance h){return use(h,[&]()->int32_t{g_gs_renderer->Flush(GSState::GSTRANSFER);finishGpu();return NOBLE_GS_OK;});}
int32_t fifo(NoblePcsx2GsInstance h,uint8_t* p,uint32_t bytes){return use(h,[&]()->int32_t{
 if((!p&&bytes)||(bytes&15)||bytes>64u*1024u*1024u)return NOBLE_GS_INVALID_ARGUMENT;if(bytes)GSInitAndReadFIFO(p,bytes/16);return NOBLE_GS_OK;
});}
int32_t vsync(NoblePcsx2GsInstance h,uint32_t field,uint32_t changed){return use(h,[&]()->int32_t{if(field>1||changed>1)return NOBLE_GS_INVALID_ARGUMENT;GSvsync(field,changed!=0);++active->epoch;return NOBLE_GS_OK;});}
int32_t rgba(NoblePcsx2GsInstance h,uint32_t width,uint32_t height,uint8_t* p,uint64_t capacity,NoblePcsx2GsFrame* out){return use(h,[&]()->int32_t{
 if(!out||out->size!=sizeof(*out)||!width||!height||width>8192||height>8192)return NOBLE_GS_INVALID_ARGUMENT;
 if(active->frameEpoch!=active->epoch||active->requestWidth!=width||active->requestHeight!=height){
  std::vector<u32> pixels;u32 w=0,hh=0;if(!GSSaveSnapshotToMemory(width,height,false,false,&w,&hh,&pixels))return NOBLE_GS_UNAVAILABLE;
  active->frame=std::move(pixels);active->frameWidth=w;active->frameHeight=hh;active->requestWidth=width;active->requestHeight=height;active->frameEpoch=active->epoch;
 }
 out->width=active->frameWidth;out->height=active->frameHeight;out->stride_bytes=out->width*4;out->required_bytes=uint64_t(out->width)*out->height*4;
 if(!p||capacity<out->required_bytes)return NOBLE_GS_BUFFER_TOO_SMALL;std::memcpy(p,active->frame.data(),out->required_bytes);return NOBLE_GS_OK;
});}
bool format(uint32_t psm,uint32_t bp,uint32_t bw,uint32_t x,uint32_t y){return psm<64&&GSLocalMemory::m_psm[psm].rp&&bp<16384&&bw>0&&bw<64&&x<2048&&y<2048;}
int32_t readPixel(NoblePcsx2GsInstance h,uint32_t psm,uint32_t bp,uint32_t bw,uint32_t x,uint32_t y,uint32_t* out){return use(h,[&]()->int32_t{
 if(!out||!format(psm,bp,bw,x,y))return NOBLE_GS_INVALID_ARGUMENT;g_gs_renderer->Flush(GSState::DOWNLOADFIFO);
 GIFRegBITBLTBUF blit{};blit.SBP=bp;blit.SBW=bw;blit.SPSM=psm;g_gs_renderer->InvalidateLocalMem(blit,GSVector4i(x,y,x+1,y+1));
 auto& mem=g_gs_renderer->m_mem;*out=(mem.*GSLocalMemory::m_psm[psm].rp)(x,y,bp,bw);return NOBLE_GS_OK;
});}
int32_t writePixel(NoblePcsx2GsInstance h,uint32_t psm,uint32_t bp,uint32_t bw,uint32_t x,uint32_t y,uint32_t value){return use(h,[&]()->int32_t{
 if(!format(psm,bp,bw,x,y))return NOBLE_GS_INVALID_ARGUMENT;g_gs_renderer->Flush(GSState::GSTRANSFER);
 GIFRegBITBLTBUF blit{};blit.DBP=bp;blit.DBW=bw;blit.DPSM=psm;g_gs_renderer->InvalidateVideoMem(blit,GSVector4i(x,y,x+1,y+1));
 auto& mem=g_gs_renderer->m_mem;(mem.*GSLocalMemory::m_psm[psm].wp)(x,y,value,bp,bw);++active->epoch;return NOBLE_GS_OK;
});}
int32_t snapshot(NoblePcsx2GsInstance h,uint8_t* p,uint32_t bytes){return use(h,[&]()->int32_t{
 if(!p||bytes<GSLocalMemory::m_vmsize)return NOBLE_GS_BUFFER_TOO_SMALL;g_gs_renderer->Flush(GSState::SAVESTATE);
 GIFRegBITBLTBUF blit{};blit.SBW=16;g_gs_renderer->InvalidateLocalMem(blit,GSVector4i(0,0,1024,1024));std::memcpy(p,g_gs_renderer->m_mem.m_vm8,GSLocalMemory::m_vmsize);return NOBLE_GS_OK;
});}
}
extern "C" __declspec(dllexport) int32_t NOBLE_GS_CALL noble_pcsx2_gs_query_api(uint32_t version,uint32_t size,NoblePcsx2GsApi* api){
 if(version!=1||size!=sizeof(*api)||!api)return NOBLE_GS_ABI_MISMATCH;
 const NoblePcsx2GsApi table={sizeof(*api),1,&identity,&lastError,&open,&close,&reset,&raw,&reg,&image,&privileged,&flush,&fifo,&vsync,&rgba,&readPixel,&writePixel,&snapshot};*api=table;return NOBLE_GS_OK;
}
