import os

# 1 Compiles app to .exe
os.system('pyinstaller nomoreintros.spec --distpath ./NoMoreIntros --clean')
# 2 7ZIP Creates .zip to portable application
os.system('C:/"Program Files"/7-Zip/7z.exe -mx=9 a "./NomoreIntrosPortable.zip" "./NoMoreIntros/NoMoreIntros"')
# 3 NSIS Creates installer to application
os.system('C:/"Program Files (x86)"/NSIS/makensisw.exe C:/Users/daniel.perez/Documents/pruebas/TestPy/NoMoreIntros/NoMoreIntros.nsi')