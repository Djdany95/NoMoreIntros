import os

zipEXE = 'C:/"Program Files"/7-Zip/7z.exe'
nsisEXE = 'C:/"Program Files (x86)"/NSIS/makensisw.exe'
outputInstaller = "C:/Users/daniel.perez/Documents/pruebas/TestPy/NoMoreIntros/NoMoreIntros.nsi"

# 0 Install dependencies
os.system('pip3 install -r requirements.txt')
# 1 Compiles app to .exe
os.system('pyinstaller nomoreintros.spec --distpath ./NoMoreIntros --clean')
# 2 7ZIP Creates .zip to portable application
os.system(zipEXE + ' -mx=9 a "./NMI-Portable.zip" "./NoMoreIntros/NoMoreIntros"')
# 3 NSIS Creates installer to application
os.system(nsisEXe + ' ' + outputInstaller)
