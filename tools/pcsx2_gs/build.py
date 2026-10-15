"""Isolated consumer build using existing MSVC/SDK, no upstream mutation."""
from pathlib import Path
import os,json,hashlib,subprocess,sys,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/fps60/pcsx2_gs_consumer_v1';SRC=ROOT/'output/reference_sources/pcsx2';OWN=Path(__file__).parent
VC=Path('C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.40.33807')
SDK=Path('C:/Program Files (x86)/Windows Kits/10');SDKVER='10.0.22621.0'
def environment():
 env=os.environ.copy();env['PATH']=str(VC/'bin/Hostx64/x64')+';'+str(SDK/'bin'/SDKVER/'x64')+';'+env['PATH']
 env['INCLUDE']=';'.join(map(str,[VC/'include',*[SDK/'Include'/SDKVER/a for a in ['ucrt','um','shared','winrt','cppwinrt']]]))
 env['LIB']=';'.join(map(str,[VC/'lib/x64',SDK/'Lib'/SDKVER/'ucrt/x64',SDK/'Lib'/SDKVER/'um/x64']))
 return env
def run(name,cmd):
 cmd=list(map(str,cmd))
 initial=name;attempt=1
 while (OUT/(name+'.log')).exists():attempt+=1;name=initial+'_attempt'+str(attempt)
 OUT.mkdir(parents=True,exist_ok=True);(OUT/(name+'.command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
 with (OUT/(name+'.log')).open('w') as log:p=subprocess.run(list(map(str,cmd)),env=environment(),cwd=OUT,stdout=log,stderr=subprocess.STDOUT)
 print(name,'exit',p.returncode,flush=True)
 if p.returncode:print((OUT/(name+'.log')).read_text(errors='replace')[-4000:]);raise SystemExit(p.returncode)
 return p
def toolchain():
 bin=OUT/'bin';bin.mkdir(exist_ok=True)
 source=OWN/'toolchain_check.cpp';exe=bin/'toolchain_check.exe'
 run('toolchain_compile',[VC/'bin/Hostx64/x64/cl.exe','/nologo','/std:c++20','/EHsc','/MD','/O2',source,'/Fo'+str(OUT/'toolchain_check.obj'),'/Fe'+str(exe),'/link','d3d11.lib'])
 run('toolchain_run',[exe])
 files=[source,exe,VC/'bin/Hostx64/x64/cl.exe',VC/'include/vector',VC/'lib/x64/msvcrt.lib',VC/'lib/x64/msvcprt.lib']
 (OUT/'toolchain.proof.json').write_text(json.dumps({'status':'ACTUAL_MSVC_CRT_STL_AND_D3D11_HARDWARE_GREEN','vc':str(VC),'sdk':SDKVER,'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+'\n')
def consumer():
 assert subprocess.check_output(['git','-C',str(SRC),'rev-parse','HEAD'],text=True).strip()=='646df006a4688063e56c0826e7ea4b8bb0c112c4'
 deps=next((OUT/'official_dependencies').rglob('include/png.h')).parent.parent
 build=OUT/'build_v2';build.mkdir(exist_ok=True);(build/'generated').mkdir(exist_ok=True)
 sourceText=(SRC/'pcsx2/CMakeLists.txt').read_text()
 def listing(name):return re.search(r'set\('+name+r'\s+(.*?)\)',sourceText,re.S)[1].split()
 gs=[s for s in listing('pcsx2GSSources') if s!='GS/GSCapture.cpp']+listing('pcsx2GSSourcesUnshared')
 gs+=['GS/Renderers/SW/GSDrawScanlineCodeGenerator.all.cpp','GS/Renderers/SW/GSSetupPrimCodeGenerator.all.cpp']
 gs+=[str(p.relative_to(SRC/'pcsx2')).replace('\\','/') for sub in ['DX11','DX12'] for p in (SRC/'pcsx2/GS/Renderers'/sub).glob('*.cpp')]
 sources=[SRC/'pcsx2'/p for p in gs]+[SRC/'pcsx2/Pcsx2Config.cpp']
 common=['AlignedMalloc','Assertions','Console','DynamicLibrary','Error','FileSystem','HostSys','Image','MD5Digest','MemorySettingsInterface','ProgressCallback','ReadbackSpinManager','Semaphore','SettingsWrapper','SmallString','StringUtil','TextureDecompress','Timer','WindowInfo','Perf','MemoryInterface']
 sources += [SRC/'common'/(p+'.cpp') for p in common]
 sources += [SRC/'common'/p for p in ['Windows/WinThreads.cpp','Windows/WinHostSys.cpp','Windows/WinMisc.cpp','StackWalker.cpp','FastJmp.cpp','FastJmp.asm']]
 sources += list((SRC/'common/emitter').glob('*.cpp'))
 sources += [SRC/'3rdparty/imgui/src'/p for p in ['imgui.cpp','imgui_draw.cpp','imgui_tables.cpp','imgui_widgets.cpp','imgui_freetype.cpp']]
 sources += [SRC/'3rdparty/D3D12MemAlloc/src/D3D12MemAlloc.cpp']
 assert all(p.is_file() for p in sources)
 (build/'sources.cmake').write_text('set(NOBLE_GS_SOURCES\n'+''.join(' "'+p.as_posix()+'"\n' for p in sources)+')\n')
 before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
 (OUT/'upstream_source_before.json').write_text(json.dumps(before,indent=2)+'\n')
 run('configure',['cmake','-S',OWN.as_posix(),'-B',build.as_posix(),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_COMPILER='+(VC/'bin/Hostx64/x64/cl.exe').as_posix(),'-DCMAKE_C_COMPILER='+(VC/'bin/Hostx64/x64/cl.exe').as_posix(),'-DPCSX2_SOURCE='+SRC.as_posix(),'-DPCSX2_DEPS='+deps.as_posix()])
 run('consumer_build',['cmake','--build',build,'--parallel','4'])
 assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items())
 dll=OUT/'bin/noble_pcsx2_gs.dll';assert dll.is_file()
 for p in (deps/'bin').glob('*.dll'):
  # Dependency closure stays private to this module; never overwrite installed binaries.
  (OUT/'bin'/p.name).write_bytes(p.read_bytes())
 (OUT/'consumer.build_proof.json').write_text(json.dumps({'status':'REAL_UPSTREAM_GS_DLL_BUILT_NO_EMULATOR_EXECUTION','sources':before,'dll_sha256':hashlib.sha256(dll.read_bytes()).hexdigest()},indent=2)+'\n')
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='toolchain':toolchain()
 elif len(sys.argv)>1 and sys.argv[1]=='consumer':consumer()
 else:raise SystemExit('use toolchain or consumer')
