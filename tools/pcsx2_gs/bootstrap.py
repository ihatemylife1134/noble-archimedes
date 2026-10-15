"""Private official-dependency acquisition; no install or upstream-tree writes."""
from pathlib import Path
import json,urllib.request,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/fps60/pcsx2_gs_consumer_v1'
URL='https://api.github.com/repos/PCSX2/pcsx2-windows-dependencies/releases/tags/latest-windows-dependencies'
def main():
 OUT.mkdir(parents=True,exist_ok=True);downloads=OUT/'downloads';downloads.mkdir(exist_ok=True)
 release=json.load(urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'Noble-GS-Consumer/1'})))
 asset=next(a for a in release['assets'] if a['name']=='pcsx2-windows-dependencies.7z')
 (OUT/'dependency_release.json').write_text(json.dumps(release,indent=2)+'\n')
 archive=downloads/asset['name'];digest=asset['digest'].split(':',1)[1]
 if not archive.exists() or archive.stat().st_size!=asset['size']:
  print('Downloading official dependencies',asset['size'],'bytes',flush=True)
  with (OUT/'dependency_download.log').open('a') as log:
   p=subprocess.run(['curl.exe','-L','--fail','--retry','2','--connect-timeout','20','--max-time','180','-C','-','-o',str(archive),asset['browser_download_url']],stdout=log,stderr=log)
  assert p.returncode==0,'official download incomplete; preserved for resume'
 actual=hashlib.sha256(archive.read_bytes()).hexdigest();assert actual==digest,(actual,digest)
 extract=OUT/'official_dependencies';extract.mkdir(exist_ok=True)
 p=subprocess.run(['7z','x','-y','-o'+str(extract),str(archive)],capture_output=True,text=True)
 (OUT/'dependency_extract.log').write_text(p.stdout+p.stderr);assert p.returncode==0
 (OUT/'dependency_package.proof.json').write_text(json.dumps({'url':asset['browser_download_url'],'size':asset['size'],'sha256':actual,'extract':str(extract),'status':'OFFICIAL_PACKAGE_SHA256_VERIFIED'},indent=2)+'\n')
 print('Official dependencies verified and privately extracted',flush=True)
if __name__=='__main__':main()
