"""First acceptance test requires a real GS DLL, never a fake backend."""
from pathlib import Path
import ctypes as C,sys,unittest,struct
ROOT=Path(__file__).resolve().parents[2]
DLL=ROOT/'output/fps60/pcsx2_gs_consumer_v1/bin/noble_pcsx2_gs.dll'
class Api(C.Structure):
 _fields_=[('size',C.c_uint32),('version',C.c_uint32)]+[(n,C.c_void_p) for n in ['identity','last_error','open','close','reset','raw_gif','write_register','image','privileged','flush','read_fifo','vsync','rgba','read_vram','write_vram','snapshot_vram']]
class Config(C.Structure):
 _fields_=[('size',C.c_uint32),('renderer',C.c_uint32),('width',C.c_uint32),('height',C.c_uint32),('resources',C.c_char_p),('flags',C.c_uint32),('reserved',C.c_uint32)]
class Priv(C.Structure):
 _fields_=[(n,C.c_uint64) for n in 'pmode smode1 smode2 srfsh synch1 synch2 syncv dispfb1 display1 dispfb2 display2 extbuf extdata extwrite bgcolor csr imr busdir siglblid'.split()]
class Frame(C.Structure):
 _fields_=[('size',C.c_uint32),('width',C.c_uint32),('height',C.c_uint32),('stride',C.c_uint32),('required',C.c_uint64)]
class Consumer:
 def __init__(self):
  self.mod=C.CDLL(str(DLL));q=self.mod.noble_pcsx2_gs_query_api;q.argtypes=[C.c_uint32,C.c_uint32,C.POINTER(Api)];q.restype=C.c_int32
  self.api=Api();assert q(1,C.sizeof(Api),C.byref(self.api))==0
  self.h=C.c_void_p();cfg=Config(C.sizeof(Config),1,64,64,str(ROOT/'output/reference_sources/pcsx2/bin/resources').encode(),0,0)
  self.check(self.fn('open',C.POINTER(Config),C.POINTER(C.c_void_p))(C.byref(cfg),C.byref(self.h)))
 def fn(self,name,*types):return C.CFUNCTYPE(C.c_int32,*types)(getattr(self.api,name))
 def check(self,result):
  if result:
   e=C.create_string_buffer(2048);self.fn('last_error',C.c_void_p,C.c_uint32)(e,len(e));raise AssertionError(str(result)+': '+e.value.decode(errors='replace'))
 def reg(self,address,value):self.check(self.fn('write_register',C.c_void_p,C.c_uint32,C.c_uint64)(self.h,address,value))
 def raw(self,path,data):
  p=C.create_string_buffer(data);self.check(self.fn('raw_gif',C.c_void_p,C.c_uint32,C.c_void_p,C.c_uint32)(self.h,path,p,len(data)))
 def image(self,data):
  p=C.create_string_buffer(data);self.check(self.fn('image',C.c_void_p,C.c_void_p,C.c_uint32)(self.h,p,len(data)))
 def pixel(self,bp,x,y=0):
  out=C.c_uint32();self.check(self.fn('read_vram',C.c_void_p,*([C.c_uint32]*5),C.POINTER(C.c_uint32))(self.h,0,bp,1,x,y,C.byref(out)));return out.value
 def close(self):self.check(self.fn('close',C.c_void_p)(self.h))
