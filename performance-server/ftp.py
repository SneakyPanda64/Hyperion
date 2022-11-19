import ftplib
import os

# def placeFiles(ftp, path):
#     for name in os.listdir(path):
#         localpath = os.path.join(path, name)
#         if os.path.isfile(localpath):
#             print("STOR", name, localpath)
#             ftp.cwd(path)
#             ftp.storbinary('STOR ' + name, open(localpath,'rb'))
#         elif os.path.isdir(localpath):
#             print("MKD", name)
#
#             try:
#                 ftp.mkd(name)
#
#             # ignore "directory already exists"
#             except error_perm as e:
#                 if not e.args[0].startswith('550'):
#                     raise
#
#             print("CWD", name)
#             ftp.cwd(name)
#             placeFiles(ftp, localpath)
#             print("CWD", "..")
#             ftp.cwd("..")
def recursiveFolder(ftp, path):

    for file in os.listdir(os.path.join(os.path.curdir, path)):
        if os.path.isdir(os.path.join(os.path.curdir, path, file)):
            if file not in ftp.nlst():
                ftp.mkd(file)
                ftp.cwd(file)
                recursiveFolder(ftp, os.path.join(path, file))
                ftp.cwd("../")
        else:
            with open(os.path.join(path, file), 'rb') as f:
                ftp.storbinary(f"STOR {file}", f)
def copyFolder(ftp, path):
    for file in path.split(os.sep):
        if file not in ftp.nlst():
            ftp.mkd(file)
        ftp.cwd(file)
    recursiveFolder(ftp, path)
    ftp.close()
def listScripts():
    ftp = login()
    ftp.cwd(os.path.join("scripts"))
    list = ftp.nlst()
    ftp.close()
    return list
def uploadScript(id):
    ftp = login()
    if id not in listScripts():
        copyFolder(ftp, os.path.join("scripts", id))
    else:
        return False
    ftp.close()
    return True
def login():
    try:
        ftp = ftplib.FTP(host=os.getenv("FTP_HOST"), timeout=2)
        ftp.login(user=os.getenv("FTP_USER"), passwd=os.getenv("FTP_PASS"))
    except Exception as e:
        print(e)
        return False
    return ftp