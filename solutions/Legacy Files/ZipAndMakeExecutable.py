import os
import zipfile
import sys
import time
import tarfile

executables = ['tModLoaderServer', 'tModLoader', 'open-folder', 'tModLoaderServer.bin.x86', 'tModLoaderServer.bin.x86_64', 'tModLoader.bin.x86', 'tModLoader.bin.x86_64', 'tModLoaderServer.bin.osx', 'tModLoaderServer.bin.osx']
extra = None

def set_permissions(tarinfo):
    filename = os.path.basename(tarinfo.name)
    #print("Deciding for " + tarinfo.name)
    if filename in executables:
        print("Execute permissions set for " + tarinfo.name)
        #tarinfo.mode = 0o100777 << 16 # 0777 # for example
        tarinfo.mode = 0o777
    return tarinfo


def zipdir(path, filename):
    # Ensure the base path is absolute
    base_path = os.path.abspath(path)

    # Prevent path traversal for the ZIP file itself
    filename = os.path.abspath(filename)
    if not filename.startswith(base_path):
        raise ValueError(f"Path traversal attempt detected for zipfile: {filename}")

    # Create the ZIP file
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as ziph:
        # ziph is zipfile handle
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                file = os.path.join(root, filename)
                destination = os.path.relpath(file, base_path)
                if extra:
                    destination = os.path.join(extra, destination)

                # Prevent path traversal by validating the destination
                if not os.path.abspath(os.path.join(base_path, destination)).startswith(base_path):
                    raise ValueError(f"Path traversal attempt detected: {destination}")

                # Prevent symlink traversal by validating the resolved file path
                real_file = os.path.realpath(file)
                if not real_file.startswith(base_path):
                    raise ValueError(f"Symlink traversal attempt detected: {real_file}")
                
                print("Zipping " + file)
                if executables and filename in executables:
                    with open(real_file, 'rb') as f:
                        bytes_content = f.read()
                    
                    info = zipfile.ZipInfo(destination)
                    info.date_time = time.localtime()[:6]
                    info.external_attr = 0o100777 << 16
                    print("Execute permissions set for " + file)
                    
                    ziph.writestr(info, bytes_content, zipfile.ZIP_DEFLATED)
                else:
                    ziph.write(real_file, destination)
            
if __name__ == '__main__':
    if(len(sys.argv) != 3 and len(sys.argv) != 4):
        print("[FolderName] [ZipFileName] [Relative] arguments needed")
        sys.exit()
        
    foldername = sys.argv[1]
    zipfilename = sys.argv[2]
    if len(sys.argv) == 4:
        extra = sys.argv[3] 

    if ".zip" in zipfilename:
        zipf = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
        zipdir(foldername, zipf)
        zipf.close()
    elif ".tar.gz" in zipfilename:
        tar = tarfile.open(zipfilename, 'w:gz')
        tar.add(foldername, arcname="", filter=set_permissions) #tar the entire folder 
        tar.close()
    else:
        print("Something went wrong")
    