def ad(registers,eop=True):return struct.pack('<QQ',len(registers)|(int(eop)<<15)|(1<<60),0xe)+b''.join(struct.pack('<QQ',v,a) for a,v in registers)
class RealModule(unittest.TestCase):
 def test_real_upstream_surfaceless_device_opens_resets_and_closes(self):
  self.assertTrue(DLL.is_file(),'real PCSX2 GS consumer DLL is not built')
  mod=C.CDLL(str(DLL)); q=mod.noble_pcsx2_gs_query_api;q.argtypes=[C.c_uint32,C.c_uint32,C.POINTER(Api)];q.restype=C.c_int32
  a=Api();self.assertEqual(q(1,C.sizeof(a),C.byref(a)),0)
  self.assertEqual(q(0,C.sizeof(a),C.byref(Api())),2)
  self.assertEqual(q(1,8,C.byref(Api())),2)
  identity=C.CFUNCTYPE(C.c_char_p)(a.identity)().decode();self.assertIn('646df006',identity);self.assertIn('PCSX2 GS',identity)
  err=C.CFUNCTYPE(C.c_int32,C.c_void_p,C.c_uint32)(a.last_error)
  error=C.create_string_buffer(2048)
  op=C.CFUNCTYPE(C.c_int32,C.POINTER(Config),C.POINTER(C.c_void_p))(a.open)
  config=Config(C.sizeof(Config),1,64,64,str(ROOT/'output/reference_sources/pcsx2/bin/resources').encode(),0,0);h=C.c_void_p()
  result=op(C.byref(config),C.byref(h));err(error,len(error));self.assertEqual(result,0,error.value.decode(errors='replace'))
  try:
   self.assertTrue(h.value)
   self.assertEqual(C.CFUNCTYPE(C.c_int32,C.c_void_p)(a.reset)(h),0)
   reg=C.CFUNCTYPE(C.c_int32,C.c_void_p,C.c_uint32,C.c_uint64)(a.write_register)
   self.assertEqual(reg(h,0x4c,1<<16),0) # actual FRAME1 path through GS.
   self.assertEqual(C.CFUNCTYPE(C.c_int32,C.c_void_p)(a.flush)(h),0)
  finally:self.assertEqual(C.CFUNCTYPE(C.c_int32,C.c_void_p)(a.close)(h),0)
 def test_actual_gs_image_fragments_all_physical_paths_and_synthetic_parser(self):
  self.assertTrue(DLL.is_file(),'real GS consumer required');gs=Consumer()
  try:
   words=(0x11223344,0x55667788,0x99aabbcc,0xddeeff00);payload=struct.pack('<4I',*words)
   for path in (1,2,3):
    bp=64+path
    packet=ad([(0x50,(bp<<32)|(1<<48)),(0x51,0),(0x52,4|(1<<32)),(0x53,0)],False)+struct.pack('<QQ',1|(1<<15)|(2<<58),0)+payload
    # Literal byte fragments split tags and IMAGE words.
    offset=0
    for length in (1,7,8,9,22,17,len(packet)-64):gs.raw(path,packet[offset:offset+length]);offset+=length
    self.assertEqual(offset,len(packet))
    self.assertEqual(tuple(gs.pixel(bp,x) for x in range(4)),words)
   # A physical PATH3 tag remains half-fed during synthesized A+D traffic.
   bp=72;packet=ad([(0x50,(bp<<32)|(1<<48)),(0x51,0),(0x52,4|(1<<32)),(0x53,0)])+struct.pack('<QQ',1|(1<<15)|(2<<58),0)+payload
   gs.raw(3,packet[:8]);gs.reg(0x4c,1<<16);gs.raw(3,packet[8:])
   self.assertEqual(tuple(gs.pixel(bp,x) for x in range(4)),words)
   gs.reg(0x50,(80<<32)|(1<<48));gs.reg(0x51,0);gs.reg(0x52,4|(1<<32));gs.reg(0x53,0)
   gs.image(payload[:3]);gs.image(payload[3:])
   self.assertEqual(tuple(gs.pixel(80,x) for x in range(4)),words)
   gs.reg(0x50,80|(1<<16));gs.reg(0x51,0);gs.reg(0x52,4|(1<<32));gs.reg(0x53,1)
   fifo=C.create_string_buffer(16);gs.check(gs.fn('read_fifo',C.c_void_p,C.c_void_p,C.c_uint32)(gs.h,fifo,16));self.assertEqual(fifo.raw,payload)
  finally:gs.close()
 def test_actual_gs_draw_privileged_snapshot_and_rgba(self):
  self.assertTrue(DLL.is_file(),'real GS consumer required');gs=Consumer()
  try:
   for addr,value in [(0x4c,1<<16),(0x4e,1<<32),(0x40,(63<<16)|(63<<48)),(0x18,0),(0x47,0),(0x46,1),(0x00,6),(0x01,0x80aa5522),(0x05,0),(0x05,(32*16)|((32*16)<<16))]:gs.reg(addr,value)
   gs.check(gs.fn('flush',C.c_void_p)(gs.h));self.assertEqual(gs.pixel(0,10,10),0x80aa5522)
   # NTSC CMOD is bits 13..14 (GSRegs); account for the real PCRTC
   # 4-dot horizontal divider and baseline display offsets, not DX=DY=0.
   p=Priv();p.pmode=1|(1<<5)|(0xff<<8);p.smode1=2<<13;p.dispfb1=1<<9;p.display1=642|(25<<12)|(3<<23)|(255<<32)|(63<<44)
   gs.check(gs.fn('privileged',C.c_void_p,C.POINTER(Priv))(gs.h,C.byref(p)));gs.check(gs.fn('vsync',C.c_void_p,C.c_uint32,C.c_uint32)(gs.h,0,1))
   frame=Frame();frame.size=C.sizeof(Frame);rgba=C.create_string_buffer(64*64*4)
   self.assertEqual(gs.fn('rgba',C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p,C.c_uint64,C.POINTER(Frame))(gs.h,64,64,None,0,C.byref(frame)),5)
   gs.check(gs.fn('rgba',C.c_void_p,C.c_uint32,C.c_uint32,C.c_void_p,C.c_uint64,C.POINTER(Frame))(gs.h,64,64,rgba,len(rgba),C.byref(frame)))
   self.assertEqual((frame.width,frame.height,frame.stride,frame.required),(64,64,256,16384));self.assertTrue(bytes((0x22,0x55,0xaa)) in rgba.raw,'rendered RGB sprite absent from RGBA snapshot')
  finally:gs.close()
 def test_pending_path1_and_image_reject_overtaking_but_identical_priv_is_nop(self):
  gs=Consumer()
  try:
   packet=ad([(0x4c,1<<16)])
   gs.raw(1,packet[:17]);p=Priv()
   self.assertEqual(gs.fn('privileged',C.c_void_p,C.POINTER(Priv))(gs.h,C.byref(p)),0)
   p.bgcolor=0xabcdef
   self.assertEqual(gs.fn('privileged',C.c_void_p,C.POINTER(Priv))(gs.h,C.byref(p)),7)
   self.assertEqual(gs.fn('flush',C.c_void_p)(gs.h),7)
   self.assertEqual(gs.fn('write_register',C.c_void_p,C.c_uint32,C.c_uint64)(gs.h,0x4c,0),7)
   other=C.create_string_buffer(ad([(0x4c,0)]))
   self.assertEqual(gs.fn('raw_gif',C.c_void_p,C.c_uint32,C.c_void_p,C.c_uint32)(gs.h,2,other,len(other.raw)-1),7)
   gs.raw(1,packet[17:]);gs.check(gs.fn('flush',C.c_void_p)(gs.h))
   gs.check(gs.fn('privileged',C.c_void_p,C.POINTER(Priv))(gs.h,C.byref(p)))
   gs.raw(1,packet[:1]);gs.check(gs.fn('reset',C.c_void_p)(gs.h));gs.check(gs.fn('flush',C.c_void_p)(gs.h))
   # Incomplete synthetic image cannot be retargeted by an intervening BITBLTBUF.
   gs.reg(0x50,(80<<32)|(1<<48));gs.reg(0x51,0);gs.reg(0x52,4|(1<<32));gs.reg(0x53,0)
   payload=struct.pack('<IIII',1,2,3,4);gs.image(payload[:3])
   self.assertEqual(gs.fn('write_register',C.c_void_p,C.c_uint32,C.c_uint64)(gs.h,0x50,0),7)
   self.assertEqual(gs.fn('flush',C.c_void_p)(gs.h),7)
   self.assertEqual(gs.fn('raw_gif',C.c_void_p,C.c_uint32,C.c_void_p,C.c_uint32)(gs.h,2,other,len(other.raw)-1),7)
   gs.image(payload[3:]);self.assertEqual(tuple(gs.pixel(80,x) for x in range(4)),(1,2,3,4))
  finally:gs.close()
 def test_stale_handles_invalid_arguments_and_reopen(self):
  gs=Consumer();old=gs.h.value;gs.close()
  self.assertEqual(gs.fn('reset',C.c_void_p)(C.c_void_p(old)),1)
  again=Consumer()
  try:
   self.assertNotEqual(old,again.h.value)
   self.assertEqual(again.fn('reset',C.c_void_p)(C.c_void_p(old)),1)
   self.assertEqual(again.fn('raw_gif',C.c_void_p,C.c_uint32,C.c_void_p,C.c_uint32)(again.h,0,None,0),1)
   self.assertEqual(again.fn('raw_gif',C.c_void_p,C.c_uint32,C.c_void_p,C.c_uint32)(again.h,1,None,1),1)
   self.assertEqual(again.fn('read_fifo',C.c_void_p,C.c_void_p,C.c_uint32)(again.h,None,17),1)
   snapshot=C.create_string_buffer(4*1024*1024);again.check(again.fn('snapshot_vram',C.c_void_p,C.c_void_p,C.c_uint32)(again.h,snapshot,len(snapshot)))
  finally:again.close()
if __name__=='__main__':unittest.main()
